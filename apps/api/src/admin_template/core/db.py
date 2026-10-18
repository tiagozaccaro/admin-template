"""Database session management.

SQLAlchemy 2 async engine backed by asyncpg, with a FastAPI-compatible
session dependency. The engine is initialized from settings.database_url
(which may come from a Docker `_FILE` secret mount); no connection
string is committed.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from admin_template.core.settings import settings


class Database:
    """Database connection manager."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self, database_url: str | None = None) -> None:
        """Initialize the async engine and session factory."""
        url = database_url or settings.database_url
        if not url:
            raise RuntimeError("DATABASE_URL is not configured")
        self.engine = create_async_engine(url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a database session."""
        if self.session_factory is None:
            self.init()
        assert self.session_factory is not None
        async with self.session_factory() as session:
            yield session


db = Database()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session."""
    async for session in db.session():
        yield session


__all__ = ["AsyncSession", "Database", "db", "get_session"]
