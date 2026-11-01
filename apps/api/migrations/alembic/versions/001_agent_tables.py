"""agent tables

Revision ID: 001_agent_tables
Revises:
Create Date: 2026-10-30 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_agent_tables"
down_revision: Union[str, None] = "9e7c3a1b2f40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("token_hash", sa.String(length=512), nullable=True),
        sa.Column(
            "capabilities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
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
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_agent_tenant_id", "agent", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_agent_status", "agent", ["status"], unique=False
    )
    op.create_index(
        "ix_agent_name_tenant_id",
        "agent",
        ["name", "tenant_id"],
        unique=True,
    )

    op.create_table(
        "agent_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
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
        sa.Column("history", postgresql.JSON(astext_type=sa.Text()), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
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
    )
    op.create_index(
        "ix_agent_session_agent_id",
        "agent_session",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_session_user_id",
        "agent_session",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_session_tenant_id",
        "agent_session",
        ["tenant_id"],
        unique=False,
    )

    op.create_table(
        "audit_entry",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("tool_name", sa.String(length=255), nullable=False),
        sa.Column(
            "args",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_audit_entry_tenant_id",
        "audit_entry",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_audit_entry_user_id",
        "audit_entry",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_audit_entry_agent_id",
        "audit_entry",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_audit_entry_tool_name",
        "audit_entry",
        ["tool_name"],
        unique=False,
    )
    op.create_index(
        "ix_audit_entry_status",
        "audit_entry",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("audit_entry")
    op.drop_table("agent_session")
    op.drop_index("ix_agent_name_tenant_id", table_name="agent")
    op.drop_index("ix_agent_status", table_name="agent")
    op.drop_index("ix_agent_tenant_id", table_name="agent")
    op.drop_table("agent")