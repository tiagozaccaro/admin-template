"""Workspace model.

Workspace bounded context: a tenant-scoped container for projects,
sources, evidence, and content, owned by a user and shared with members
via roles.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User


class Workspace(Base):
    """Tenant-scoped container owned by a user."""

    __tablename__ = "workspace"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])

    def __repr__(self) -> str:
        return f"Workspace(id={self.id!r}, name={self.name!r})"


__all__ = ["Workspace"]
