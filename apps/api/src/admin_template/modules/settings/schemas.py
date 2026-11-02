"""Pydantic schemas for the settings endpoint."""

import json

from pydantic import BaseModel, field_validator


class SettingsBase(BaseModel):
    app_name: str
    app_description: str
    maintenance_mode: bool
    session_ttl_minutes: int
    chat_models: str
    provider_settings: str = "{}"


class SettingsRead(SettingsBase):
    """Current application settings."""


class SettingsUpdate(SettingsBase):
    """Incoming settings update payload."""

    @field_validator("chat_models")
    @classmethod
    def _validate_chat_models(cls, value: str) -> str:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("chat_models must be valid JSON") from exc
        if not isinstance(parsed, list):
            raise ValueError("chat_models must be a JSON list")
        for entry in parsed:
            if not isinstance(entry, str):
                raise ValueError("each chat_models entry must be a provider ID string")
        return value

    @field_validator("provider_settings")
    @classmethod
    def _validate_provider_settings(cls, value: str) -> str:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("provider_settings must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ValueError("provider_settings must be a JSON object")
        for entry in parsed.values():
            if not isinstance(entry, dict):
                raise ValueError("each provider entry must be an object")
        return value
