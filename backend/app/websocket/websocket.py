import logging
from typing import List, Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.current_run_json: List[dict] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if self.current_run_json:
            logging.warning(f"Sending current run json: {self.current_run_json}")
            for message in self.current_run_json:
                await websocket.send_json(message)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, message: Any):
        logging.warning(f"Sent message: {message}")
        for connection in self.active_connections:
            self.current_run_json.append(message)
            await connection.send_json(message)

    async def send_text(self, message: str):
        logging.warning(f"Sent message: {message}")
        for connection in self.active_connections:
            await connection.send_text(message)

    def delete_current_run_json(self):
        self.current_run_json = []


manager = ConnectionManager()
