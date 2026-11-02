"""Agent registry REST endpoints.

Implements the full agent contract from contracts/api.md with tenant
isolation enforced at the service layer.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.modules.agents import service as agent_service
from admin_template.modules.agents.audit import list_audit as list_audit_entries
from admin_template.modules.agents.audit import persist_audit, update_audit_status
from admin_template.modules.agents.models.agent import Agent
from admin_template.modules.identity.models.user import User
from admin_template.modules.tenancy.models.tenant_membership import TenantRole

_bearer_scheme = HTTPBearer(auto_error=False)

router = APIRouter(tags=["agents"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AgentCreate(BaseModel):
    name: str
    url: str
    token: str | None = None
    capabilities: dict | None = None

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("url must not be empty")
        return value


class AgentUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    token: str | None = None
    capabilities: dict | None = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    capabilities: dict | None = None
    tenant_id: uuid.UUID
    status: str
    last_seen_at: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    latency_ms: int | None = None


class AuditEntryResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    agent_id: uuid.UUID
    tool_name: str
    args: dict | None = None
    result_summary: str | None = None
    status: str
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/audit", response_model=list[AuditEntryResponse])
async def list_audit(
    user: Annotated[User, Depends(get_current_user_from_session)],
    agent_id: uuid.UUID | None = Query(default=None),
    tool_name: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    """Return audit entries for the user's tenant, newest first."""
    tenant_id = await _get_tenant_id(user)
    entries = await list_audit_entries(
        tenant_id,
        agent_id=agent_id,
        tool_name=tool_name,
        limit=limit,
    )
    return [
        AuditEntryResponse(
            id=e.id,
            tenant_id=e.tenant_id,
            user_id=e.user_id,
            agent_id=e.agent_id,
            tool_name=e.tool_name,
            args=e.args,
            result_summary=e.result_summary,
            status=e.status,
            created_at=e.created_at.isoformat(),
        )
        for e in entries
    ]


# ---------------------------------------------------------------------------
# Chat proxy
# ---------------------------------------------------------------------------


