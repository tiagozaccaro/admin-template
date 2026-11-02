"""Settings API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.core.settings import settings
from admin_template.modules.identity.models.user import User
from admin_template.modules.settings.schemas import SettingsRead, SettingsUpdate

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=SettingsRead)
async def get_settings(
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> SettingsRead:
    """Return the current application settings."""
    return SettingsRead(
        app_name=settings.app_name,
        app_description=settings.app_description,
        maintenance_mode=settings.maintenance_mode,
        session_ttl_minutes=settings.session_ttl_minutes,
        chat_models=settings.chat_models,
        provider_settings=settings.provider_settings,
    )


@router.post("/settings", response_model=SettingsRead)
async def update_settings(
    settings_in: SettingsUpdate,
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> SettingsRead:
    """Update application settings (in-memory for the running process)."""
    settings.app_name = settings_in.app_name
    settings.app_description = settings_in.app_description
    settings.maintenance_mode = settings_in.maintenance_mode
    settings.session_ttl_minutes = settings_in.session_ttl_minutes
    settings.chat_models = settings_in.chat_models
    settings.provider_settings = settings_in.provider_settings
    return SettingsRead(
        app_name=settings.app_name,
        app_description=settings.app_description,
        maintenance_mode=settings.maintenance_mode,
        session_ttl_minutes=settings.session_ttl_minutes,
        chat_models=settings.chat_models,
        provider_settings=settings.provider_settings,
    )
