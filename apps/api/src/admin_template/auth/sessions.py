"""Server-side session management.

Sessions are created after successful Google OIDC authentication and are
referenced by an httpOnly cookie (web) or a bearer token (mobile). Sessions
expire and can be revoked.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from admin_template.core.db import db
from admin_template.core.settings import settings
from admin_template.modules.identity.models.session import Session
from admin_template.modules.identity.models.user import User

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False)


async def _session_factory():
    """Return the initialized async session factory."""
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def create_session(user_id: uuid.UUID) -> Session:
    """Create a new server-side session for a user."""
    session = Session(
        user_id=user_id,
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.session_ttl_minutes),
    )
    async with (await _session_factory())() as database_session:
        database_session.add(session)
        await database_session.commit()
        await database_session.refresh(session)
        return session


async def get_session_by_id(session_id: uuid.UUID) -> Session | None:
    """Return a session by id, or None when not found."""
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalars().first()


async def is_session_valid(session_id: uuid.UUID) -> bool:
    """Return True when the session exists, is not revoked, and not expired."""
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalars().first()
        if session is None or session.revoked_at is not None:
            return False
        return session.expires_at > datetime.now(UTC)


async def revoke_session(session_id: uuid.UUID) -> None:
    """Revoke a session by id (no-op when already revoked/missing)."""
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalars().first()
        if session is not None and session.revoked_at is None:
            session.revoked_at = datetime.now(UTC)
            await database_session.commit()


async def rotate_session(session_id: uuid.UUID) -> Session:
    """Revoke the given session and create a fresh one for the same user."""
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalars().first()
        if session is None:
            raise ValueError("Session not found")
        user_id = session.user_id
        session.revoked_at = datetime.now(UTC)
        new_session = Session(
            user_id=user_id,
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.session_ttl_minutes),
        )
        database_session.add(new_session)
        await database_session.commit()
        await database_session.refresh(new_session)
        return new_session


async def get_current_user_from_session(
    session_id: Annotated[
        str | None, Cookie(alias=settings.session_cookie_name)
    ] = None,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> User:
    """Dependency: resolve the authenticated User from a session cookie or
    bearer token (deny-by-default).

    Web clients present the session via an httpOnly cookie; mobile clients
    present the session id as a bearer token. Returns the User or raises
    HTTPException 401.
    """
    token = session_id or (credentials.credentials if credentials else None)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication session",
            headers={"WWW-Authenticate": 'Bearer realm="admin-template"'},
        )
    try:
        session_uuid = uuid.UUID(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session identifier",
        ) from exc

    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(Session).where(Session.id == session_uuid)
        )
        session = result.scalars().first()
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= datetime.now(UTC)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or revoked",
            )
        user = await database_session.get(User, session.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session user not found",
            )
        return user
