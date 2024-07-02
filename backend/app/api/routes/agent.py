from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, FastAPI

# Importer l'agent
from app.monitoring_agent.main import run

router = APIRouter()

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/run")
async def run_agent():
    try:
        await run(manager)
        return {"message": "Agent runned successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
