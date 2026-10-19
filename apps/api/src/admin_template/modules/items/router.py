"""Item router."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.auth.sessions import get_current_user_from_session
from admin_template.core.db import get_session
from admin_template.modules.identity.models.user import User
from admin_template.modules.items import crud, schemas

router = APIRouter(tags=["items"])


@router.get("/items")
async def list_items(
    tenant_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    return await crud.item.get_by_tenant(db, tenant_id, skip, limit)  # type: ignore[arg-type]


@router.post("/items")
async def create_item(
    item_in: schemas.ItemCreate,
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    return await crud.item.create(db, item_in.model_dump())  # type: ignore[arg-type]


@router.get("/items/{item_id}")
async def get_item(
    item_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.get(db, item_id)  # type: ignore[arg-type]
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/items/{item_id}")
async def update_item(
    item_id: uuid.UUID,
    item_in: schemas.ItemUpdate,
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.get(db, item_id)  # type: ignore[arg-type]
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return await crud.item.update(db, db_item, item_in.model_dump(exclude_unset=True))  # type: ignore[arg-type]


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
    user: Annotated[User, Depends(get_current_user_from_session)] = None,  # type: ignore[assignment]
):
    db_item = await crud.item.delete(db, item_id)  # type: ignore[arg-type]
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}
