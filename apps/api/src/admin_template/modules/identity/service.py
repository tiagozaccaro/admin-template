"""Identity service: external identity linking/unlinking.

External identities are never silently merged across accounts. A given
(provider, provider_sub) binds to exactly one user; linking a provider
identity already bound to a different user raises an error. This prevents
account takeover via two provider identities sharing an email.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select

from admin_template.auth.oidc import IDTokenClaims
from admin_template.core.db import db
from admin_template.modules.identity.models.external_identity import ExternalIdentity
from admin_template.modules.identity.models.user import User


async def _session_factory():
    """Return the initialized async session factory."""
    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    return db.session_factory


class IdentityLinkError(ValueError):
    """Raised when an external identity cannot be linked."""


async def get_or_create_user_from_claims(claims: IDTokenClaims) -> User:
    """Get or create the internal User for validated Google ID token claims.

    Links the external Google identity to the user, creating both when
    neither exists. When the Google identity is already bound to a
    different user, raises IdentityLinkError (no silent merge).
    """
    async with (await _session_factory())() as database_session:
        # 1. Resolve by existing external identity (provider + sub).
        result = await database_session.execute(
            select(ExternalIdentity).where(
                ExternalIdentity.provider == "google",
                ExternalIdentity.provider_sub == claims.sub,
            )
        )
        external = result.scalars().first()
        if external is not None:
            user = await database_session.get(User, external.user_id)
            if user is None:
                raise IdentityLinkError("External identity references missing user")
            if claims.name and user.display_name != claims.name:
                user.display_name = claims.name
                await database_session.commit()
            return user

        # 2. No external identity yet: try to find an existing user by email
        #    and link it (explicit linking for shared email). If no user,
        #    create a new one.
        if claims.email:
            result = await database_session.execute(
                select(User).where(User.email == claims.email)
            )
            user = result.scalars().first()
            if user is None:
                user = User(
                    keycloak_sub=claims.sub,
                    email=claims.email,
                    display_name=claims.name,
                )
                database_session.add(user)
                await database_session.flush()
            elif claims.name and user.display_name != claims.name:
                user.display_name = claims.name
        else:
            user = User(
                keycloak_sub=claims.sub,
                email="",
                display_name=claims.name,
            )
            database_session.add(user)
            await database_session.flush()

        # 3. Link the external identity.
        external = ExternalIdentity(
            user_id=user.id,
            provider="google",
            provider_sub=claims.sub,
            provider_email=claims.email,
        )
        database_session.add(external)
        await database_session.commit()
        await database_session.refresh(user)
        return user


async def link_external_identity(
    user_id: uuid.UUID, claims: IDTokenClaims
) -> ExternalIdentity:
    """Explicitly link a Google identity to an existing user.

    Raises IdentityLinkError when the identity is already bound to a
    different user (no silent merge).
    """
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(ExternalIdentity).where(
                ExternalIdentity.provider == "google",
                ExternalIdentity.provider_sub == claims.sub,
            )
        )
        existing = result.scalars().first()
        if existing is not None and existing.user_id != user_id:
            raise IdentityLinkError(
                "Google identity is already bound to another account"
            )
        if existing is None:
            external = ExternalIdentity(
                user_id=user_id,
                provider="google",
                provider_sub=claims.sub,
                provider_email=claims.email,
            )
            database_session.add(external)
            await database_session.commit()
            await database_session.refresh(external)
            return external
        return existing


async def unlink_external_identity(user_id: uuid.UUID, provider_sub: str) -> None:
    """Unlink the Google identity for a user (provider_sub match)."""
    async with (await _session_factory())() as database_session:
        result = await database_session.execute(
            select(ExternalIdentity).where(
                ExternalIdentity.provider == "google",
                ExternalIdentity.provider_sub == provider_sub,
                ExternalIdentity.user_id == user_id,
            )
        )
        external = result.scalars().first()
        if external is not None:
            await database_session.delete(external)
            await database_session.commit()
