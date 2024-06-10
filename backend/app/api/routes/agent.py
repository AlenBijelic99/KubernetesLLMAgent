from fastapi import APIRouter, HTTPException

# Importer l'agent
from app.monitoring_agent.main import run

router = APIRouter()


@router.post("/run")
async def run_agent():
    try:
        run()
        return {"message": "Agent started successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
