"""Factory for the shared async Redis client."""

from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    """Return a cached async Redis client built from application settings."""
    settings = get_settings()
    return Redis.from_url(  # type: ignore[no-any-return]
        settings.redis_url, decode_responses=False
    )
