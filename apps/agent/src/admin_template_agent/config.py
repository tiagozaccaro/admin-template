"""Agent daemon configuration.

Loaded from environment variables with sensible defaults for local
development. Sensitive values (tokens) are read from env or Docker
`_FILE` secret mounts; nothing is committed to the repository.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Runtime configuration for the standalone agent daemon."""

    model_config = SettingsConfigDict(
        env_file=[
            str(Path.cwd() / ".env"),
            str(Path(__file__).resolve().parents[4] / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8100
    log_level: str = "INFO"

    # Agent identity
    agent_name: str = "local-agent"
    agent_id: str = "local"

    # Model / LLM
    model: str = "test"
    model_provider: str = "openai"
    model_api_key: str | None = Field(
        default=None, description="LLM API key (or set via env)"
    )
    model_api_base: str | None = Field(
        default=None, description="Custom OpenAI-compatible base URL"
    )

    # Auth: bearer token accepted by this daemon
    agent_token: str | None = Field(
        default=None,
        description="Bearer token required for chat/config endpoints",
    )
    agent_admin_token: str | None = Field(
        default=None,
        description="Separate bearer token required for mutating config (FR-009 RBAC). "
        "When set, config writes require this token instead of agent_token.",
    )

    # Core API integration
    api_url: str = "http://localhost:8000"
    api_token: str | None = Field(
        default=None, description="Token used to register this agent with the API"
    )

    # Tools
    allowed_paths: list[str] | None = None
    allow_shell: bool = Field(
        default=False, description="Whether shell tool is enabled"
    )
    require_approval_for_destructive: bool = Field(
        default=True,
        description="Whether destructive tools require approval",
    )
    prompt: str | None = Field(
        default=None,
        description="System prompt override for the agent",
    )
    tools: list[str] | None = Field(
        default=None,
        description="List of enabled tool names",
    )

    # MCP
    mcp_servers: list[str] | None = None

    # Skills
    skills_dir: str = Field(
        default="skills", description="Directory of skill markdown bundles"
    )

    # Sessions
    session_store_path: str = Field(
        default=".agent-sessions.json",
        description="Path to the JSON session persistence file",
    )

    # Audit
    audit_log_path: str = Field(
        default="audit.log", description="Path to the JSON-lines audit log"
    )

    # Observability
    otlp_endpoint: str = "http://localhost:4318/v1/traces"

    @field_validator("allowed_paths", "mcp_servers", mode="before")
    @classmethod
    def _split_csv(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


config = Config()

__all__ = ["Config", "config"]
