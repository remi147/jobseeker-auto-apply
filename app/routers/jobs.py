from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.job import Job
from app.models.profile import Profile
from app.models.application import Application
from app.services.ingest_service import IngestService
from app.services.matching_service import MatchingService
from app.core.config import settings

router = APIRouter()


@router.post("/ingest")
async def ingest_jobs(db: Session = Depends(get_db)):
    service = IngestService(db)
    result = await service.ingest_all()
    return {"message": "Ingestion complete", **result}


@router.post("/match")
def match_jobs(db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.is_active == True).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No active profile found. Create one at POST /profiles/")
    jobs = db.query(Job).filter(Job.status == "new").all()
    matcher = MatchingService()
    queued = 0
    for job in jobs:
        result = matcher.score(profile, job)
        job.match_score = result.score
        if result.score >= settings.min_match_score and not result.blockers:
            job.status = "matched"
            app = Application(
                job_id=job.id,
                profile_id=profile.id,
                status="pending_review",
                match_score=result.score,
                score_breakdown=result.breakdown,
            )
            db.add(app)
            queued += 1
        else:
            job.status = "below_threshold"
    db.commit()
    return {"matched": queued, "total_scored": len(jobs)}


@router.get("/")
def list_jobs(status: str = None, db: Session = Depends(get_db)):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    return q.order_by(Job.match_score.desc().nullslast()).all()
