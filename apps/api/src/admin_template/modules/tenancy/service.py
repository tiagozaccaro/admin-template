"""Tenant service."""

from __future__ import annotations

import uuid

from sqlalchemy import select

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


async def create_tenant(owner_id: uuid.UUID, name: str, slug: str) -> Tenant:
    async with (await _session_factory())() as session:
        tenant = Tenant(owner_user_id=owner_id, name=name, slug=slug)
        session.add(tenant)
        await session.flush()
        membership = TenantMembership(
            user_id=owner_id,
            tenant_id=tenant.id,
            role=TenantRole.OWNER,
        )
        session.add(membership)
        await session.commit()
        await session.refresh(tenant)
        return tenant


async def list_tenants(user_id: uuid.UUID) -> list[Tenant]:
    async with (await _session_factory())() as session:
        result = await session.execute(
            select(Tenant)
            .join(TenantMembership)
            .where(TenantMembership.user_id == user_id)
        )
        return list(result.scalars().all())


async def get_tenant(tenant_id: uuid.UUID) -> Tenant | None:
    async with (await _session_factory())() as session:
        return await session.get(Tenant, tenant_id)


async def update_tenant_settings(
    tenant_id: uuid.UUID, name: str | None = None, branding: dict | None = None
) -> Tenant | None:
    async with (await _session_factory())() as session:
        tenant = await session.get(Tenant, tenant_id)
        if tenant is None:
            return None
        if name is not None:
            tenant.name = name
        if branding is not None:
            tenant.branding = branding
        await session.commit()
        await session.refresh(tenant)
        return tenant


__all__ = [
    "create_tenant",
    "get_tenant",
    "list_tenants",
    "update_tenant_settings",
]
