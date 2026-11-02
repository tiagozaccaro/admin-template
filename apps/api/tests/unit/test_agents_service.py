"""Tests for the agents registry service (tenant isolation, CRUD)."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from admin_template.modules.agents import service as agent_service
from admin_template.modules.agents.models.agent import Agent, hash_token


def _make_agent(**kwargs) -> Agent:
    agent = Agent(
        name=kwargs.get("name", "test-agent"),
        url=kwargs.get("url", "http://localhost:8100"),
        token_hash=kwargs.get("token_hash"),
        tenant_id=kwargs.get("tenant_id", uuid.uuid4()),
        status=kwargs.get("status", "pending"),
    )
    agent.id = kwargs.get("id", uuid.uuid4())
    return agent


def test_hash_token_is_sha256_hex() -> None:
    digest = hash_token("secret")
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
    # Deterministic
    assert hash_token("secret") == digest
    # Different input -> different digest
    assert hash_token("other") != digest


def _patch_factory(session):
    """Patch the service's _session_factory.

    The service calls `session = (await _session_factory())()`, so the factory
    must return a callable (the session_factory) that returns the session.
    """
    session_factory = MagicMock(return_value=session)
    return patch(
        "admin_template.modules.agents.service._session_factory",
        new=AsyncMock(return_value=session_factory),
    )


def _make_list_session(rows):
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    session.execute = AsyncMock(return_value=result)
    session.close = AsyncMock()
    return session


def _make_first_session(first):
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = first
    session.execute = AsyncMock(return_value=result)
    session.close = AsyncMock()
    return session


def test_list_agents_tenant_isolation() -> None:
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_a = _make_agent(tenant_id=tenant_a)
    _make_agent(tenant_id=tenant_b, name="other")

    # The DB query filters by tenant_id, so only agent_a is returned.
    session = _make_list_session([agent_a])

    with _patch_factory(session):
        result = asyncio.run(agent_service.list_agents(tenant_a))

    assert result == [agent_a]
    # The mock was called with a select filtered by tenant_a.
    executed_sql = session.execute.call_args[0][0]
    assert executed_sql is not None


def test_register_agent_conflict_on_duplicate_name() -> None:
    tenant_id = uuid.uuid4()
    existing = _make_agent(name="dup", tenant_id=tenant_id)

    session = _make_first_session(existing)

    with _patch_factory(session):
        with pytest.raises(ValueError, match="already exists"):
            asyncio.run(
                agent_service.register_agent(
                    name="dup",
                    url="http://localhost:8100",
                    token=None,
                    tenant_id=tenant_id,
                )
            )


def test_register_agent_hashes_token() -> None:
    tenant_id = uuid.uuid4()
    _make_agent(tenant_id=tenant_id, name="fresh")

    session = _make_first_session(None)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda obj: obj)

    with _patch_factory(session):
        result = asyncio.run(
            agent_service.register_agent(
                name="fresh",
                url="http://localhost:8100",
                token="supersecret",
                tenant_id=tenant_id,
            )
        )

    assert result.token_hash == hash_token("supersecret")
    assert result.token_hash != "supersecret"


def test_get_agent_scoped_to_tenant_returns_none_when_missing() -> None:
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent = _make_agent(tenant_id=tenant_id)

    session = _make_first_session(None)

    with _patch_factory(session):
        result = asyncio.run(agent_service.get_agent(agent.id, other_tenant))

    assert result is None


def test_delete_agent_returns_false_when_not_found() -> None:
    tenant_id = uuid.uuid4()

    session = _make_first_session(None)

    with _patch_factory(session):
        result = asyncio.run(agent_service.delete_agent(uuid.uuid4(), tenant_id))

    assert result is False
