"""Admin Template API core module.

Provides settings, database, observability, and security placeholders that
are implemented in T013-T016.
"""

from . import (
    obs,
    security,
)
from .db import db
from .settings import settings

__all__ = ["db", "obs", "security", "settings"]
