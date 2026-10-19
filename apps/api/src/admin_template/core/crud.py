"""Generic CRUD base utilities."""

from __future__ import annotations

import uuid
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase[ModelType: Base]:
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: uuid.UUID | str) -> ModelType | None:
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)  # type: ignore[call-arg]
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: uuid.UUID | str) -> ModelType | None:
        obj = await db.get(self.model, id)
        if obj is None:
            return None
        await db.delete(obj)
        await db.commit()
        return obj


__all__ = ["CRUDBase"]
