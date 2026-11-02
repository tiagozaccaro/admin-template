"""Agent core.

Wraps Pydantic AI with the agent's tools (filesystem, shell), guardrails,
MCP integration, and skills. Supports both synchronous and streaming
execution.

Destructive tools (FR-006 / SC-003) block on an approval registry: the tool
call suspends until a human resolves the approval via the daemon's
`POST /approve/{id}` endpoint. The registry is passed per chat turn via a
contextvar so concurrent sessions do not share state.
"""

from __future__ import annotations

import contextvars
import json
import logging
import urllib.request
from collections.abc import AsyncIterator, Iterator
from typing import Any

from pydantic_ai import RunContext

from admin_template_agent.agent.guardrails import requires_approval
from admin_template_agent.agent.tools.filesystem import read_file, write_file
from admin_template_agent.agent.tools.shell import run as run_shell
from admin_template_agent.approvals import ApprovalRegistry
from admin_template_agent.audit import log_audit, update_audit_status
from admin_template_agent.config import config
from admin_template_agent.skills import load_skills

logger = logging.getLogger(__name__)

# Per-chat-turn approval registry. Tools read this to suspend on
# destructive actions; the SSE endpoint writes it before streaming.
_approvals_ctx: contextvars.ContextVar[ApprovalRegistry | None] = contextvars.ContextVar(
    "agent_approvals", default=None
)


def _fetch_core_settings() -> tuple[str, dict[str, dict[str, str]]]:
    """Fetch (chat_models_json, provider_settings) from the core API.

    Returns ("[]", {}) when the API is unreachable so the agent can
    still start in local/test mode.
    """
    try:
        req = urllib.request.Request(
            f"{config.api_url.rstrip('/')}/api/v1/settings",
            headers={"Accept": "application/json"},
        )
        if config.api_token:
            req.add_header("Authorization", f"Bearer {config.api_token}")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("chat_models", "[]"), data.get("provider_settings") or {}
    except Exception:
        logger.warning("Failed to fetch settings from core API")
        return "[]", {}


def _make_model() -> Any:
    """Construct a Pydantic AI model from core API settings.

    The model name and provider credentials are fetched from the core
    API's settings endpoint (chat_models + provider_settings) so the
    agent daemon does not need its own model or provider fields
    configured. Returns a string model name when credentials are
    unavailable so the agent can still start in local/test mode.
    """
    try:
        from pydantic_ai.models.openai import OpenAIChatModel
    except Exception:  # pragma: no cover - dependency optional at runtime
        return "test"

    chat_models_json, provider_settings = _fetch_core_settings()
    try:
        chat_models = json.loads(chat_models_json)
    except (json.JSONDecodeError, TypeError):
        chat_models = []
    if not chat_models or not provider_settings:
        # No credentials configured -> fall back to test model string.
        return config.model

    first = chat_models[0]
    provider = first.get("provider") if isinstance(first, dict) else None
    model_name = first.get("model") if isinstance(first, dict) else None
    creds = provider_settings.get(provider) if provider else None
    if not isinstance(creds, dict) or not model_name:
        return config.model

    kwargs: dict[str, Any] = {}
    if creds.get("api_key"):
        kwargs["api_key"] = creds["api_key"]
    if creds.get("base_url"):
        kwargs["base_url"] = creds["base_url"]
    if not kwargs:
        return config.model
    try:
        return OpenAIChatModel(model_name, **kwargs)
    except Exception:
        logger.warning("Failed to construct OpenAI model; using test model")
        return "test"


class AgentCore:
    """Pydantic AI agent with admin tools and guardrails."""

    def __init__(
        self,
        model: str | Any | None = None,
        skills_dir: str | None = None,
    ) -> None:
        from pydantic_ai import Agent

        model = model or _make_model()
        self.agent = Agent(model)
        self.skills = load_skills(skills_dir or config.skills_dir)
        self._register_tools()

    def _register_tools(self) -> None:
        @self.agent.tool
        def read_file_tool(ctx: RunContext[object], path: str) -> str:
            """Read a file from the local filesystem."""
            return read_file(path)

        @self.agent.tool
        def write_file_tool(
            ctx: RunContext[object],
            path: str,
            content: str,
        ) -> str:
            """Write content to a file on the local filesystem."""
            approvals = _approvals_ctx.get()
            if requires_approval("write_file"):
                audit_id = log_audit(
                    {
                        "tool_name": "write_file",
                        "args": {"path": path},
                        "status": "pending_approval",
                    }
                )
                if approvals is None:
                    return "approval required"
                approved = approvals.request_approval(
                    "write_file",
                    {"path": path, "content": content},
                    f"write {len(content)} bytes to {path}",
                )
                if not approved:
                    update_audit_status(audit_id, "denied", "user denied write_file")
                    return "denied by user"
                write_file(path, content)
                update_audit_status(audit_id, "ok", "written")
                return "written"
            write_file(path, content)
            log_audit(
                {
                    "tool_name": "write_file",
                    "args": {"path": path},
                    "result_summary": "written",
                    "status": "ok",
                }
            )
            return "written"

        @self.agent.tool
        def shell_tool(ctx: RunContext[object], command: str) -> str:
            """Run a shell command."""
            approvals = _approvals_ctx.get()
            if requires_approval("shell"):
                audit_id = log_audit(
                    {
                        "tool_name": "shell",
                        "args": {"command": command},
                        "status": "pending_approval",
                    }
                )
                if approvals is None:
                    return "approval required"
                if not config.allow_shell:
                    update_audit_status(audit_id, "denied", "shell tool disabled")
                    return "shell tool disabled"
                approved = approvals.request_approval(
                    "shell",
                    {"command": command},
                    f"run shell command: {command}",
                )
                if not approved:
                    update_audit_status(audit_id, "denied", "user denied shell command")
                    return "denied by user"
                result = run_shell(command)
                update_audit_status(
                    audit_id,
                    "ok" if result.returncode == 0 else "error",
                    (result.stdout or result.stderr)[:500],
                )
                return result.stdout or result.stderr
            if not config.allow_shell:
                return "shell tool disabled"
            result = run_shell(command)
            log_audit(
                {
                    "tool_name": "shell",
                    "args": {"command": command},
                    "result_summary": (result.stdout or result.stderr)[:500],
                    "status": "ok" if result.returncode == 0 else "error",
                }
            )
            return result.stdout or result.stderr

    def chat(self, message: str) -> str:
        """Run a synchronous chat turn and return the final output."""
        result = self.agent.run_sync(message)
        return str(result.output)

    async def chat_stream(
        self,
        message: str,
        approvals: ApprovalRegistry | None = None,
    ) -> AsyncIterator[str]:
        """Stream chat output token-by-token as an async iterator.

        When `approvals` is provided, destructive tools will block on the
        registry and the SSE endpoint will emit `approval_request` events
        for the client to resolve.
        """
        token = None
        if approvals is not None:
            token = _approvals_ctx.set(approvals)
        try:
            async with self.agent.run_stream(message) as result:
                async for chunk in result.stream_text():
                    yield chunk
        finally:
            if token is not None:
                _approvals_ctx.reset(token)

    def chat_stream_sync(
        self,
        message: str,
        approvals: ApprovalRegistry | None = None,
    ) -> Iterator[str]:
        """Stream chat output token-by-token as a sync iterator."""
        token = None
        if approvals is not None:
            token = _approvals_ctx.set(approvals)
        try:
            for chunk in self.agent.run_stream_sync(message).stream_text():
                yield chunk
        finally:
            if token is not None:
                _approvals_ctx.reset(token)


__all__ = ["AgentCore", "_approvals_ctx"]
