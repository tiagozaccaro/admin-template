"""Application settings and configuration.

Pydantic Settings-based configuration loaded from the environment.
Sensitive values are resolved from environment variables or Docker
`_FILE` secret mounts; no secrets are committed to the repository.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
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
    cors_origins: list[str] = []

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
