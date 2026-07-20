"""Manages active WebSocket connections and broadcasts."""

from typing import Any

import structlog
from fastapi import WebSocket

log = structlog.get_logger(__name__)


class ConnectionManager:
    """Tracks active WebSocket connections and broadcasts JSON messages."""

    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._active.append(websocket)
        log.info("websocket.connected", total=len(self._active))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the active pool."""
        if websocket in self._active:
            self._active.remove(websocket)
        log.info("websocket.disconnected", total=len(self._active))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a JSON message to every active connection, pruning dead ones."""
        dead: list[WebSocket] = []
        for ws in self._active:
            try:
                await ws.send_json(message)
            except Exception as exc:
                log.warning("websocket.send_failed", error=str(exc))
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws)

        log.debug(
            "websocket.broadcast",
            clients=len(self._active),
            message_event=message.get("event"),
        )


manager = ConnectionManager()
