import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.websocket.websocket import manager


def _token_from_headers(headers: dict[str, str]) -> str:
    return headers["Authorization"].removeprefix("Bearer ")


def test_websocket_rejects_missing_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pass


def test_websocket_rejects_invalid_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=not-a-valid-token"):
            pass


def test_websocket_replays_current_run_events(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    token = _token_from_headers(superuser_token_headers)
    buffered_event = {"metric_analyser": {"messages": []}}
    manager.current_run_json = [buffered_event]
    try:
        with client.websocket_connect(f"/ws?token={token}") as websocket:
            assert websocket.receive_json() == buffered_event
    finally:
        manager.delete_current_run_json()
        assert manager.active_connections == []
