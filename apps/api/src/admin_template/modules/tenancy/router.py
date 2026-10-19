"""Tenant API endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.modules.identity.models.user import User
from admin_template.modules.tenancy import invitations as invitations_service
from admin_template.modules.tenancy import memberships as memberships_service
from admin_template.modules.tenancy import ownership as ownership_service
from admin_template.modules.tenancy import service as tenants_service
from admin_template.modules.tenancy.models.tenant_membership import TenantRole

router = APIRouter(tags=["tenants"])


@router.get("/")
async def list_tenants(user: Annotated[User, Depends(get_current_user_from_session)]):
    return await tenants_service.list_tenants(user.id)


@router.post("/")
async def create_tenant(
    name: str,
    slug: str,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    tenant = await tenants_service.create_tenant(user.id, name, slug)
    return {"id": str(tenant.id), "name": tenant.name, "slug": tenant.slug}


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: uuid.UUID):
    tenant = await tenants_service.get_tenant(tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/{tenant_id}/members")
async def list_members(tenant_id: uuid.UUID):
    return await memberships_service.list_members(tenant_id)


@router.post("/{tenant_id}/invitations")
async def create_invitation(
    tenant_id: uuid.UUID,
    email: str,
    role: TenantRole = TenantRole.MEMBER,
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    invitation, token = await invitations_service.create_invitation(
        tenant_id, email, role, user.id if user else None
    )
    return {
        "id": str(invitation.id),
        "token": token,
        "expires_at": invitation.expires_at,
    }


@router.post("/invitations/accept")
async def accept_invitation(
    token: str,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    invitation = await invitations_service.accept_invitation(token, user.id)
    if invitation is None:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    return {"status": "accepted", "tenant_id": str(invitation.tenant_id)}


@router.post("/{tenant_id}/transfer")
async def transfer_ownership(
    tenant_id: uuid.UUID,
    to_user_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
):
    success = await ownership_service.transfer_ownership(tenant_id, user.id, to_user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Transfer failed")
    return {"status": "transferred"}
