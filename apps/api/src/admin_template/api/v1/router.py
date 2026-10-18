"""API v1 router.

Mounts versioned route modules. Future modules (tenants, dashboard, CRUD,
AI, etc.) mount here under ``/api/v1``. Auth routes live at top-level
``/auth`` per the API contract.
"""

from fastapi import APIRouter

router = APIRouter()

__all__ = ["router"]
