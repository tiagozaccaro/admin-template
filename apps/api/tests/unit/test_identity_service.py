"""Unit tests for the identity service (US2).

Covers database failure handling in get_or_create_user_from_claims so an
unreachable database surfaces as IdentityServiceUnavailableError instead of
propagating a raw connection error as a 500.
"""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from admin_template.api.main import app
from admin_template.auth.oidc import IDTokenClaims
from admin_template.modules.identity.service import (
    IdentityServiceUnavailableError,
    get_or_create_user_from_claims,
)


class _FailingSession:
    """A mock session whose execute() raises a DB connection error."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, *args, **kwargs):
        raise ConnectionRefusedError("Connection refused")

    async def get(self, *args, **kwargs):
        return None

    async def commit(self):
        return None

    async def refresh(self, *args, **kwargs):
        return None


class _FailingFactory:
    """A mock session factory that always returns a failing session."""

    def __call__(self):
        return _FailingSession()


class _SqlalchemyFailingSession:
    """A mock session whose execute() raises a SQLAlchemy error."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, *args, **kwargs):
        raise SQLAlchemyError("DB connection failed")

    async def get(self, *args, **kwargs):
        return None

    async def commit(self):
        return None

    async def refresh(self, *args, **kwargs):
        return None


class _SqlalchemyFailingFactory:
    """A mock session factory that returns a SQLAlchemy-failing session."""

    def __call__(self):
        return _SqlalchemyFailingSession()


def _claims() -> IDTokenClaims:
    return IDTokenClaims(
        sub="google-sub-1",
        email="user@example.com",
        name="User Example",
        email_verified=True,
        issuer="https://accounts.google.com",
        audience="test-client-id",
    )


def _run(coro):
    """Run an async coroutine synchronously (pytest-asyncio is not installed)."""
    return asyncio.run(coro)


async def _mock_session_factory(factory):
    """Async mock of _session_factory that returns the given factory."""
    return factory


def _monkeypatch_factory(monkeypatch, factory):
    monkeypatch.setattr(
        "admin_template.modules.identity.service._session_factory",
        lambda: _mock_session_factory(factory),
    )


def test_get_or_create_user_db_down_raises_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the database refuses connections, the service should raise
    IdentityServiceUnavailableError rather than leaking a raw 500."""
    _monkeypatch_factory(monkeypatch, _FailingFactory())
    with pytest.raises(IdentityServiceUnavailableError):
        _run(get_or_create_user_from_claims(_claims()))


def test_get_or_create_user_db_down_wraps_sqlalchemy_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SQLAlchemyError connection failures should also normalize to
    IdentityServiceUnavailableError."""
    _monkeypatch_factory(monkeypatch, _SqlalchemyFailingFactory())
    with pytest.raises(IdentityServiceUnavailableError):
        _run(get_or_create_user_from_claims(_claims()))


def test_callback_db_down_returns_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the identity service is unavailable due to a DB connection
    failure, the callback should return HTTP 503 instead of a raw 500."""

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
        return _claims()

    async def failing_get_or_create(claims):
        raise IdentityServiceUnavailableError(
            "Identity service is temporarily unavailable"
        )

    async def fake_create_session(user_id):
        return SimpleNamespace(id="00000000-0000-0000-0000-000000000002")

    monkeypatch.setattr(
        "admin_template.auth.router.build_authorization_url", fake_start
    )
    monkeypatch.setattr("admin_template.auth.router.exchange_code", fake_exchange)
    monkeypatch.setattr("admin_template.auth.router.validate_id_token", fake_validate)
    monkeypatch.setattr(
        "admin_template.auth.router.get_or_create_user_from_claims",
        failing_get_or_create,
    )
    monkeypatch.setattr(
        "admin_template.auth.router.create_session", fake_create_session
    )

    client = TestClient(app)
    response = client.get("/auth/callback?code=auth-code&state=abc")
    assert response.status_code == 503
