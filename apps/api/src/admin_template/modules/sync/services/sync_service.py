"""Sync service.

Delta sync cursor management and idempotent push handling (T087/T088)
per contracts/sync-api.md.
"""

from __future__ import annotations

import base64
import binascii
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.modules.sync.models.cursor import SyncCursor
from admin_template.modules.sync.models.idempotency import IdempotencyKey

DEFAULT_TTL_SECONDS = 86400  # 24 hours


class SyncService:
    """Manages sync cursors and idempotent response caching."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def parse_cursor(cursor: str | None) -> datetime | None:
        """Decode an opaque base64 (updated_at, id) cursor to a datetime."""
        if not cursor:
            return None
        try:
            decoded = base64.b64decode(cursor, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Invalid cursor") from exc
        # Cursor payload: ISO-8601 updated_at followed by '|' and an id.
        text = decoded.decode("utf-8", errors="replace")
        if "|" not in text:
            raise ValueError("Invalid cursor")
        ts_part = text.split("|", 1)[0]
        return datetime.fromisoformat(ts_part)

    async def get_cursor(self, user_id: str) -> SyncCursor | None:
        """Get the user's current sync cursor."""
        result = await self.session.execute(
            select(SyncCursor).where(SyncCursor.user_id == uuid.UUID(user_id))
        )
        return result.scalars().first()

    async def set_cursor(
        self, user_id: str, last_cursor: datetime
    ) -> SyncCursor:
        """Create or update the user's sync cursor."""
        existing = await self.get_cursor(user_id)
        if existing is not None:
            existing.last_cursor = last_cursor
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        cursor = SyncCursor(
            user_id=uuid.UUID(user_id),
            last_cursor=last_cursor,
        )
        self.session.add(cursor)
        await self.session.flush()
        await self.session.refresh(cursor)
        return cursor

    async def check_idempotency(
        self,
        user_id: str,
        endpoint: str,
        key: str,
    ) -> dict[str, Any] | None:
        """Return a cached response for an idempotency key, if present and not expired."""
        result = await self.session.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.key == key,
                IdempotencyKey.user_id == uuid.UUID(user_id),
                IdempotencyKey.endpoint == endpoint,
            )
        )
        row = result.scalars().first()
        if row is None:
            return None
        if row.expires_at < datetime.now(UTC):
            return None
        return {
            "response_status": row.response_status,
            "response_body": row.response_body,
        }

    async def record_idempotency(
        self,
        user_id: str,
        endpoint: str,
        key: str,
        response_status: int,
        response_body: dict[str, Any],
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> IdempotencyKey:
        """Record an idempotent response."""
        idem = IdempotencyKey(
            key=key,
            user_id=uuid.UUID(user_id),
            endpoint=endpoint,
            response_status=response_status,
            response_body=response_body,
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
        )
        self.session.add(idem)
        await self.session.flush()
        await self.session.refresh(idem)
        return idem


__all__ = ["SyncService"]
