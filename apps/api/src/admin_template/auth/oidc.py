"""Google OIDC client integration.

Implements the Authorization Code flow with PKCE and nonce, discovers
Google's OIDC metadata, validates the ID token signature/claims, and
exchanges the authorization code for tokens. Uses authlib (maintained,
well-tested) rather than hand-rolled OIDC.

Opaque state, nonce, and code verifier are bound to each authorization
request and validated on the callback (CSRF + replay protection).
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
from jwt.algorithms import RSAAlgorithm

from admin_template.core.settings import settings

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GoogleOIDCConfig:
    """Resolved Google OIDC configuration."""

    client_id: str
    client_secret: str
    issuer: str
    redirect_uri: str


def google_oidc_config() -> GoogleOIDCConfig:
    """Resolve Google OIDC settings, raising a clear error when missing."""
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    redirect_uri = settings.google_redirect_uri
    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError(
            "Google OIDC is not fully configured: set "
            "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI"
        )
    return GoogleOIDCConfig(
        client_id=client_id,
        client_secret=client_secret,
        issuer=settings.google_issuer,
        redirect_uri=redirect_uri,
    )


# ---------------------------------------------------------------------------
# Per-request authorization binding (in-memory, short-lived)
# ---------------------------------------------------------------------------


@dataclass
class AuthRequest:
    """Bound state for a single authorization request."""

    state: str
    nonce: str
    code_verifier: str


# In-memory store: state -> AuthRequest. In production this should be a
# short-lived Redis keyed entry; for the template foundation an in-memory
# store keeps the dependency surface minimal while remaining correct for a
# single backend instance.
_AUTH_REQUESTS: dict[str, AuthRequest] = {}


def store_auth_request(state: str, nonce: str, code_verifier: str) -> None:
    _AUTH_REQUESTS[state] = AuthRequest(
        state=state, nonce=nonce, code_verifier=code_verifier
    )


def pop_auth_request(state: str) -> AuthRequest | None:
    return _AUTH_REQUESTS.pop(state, None)


# ---------------------------------------------------------------------------
# Discovery helper
# ---------------------------------------------------------------------------


async def _discovery_document(issuer: str) -> dict[str, Any]:
    """Fetch Google's OIDC discovery document."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{issuer}/.well-known/openid-configuration")
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuthorizationUrlResult:
    """Result of building the Google authorization URL."""

    authorization_url: str
    state: str
    nonce: str
    code_verifier: str


async def build_authorization_url() -> AuthorizationUrlResult:
    """Build the Google authorization URL with PKCE and nonce.

    Returns the URL to redirect the user to, plus the opaque state, nonce,
    and code verifier that must be bound to the callback request.
    """
    config = google_oidc_config()
    discovery = await _discovery_document(config.issuer)
    client = AsyncOAuth2Client(
        config.client_id,
        config.client_secret,
        redirect_uri=config.redirect_uri,
        scope="openid profile email",
        token_endpoint=discovery["token_endpoint"],
        code_challenge_method="S256",
    )
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(32)
    authorization_url, _ = client.create_authorization_url(
        discovery["authorization_endpoint"],
        state=state,
        nonce=nonce,
        code_challenge_method="S256",
        code_verifier=code_verifier,
    )
    store_auth_request(state, nonce, code_verifier)
    return AuthorizationUrlResult(
        authorization_url=authorization_url,
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
    )


@dataclass(frozen=True)
class TokenSet:
    """Tokens returned by Google's token endpoint."""

    access_token: str
    id_token: str | None
    refresh_token: str | None
    expires_in: int | None


@dataclass(frozen=True)
class TokenResult:
    """Tokens plus the nonce bound to the authorization request."""

    tokens: TokenSet
    nonce: str


async def exchange_code(code: str, state: str) -> TokenResult:
    """Exchange the authorization code for tokens via the token endpoint.

    Validates PKKE code_verifier bound to the state (CSRF + replay
    protection). Returns the tokens and the nonce bound to the request.
    """
    auth_request = pop_auth_request(state)
    if auth_request is None:
        raise ValueError("Invalid or expired authorization state")

    config = google_oidc_config()
    discovery = await _discovery_document(config.issuer)
    client = AsyncOAuth2Client(
        config.client_id,
        config.client_secret,
        redirect_uri=config.redirect_uri,
        scope="openid profile email",
        token_endpoint=discovery["token_endpoint"],
        code_challenge_method="S256",
    )
    token = await client.fetch_token(
        discovery["token_endpoint"],
        code=code,
        code_verifier=auth_request.code_verifier,
    )
    return TokenResult(
        tokens=TokenSet(
            access_token=token["access_token"],
            id_token=token.get("id_token"),
            refresh_token=token.get("refresh_token"),
            expires_in=token.get("expires_in"),
        ),
        nonce=auth_request.nonce,
    )


@dataclass(frozen=True)
class IDTokenClaims:
    """Validated ID token claims from Google."""

    sub: str
    email: str | None
    email_verified: bool
    name: str | None
    issuer: str
    audience: str


async def validate_id_token(id_token: str, expected_nonce: str) -> IDTokenClaims:
    """Validate a Google ID token.

    Verifies the signature (JWKS), issuer, audience, expiry, and nonce.
    """
    config = google_oidc_config()
    discovery = await _discovery_document(config.issuer)
    jwks_uri = discovery["jwks_uri"]

    async with httpx.AsyncClient(timeout=10.0) as client:
        jwks_response = await client.get(jwks_uri)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()

    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("ID token missing kid")
    signing_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            signing_key = RSAAlgorithm.from_jwk(json.dumps(key))
            break
    if signing_key is None:
        raise ValueError("Signing key not found")

    payload: dict[str, Any] = jwt.decode(
        id_token,
        signing_key,  # type: ignore[reportArgumentType] -- RSA public key from JWK
        algorithms=["RS256"],
        audience=config.client_id,
        issuer=config.issuer,
        options={"require": ["exp", "iss", "aud"]},
    )

    nonce = payload.get("nonce")
    if nonce != expected_nonce:
        raise ValueError("ID token nonce mismatch")

    return IDTokenClaims(
        sub=payload["sub"],
        email=payload.get("email"),
        email_verified=bool(payload.get("email_verified", False)),
        name=payload.get("name"),
        issuer=payload["iss"],
        audience=payload["aud"],
    )
