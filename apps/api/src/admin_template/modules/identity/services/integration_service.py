"""Integration service.

Links secure account integrations with encrypted token storage (T086).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_template.modules.identity.models.integration import AccountIntegration


class IntegrationService:
    """Creates and queries user account integrations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def link_integration(
        self,
        user_id: str,
        provider: str,
        external_id: str,
        encrypted_token: bytes,
        scopes: list[str],
    ) -> AccountIntegration:
        """Link a secure account integration for a user."""
        integration = AccountIntegration(
            user_id=uuid.UUID(user_id),
            provider=provider,
            external_id=external_id,
            encrypted_token=encrypted_token,
            scopes=scopes,
        )
        self.session.add(integration)
        await self.session.flush()
        await self.session.refresh(integration)
        return integration

    async def get_integration(self, integration_id: str) -> AccountIntegration | None:
        """Get an integration by id."""
        result = await self.session.execute(
            select(AccountIntegration).where(
                AccountIntegration.id == uuid.UUID(integration_id)
            )
        )
        return result.scalars().first()

    async def list_integrations(self, user_id: str) -> list[AccountIntegration]:
        """List integrations for a user."""
        result = await self.session.execute(
            select(AccountIntegration).where(
                AccountIntegration.user_id == uuid.UUID(user_id)
            )
        )
        return list(result.scalars().all())

    async def revoke_integration(self, integration_id: str) -> bool:
        """Revoke an integration by setting revoked_at."""
        integration = await self.get_integration(integration_id)
        if integration is None:
            return False
        from datetime import UTC, datetime

        integration.revoked_at = datetime.now(UTC)
        await self.session.flush()
        return True


__all__ = ["IntegrationService"]
