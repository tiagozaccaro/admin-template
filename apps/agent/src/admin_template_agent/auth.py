"""Bearer-token authentication for the agent daemon.

Validates the `Authorization: Bearer <token>` header against the configured
agent token. When no token is configured, requests are allowed (local dev).
Supports two-tier auth: a read/write token and an admin-only token for
mutating configuration (FR-009).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from admin_template_agent.config import config

_bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str | None:
    """Return the token string when valid, or raise 401 when invalid."""
    expected = config.agent_token
    if not expected:
        # No token configured -> allow (local dev mode).
        return None
    if credentials is None or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing agent token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str | None:
    """Require the admin token for mutating configuration endpoints (FR-009).

    Falls back to the regular agent token when no admin token is configured.
    """
    expected = config.agent_admin_token or config.agent_token
    if not expected:
        return None
    if credentials is None or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin token required for this operation",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


__all__ = ["verify_admin_token", "verify_token"]
