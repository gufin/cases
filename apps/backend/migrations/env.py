import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings

# Import all models so they register with Base.metadata
import app.db.models  # noqa: F401
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    asyncpg does not support offline SQL generation directly.
    Use a sync psycopg2 URL if you need --sql output.
    """
    raise NotImplementedError(
        "Offline mode is not supported with asyncpg. "
        "Use a sync driver URL for --sql generation."
    )


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def _async_url(url: str) -> str:
    """Ensure the URL uses the asyncpg driver scheme."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def run_async_migrations() -> None:
    async_engine = create_async_engine(_async_url(settings.database_url))
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await async_engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
