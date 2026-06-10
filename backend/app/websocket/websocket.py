import logging
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Broadcasts agent run events to all connected websocket clients.

    Events of the run in progress are buffered so that clients connecting
    mid-run receive the events emitted before they joined.
    """

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self.current_run_json: list[Any] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        for message in self.current_run_json:
            await websocket.send_json(message)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_json(self, message: Any) -> None:
        logging.debug("Broadcasting message: %s", message)
        self.current_run_json.append(message)
        for connection in self.active_connections:
            await connection.send_json(message)

    async def send_text(self, message: str) -> None:
        logging.debug("Broadcasting message: %s", message)
        for connection in self.active_connections:
            await connection.send_text(message)

    def delete_current_run_json(self) -> None:
        self.current_run_json = []


manager = ConnectionManager()
