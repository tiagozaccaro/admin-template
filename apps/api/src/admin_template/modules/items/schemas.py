"""Item schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    tenant_id: uuid.UUID


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


__all__ = ["Item", "ItemCreate", "ItemUpdate"]
