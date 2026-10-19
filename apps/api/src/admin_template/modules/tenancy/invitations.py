"""Invitation service."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from admin_template.core.db import db
from admin_template.modules.tenancy.models.invitation import Invitation
from admin_template.modules.tenancy.models.tenant_membership import (
    TenantMembership,
    TenantRole,
)


async def _session_factory():
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_invitation(
    tenant_id: uuid.UUID,
    email: str,
    role: TenantRole,
    created_by: uuid.UUID | None,
    expires_in_days: int = 7,
) -> tuple[Invitation, str]:
    async with (await _session_factory())() as session:
        token = secrets.token_urlsafe(32)
        invitation = Invitation(
            tenant_id=tenant_id,
            email=email,
            role=role,
            token_hash=_hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
            created_by=created_by,
        )
        session.add(invitation)
        await session.commit()
        await session.refresh(invitation)
        return invitation, token


async def get_invitation_by_token(token: str) -> Invitation | None:
    token_hash = _hash_token(token)
    async with (await _session_factory())() as session:
        result = await session.execute(
            select(Invitation).where(Invitation.token_hash == token_hash)
        )
        return result.scalars().first()


async def accept_invitation(token: str, user_id: uuid.UUID) -> Invitation | None:
    token_hash = _hash_token(token)
    async with (await _session_factory())() as session:
        result = await session.execute(
            select(Invitation).where(Invitation.token_hash == token_hash)
        )
        invitation = result.scalars().first()
        if invitation is None:
            return None
        if invitation.revoked_at is not None:
            return None
        if invitation.accepted_at is not None:
            return None
        if invitation.expires_at <= datetime.now(UTC):
            return None

        membership = TenantMembership(
            tenant_id=invitation.tenant_id,
            user_id=user_id,
            role=invitation.role,
        )
        session.add(membership)
        result = await session.execute(
            update(Invitation)
            .where(Invitation.id == invitation.id)
            .values(accepted_at=datetime.now(UTC))
            .returning(Invitation)
        )
        await session.commit()
        return result.scalars().first()


async def revoke_invitation(invitation_id: uuid.UUID) -> Invitation | None:
    async with (await _session_factory())() as session:
        result = await session.execute(
            update(Invitation)
            .where(Invitation.id == invitation_id)
            .values(revoked_at=datetime.now(UTC))
            .returning(Invitation)
        )
        invitation = result.scalars().first()
        await session.commit()
        return invitation


async def expire_invitation(invitation_id: uuid.UUID) -> Invitation | None:
    async with (await _session_factory())() as session:
        result = await session.execute(
            update(Invitation)
            .where(Invitation.id == invitation_id)
            .values(expires_at=datetime.now(UTC))
            .returning(Invitation)
        )
        invitation = result.scalars().first()
        await session.commit()
        return invitation


__all__ = [
    "accept_invitation",
    "create_invitation",
    "expire_invitation",
    "get_invitation_by_token",
    "revoke_invitation",
]
