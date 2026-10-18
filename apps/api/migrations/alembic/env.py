"""Alembic environment configuration skeleton.

Connected to the SQLAlchemy metadata in T013-T016 once the domain models
exist. Until then, target_metadata is a placeholder so `alembic` commands
can be exercised against the apps/api/migrations/alembic directory.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all domain models so they are registered on the shared
# SQLAlchemy Base.metadata for Alembic autogenerate support.
from admin_template.db.base import Base  # noqa: E402
from admin_template.modules.identity.models import user  # noqa: F401,E402
from admin_template.modules.identity.models import integration  # noqa: F401,E402
from admin_template.modules.workspace.models import workspace  # noqa: F401,E402
from admin_template.modules.workspace.models import member  # noqa: F401,E402
from admin_template.modules.sync.models import cursor  # noqa: F401,E402
from admin_template.modules.sync.models import idempotency  # noqa: F401,E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _required_url(config) -> str:
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise RuntimeError("sqlalchemy.url is not configured in alembic.ini")
    return url


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        _required_url(config),
        poolclass=pool.NullPool,
    )

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    import asyncio

    asyncio.run(run_async_migrations())


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