@router.post("/{agent_id}/chat")
async def chat_with_agent(
    agent_id: uuid.UUID,
    body: dict,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    """Proxy a chat request to a registered agent and stream the response."""
    tenant_id = await _get_tenant_id(user)
    agent = await agent_service.get_agent(agent_id, tenant_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    prompt_input = body.get("prompt_input") or body.get("message") or ""
    if not prompt_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prompt_input is required",
        )

    async def _stream() -> AsyncIterator[str]:
        import json

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    agent.url.rstrip("/") + "/chat/agent",
                    json={
                        "prompt_input": prompt_input,
                        "model": body.get("model"),
                        "session_id": body.get("session_id"),
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        yield f"{line}\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)[:500]})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


__all__ = ["router", "_check_agent_admin_role"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_tenant_id(user: User) -> uuid.UUID:
    """Resolve the user's active tenant id."""
    from admin_template.modules.tenancy import ownership as ownership_service

    tenant = await ownership_service.get_default_tenant(user.id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no tenant. Create one first.",
        )
    return tenant.id


async def _check_agent_admin_role(user: User, tenant_id: uuid.UUID) -> bool:
    """Return True when *user* is an ADMIN or OWNER of *tenant_id*."""
    from admin_template.core.db import db
    from admin_template.modules.tenancy.models.tenant_membership import (
        TenantMembership,
    )

    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    async with db.session_factory() as session:
        result = await session.execute(
            TenantMembership.__table__.select().where(
                (TenantMembership.tenant_id == tenant_id) & (TenantMembership.user_id == user.id)
            )
        )
        row = result.first()
    return not (row is None or row.role not in (TenantRole.ADMIN, TenantRole.OWNER))


async def _require_agent_admin(
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> tuple[User, uuid.UUID]:
    """Require the user to be an admin or owner of their tenant.

    Returns (user, tenant_id) for use by mutating agent endpoints.
    """
    tenant_id = await _get_tenant_id(user)
    if not await _check_agent_admin_role(user, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions: admin or owner role required",
        )
    return user, tenant_id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    user: Annotated[User, Depends(get_current_user_from_session)],
    limit: int = Query(default=100, ge=1, le=500),
):
    tenant_id = await _get_tenant_id(user)
    agents = await agent_service.list_agents(tenant_id)
    return [_agent_response(a) for a in agents[:limit]]


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreate,
    user: Annotated[User, Depends(get_current_user_from_session)],
    admin: Annotated[tuple[User, uuid.UUID], Depends(_require_agent_admin)],
):
    tenant_id = await _get_tenant_id(user)
    try:
        agent = await agent_service.register_agent(
            name=body.name,
            url=body.url,
            token=body.token,
            tenant_id=tenant_id,
            capabilities=body.capabilities,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _agent_response(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    tenant_id = await _get_tenant_id(user)
    agent = await agent_service.get_agent(agent_id, tenant_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return _agent_response(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    body: AgentUpdate,
    user: Annotated[User, Depends(get_current_user_from_session)],
    _: Annotated[None, Depends(_require_agent_admin)],
):
    tenant_id = await _get_tenant_id(user)
    agent = await agent_service.update_agent(
        agent_id,
        tenant_id,
        name=body.name,
        url=body.url,
        token=body.token,
        capabilities=body.capabilities,
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return _agent_response(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
    _: Annotated[None, Depends(_require_agent_admin)],
):
    tenant_id = await _get_tenant_id(user)
    deleted = await agent_service.delete_agent(agent_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")


@router.post("/{agent_id}/health", response_model=HealthResponse)
async def health_check_agent(
    agent_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    """Probe a registered agent's /health endpoint and update status."""
    tenant_id = await _get_tenant_id(user)
    agent = await agent_service.get_agent(agent_id, tenant_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    status_value, latency_ms = await _probe_agent(agent)
    await agent_service.update_agent_status(
        agent.id,
        status_value,
    )
    return HealthResponse(status=status_value, latency_ms=latency_ms)


async def _probe_agent(agent: Agent) -> tuple[str, int | None]:
    """Perform an HTTP health probe against the agent daemon."""
    import time

    url = agent.url.rstrip("/") + "/health"
    headers = {}
    token = getattr(agent, "_raw_token", None) or getattr(agent, "registration_token", None)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers)
        latency = int((time.perf_counter() - started) * 1000)
        if resp.status_code == 200:
            return "healthy", latency
        if resp.status_code in (401, 403):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp2 = await client.get(url)
                latency = int((time.perf_counter() - started) * 1000)
                if resp2.status_code == 200:
                    return "healthy", latency
            except Exception:  # noqa: S110 — best-effort fallback
                pass
            return "unhealthy", latency
        return "unhealthy", latency
    except Exception:
        latency = int((time.perf_counter() - started) * 1000)
        return "offline", latency


def _agent_response(agent: Agent) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        url=agent.url,
        capabilities=agent.capabilities,
        tenant_id=agent.tenant_id,
        status=agent.status,
        last_seen_at=agent.last_seen_at.isoformat() if agent.last_seen_at else None,
        created_at=agent.created_at.isoformat(),
    )


@router.post("/audit", response_model=AuditEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    body: dict,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
):
    """Accept an audit record pushed by a registered agent daemon.

    Authenticates the agent by its bearer token (the same token stored at
    registration), then persists the entry under the agent's tenant. This is
    the path by which tool invocations from `apps/agent` reach the web audit
    log (FR-007 / SC-004).
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    agent = await agent_service.get_agent_by_token(credentials.credentials)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown agent token",
        )

    tool_name = body.get("tool_name")
    if not tool_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tool_name is required",
        )
    entry = await persist_audit(
        tenant_id=agent.tenant_id,
        user_id=body.get("user_id") or agent.tenant_id,
        agent_id=agent.id,
        tool_name=tool_name,
        args=body.get("args"),
        result_summary=body.get("result_summary"),
        status=body.get("status", "pending"),
    )
    return AuditEntryResponse(
        id=entry.id,
        tenant_id=entry.tenant_id,
        user_id=entry.user_id,
        agent_id=entry.agent_id,
        tool_name=entry.tool_name,
        args=entry.args,
        result_summary=entry.result_summary,
        status=entry.status,
        created_at=entry.created_at.isoformat(),
    )


@router.patch("/audit/{audit_id}", response_model=AuditEntryResponse)
async def update_audit(
    audit_id: uuid.UUID,
    body: dict,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
):
    """Update an audit entry's status/summary (pushed by the agent daemon)."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    agent = await agent_service.get_agent_by_token(credentials.credentials)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown agent token",
        )
    entry = await update_audit_status(
        audit_id,
        body.get("status", "ok"),
        result_summary=body.get("result_summary"),
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit entry not found")
    return AuditEntryResponse(
        id=entry.id,
        tenant_id=entry.tenant_id,
        user_id=entry.user_id,
        agent_id=entry.agent_id,
        tool_name=entry.tool_name,
        args=entry.args,
        result_summary=entry.result_summary,
        status=entry.status,
        created_at=entry.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
