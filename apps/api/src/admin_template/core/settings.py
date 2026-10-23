"""Application settings and configuration.

Pydantic Settings-based configuration loaded from the environment.
Sensitive values are resolved from environment variables or Docker
`_FILE` secret mounts; no secrets are committed to the repository.
"""

import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    _env_files = [Path.cwd() / ".env", Path(__file__).resolve().parents[3] / ".env"]
    model_config = SettingsConfigDict(
        env_file=[str(p) for p in _env_files if p.is_file()],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Admin Template API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    api_port: int = 8000
    cors_origins: Annotated[list[str], NoDecode] = []

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return json.loads(value)
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    # Database (postgres + asyncpg). Resolved from DATABASE_URL or a
    # DATABASE_URL_FILE Docker secret mount; no default (must be provided).
    database_url: str | None = Field(
        default=None, description="SQLAlchemy async database URL"
    )
    database_url_file: str | None = None

    # Redis (queue + cache + sessions)
    redis_url: str = "redis://localhost:6379/0"

    # Keycloak OIDC
    keycloak_jwks_url: str | None = Field(
        default=None, description="Keycloak JWKS endpoint URL"
    )
    keycloak_issuer: str | None = Field(default=None, description="Keycloak issuer URL")
    keycloak_audience: str = "admin-template-api"
    access_token_expire_minutes: int = 5

    # Google OIDC
    google_client_id: str | None = Field(
        default=None, description="Google OAuth client ID"
    )
    google_client_secret: str | None = Field(
        default=None, description="Google OAuth client secret"
    )
    google_issuer: str = Field(
        default="https://accounts.google.com", description="Google OIDC issuer"
    )
    google_redirect_uri: str | None = Field(
        default=None, description="Google OIDC redirect URI (backend callback)"
    )
    auth_redirect_uri: str | None = Field(
        default="http://localhost:3000/auth/callback",
        description="Post-login redirect URI for the client (web/mobile)",
    )

    # Sessions (server-side, httpOnly cookie for web / bearer token for mobile)
    session_cookie_name: str = Field(
        default="admin_template_session", description="Session cookie name"
    )
    session_cookie_secure: bool = Field(
        default=False, description="Whether the session cookie is Secure"
    )
    session_cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax", description="Session cookie SameSite attribute"
    )
    session_ttl_minutes: int = Field(
        default=60 * 24 * 7, description="Session TTL in minutes"
    )

    # OpenTelemetry trace export endpoint
    otlp_endpoint: str = "http://localhost:4318/v1/traces"

    def model_post_init(self, /, __context) -> None:
        """Resolve Docker `_FILE` secret mounts after field init.

        If `database_url` was not provided via env, read it from the file
        pointed to by `database_url_file` (a Docker secret mount). This
        keeps secrets out of the image and out of version control.
        """
        if self.database_url is None and self.database_url_file:
            try:
                with open(self.database_url_file, "r", encoding="utf-8") as fh:
                    object.__setattr__(self, "database_url", fh.read().strip())
            except FileNotFoundError:
                pass


settings = Settings()

__all__ = ["Settings", "settings"]
