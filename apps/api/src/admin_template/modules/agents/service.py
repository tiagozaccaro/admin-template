"""Agent registry service.

Provides CRUD operations for registered agents with tenant isolation,
token hashing, and default-agent provisioning for self-hosted servers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from admin_template.core.settings import settings
from admin_template.modules.agents.models.agent import Agent, hash_token


async def _session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the initialized async session factory."""
    from admin_template.core.db import db

    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def _get_session(session: AsyncSession | None) -> AsyncSession:
    """Return the passed session or create a new one from the factory."""
    if session is not None:
        return session
    factory = await _session_factory()
    return factory()


async def get_agent_by_token(
    token: str,
    session: AsyncSession | None = None,
) -> Agent | None:
    """Return the agent whose stored token_hash matches the given token.

    Used by the core API to authenticate agent-daemon callbacks (audit
    pushes, status updates) without exposing the raw token.
    """
    own_session = session is None
    session = await _get_session(session)
    try:
        digest = hash_token(token)
        result = await session.execute(
            select(Agent).where(Agent.token_hash == digest)
        )
        return result.scalars().first()
    finally:
        if own_session:
            await session.close()


async def list_agents(
    tenant_id: uuid.UUID,
    session: AsyncSession | None = None,
) -> list[Agent]:
    """Return all agents visible to the given tenant."""
    own_session = session is None
    session = await _get_session(session)
    try:
        result = await session.execute(
            select(Agent).where(Agent.tenant_id == tenant_id)
        )
        return list(result.scalars().all())
    finally:
        if own_session:
            await session.close()


async def get_agent(
    agent_id: uuid.UUID,
    tenant_id: uuid.UUID,
    session: AsyncSession | None = None,
) -> Agent | None:
    """Return a single agent scoped to the tenant, or None."""
    own_session = session is None
    session = await _get_session(session)
    try:
        result = await session.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()
    finally:
        if own_session:
            await session.close()


async def register_agent(
    name: str,
    url: str,
    token: str | None,
    tenant_id: uuid.UUID,
    capabilities: dict | None = None,
    session: AsyncSession | None = None,
) -> Agent:
    """Create a new agent record with tenant isolation.

    Raises ValueError when the agent name already exists for the tenant.
    """
    own_session = session is None
    session = await _get_session(session)
    try:
        existing = await session.execute(
            select(Agent).where(
                Agent.name == name,
                Agent.tenant_id == tenant_id,
            )
        )
        if existing.scalars().first() is not None:
            raise ValueError(
                f"An agent named {name!r} already exists for this tenant"
            )

        agent = Agent(
            name=name,
            url=url,
            token_hash=hash_token(token) if token else None,
            health_token=token,
            capabilities=capabilities,
            tenant_id=tenant_id,
            status="pending",
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        return agent
    finally:
        if own_session:
            await session.close()


async def update_agent(
    agent_id: uuid.UUID,
    tenant_id: uuid.UUID,
    *,
    name: str | None = None,
    url: str | None = None,
    token: str | None = None,
    capabilities: dict | None = None,
    status: str | None = None,
    session: AsyncSession | None = None,
) -> Agent | None:
    """Update an agent's mutable fields. Returns None when not found."""
    own_session = session is None
    session = await _get_session(session)
    try:
        agent = await get_agent(agent_id, tenant_id, session)
        if agent is None:
            return None
        if name is not None:
            agent.name = name
        if url is not None:
            agent.url = url
        if token is not None:
            agent.token_hash = hash_token(token)
            agent.health_token = token
        if capabilities is not None:
            agent.capabilities = capabilities
        if status is not None:
            agent.status = status
        agent.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(agent)
        return agent
    finally:
        if own_session:
            await session.close()


async def delete_agent(
    agent_id: uuid.UUID,
    tenant_id: uuid.UUID,
    session: AsyncSession | None = None,
) -> bool:
    """Delete an agent scoped to the tenant. Returns True when deleted."""
    own_session = session is None
    session = await _get_session(session)
    try:
        agent = await get_agent(agent_id, tenant_id, session)
        if agent is None:
            return False
        await session.delete(agent)
        await session.commit()
        return True
    finally:
        if own_session:
            await session.close()


async def update_agent_status(
    agent_id: uuid.UUID,
    status: str,
    last_seen_at: datetime | None = None,
    session: AsyncSession | None = None,
) -> Agent | None:
    """Update an agent's status (used by health checks)."""
    own_session = session is None
    session = await _get_session(session)
    try:
        result = await session.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalars().first()
        if agent is None:
            return None
        agent.status = status
        agent.last_seen_at = last_seen_at or datetime.now(UTC)
        agent.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(agent)
        return agent
    finally:
        if own_session:
            await session.close()


async def provision_default_agent(tenant_id: uuid.UUID) -> Agent | None:
    """Provision a default local agent for self-hosted servers (FR-010).

    Only creates an agent when one does not already exist for the tenant.
    """
    if not settings.provision_default_agent:
        return None
    url = settings.default_agent_url
    token = settings.default_agent_token
    name = settings.default_agent_name
    existing = await list_agents(tenant_id)
    for agent in existing:
        if agent.name == name:
            return agent
    try:
        return await register_agent(
            name=name,
            url=url,
            token=token,
            tenant_id=tenant_id,
            capabilities={
                "models": [],
                "tools": ["filesystem", "shell"],
                "streaming": True,
            },
        )
    except ValueError:
        return None


__all__ = [
    "delete_agent",
    "get_agent",
    "get_agent_by_token",
    "list_agents",
    "provision_default_agent",
    "register_agent",
    "update_agent",
    "update_agent_status",
]
