"""Item CRUD."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.core.crud import CRUDBase
from admin_template.modules.items.models import Item


class CRUDItem(CRUDBase[Item]):
    async def get_by_tenant(
        self, db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Item]:
        result = await db.execute(
            select(Item).where(Item.tenant_id == tenant_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


item = CRUDItem(Item)


__all__ = ["CRUDItem", "item"]
