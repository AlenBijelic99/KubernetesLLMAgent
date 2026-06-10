import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_run
from app.models import AgentRun, AgentRunAndEventsPublic, AgentRunsPublic, Message
from app.monitoring_agent.main import run
from app.websocket.websocket import manager

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=Message)
async def run_agent(session: SessionDep, _current_user: CurrentUser) -> Any:
    """
    Run the monitoring agent. Events are broadcast over the websocket while
    the run progresses and are persisted with the run.
    """
    agent_run = create_run(session=session)
    logging.info("Agent run %s created", agent_run.id)
    try:
        await run(manager, session, agent_run.id)
    except Exception:
        logging.exception("Agent run %s failed", agent_run.id)
        raise HTTPException(status_code=500, detail="Agent run failed")
    return Message(message="Agent run finished successfully")


@router.get("/runs", response_model=AgentRunsPublic)
def get_runs(
    session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get all agent executions.
    """
    count_statement = select(func.count()).select_from(AgentRun)
    count = session.exec(count_statement).one()
    statement = (
        select(AgentRun)
        .order_by(col(AgentRun.start_time).desc())
        .offset(skip)
        .limit(limit)
    )
    runs = session.exec(statement).all()
    return AgentRunsPublic(data=runs, count=count)


@router.get("/run/{id}", response_model=AgentRunAndEventsPublic)
def get_run(session: SessionDep, _current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get an agent execution by id, with its events in chronological order.
    """
    agent_run = session.get(AgentRun, id)
    if not agent_run:
        raise HTTPException(status_code=404, detail="Run not found")
    agent_run.events.sort(key=lambda e: e.inserted_at)
    return agent_run
