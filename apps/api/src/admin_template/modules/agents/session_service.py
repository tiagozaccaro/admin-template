"""AgentSession service: persist chat history to the DB.

FR-001 / plan data model require conversation history to be persisted
across restarts. This module provides the persistence path the daemon's
`SessionStore` delegates to when configured.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from admin_template.modules.agents.models.agent_session import AgentSession


async def _session_factory() -> async_sessionmaker[AsyncSession]:
    from admin_template.core.db import db

    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def _get_session(session: AsyncSession | None) -> AsyncSession:
    if session is not None:
        return session
    factory = await _session_factory()
    return factory()


async def upsert_session(
    *,
    agent_id: uuid.UUID,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    session_id: uuid.UUID,
    history: list[dict],
    session: AsyncSession | None = None,
) -> AgentSession:
    """Create or update the history for a chat session.

    When a session row already exists for the given (agent, user, tenant,
    session_id) tuple, its history is replaced; otherwise a new row is
    inserted.
    """
    own_session = session is None
    session = await _get_session(session)
    try:
        result = await session.execute(
            select(AgentSession).where(
                AgentSession.agent_id == agent_id,
                AgentSession.user_id == user_id,
                AgentSession.tenant_id == tenant_id,
                AgentSession.id == session_id,
            )
        )
        existing = result.scalars().first()
        if existing is not None:
            existing.history = history
            existing.updated_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(existing)
            return existing

        entry = AgentSession(
            id=session_id,
            agent_id=agent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            history=history,
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry
    finally:
        if own_session:
            await session.close()


async def load_session(
    session_id: uuid.UUID,
    agent_id: uuid.UUID | None = None,
    session: AsyncSession | None = None,
) -> list[dict] | None:
    """Return the stored history for a session, or None when absent."""
    own_session = session is None
    session = await _get_session(session)
    try:
        stmt = select(AgentSession).where(AgentSession.id == session_id)
        if agent_id is not None:
            stmt = stmt.where(AgentSession.agent_id == agent_id)
        result = await session.execute(stmt)
        entry = result.scalars().first()
        if entry is None:
            return None
        return entry.history or []
    finally:
        if own_session:
            await session.close()


__all__ = ["load_session", "upsert_session"]
