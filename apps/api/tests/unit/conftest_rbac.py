"""Shared fixtures for agent-management RBAC tests.

Patches the ownership + DB session dependencies so that the RBAC check in
``_require_agent_admin`` can be exercised without a live database.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.auth.sessions import get_current_user_from_session
from admin_template.core.db import db as test_db
from admin_template.modules.tenancy import ownership as ownership_service


@pytest.fixture(autouse=True)
def _patch_ownership_and_db(monkeypatch):
    """Mock the tenant-ownership lookup and the RBAC DB query."""

    async def fake_get_default_tenant(user_id):
        tenant = MagicMock()
        tenant.id = uuid.uuid4()
        return tenant

    monkeypatch.setattr(ownership_service, "get_default_tenant", fake_get_default_tenant)

    membership_row = MagicMock()
    membership_row.role = "member"

    session = MagicMock()
    result = MagicMock()
    result.first.return_value = membership_row
    session.execute = AsyncMock(return_value=result)
    session.close = AsyncMock()
    test_db.session_factory = MagicMock(return_value=session)

    yield

    app.dependency_overrides.clear()
    test_db.session_factory = None


@pytest.fixture
def client() -> "TestClient":
    return TestClient(app)


def set_membership_role(role: str) -> None:
    """Override the mocked membership row's role for the current test."""
    session = test_db.session_factory.return_value  # type: ignore[attr-defined]
    session.execute.return_value.first.return_value.role = role


def override_session(user) -> None:
    async def override_session():
        return user

    app.dependency_overrides[get_current_user_from_session] = override_session
