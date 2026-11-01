"""agent health_token column

Revision ID: 002_agent_health_token
Revises: 001_agent_tables
Create Date: 2026-11-01 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_agent_health_token"
down_revision: Union[str, None] = "001_agent_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agent",
        sa.Column(
            "health_token",
            sa.String(length=512),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_agent_health_token",
        "agent",
        ["health_token"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_health_token", table_name="agent")
    op.drop_column("agent", "health_token")


__all__ = ["upgrade", "downgrade"]