"""Sync cursor model.

Sync bounded context: an opaque per-user cursor (updated_at, id) used for
delta sync pagination per contracts/sync-api.md.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User


class SyncCursor(Base):
    """A per-user pagination cursor for incremental sync."""

    __tablename__ = "sync_cursor"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_cursor: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f"SyncCursor(user_id={self.user_id!r}, last_cursor={self.last_cursor!r})"


__all__ = ["SyncCursor"]
