"""Redis-backed implementation of QueueServicePort."""

import structlog
from redis.asyncio import Redis

from app.domain.exceptions import QueuePublishError
from app.domain.interfaces.queue_service import QueueServicePort

DEQUEUE_TIMEOUT_SECONDS = 5

log = structlog.get_logger(__name__)


class RedisQueueService(QueueServicePort):
    """Implements QueueServicePort backed by a Redis list (BLPOP/RPUSH)."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def enqueue(self, queue_name: str, payload: str) -> None:
        try:
            await self._redis.rpush(queue_name, payload)  # type: ignore[misc]
            log.info("queue.enqueued", queue=queue_name, payload=payload)
        except Exception as exc:
            log.error("queue.enqueue_failed", queue=queue_name, error=str(exc))
            raise QueuePublishError(
                f"Failed to enqueue payload on '{queue_name}'"
            ) from exc

    async def dequeue(self, queue_name: str) -> str | None:
        result = await self._redis.blpop(  # type: ignore[misc]
            [queue_name], timeout=DEQUEUE_TIMEOUT_SECONDS
        )
        if result is None:
            return None
        _, payload = result
        return payload.decode("utf-8") if isinstance(payload, bytes) else payload
