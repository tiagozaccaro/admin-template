"""Agent model.

Registry bounded context: a standalone machine admin agent daemon registered
in the core API so web/mobile clients can discover and chat with multiple
agents across machines.
"""

import hashlib
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_template.db.base import Base
from admin_template.modules.tenancy.models.tenant import Tenant


class Agent(Base):
    """A registered standalone admin agent daemon."""

    __tablename__ = "agent"
    __table_args__ = (
        Index("ix_agent_name_tenant_id", "name", "tenant_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    token_hash: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # Plaintext bearer token used by the core API to authenticate
    # outbound requests (health probes, audit pushes) to the daemon. Stored
    # separately from token_hash so the probe path never needs to reverse
    # the SHA-256 (FR-003).
    health_token: Mapped[str | None] = mapped_column(
        String(512), nullable=True, index=True
    )
    capabilities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), default="offline", nullable=False, index=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", foreign_keys=[tenant_id])

    def __repr__(self) -> str:
        return f"Agent(id={self.id!r}, name={self.name!r}, status={self.status!r})"


def hash_token(token: str) -> str:
    """Return a SHA-256 hex digest of an agent bearer token.

    Tokens are stored hashed so a database leak does not expose live credentials.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


__all__ = ["Agent", "hash_token"]
