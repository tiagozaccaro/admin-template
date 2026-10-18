"""Admin Template API core module.

Provides settings, database, observability, and security foundations used by
the FastAPI application and its routers.
"""

from . import (
    obs,
    security,
)
from .db import db
from .settings import settings

__all__ = ["db", "obs", "security", "settings"]
