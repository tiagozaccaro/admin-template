"""Permission dependencies and decorators for tenancy-aware authz."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.core.db import db
from admin_template.modules.identity.models.user import User
from admin_template.modules.tenancy.models.tenant_membership import (
    TenantMembership,
    TenantRole,
)


async def _session_factory():
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def get_tenant_membership(
    tenant_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user_from_session)],
) -> TenantMembership:
    async with (await _session_factory())() as session:
        result = await session.execute(
            TenantMembership.__table__.select().where(
                (TenantMembership.tenant_id == tenant_id)
                & (TenantMembership.user_id == user.id)
            )
        )
        row = result.first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this tenant",
            )
        membership = TenantMembership(
            id=row.id,
            user_id=row.user_id,
            tenant_id=row.tenant_id,
            role=row.role,
            created_at=row.created_at,
        )
        return membership


def require_roles(*roles: TenantRole):
    async def dependency(
        membership: Annotated[TenantMembership, Depends(get_tenant_membership)],
    ) -> TenantMembership:
        if membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return membership

    return dependency


__all__ = ["get_tenant_membership", "require_roles"]
