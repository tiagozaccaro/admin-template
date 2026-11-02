"""Tenant membership model."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.identity.models.user import User
from admin_template.modules.tenancy.models.tenant import Tenant


class TenantRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TenantMembership(Base):
    """User-tenant association with role."""

    __tablename__ = "tenant_membership"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_tenant_membership_user_tenant"),
        Index("ix_tenant_membership_user_id", "user_id"),
        Index("ix_tenant_membership_tenant_id", "tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[TenantRole] = mapped_column(
        SAEnum(TenantRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    tenant: Mapped["Tenant"] = relationship("Tenant", foreign_keys=[tenant_id])


__all__ = ["TenantMembership", "TenantRole"]
