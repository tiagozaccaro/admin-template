"""Dashboard aggregation service."""

from __future__ import annotations

import uuid


async def get_dashboard_metrics(tenant_id: uuid.UUID) -> dict:
    return {
        "tenant_id": str(tenant_id),
        "users": 0,
        "workspaces": 0,
        "recent_activity": [],
    }


__all__ = ["get_dashboard_metrics"]
