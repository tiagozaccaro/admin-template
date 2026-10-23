"""Security: JWT validation and RBAC.

JWT RS256 validation against the Keycloak JWKS endpoint, audience
``keycloak_audience`` (default ``admin-template-api``), deny-by-default
authentication, and 401/403 handling.

No tokens are ever logged.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Annotated, Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.core.db import get_session
from admin_template.core.settings import settings
from admin_template.modules.workspace.models.member import (
    WorkspaceMember,
    WorkspaceRole,
)

# ---------------------------------------------------------------------------
# JWKS
# ---------------------------------------------------------------------------

_JWKS_CACHE: dict[str, Any] | None = None
_JWKS_FETCHED_AT: float = 0.0
_JWKS_TTL_SECONDS = 300

bearer_scheme = HTTPBearer(auto_error=False)


async def _fetch_jwks() -> dict[str, Any]:
    """Fetch and cache the Keycloak JWKS document."""
    global _JWKS_CACHE, _JWKS_FETCHED_AT
    now = time.monotonic()
    if _JWKS_CACHE is not None and now - _JWKS_FETCHED_AT < _JWKS_TTL_SECONDS:
        return _JWKS_CACHE
    if not settings.keycloak_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWKS URL not configured",
        )
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(settings.keycloak_jwks_url)
        response.raise_for_status()
        jwks: dict[str, Any] = response.json()
        _JWKS_CACHE = jwks
        _JWKS_FETCHED_AT = now
        return jwks


def _signing_key(kid: str) -> Any:
    """Return the RSA public key for a JWKS kid."""
    jwks = _JWKS_CACHE
    if jwks is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWKS not available",
        )
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return RSAAlgorithm.from_jwk(json.dumps(key))
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Signing key not found",
    )


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------


async def validate_token(token: str) -> dict[str, Any]:
    """Validate a JWT RS256 access token.

    Verifies signature, audience (``keycloak_audience``), issuer, and expiry.
    Returns the token payload on success; raises HTTPException 401 on any
    failure (deny-by-default).
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        ) from exc

    kid = header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing kid",
        )

    try:
        key = _signing_key(kid)
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.keycloak_audience,
            issuer=settings.keycloak_issuer,
            options={"require": ["exp", "iss", "aud"]},
        )
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        ) from exc
    except jwt.InvalidAudienceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid audience",
        ) from exc
    except jwt.InvalidIssuerError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid issuer",
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    return payload


# ---------------------------------------------------------------------------
# Authentication / authorization dependencies
# ---------------------------------------------------------------------------


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, Any]:
    """FastAPI dependency: deny-by-default Bearer token authentication.

    Returns the validated token payload. Raises HTTPException 401 when no
    token is present or validation fails.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": 'Bearer realm="admin-template"'},
        )
    return await validate_token(credentials.credentials)


def require_role(*roles: str):
    """Dependency factory: require the user to hold one of the given roles.

    Raises HTTPException 403 when the authenticated user lacks every
    requested role (deny-by-default).
    """

    async def role_dependency(
        user: Annotated[dict[str, Any], Depends(get_current_user)],
    ) -> dict[str, Any]:
        realm_roles = set(user.get("realm_access", {}).get("roles", []))
        client_roles = set(
            user.get("resource_access", {})
            .get(settings.keycloak_audience, {})
            .get("roles", [])
        )
        user_roles = realm_roles | client_roles
        if not set(roles) & user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return role_dependency


# ---------------------------------------------------------------------------
# Workspace-level RBAC (deny-by-default, FR-014)
# ---------------------------------------------------------------------------

# Role hierarchy: higher index = more privileges.
_ROLE_RANK = {
    WorkspaceRole.VIEWER: 0,
    WorkspaceRole.MEMBER: 1,
    WorkspaceRole.OWNER: 2,
}


def require_workspace_role(required_role: WorkspaceRole):
    """Dependency factory: require the user to hold at least [required_role]
    in the given workspace.

    Raises HTTPException 403 when the authenticated user lacks sufficient
    workspace role (deny-by-default).

    Usage in a route:

        @router.get("/{workspace_id}/projects")
        async def list_projects(
            workspace_id: str,
            user: Annotated[dict, Depends(require_workspace_role(WorkspaceRole.VIEWER))],
            session: ...,
        ) -> ...
    """

    async def workspace_role_dependency(
        user: Annotated[dict[str, Any], Depends(get_current_user)],
        workspace_id: str,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> dict[str, Any]:
        keycloak_sub = user.get("sub")
        if not keycloak_sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
            )

        result = await session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == uuid.UUID(workspace_id),
            )
        )
        memberships = result.scalars().all()
        user_membership = next(
            (m for m in memberships if str(m.user_id) == keycloak_sub), None
        )
        if user_membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this workspace",
            )

        user_rank = _ROLE_RANK.get(user_membership.role, -1)
        required_rank = _ROLE_RANK.get(required_role, 0)
        if user_rank < required_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient workspace role: {required_role.value} required",
            )
        return user

    return workspace_role_dependency


__all__ = [
    "bearer_scheme",
    "get_current_user",
    "hash_password",
    "require_role",
    "require_workspace_role",
    "verify_password",
]


# ---------------------------------------------------------------------------
# Password hashing (local auth) — stdlib only, scrypt KDF
# ---------------------------------------------------------------------------

import base64
import hashlib
import hmac
import secrets

_PASSWORD_SCHEME = "scrypt"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 64
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a password using scrypt. Returns a self-describing string."""
    if not password:
        raise ValueError("password must not be empty")
    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    )
    return (
        f"{_PASSWORD_SCHEME}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(derived).decode('ascii')}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a stored scrypt hash (constant-time)."""
    try:
        scheme, n, r, p, salt_b64, derived_b64 = password_hash.split("$")
    except ValueError:
        return False
    if scheme != _PASSWORD_SCHEME:
        return False
    try:
        n_i, r_i, p_i = int(n), int(r), int(p)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(derived_b64)
    except (ValueError, TypeError):
        return False
    try:
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n_i,
            r=r_i,
            p=p_i,
            dklen=len(expected),
        )
    except (ValueError, OverflowError):
        return False
    return hmac.compare_digest(derived, expected)
