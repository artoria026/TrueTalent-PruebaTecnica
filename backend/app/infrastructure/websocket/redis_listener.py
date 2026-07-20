"""Relays Redis pub/sub transaction events to this process's WebSocket clients."""

import asyncio
import json

import structlog
from redis.asyncio import Redis

from app.infrastructure.queue.transaction_events import TRANSACTIONS_UPDATES_CHANNEL
from app.infrastructure.websocket.connection_manager import manager

log = structlog.get_logger(__name__)


async def relay_transaction_updates(redis_client: Redis) -> None:
    """Subscribe to the transactions channel and broadcast every message received."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(TRANSACTIONS_UPDATES_CHANNEL)
    log.info("websocket.relay_started", channel=TRANSACTIONS_UPDATES_CHANNEL)
    try:
        async for raw_message in pubsub.listen():
            if raw_message["type"] != "message":
                continue
            payload = json.loads(raw_message["data"])
            await manager.broadcast(payload)
    except asyncio.CancelledError:
        raise
    finally:
        await pubsub.unsubscribe(TRANSACTIONS_UPDATES_CHANNEL)
        await pubsub.aclose()
