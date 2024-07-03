import logging
from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, FastAPI
from sqlalchemy.orm import joinedload
from sqlmodel import select, desc

from app.api.deps import SessionDep
from app.crud import create_run
from app.models import AgentRun, AgentRunsPublic, Event

# Importer l'agent
from app.monitoring_agent.main import run
from app.websocket.websocket import manager

router = APIRouter()


@router.post("/run")
async def run_agent(session: SessionDep):
    logging.warning("Running agent")
    try:
        agent_run = create_run(session)
        logging.warning("Agent run created")

        await run(manager, session, agent_run.id)
        logging.warning("Agent runned")
        return {"message": "Agent runned successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs", response_model=AgentRunsPublic)
async def get_runs(session: SessionDep) -> AgentRunsPublic:
    logging.warning("Getting runs")

    # Get all runs with their events
    runs = session.exec(select(AgentRun).order_by(desc(AgentRun.start_time))).all()

    # Sort events by id
    for run in runs:
        run.events.sort(key=lambda e: e.id)

    return AgentRunsPublic(data=runs, count=len(runs))


@router.get("/run/{id}")
async def get_run(session: SessionDep, id: int):
    run = session.get(AgentRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
