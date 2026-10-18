"""Account integration model.

Identity bounded context: a securely stored external account connection
associated with a user profile (FR-013). Tokens are stored as encrypted
bytea; never logged.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User


class AccountIntegration(Base):
    """A linked external account, with an encrypted access token."""

    __tablename__ = "account_integration"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(nullable=False)
    external_id: Mapped[str] = mapped_column(nullable=False)
    encrypted_token: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f"AccountIntegration(id={self.id!r}, provider={self.provider!r})"


__all__ = ["AccountIntegration"]
