"""Tenancy module."""

from admin_template.modules.tenancy import service
from admin_template.modules.tenancy.router import router

__all__ = ["router", "service"]
