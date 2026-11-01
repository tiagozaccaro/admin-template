"""Audit persistence for agent tool invocations.

Every tool call executed by an agent is recorded here so it can be viewed
in the web audit log and surfaced to administrators.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from admin_template.modules.agents.models.audit_entry import AuditEntry


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


async def persist_audit(
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    agent_id: uuid.UUID,
    tool_name: str,
    args: dict | None = None,
    result_summary: str | None = None,
    status: str = "pending",
    session: AsyncSession | None = None,
) -> AuditEntry:
    """Persist an audit record and return the created entry."""
    own_session = session is None
    session = await _get_session(session)
    try:
        entry = AuditEntry(
            tenant_id=tenant_id,
            user_id=user_id,
            agent_id=agent_id,
            tool_name=tool_name,
            args=args,
            result_summary=result_summary,
            status=status,
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry
    finally:
        if own_session:
            await session.close()


async def update_audit_status(
    audit_id: uuid.UUID,
    status: str,
    result_summary: str | None = None,
    session: AsyncSession | None = None,
) -> AuditEntry | None:
    """Update the status/summary of an existing audit entry."""
    own_session = session is None
    session = await _get_session(session)
    try:
        result = await session.execute(
            select(AuditEntry).where(AuditEntry.id == audit_id)
        )
        entry = result.scalars().first()
        if entry is None:
            return None
        entry.status = status
        if result_summary is not None:
            entry.result_summary = result_summary
        await session.commit()
        await session.refresh(entry)
        return entry
    finally:
        if own_session:
            await session.close()


async def list_audit(
    tenant_id: uuid.UUID,
    *,
    agent_id: uuid.UUID | None = None,
    tool_name: str | None = None,
    limit: int = 100,
    session: AsyncSession | None = None,
) -> list[AuditEntry]:
    """Return audit entries for a tenant, newest first."""
    own_session = session is None
    session = await _get_session(session)
    try:
        stmt = select(AuditEntry).where(AuditEntry.tenant_id == tenant_id)
        if agent_id is not None:
            stmt = stmt.where(AuditEntry.agent_id == agent_id)
        if tool_name is not None:
            stmt = stmt.where(AuditEntry.tool_name == tool_name)
        stmt = stmt.order_by(AuditEntry.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    finally:
        if own_session:
            await session.close()


__all__ = ["list_audit", "persist_audit", "update_audit_status"]
