"""Redis-backed implementation of AIModeRepositoryPort."""

from redis.asyncio import Redis

from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort

AI_MODE_REDIS_KEY = "ai:force_mock"
_TRUE_VALUE = b"1"
_FALSE_VALUE = b"0"


class RedisAIModeRepository(AIModeRepositoryPort):
    """Persists the global AI mode toggle as a single Redis key."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def get_force_mock(self) -> bool:
        value = await self._redis.get(AI_MODE_REDIS_KEY)
        return bool(value == _TRUE_VALUE)

    async def set_force_mock(self, value: bool) -> None:
        await self._redis.set(AI_MODE_REDIS_KEY, _TRUE_VALUE if value else _FALSE_VALUE)
