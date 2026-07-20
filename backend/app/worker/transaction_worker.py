"""Background worker that processes queued transactions."""

import asyncio
import json
import random

import structlog
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.entities.transaction import TransactionStatus
from app.infrastructure.db.repositories.transaction_repository import (
    TransactionRepository,
)
from app.infrastructure.db.session import get_session
from app.infrastructure.queue.redis_client import get_redis_client
from app.infrastructure.queue.redis_queue import RedisQueueService
from app.infrastructure.queue.transaction_events import publish_transaction_update

MIN_PROCESSING_SECONDS = 2.0
MAX_PROCESSING_SECONDS = 4.0
FAILURE_PROBABILITY = 0.1

configure_logging()
log = structlog.get_logger(__name__)


async def _process_one(
    queue: RedisQueueService, queue_name: str, redis_client: Redis
) -> None:
    raw_payload = await queue.dequeue(queue_name)
    if not raw_payload:
        return

    transaction_id = json.loads(raw_payload)["transaction_id"]
    log.info("worker.processing", transaction_id=transaction_id)

    try:
        await asyncio.sleep(
            random.uniform(  # noqa: S311 -- simulated latency, not security-sensitive
                MIN_PROCESSING_SECONDS, MAX_PROCESSING_SECONDS
            )
        )
        new_status = (
            TransactionStatus.FAILED
            if random.random() < FAILURE_PROBABILITY  # noqa: S311
            else TransactionStatus.PROCESSED
        )

        async for session in get_session():
            repo = TransactionRepository(session)
            updated = await repo.update_status(transaction_id, new_status)
            break

        await publish_transaction_update(
            redis_client,
            {
                "event": "transaction.updated",
                "id": str(updated.id),
                "status": updated.status.value,
            },
        )
        log.info("worker.done", transaction_id=transaction_id, status=new_status.value)
    except Exception as exc:
        log.error("worker.error", transaction_id=transaction_id, error=str(exc))
        async for session in get_session():
            repo = TransactionRepository(session)
            await repo.update_status(transaction_id, TransactionStatus.FAILED)
            break


async def run_worker() -> None:
    """Continuously dequeue and process transactions until cancelled."""
    settings = get_settings()
    redis_client = get_redis_client()
    queue = RedisQueueService(redis_client)
    log.info("worker.started", queue=settings.transactions_queue_name)

    while True:
        await _process_one(queue, settings.transactions_queue_name, redis_client)


if __name__ == "__main__":
    asyncio.run(run_worker())
