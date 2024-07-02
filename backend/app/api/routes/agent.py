from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, FastAPI

# Importer l'agent
from app.monitoring_agent.main import run
from app.websocket.websocket import manager

router = APIRouter()


@router.post("/run")
async def run_agent():
    try:
        await run(manager)
        return {"message": "Agent runned successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
