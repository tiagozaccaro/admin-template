"""Pytest fixtures for the Admin Template API contract tests."""

import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import configure_mappers

from admin_template.api.main import app
from admin_template.core.settings import settings

PLACEHOLDER_PRINCIPAL = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client bound to the application instance."""
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def _configure_sqlalchemy_mappers() -> None:
    """Configure SQLAlchemy mappers once before tests.

    Required because US2 models use joined-table inheritance
    (ContentItem -> Idea/Script) and string forward references that
    resolve lazily at mapper-configuration time.
    """
    configure_mappers()


@pytest.fixture(scope="session", autouse=True)
def _seed_placeholder_principal() -> None:
    """Create the placeholder user/workspace that contract tests reference.

    The sources/stories routers currently default workspace_id and
    connected_by to a placeholder principal (auth is wired in T094/T094).
    Seed those rows so foreign-key constraints are satisfied against a real
    database. Idempotent: safe to re-run against an already-seeded database.
    """

    async def _seed() -> None:
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        from admin_template.modules.identity.models.user import User
        from admin_template.modules.workspace.models.workspace import Workspace

        async with session_factory() as session:
            await session.execute(
                insert(User.__table__)
                .values(
                    id=PLACEHOLDER_PRINCIPAL,
                    keycloak_sub=PLACEHOLDER_PRINCIPAL,
                    email="placeholder@example.com",
                    display_name="Placeholder",
                )
                .on_conflict_do_nothing()
            )
            await session.execute(
                insert(Workspace.__table__)
                .values(
                    id=PLACEHOLDER_PRINCIPAL,
                    owner_id=PLACEHOLDER_PRINCIPAL,
                    name="Placeholder Workspace",
                )
                .on_conflict_do_nothing()
            )
            await session.commit()
        await engine.dispose()

    asyncio.run(_seed())


@pytest.fixture(scope="session", autouse=True)
def _dispose_db_engine() -> None:
    """Dispose the async engine's connection pool after the test session.

    Prevents asyncpg from aborting connections on a closed event loop at
    interpreter shutdown (async SQLAlchemy + sync TestClient teardown).
    """
    yield
    from admin_template.core.db import db

    if db.engine is not None:
        try:
            asyncio.run(db.engine.dispose())
        except Exception:  # noqa: BLE001 -- best-effort cleanup
            pass
