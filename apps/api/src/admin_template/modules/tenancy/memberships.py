"""Membership service."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select, update

from admin_template.core.db import db
from admin_template.modules.tenancy.models.tenant_membership import (
    TenantMembership,
    TenantRole,
)


async def _session_factory():
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


async def list_members(tenant_id: uuid.UUID) -> list[TenantMembership]:
    async with (await _session_factory())() as session:
        result = await session.execute(
            select(TenantMembership).where(TenantMembership.tenant_id == tenant_id)
        )
        return list(result.scalars().all())


async def add_member(
    tenant_id: uuid.UUID, user_id: uuid.UUID, role: TenantRole
) -> TenantMembership:
    async with (await _session_factory())() as session:
        membership = TenantMembership(tenant_id=tenant_id, user_id=user_id, role=role)
        session.add(membership)
        await session.commit()
        await session.refresh(membership)
        return membership


async def remove_member(tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
    async with (await _session_factory())() as session:
        await session.execute(
            delete(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == user_id,
            )
        )
        await session.commit()


async def change_role(
    tenant_id: uuid.UUID, user_id: uuid.UUID, role: TenantRole
) -> TenantMembership | None:
    async with (await _session_factory())() as session:
        result = await session.execute(
            update(TenantMembership)
            .where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == user_id,
            )
            .values(role=role)
            .returning(TenantMembership)
        )
        membership = result.scalars().first()
        await session.commit()
        return membership


__all__ = ["add_member", "change_role", "list_members", "remove_member"]
