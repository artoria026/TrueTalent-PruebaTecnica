"""Integration tests for the WebSocket endpoint."""

from starlette.testclient import TestClient

from app.main import app


def test_websocket_connect_and_disconnect_closes_cleanly() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/v1/transactions/stream") as websocket:
        websocket.close()
