"""Integrations router.

POST /api/v1/integrations per T089 (Phase 6 US4). Delegates to
IntegrationService (T086) for secure token storage.

Authentication (deny-by-default, constitution VII) is enforced by the
T094 RBAC middleware in Phase 7; until then the endpoint is usable for
the T077 contract tests.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.core.db import get_session
from admin_template.modules.identity.services.integration_service import (
    IntegrationService,
)

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


class IntegrationCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    external_id: str = Field(..., min_length=1)
    encrypted_token: str = Field(..., min_length=1)
    scopes: list[str] = Field(default_factory=list)


class IntegrationResponse(BaseModel):
    id: str
    user_id: str
    provider: str
    external_id: str
    encrypted_token: str
    scopes: list[str]
    created_at: str
    revoked_at: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("id", "user_id", mode="before")
    @classmethod
    def _coerce_uuid(cls, value: Any) -> str:
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    @field_validator("encrypted_token", mode="before")
    @classmethod
    def _coerce_token(cls, value: Any) -> str:
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", errors="replace")
        return str(value)

    @field_validator("created_at", "revoked_at", mode="before")
    @classmethod
    def _coerce_datetime(cls, value: Any) -> str | None:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def link_integration(
    payload: IntegrationCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IntegrationResponse:
    """Link a secure account integration for a user."""
    service = IntegrationService(session)
    integration = await service.link_integration(
        user_id=payload.user_id,
        provider=payload.provider,
        external_id=payload.external_id,
        encrypted_token=payload.encrypted_token.encode("utf-8"),
        scopes=payload.scopes,
    )
    return IntegrationResponse.model_validate(integration)


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[IntegrationResponse]:
    """List integrations for a user."""
    service = IntegrationService(session)
    integrations = await service.list_integrations(user_id)
    return [IntegrationResponse.model_validate(i) for i in integrations]


@router.post("/{integration_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_integration(
    integration_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Revoke an account integration."""
    service = IntegrationService(session)
    revoked = await service.revoke_integration(integration_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )


__all__ = ["router"]
