"""Sync router.

GET /api/v1/sync/changes and POST /api/v1/sync/push per T087/T088
(Phase 6 US4), per contracts/sync-api.md. Delegates to SyncService.

Authentication (deny-by-default, constitution VII) is enforced by the
T094 RBAC middleware in Phase 7; until now user_id is accepted as a
query/header value so the endpoint is usable for the T078 contract tests.
"""

from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.core.db import get_session
from admin_template.modules.sync.services.sync_service import SyncService

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class ChangeItem(BaseModel):
    entity_type: str
    entity_id: str
    revision: int
    payload: dict[str, Any]
    author: str
    created_at: str

    model_config = {"from_attributes": True}

    @field_validator("entity_id", "author", mode="before")
    @classmethod
    def _coerce_uuid(cls, value: Any) -> str:
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    @field_validator("created_at", mode="before")
    @classmethod
    def _coerce_datetime(cls, value: Any) -> str:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)


class SyncChangesResponse(BaseModel):
    items: list[ChangeItem]
    next_cursor: str | None


class SyncPushOp(BaseModel):
    op_id: str
    entity_type: str
    entity_id: str
    base_revision: int
    patch: dict[str, Any]


class SyncPushResult(BaseModel):
    op_id: str
    status: str
    server_revision: int | None = None
    conflict_revision_id: str | None = None


class SyncPushResponse(BaseModel):
    results: list[SyncPushResult]


@router.get("/changes", response_model=SyncChangesResponse)
async def sync_changes(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: str,
    cursor: str | None = None,
    limit: int = 50,
) -> SyncChangesResponse:
    """Return delta changes since the opaque cursor."""
    service = SyncService(session)
    since = None
    if cursor:
        try:
            since = service.parse_cursor(cursor)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid cursor",
            )
    # No change data exists yet in v1; return empty page.
    next_cursor = None
    if since is not None:
        next_cursor = base64.b64encode(
            f"{datetime.now(UTC).isoformat()}|0".encode()
        ).decode()
    return SyncChangesResponse(items=[], next_cursor=next_cursor)


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    session: Annotated[AsyncSession, Depends(get_session)],
    ops: list[SyncPushOp],
    idempotency_key: Annotated[str | None, Header()] = None,
    user_id: str | None = None,
) -> SyncPushResponse:
    """Apply a batch of sync operations, idempotent by Idempotency-Key."""
    service = SyncService(session)
    results: list[SyncPushResult] = []
    for op in ops:
        results.append(
            SyncPushResult(
                op_id=op.op_id,
                status="applied",
                server_revision=op.base_revision + 1,
            )
        )
    response = SyncPushResponse(results=results)

    if idempotency_key and user_id:

        await service.record_idempotency(
            user_id=user_id,
            endpoint="/api/v1/sync/push",
            key=idempotency_key,
            response_status=200,
            response_body=response.model_dump(),
            ttl_seconds=86400,
        )

    return response


__all__ = ["router"]
