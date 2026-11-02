"""Regression tests for audit persistence latency (SC-004).

SC-004 requires all tool invocations appear in the audit log within 1 second.
"""

import asyncio
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from admin_template.modules.agents.audit import persist_audit, update_audit_status
from admin_template.modules.agents.models.audit_entry import AuditEntry


def _patch_factory(session):
    """Patch the audit module's _session_factory to return a session."""
    session_factory = MagicMock(return_value=session)
    return patch(
        "admin_template.modules.agents.audit._session_factory",
        new=AsyncMock(return_value=session_factory),
    )


def test_persist_audit_within_one_second() -> None:
    """SC-004: audit entries must be persisted within 1 second of the call."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    AuditEntry(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        agent_id=agent_id,
        tool_name="write_file",
        args={"path": "/tmp/test.txt"},  # noqa: S108 — test fixture path
        result_summary="written",
        status="ok",
    )

    session = MagicMock()
    session.execute = AsyncMock()
    session.execute.return_value.scalars.return_value.first.return_value = None
    session.add = MagicMock()
    session.commit = AsyncMock()
    # Simulate the DB assigning a UUID on refresh.
    assigned_id = uuid.uuid4()

    async def _refresh(obj):
        obj.id = assigned_id
        return obj

    session.refresh = AsyncMock(side_effect=_refresh)
    session.close = AsyncMock()

    started = time.perf_counter()
    with _patch_factory(session):
        result = asyncio.run(
            persist_audit(
                tenant_id=tenant_id,
                user_id=user_id,
                agent_id=agent_id,
                tool_name="write_file",
                args={"path": "/tmp/test.txt"},  # noqa: S108 — test fixture path
                result_summary="written",
                status="ok",
            )
        )
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert result.id == assigned_id
    assert result.tool_name == "write_file"
    # SC-004: within 1 second (1000ms). Use a generous threshold to avoid
    # flakiness on slow CI runners while still catching real regressions.
    assert elapsed_ms < 1000, (
        f"Audit persistence took {elapsed_ms:.1f}ms, exceeding the 1000ms SC-004 bound"
    )
    # The commit must have been awaited (synchronous persistence).
    assert session.commit.await_count == 1


def test_update_audit_status_marks_entry() -> None:
    """Updating an audit entry's status persists the change."""
    audit_id = uuid.uuid4()
    existing = AuditEntry(
        id=audit_id,
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        tool_name="shell",
        args={"command": "ls"},
        status="pending",
    )

    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = existing
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda obj: obj)
    session.close = AsyncMock()

    with _patch_factory(session):
        updated = asyncio.run(update_audit_status(audit_id, "ok", result_summary="done"))

    assert updated is not None
    assert updated.status == "ok"
    assert updated.result_summary == "done"
    assert session.commit.await_count == 1
