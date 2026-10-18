"""Integration tests for Google OIDC authentication (US2).

Covers the authorization start, callback (success / error / missing params /
invalid state / tampered ID token / identity link conflict), logout, and
session revocation. All external OIDC calls and database-backed service
calls are monkeypatched so these tests run without network or PostgreSQL.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.modules.identity.service import IdentityLinkError


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class _FakeUser:
    def __init__(self) -> None:
        self.id = "00000000-0000-0000-0000-000000000001"


class _FakeSession:
    def __init__(self) -> None:
        self.id = "00000000-0000-0000-0000-000000000002"


def _patch_auth(monkeypatch: pytest.MonkeyPatch) -> None:
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

    async def fake_get_or_create(claims):
        return _FakeUser()

    async def fake_create_session(user_id):
        return _FakeSession()

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


def test_google_start_returns_url_state_nonce(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)
    response = client.get("/auth/google/start")
    assert response.status_code == 200
    body = response.json()
    assert "authorization_url" in body
    assert body["state"] == "abc"
    assert body["nonce"] == "nonce-123"


def test_callback_success_returns_session(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)
    response = client.get(
        "/auth/callback?code=auth-code&state=abc", follow_redirects=False
    )
    assert response.status_code in (301, 302, 307, 308)
    assert "session_id" in response.headers["location"]


def test_callback_error_returns_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)
    response = client.get("/auth/callback?error=access_denied")
    assert response.status_code == 400


def test_callback_missing_code_returns_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)
    response = client.get("/auth/callback?state=abc")
    assert response.status_code == 400


def test_callback_missing_state_returns_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)
    response = client.get("/auth/callback?code=auth-code")
    assert response.status_code == 400


def test_callback_invalid_state_returns_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)

    async def fake_exchange(code: str, state: str):
        raise ValueError("Invalid or expired authorization state")

    monkeypatch.setattr("admin_template.auth.router.exchange_code", fake_exchange)
    response = client.get("/auth/callback?code=auth-code&state=stale")
    assert response.status_code == 400


def test_callback_tampered_id_token_returns_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)

    async def fake_validate(id_token: str, expected_nonce: str):
        raise ValueError("Invalid token")

    monkeypatch.setattr("admin_template.auth.router.validate_id_token", fake_validate)
    response = client.get("/auth/callback?code=auth-code&state=abc")
    assert response.status_code == 400


def test_callback_identity_link_conflict_returns_409(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_auth(monkeypatch)

    async def fake_get_or_create(claims):
        raise IdentityLinkError("Google identity is already bound to another account")

    monkeypatch.setattr(
        "admin_template.auth.router.get_or_create_user_from_claims",
        fake_get_or_create,
    )
    response = client.get("/auth/callback?code=auth-code&state=abc")
    assert response.status_code == 409


def test_logout_revokes_session(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    revoked = []

    async def fake_revoke(session_id) -> None:
        revoked.append(str(session_id))

    monkeypatch.setattr("admin_template.auth.router.revoke_session", fake_revoke)
    response = client.post(
        "/auth/logout?session_id=00000000-0000-0000-0000-000000000002"
    )
    assert response.status_code == 200
    assert response.json() == {"status": "revoked"}
    assert revoked == ["00000000-0000-0000-0000-000000000002"]
