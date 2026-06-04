from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.db import get_db
from app.models.job import Job
from app.models.profile import Profile
from app.models.application import Application
from app.services.ingest_service import IngestService
from app.services.matching_service import MatchingService
from app.schemas.job import JobOut
from app.core.config import settings

router = APIRouter()


@router.post("/ingest")
async def ingest_jobs(db: Session = Depends(get_db)):
    """Trigger a manual job ingestion from all configured ATS connectors."""
    service = IngestService(db)
    result = await service.ingest_all()
    return {"message": "Ingestion complete", **result}


@router.post("/match")
def match_jobs(db: Session = Depends(get_db)):
    """Score all new jobs against the active profile and queue matches for review."""
    profile = db.query(Profile).filter(Profile.is_active == True).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="No active profile found. Create one at POST /profiles/",
        )
    jobs = db.query(Job).filter(Job.status == "new").all()
    matcher = MatchingService()
    queued = 0
    for job in jobs:
        result = matcher.score(profile, job)
        job.match_score = result.score
        if result.score >= settings.min_match_score and not result.blockers:
            job.status = "matched"
            exists = db.query(Application).filter(
                Application.job_id == job.id,
                Application.profile_id == profile.id,
            ).first()
            if not exists:
                app = Application(
                    job_id=job.id,
                    profile_id=profile.id,
                    status="pending_review",
                    match_score=result.score,
                    score_breakdown=result.breakdown,
                    ats_type=job.ats_type,
                )
                db.add(app)
                queued += 1
        else:
            job.status = "below_threshold"
    db.commit()
    return {
        "matched": queued,
        "total_scored": len(jobs),
        "threshold": settings.min_match_score,
    }


@router.post("/ingest-and-match")
async def ingest_and_match(db: Session = Depends(get_db)):
    """Convenience: ingest then immediately match."""
    ingest_svc = IngestService(db)
    ingest_result = await ingest_svc.ingest_all()

    profile = db.query(Profile).filter(Profile.is_active == True).first()
    if not profile:
        return {"ingest": ingest_result, "match": "skipped - no active profile"}

    jobs = db.query(Job).filter(Job.status == "new").all()
    matcher = MatchingService()
    queued = 0
    for job in jobs:
        result = matcher.score(profile, job)
        job.match_score = result.score
        if result.score >= settings.min_match_score and not result.blockers:
            job.status = "matched"
            exists = db.query(Application).filter(
                Application.job_id == job.id,
                Application.profile_id == profile.id,
            ).first()
            if not exists:
                app = Application(
                    job_id=job.id,
                    profile_id=profile.id,
                    status="pending_review",
                    match_score=result.score,
                    score_breakdown=result.breakdown,
                    ats_type=job.ats_type,
                )
                db.add(app)
                queued += 1
        else:
            job.status = "below_threshold"
    db.commit()
    return {"ingest": ingest_result, "match": {"queued": queued, "scored": len(jobs)}}


@router.get("/", response_model=list[JobOut])
def list_jobs(
    status: Optional[str] = None,
    remote: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    if remote is not None:
        q = q.filter(Job.remote == remote)
    return q.order_by(Job.match_score.desc().nullslast()).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted", "id": job_id}
