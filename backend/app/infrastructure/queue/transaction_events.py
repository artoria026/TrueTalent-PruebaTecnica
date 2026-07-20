"""Redis pub/sub channel the worker uses to notify the API of transaction updates."""

import json
from typing import Any

from redis.asyncio import Redis

TRANSACTIONS_UPDATES_CHANNEL = "transactions:updates"


async def publish_transaction_update(
    redis_client: Redis, message: dict[str, Any]
) -> None:
    """Publish a transaction update event for the API process to relay."""
    await redis_client.publish(TRANSACTIONS_UPDATES_CHANNEL, json.dumps(message))
