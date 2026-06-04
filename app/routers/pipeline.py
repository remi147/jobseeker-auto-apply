"""Pipeline router - triggers the full ingest->match->submit cycle on demand."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.apply_service import ApplyService

router = APIRouter()


@router.post("/run")
async def run_pipeline(db: Session = Depends(get_db)):
    """Manually trigger the full pipeline: ingest -> match -> (auto-submit if AUTO_APPLY=true)."""
    svc = ApplyService(db)
    result = await svc.run_pipeline()
    return result
