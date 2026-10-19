"""Ownership transfer service."""

from __future__ import annotations

import uuid

from sqlalchemy import update

from admin_template.core.db import db
from admin_template.modules.tenancy.models.tenant import Tenant
from admin_template.modules.tenancy.models.tenant_membership import (
    TenantMembership,
    TenantRole,
)


async def _session_factory():
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def transfer_ownership(
    tenant_id: uuid.UUID, from_user_id: uuid.UUID, to_user_id: uuid.UUID
) -> bool:
    async with (await _session_factory())() as session:
        tenant = await session.get(Tenant, tenant_id)
        if tenant is None or tenant.owner_user_id != from_user_id:
            return False

        await session.execute(
            update(TenantMembership)
            .where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == from_user_id,
            )
            .values(role=TenantRole.ADMIN)
        )
        await session.execute(
            update(TenantMembership)
            .where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == to_user_id,
            )
            .values(role=TenantRole.OWNER)
        )
        tenant.owner_user_id = to_user_id
        await session.commit()
        return True


__all__ = ["transfer_ownership"]
