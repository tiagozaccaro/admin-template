"""API v1 router."""

from fastapi import APIRouter

from admin_template.modules.agents.router import router as agents_router
from admin_template.modules.dashboard.router import router as dashboard_router
from admin_template.modules.items.router import router as items_router
from admin_template.modules.settings.router import router as settings_router
from admin_template.modules.tenancy.router import router as tenancy_router

router = APIRouter()

router.include_router(agents_router, prefix="/agents", tags=["agents"])
router.include_router(tenancy_router, prefix="/tenants", tags=["tenants"])
router.include_router(dashboard_router, tags=["dashboard"])
router.include_router(items_router, tags=["items"])
router.include_router(settings_router, tags=["settings"])

__all__ = ["router"]
