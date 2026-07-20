"""WebSocket endpoint for real-time transaction updates."""

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.websocket.connection_manager import manager

router = APIRouter(prefix="/transactions", tags=["websocket"])

log = structlog.get_logger(__name__)


@router.websocket("/stream")
async def transactions_websocket(websocket: WebSocket) -> None:
    """Accept a WebSocket connection and keep it open until the client leaves."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log.info("websocket.client_left")
