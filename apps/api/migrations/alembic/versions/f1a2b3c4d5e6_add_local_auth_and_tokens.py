"""Add local auth fields and verification/reset token tables

Revision ID: f1a2b3c4d5e6
Revises: e4f8a2b3c1d0
Create Date: 2026-10-23 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "f1a2b3c4d5e6"
down_revision = "e4f8a2b3c1d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "keycloak_sub", existing_type=sa.String(255), nullable=True)
    op.add_column("user", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("user", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("user", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_user_email", "user", ["email"], unique=False)

    op.create_table(
        "email_verification_token",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_email_verification_token_hash"),
    )
    op.create_index("ix_email_verification_token_user_id", "email_verification_token", ["user_id"])

    op.create_table(
        "password_reset_token",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_password_reset_token_hash"),
    )
    op.create_index("ix_password_reset_token_user_id", "password_reset_token", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_password_reset_token_user_id", table_name="password_reset_token")
    op.drop_table("password_reset_token")
    op.drop_index("ix_email_verification_token_user_id", table_name="email_verification_token")
    op.drop_table("email_verification_token")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_column("user", "deleted_at")
    op.drop_column("user", "email_verified")
    op.drop_column("user", "password_hash")
    op.alter_column("user", "keycloak_sub", existing_type=sa.String(255), nullable=False)