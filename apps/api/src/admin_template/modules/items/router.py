"""Item router."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.core.db import get_session
from admin_template.modules.items import crud, schemas
from admin_template.permissions.deps import TenantMembership, get_tenant_membership

router = APIRouter()


@router.get("/items")
async def list_items(
    tenant_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    membership: Annotated[TenantMembership, Depends(get_tenant_membership)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
):
    return await crud.item.get_by_tenant(db, tenant_id, skip, limit)  # type: ignore[arg-type]


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: schemas.ItemCreate,
    tenant_id: uuid.UUID,
    membership: Annotated[TenantMembership, Depends(get_tenant_membership)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
):
    if (
        membership is None
        or membership.tenant_id != tenant_id
        or item_in.tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this tenant"
        )
    return await crud.item.create(db, item_in.model_dump())  # type: ignore[arg-type]


@router.get("/items/{item_id}")
async def get_item(
    item_id: uuid.UUID,
    tenant_id: uuid.UUID,
    membership: Annotated[TenantMembership, Depends(get_tenant_membership)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.get(db, item_id)  # type: ignore[arg-type]
    if db_item is None or getattr(db_item, "tenant_id", None) != tenant_id:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/items/{item_id}")
async def update_item(
    item_id: uuid.UUID,
    item_in: schemas.ItemUpdate,
    tenant_id: uuid.UUID,
    membership: Annotated[TenantMembership, Depends(get_tenant_membership)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.get(db, item_id)  # type: ignore[arg-type]
    if db_item is None or getattr(db_item, "tenant_id", None) != tenant_id:
        raise HTTPException(status_code=404, detail="Item not found")
    return await crud.item.update(db, db_item, item_in.model_dump(exclude_unset=True))  # type: ignore[arg-type]


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    tenant_id: uuid.UUID,
    membership: Annotated[TenantMembership, Depends(get_tenant_membership)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.get(db, item_id)  # type: ignore[arg-type]
    if db_item is None or getattr(db_item, "tenant_id", None) != tenant_id:
        raise HTTPException(status_code=404, detail="Item not found")
    await crud.item.delete(db, item_id)  # type: ignore[arg-type]
