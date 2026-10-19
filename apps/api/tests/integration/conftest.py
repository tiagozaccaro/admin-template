"""Conftest for integration tests."""

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.auth import sessions


@pytest.fixture(autouse=True)
def mock_auth(monkeypatch: pytest.MonkeyPatch):
    async def fake_get_current_user():
        from admin_template.modules.identity.models.user import User

        return User(keycloak_sub="sub", email="test@test.com", display_name="Test")

    monkeypatch.setattr(
        "admin_template.auth.sessions.get_current_user_from_session",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        sessions, "get_current_user_from_session", fake_get_current_user
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
