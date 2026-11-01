"""Regression tests for agent-management RBAC enforcement (FR-009).

Constitution Article VI requires access-control rules to be verified by
automated tests, not just enforced server-side. These tests assert that
non-admin/non-owner roles receive 403 on POST/PATCH/DELETE agent
endpoints while admins/owners proceed.
"""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.auth.sessions import get_current_user_from_session
from admin_template.modules.agents import router as agent_router
from admin_template.modules.agents import service as agent_service
from admin_template.modules.tenancy import ownership as ownership_service
from admin_template.modules.tenancy.models.tenant_membership import TenantRole


def _make_user(role: TenantRole) -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "user@example.com"
    user.role = role
    return user


def _make_agent_response(agent_id: uuid.UUID, tenant_id: uuid.UUID) -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=agent_id,
        name="x",
        url="http://localhost:8100",
        capabilities={},
        tenant_id=tenant_id,
        status="active",
        last_seen_at=None,
        created_at=now,
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _mock_ownership(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_default_tenant(user_id):
        tenant = MagicMock()
        tenant.id = uuid.uuid4()
        return tenant

    monkeypatch.setattr(
        ownership_service, "get_default_tenant", fake_get_default_tenant
    )


@pytest.fixture
def rbac(monkeypatch: pytest.MonkeyPatch):
    """Provide a callable that overrides the RBAC check for the current test."""

    def _patch(user: MagicMock, allowed: bool) -> None:
        async def override_session():
            return user

        async def override_check_role(_user, _tenant_id):
            return allowed

        monkeypatch.setattr(
            agent_router,
            "_check_agent_admin_role",
            override_check_role,
        )
        app.dependency_overrides[get_current_user_from_session] = override_session

    return _patch


def test_create_agent_requires_admin_role(client: TestClient, rbac) -> None:
    """POST / must return 403 for a MEMBER role."""
    rbac(_make_user(TenantRole.MEMBER), allowed=False)
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "x",
            "url": "http://localhost:8100",
            "token": "t",
            "capabilities": {},
        },
    )
    assert response.status_code == 403, response.text


def test_create_agent_allows_owner_role(
    client: TestClient, rbac, monkeypatch
) -> None:
    """POST / must allow OWNER role and return 201."""
    user = _make_user(TenantRole.OWNER)
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    fake_agent = _make_agent_response(agent_id, tenant_id)

    async def override_register_agent(*a, **kw):
        return fake_agent

    rbac(user, allowed=True)
    monkeypatch.setattr(agent_service, "register_agent", override_register_agent)
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "x",
            "url": "http://localhost:8100",
            "token": "t",
            "capabilities": {},
        },
    )
    assert response.status_code == 201, response.text


def test_update_agent_requires_admin_role(client: TestClient, rbac) -> None:
    """PATCH /{id} must return 403 for a MEMBER role."""
    rbac(_make_user(TenantRole.MEMBER), allowed=False)
    response = client.patch(
        "/api/v1/agents/" + str(uuid.uuid4()),
        json={"name": "renamed"},
    )
    assert response.status_code == 403, response.text


def test_delete_agent_requires_admin_role(client: TestClient, rbac) -> None:
    """DELETE /{id} must return 403 for a MEMBER role."""
    rbac(_make_user(TenantRole.MEMBER), allowed=False)
    response = client.delete("/api/v1/agents/" + str(uuid.uuid4()))
    assert response.status_code == 403, response.text


def test_delete_agent_allows_admin_role(
    client: TestClient, rbac, monkeypatch
) -> None:
    """DELETE /{id} must allow ADMIN role and return 204."""
    user = _make_user(TenantRole.ADMIN)

    async def override_delete_agent(*a, **kw):
        return True

    rbac(user, allowed=True)
    monkeypatch.setattr(agent_service, "delete_agent", override_delete_agent)
    response = client.delete("/api/v1/agents/" + str(uuid.uuid4()))
    assert response.status_code == 204, response.text


def test_viewer_role_blocked_on_all_mutations(client: TestClient, rbac) -> None:
    """VIEWER role must be blocked on POST, PATCH, and DELETE."""
    rbac(_make_user(TenantRole.VIEWER), allowed=False)
    assert (
        client.post(
            "/api/v1/agents",
            json={
                "name": "x",
                "url": "http://localhost:8100",
                "token": "t",
                "capabilities": {},
            },
        ).status_code
        == 403
    )
    assert (
        client.patch(
            "/api/v1/agents/" + str(uuid.uuid4()),
            json={"name": "renamed"},
        ).status_code
        == 403
    )
    assert (
        client.delete("/api/v1/agents/" + str(uuid.uuid4())).status_code
        == 403
    )
