"""Dashboard API endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.modules.dashboard import service
from admin_template.modules.identity.models.user import User

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def get_dashboard(
    tenant_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    return await service.get_dashboard_metrics(tenant_id)


@router.get("/api/v1/dashboard")
async def get_dashboard_v1(
    tenant_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    return await service.get_dashboard_metrics(tenant_id)
