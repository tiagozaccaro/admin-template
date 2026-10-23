"""Tests for identity service (low coverage: 19%)."""

import asyncio
import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from admin_template.auth.oidc import IDTokenClaims
from admin_template.modules.identity.models.external_identity import ExternalIdentity
from admin_template.modules.identity.models.user import User
from admin_template.modules.identity.service import (
    IdentityLinkError,
    get_or_create_user_from_claims,
    link_external_identity,
    unlink_external_identity,
)


def test_identity_link_error_raised():
    """Verify IdentityLinkError can be raised and caught."""
    with pytest.raises(IdentityLinkError):
        raise IdentityLinkError("test")


def _claims(sub: str = "google-sub-1", email: str | None = "user@example.com") -> IDTokenClaims:
    return IDTokenClaims(
        sub=sub,
        email=email,
        email_verified=True,
        name="Test User",
        issuer="https://accounts.google.com",
        audience="test-aud",
    )


class _FakeSession:
    """Minimal async session stand-in."""
    def __init__(self, external=None, user=None):
        self.external = external
        self.user = user
        self.deleted = []
        self.committed = False
        self.flushed = False

    async def execute(self, *_a, **_k):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = self.external
        mock_result.scalars.return_value = mock_scalars
        return mock_result

    async def get(self, model, *ids, **kwargs):
        return self.user

    async def add(self, obj):
        self.flushed = True

    async def delete(self, obj):
        self.deleted.append(obj)

    async def commit(self):
        self.committed = True

    async def flush(self):
        self.flushed = True

    async def refresh(self, obj):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSessionFactory:
    def __init__(self, session):
        self.session = session

    def __call__(self):
        return self.session


def _run(coro):
    """Run coroutine in fresh event loop (avoids pytest-asyncio conflicts)."""
    return asyncio.new_event_loop().run_until_complete(coro)


def test_get_or_create_user_from_claims_creates_new():
    """Creates user + external identity when neither exists."""
    session = _FakeSession()
    factory = _FakeSessionFactory(session)

    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        user = _run(get_or_create_user_from_claims(_claims()))

    assert isinstance(user, User)
    assert user.email == "user@example.com"
    assert user.display_name == "Test User"
    assert session.flushed is True
    assert session.committed is True


def test_get_or_create_user_from_claims_existing_external():
    """Returns existing user when external identity is already bound."""
    existing_user = User(
        keycloak_sub="google-sub-1",
        email="user@example.com",
        display_name="Test User",
    )
    external = MagicMock()
    external.user_id = existing_user.id if hasattr(existing_user, "id") else uuid.uuid4()
    session = _FakeSession(external=external, user=existing_user)
    factory = _FakeSessionFactory(session)

    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        user = _run(get_or_create_user_from_claims(_claims()))

    assert user is existing_user


def test_get_or_create_user_from_claims_missing_user_raises():
    """Raises IdentityLinkError when external identity points to missing user."""
    external = MagicMock()
    external.user_id = uuid.uuid4()
    session = _FakeSession(external=external, user=None)
    factory = _FakeSessionFactory(session)

    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        with pytest.raises(IdentityLinkError):
            _run(get_or_create_user_from_claims(_claims()))


def test_link_external_identity_no_conflict():
    """Linking an unbound identity succeeds."""
    session = _FakeSession()
    factory = _FakeSessionFactory(session)

    user_id = uuid.uuid4()
    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        external = _run(link_external_identity(user_id, _claims()))

    assert isinstance(external, ExternalIdentity)
    assert external.user_id == user_id
    assert external.provider == "google"
    assert external.provider_sub == "google-sub-1"
    assert session.committed is True


def test_link_external_identity_conflict():
    """Linking an identity bound to another user raises IdentityLinkError."""
    existing_user_id = uuid.uuid4()
    session = _FakeSession(external=ExternalIdentity(
        user_id=existing_user_id,
        provider="google",
        provider_sub="google-sub-1",
        provider_email="other@example.com",
    ))
    factory = _FakeSessionFactory(session)

    user_id = uuid.uuid4()
    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        with pytest.raises(IdentityLinkError):
            _run(link_external_identity(user_id, _claims()))


def test_unlink_external_identity_deletes():
    """Unlinking an existing identity deletes it."""
    external = ExternalIdentity(
        user_id=uuid.uuid4(),
        provider="google",
        provider_sub="sub-to-unlink",
        provider_email="old@example.com",
    )
    session = _FakeSession(external=external)
    factory = _FakeSessionFactory(session)

    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        _run(unlink_external_identity(external.user_id, "sub-to-unlink"))

    assert session.deleted == [external]
    assert session.committed is True


def test_unlink_external_identity_not_found_noop():
    """Unlinking a non-existent identity does nothing."""
    session = _FakeSession(external=None)
    factory = _FakeSessionFactory(session)

    with patch(
        "admin_template.modules.identity.service._session_factory",
        return_value=factory,
    ):
        _run(unlink_external_identity(uuid.uuid4(), "none"))

    assert session.deleted == []