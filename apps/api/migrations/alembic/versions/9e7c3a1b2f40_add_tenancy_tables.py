"""Add tenancy tables (tenant, tenant_membership, invitation)

Revision ID: 9e7c3a1b2f40
Revises: f1a2b3c4d5e6
Create Date: 2026-10-31 00:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e7c3a1b2f40"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("branding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["user.id"],
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_tenant_slug", "tenant", ["slug"], unique=True)

    op.create_table(
        "tenant_membership",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "member",
                "viewer",
                name="tenantrole",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "tenant_id", name="uq_tenant_membership_user_tenant"),
    )
    op.create_index("ix_tenant_membership_user_id", "tenant_membership", ["user_id"])
    op.create_index("ix_tenant_membership_tenant_id", "tenant_membership", ["tenant_id"])

    op.create_table(
        "invitation",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "member",
                "viewer",
                name="tenantrole",
            ),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["user.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("token_hash", name="uq_invitation_token_hash"),
    )
    op.create_index("ix_invitation_tenant_id", "invitation", ["tenant_id"])
    op.create_index("ix_invitation_email", "invitation", ["email"])


def downgrade() -> None:
    op.drop_index("ix_invitation_email", table_name="invitation")
    op.drop_index("ix_invitation_tenant_id", table_name="invitation")
    op.drop_table("invitation")
    op.execute("DROP TYPE IF EXISTS tenantrole")
    op.drop_index("ix_tenant_membership_tenant_id", table_name="tenant_membership")
    op.drop_index("ix_tenant_membership_user_id", table_name="tenant_membership")
    op.drop_table("tenant_membership")
    op.drop_index("ix_tenant_slug", table_name="tenant")
    op.drop_table("tenant")
