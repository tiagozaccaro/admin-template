"""Authentication routes: Google OIDC start/callback/logout."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from admin_template.auth.oidc import (
    AuthorizationUrlResult,
    build_authorization_url,
    exchange_code,
    validate_id_token,
)
from admin_template.auth.sessions import (
    create_session,
    get_current_user_from_session,
    revoke_session,
)
from admin_template.core.settings import settings
from admin_template.modules.identity.models.user import User
from admin_template.modules.identity.service import (
    IdentityLinkError,
    IdentityServiceUnavailableError,
    get_or_create_user_from_claims,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


class AuthorizationStartResponse(BaseModel):
    authorization_url: str
    state: str
    nonce: str


class LogoutResponse(BaseModel):
    status: str


@router.get(
    "/google/start",
    response_model=AuthorizationStartResponse,
    summary="Start Google OIDC login",
)
async def google_start() -> AuthorizationStartResponse:
    """Begin the Google OIDC Authorization Code flow.

    Returns the authorization URL plus the state/nonce that the client must
    bind to the callback request (CSRF + replay protection). The client
    stores the returned code_verifier and uses it when exchanging the code.
    """
    result: AuthorizationUrlResult = await build_authorization_url()
    return AuthorizationStartResponse(
        authorization_url=result.authorization_url,
        state=result.state,
        nonce=result.nonce,
    )


@router.get("/callback", summary="OIDC callback")
async def google_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> object:
    """Handle the Google OIDC callback.

    Exchanges the code for tokens (validating PKCE via the state-bound
    code_verifier), validates the ID token, creates/links the user and
    external identity, creates a server-side session, and redirects to the
    client with the session id.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OIDC error: {error}",
        )
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state",
        )

    # Exchange code for tokens; validates PKCE code_verifier bound to state.
    try:
        token_result = await exchange_code(code=code, state=state)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    id_token = token_result.tokens.id_token
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ID token returned",
        )

    # Validate the ID token, including the nonce bound to the original
    # authorization request (replay protection).
    try:
        claims = await validate_id_token(
            id_token=id_token, expected_nonce=token_result.nonce
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    try:
        user = await get_or_create_user_from_claims(claims)
    except IdentityLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except IdentityServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    db_session = await create_session(user.id)

    # Redirect the client (web or mobile) back with the session id so it can
    # establish its session (httpOnly cookie on web, bearer token on mobile).
    redirect_uri = settings.auth_redirect_uri or settings.google_redirect_uri or "/"
    url = (
        f"{redirect_uri.rstrip('?')}?session_id={db_session.id}"
        if "?" in redirect_uri
        else f"{redirect_uri.rstrip('/')}?session_id={db_session.id}"
    )
    response = RedirectResponse(url=url)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=str(db_session.id),
        path="/",
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
    )
    return response


@router.get("/me", response_model=dict, summary="Current user profile")
async def me(
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> dict:
    """Return the authenticated user's profile (session via cookie or bearer)."""
    return {
        "id": str(user.id),
        "keycloak_sub": user.keycloak_sub,
        "email": user.email,
        "display_name": user.display_name,
    }


@router.post("/logout", response_model=LogoutResponse, summary="Logout")
async def logout(
    response: Response,
    session_id: str | None = Query(default=None),
    session_cookie: str | None = Cookie(
        default=None, alias=settings.session_cookie_name
    ),
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> LogoutResponse:
    """Revoke a server-side session (logout)."""
    token = (
        session_id
        or session_cookie
        or (credentials.credentials if credentials else None)
    )
    if token:
        try:
            await revoke_session(uuid.UUID(token))
        except (ValueError, AttributeError):
            pass
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
    )
    return LogoutResponse(status="revoked")


# ---------------------------------------------------------------------------
# Local auth lifecycle (register / verify / reset / delete)
# ---------------------------------------------------------------------------

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel as _BM

from admin_template.core.db import db as _db
from admin_template.core.email import EmailMessage, send_email
from admin_template.core.security import hash_password
from admin_template.modules.identity.models.email_verification_token import (
    EmailVerificationToken,
)
from admin_template.modules.identity.models.password_reset_token import (
    PasswordResetToken,
)


class RegisterRequest(_BM):
    email: str
    password: str
    display_name: str | None = None


class TokenRequest(_BM):
    token: str


class ResetRequest(_BM):
    email: str


class ResetConfirmRequest(_BM):
    token: str
    new_password: str


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


async def _session_factory():
    if _db.session_factory is None:
        _db.init()
    assert _db.session_factory is not None
    return _db.session_factory


@router.post("/register", summary="Register with email/password")
async def register(payload: RegisterRequest) -> dict:
    async with (await _session_factory())() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == payload.email))
        if result.scalars().first() is not None:
            raise HTTPException(status_code=409, detail="Email already registered")
        user = User(
            email=payload.email,
            display_name=payload.display_name,
            password_hash=hash_password(payload.password),
            email_verified=False,
        )
        session.add(user)
        await session.flush()

        raw = secrets.token_urlsafe(32)
        session.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=_hash_token(raw),
                expires_at=datetime.now(UTC) + timedelta(hours=24),
            )
        )
        await session.commit()
        await session.refresh(user)

    await send_email(
        EmailMessage(
            to=payload.email,
            subject="Verify your email",
            body=f"Use this token to verify: {raw}",
        )
    )
    return {"status": "registered", "user_id": str(user.id)}


@router.post("/verify-email", summary="Verify email with token")
async def verify_email(payload: TokenRequest) -> dict:
    async with (await _session_factory())() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == _hash_token(payload.token)
            )
        )
        tok = result.scalars().first()
        if tok is None or tok.used_at is not None:
            raise HTTPException(status_code=400, detail="Invalid or used token")
        if tok.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Token expired")
        user = await session.get(User, tok.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.email_verified = True
        tok.used_at = datetime.now(UTC)
        await session.commit()
    return {"status": "verified"}


@router.post("/request-reset", summary="Request password reset")
async def request_reset(payload: ResetRequest) -> dict:
    async with (await _session_factory())() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == payload.email))
        user = result.scalars().first()
        if user is not None and user.deleted_at is None:
            raw = secrets.token_urlsafe(32)
            session.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=_hash_token(raw),
                    expires_at=datetime.now(UTC) + timedelta(hours=1),
                )
            )
            await session.commit()
            await send_email(
                EmailMessage(
                    to=payload.email,
                    subject="Password reset",
                    body=f"Use this token to reset: {raw}",
                )
            )
    return {"status": "ok"}


@router.post("/reset-password", summary="Reset password with token")
async def reset_password(payload: ResetConfirmRequest) -> dict:
    async with (await _session_factory())() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == _hash_token(payload.token)
            )
        )
        tok = result.scalars().first()
        if tok is None or tok.used_at is not None:
            raise HTTPException(status_code=400, detail="Invalid or used token")
        if tok.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Token expired")
        user = await session.get(User, tok.user_id)
        if user is None or user.deleted_at is not None:
            raise HTTPException(status_code=404, detail="User not found")
        user.password_hash = hash_password(payload.new_password)
        tok.used_at = datetime.now(UTC)
        await session.commit()
    return {"status": "reset"}


@router.delete("/account", summary="Soft-delete account")
async def delete_account(
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> dict:
    async with (await _session_factory())() as session:
        db_user = await session.get(User, user.id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.deleted_at = datetime.now(UTC)
        db_user.email = f"deleted-{db_user.id}@example.invalid"
        db_user.display_name = None
        db_user.password_hash = None
        await session.commit()
    return {"status": "deleted"}
