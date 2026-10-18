"""Conftest for E2E smoke tests."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.modules.identity.service import IdentityLinkError


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def patch_auth_for_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_start():
        return SimpleNamespace(
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth?state=abc",
            state="abc",
            nonce="nonce-123",
        )

    async def fake_exchange(code: str, state: str):
        return SimpleNamespace(
            tokens=SimpleNamespace(id_token="valid.id.token", access_token="at"),
            nonce="nonce-123",
        )

    async def fake_validate(id_token: str, expected_nonce: str):
        return SimpleNamespace(
            sub="google-sub-1",
            email="user@example.com",
            email_verified=True,
        )

    class _FakeUser:
        def __init__(self) -> None:
            self.id = "00000000-0000-0000-0000-000000000001"
            self.keycloak_sub = "google-sub-1"
            self.email = "user@example.com"
            self.display_name = "Test User"

    class _FakeSession:
        def __init__(self) -> None:
            self.id = "00000000-0000-0000-0000-000000000002"

    async def fake_get_or_create(claims):
        return _FakeUser()

    async def fake_create_session(user_id):
        return _FakeSession()

    async def fake_revoke_session(session_id):
        pass

    async def fake_get_user_from_session(session_id, credentials=None):
        # For smoke tests, we want to validate unauth behavior separately
        # But for integration context, we can be flexible
        token = session_id or (credentials.credentials if credentials else None)
        if token == "00000000-0000-0000-0000-000000000002" or token == "Bearer 00000000-0000-0000-0000-000000000002":
            return _FakeUser()
        raise Exception("Invalid session")

    monkeypatch.setattr(
        "admin_template.auth.router.build_authorization_url", fake_start
    )
    monkeypatch.setattr("admin_template.auth.router.exchange_code", fake_exchange)
    monkeypatch.setattr("admin_template.auth.router.validate_id_token", fake_validate)
    monkeypatch.setattr(
        "admin_template.auth.router.get_or_create_user_from_claims",
        fake_get_or_create,
    )
    monkeypatch.setattr(
        "admin_template.auth.router.create_session", fake_create_session
    )
    monkeypatch.setattr(
        "admin_template.auth.router.revoke_session", fake_revoke_session
    )
