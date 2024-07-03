import logging
from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, FastAPI
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import AgentRun, AgentRunsPublic

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


@router.get("runs", response_model=AgentRunsPublic)
async def get_runs(session: SessionDep):
    logging.warning("Getting runs")
    runs = session.exec(select(AgentRun)).all()
    return AgentRunsPublic(data=runs, count=len(runs))


@router.get("/run/{id}")
async def get_run(session: SessionDep, id: int):
    run = session.get(AgentRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
