"""WorkspaceMember model.

Workspace bounded context: a user's membership in a workspace with a
role (owner/member/viewer). Composite primary key (workspace_id, user_id).
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User
from admin_template.modules.workspace.models.workspace import Workspace


class WorkspaceRole(str, Enum):
    """Workspace membership roles (deny-by-default, least privilege)."""

    OWNER = "owner"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceMember(Base):
    """A user's membership in a workspace."""

    __tablename__ = "workspace_member"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        SAEnum(WorkspaceRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=WorkspaceRole.VIEWER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace", foreign_keys=[workspace_id]
    )
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"WorkspaceMember(workspace_id={self.workspace_id!r}, user_id={self.user_id!r}, role={self.role!r})"


__all__ = ["WorkspaceMember", "WorkspaceRole"]
