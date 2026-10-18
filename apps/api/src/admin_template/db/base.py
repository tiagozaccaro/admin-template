"""Shared SQLAlchemy declarative base.

All domain models inherit from this Base so foreign-key relationships and
Alembic autogenerate operate over a single metadata registry.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all Admin Template domain models."""


__all__ = ["Base"]
