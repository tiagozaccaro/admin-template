"""API v1 router."""

from fastapi import APIRouter

from admin_template.modules.tenancy.router import router as tenancy_router

router = APIRouter()

router.include_router(tenancy_router, prefix="/tenants", tags=["tenants"])

__all__ = ["router"]
