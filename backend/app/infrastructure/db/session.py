"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create the async SQLAlchemy engine from application settings."""
    return create_async_engine(
        settings.database_url, echo=settings.app_debug, pool_pre_ping=True
    )


_engine: AsyncEngine = create_engine(get_settings())
_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    _engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Yield an AsyncSession for use as a FastAPI dependency."""
    async with _session_factory() as session:
        yield session
