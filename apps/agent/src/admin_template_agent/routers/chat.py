"""Chat router for the agent daemon.

Implements the contract from contracts/api.md:
- GET /health
- GET /models
- POST /chat/agent -> SSE stream
- GET /tools
- GET/PUT /config
- GET /sessions/{id}
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from admin_template_agent.agent.core import AgentCore, _fetch_core_settings
from admin_template_agent.approvals import ApprovalRegistry, new_registry
from admin_template_agent.audit import log_audit
from admin_template_agent.auth import verify_admin_token, verify_token
from admin_template_agent.config import config
from admin_template_agent.session import SessionStore

logger = logging.getLogger(__name__)


router = APIRouter()

_agent = AgentCore()
_sessions = SessionStore()

# Active approval registries keyed by session_id
_approvals_by_session: dict[str, ApprovalRegistry] = {}

_TOOLS: list[dict] = [
    {"name": "read_file", "description": "Read a file from the local filesystem", "destructive": False},
    {"name": "write_file", "description": "Write content to a file on the local filesystem", "destructive": True},
    {"name": "shell", "description": "Run a shell command", "destructive": True},
]


def _get_agent() -> AgentCore:
    return _agent


def _get_sessions() -> SessionStore:
    return _sessions


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent": config.agent_name, "model": config.model}


def _fetch_core_models() -> list[dict]:
    """Fetch the configured chat models from the core API.

    Returns a list of {id, provider, owned_by} dicts. Falls back to the
    local config when the API is unreachable.
    """
    import json

    try:
        chat_models_json, _ = _fetch_core_settings()
        chat_models = json.loads(chat_models_json)
        return [
            {
                "id": entry.get("model"),
                "provider": entry.get("provider"),
                "owned_by": entry.get("provider"),
            }
            for entry in chat_models
            if isinstance(entry, dict)
            and entry.get("model")
            and entry.get("provider")
        ]
    except Exception:
        logger.warning("Failed to fetch models from core API")
        return [
            {
                "id": config.model,
                "provider": config.model_provider,
                "owned_by": config.model_provider,
            }
        ]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@router.get("/models")
async def list_models() -> list[dict]:
    return _fetch_core_models()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@router.get("/tools")
async def list_tools() -> list[dict]:
    """List the tools registered on this agent."""
    return list(_TOOLS)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@router.get("/config")
async def get_config(
    token: Annotated[str | None, Depends(verify_token)],
) -> dict:
    chat_models_json, provider_settings = _fetch_core_settings()
    try:
        chat_models = json.loads(chat_models_json)
    except (json.JSONDecodeError, TypeError):
        chat_models = []
    return {
        "agent_name": config.agent_name,
        "agent_id": config.agent_id,
        "chat_models": chat_models,
        "provider_settings": provider_settings,
        "tools": [t["name"] for t in _TOOLS],
        "allow_shell": config.allow_shell,
        "require_approval_for_destructive": config.require_approval_for_destructive,
        "mcp_servers": config.mcp_servers or [],
        "skills": [s.name for s in _agent.skills],
    }


@router.put("/config")
async def update_config(
    body: dict,
    token: Annotated[str | None, Depends(verify_admin_token)],
) -> dict:
    """Update agent configuration at runtime (FR-008, FR-009).

    Requires the admin token. Allowed keys: prompt, tools, mcp_servers,
    skills, allow_shell, require_approval_for_destructive. Model and
    provider are configured on the core API settings page, not here.
    """
    allowed = {
        "prompt",
        "tools",
        "mcp_servers",
        "skills",
        "allow_shell",
        "require_approval_for_destructive",
    }
    for key, value in body.items():
        if key in allowed:
            setattr(config, key, value)
    return await get_config(token)


# ---------------------------------------------------------------------------
# Approvals
# ---------------------------------------------------------------------------


@router.post("/approve/{approval_id}")
async def approve_action(
    approval_id: str,
    body: dict,
    token: Annotated[str | None, Depends(verify_token)],
) -> dict:
    """Resolve a pending destructive-action approval (FR-006 / SC-003).

    Body: { "approved": true|false }
    Returns the updated approval status.
    """
    approved = bool(body.get("approved", False))
    registry = _approvals_by_session.get(_session_for_approval(approval_id))
    if registry is None:
        # Fall back to a global lookup across all active sessions.
        for reg in _approvals_by_session.values():
            if reg.status(approval_id) is not None:
                registry = reg
                break
    if registry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found or already resolved",
        )
    if not registry.resolve(approval_id, approved):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found or already resolved",
        )
    return registry.status(approval_id) or {"id": approval_id, "resolved": True}


def _session_for_approval(approval_id: str) -> str:
    """Return the session_id whose registry holds the given approval id."""
    for sid, reg in _approvals_by_session.items():
        if reg.status(approval_id) is not None:
            return sid
    return ""


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    token: Annotated[str | None, Depends(verify_token)],
) -> dict:
    history = _sessions.load(session_id)
    return {"session_id": session_id, "history": history}


# ---------------------------------------------------------------------------
# Chat (SSE streaming)
# ---------------------------------------------------------------------------


@router.post("/chat/agent")
async def chat_agent(
    body: dict,
    token: Annotated[str | None, Depends(verify_token)],
) -> StreamingResponse:
    """Stream a chat response as Server-Sent Events.

    Request body: { prompt_input, model, session_id }
    """
    prompt_input = body.get("prompt_input") or body.get("message") or ""
    session_id = body.get("session_id") or "default"

    if not prompt_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prompt_input is required",
        )

    # Persist user message.
    _sessions.append(session_id, "user", prompt_input)

    # Create approval registry for this turn
    approvals = new_registry()
    _approvals_by_session[session_id] = approvals

    async def event_stream() -> AsyncIterator[str]:
        import time

        started = time.perf_counter()
        first_token_emitted = False

        async def _drain_approvals() -> AsyncIterator[str]:
            """Forward any queued approval requests and block on resolution."""
            while not approvals.queue.empty():
                try:
                    approval_req = approvals.queue.get_nowait()
                except Exception:
                    break
                payload = json.dumps({"approval_request": approval_req})
                yield f"data: {payload}\n\n"
                approval_id = approval_req.get("id")
                if approval_id:
                    await approvals.wait_for_resolve(approval_id)

        try:
            async for chunk in _agent.chat_stream(prompt_input, approvals=approvals):
                _sessions.append(session_id, "assistant", chunk)
                # Forward approvals that arrived while streaming tokens.
                async for event in _drain_approvals():
                    yield event
                latency_ms = int((time.perf_counter() - started) * 1000)
                if not first_token_emitted:
                    payload = json.dumps(
                        {"delta": chunk, "first_token_ms": latency_ms}
                    )
                    first_token_emitted = True
                else:
                    payload = json.dumps({"delta": chunk})
                yield f"data: {payload}\n\n"
            # Drain any approvals that arrived after the last token.
            async for event in _drain_approvals():
                yield event
        except Exception as exc:  # pragma: no cover - defensive
            log_audit(
                {
                    "tool_name": "chat",
                    "args": {"prompt_input": prompt_input[:200]},
                    "result_summary": str(exc)[:500],
                    "status": "error",
                }
            )
            payload = json.dumps({"error": str(exc)[:500]})
            yield f"data: {payload}\n\n"
        finally:
            _approvals_by_session.pop(session_id, None)
        total_ms = int((time.perf_counter() - started) * 1000)
        payload = json.dumps({"latency_ms": total_ms, "done": True})
        yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat")
async def chat(
    body: dict,
    token: Annotated[str | None, Depends(verify_token)],
) -> dict:
    """Non-streaming chat endpoint."""
    prompt_input = body.get("prompt_input") or body.get("message") or ""
    if not prompt_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prompt_input is required",
        )
    _sessions.append("default", "user", prompt_input)
    reply = _agent.chat(prompt_input)
    _sessions.append("default", "assistant", reply)
    return {"reply": reply}


__all__ = ["router"]
