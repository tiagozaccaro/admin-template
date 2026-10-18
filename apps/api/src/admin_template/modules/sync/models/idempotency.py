"""Idempotency key model.

Sync bounded context: records responses keyed by Idempotency-Key header
so mutating endpoints are safely replayable per contracts/sync-api.md.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User


class IdempotencyKey(Base):
    """A recorded idempotent response for a user/endpoint/key."""

    __tablename__ = "idempotency_key"

    key: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(nullable=False)
    response_status: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f"IdempotencyKey(key={self.key!r}, endpoint={self.endpoint!r})"


__all__ = ["IdempotencyKey"]
