from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.db import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.audit_log import AuditLog
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector

router = APIRouter()


@router.get("/")
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()


@router.get("/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("/{application_id}/submit")
async def submit_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != "approved":
        raise HTTPException(status_code=400, detail=f"Application must be approved first. Current status: {app.status}")

    job = db.query(Job).filter(Job.id == app.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Duplicate check
    duplicate = db.query(Application).filter(
        Application.job_id == app.job_id,
        Application.profile_id == app.profile_id,
        Application.status == "submitted",
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Duplicate application detected")

    payload = {"external_id": job.external_id, "url": job.url, "form": {}, "files": {}}

    try:
        if job.ats_type == "greenhouse":
            connector = GreenhouseConnector()
        elif job.ats_type == "lever":
            connector = LeverConnector()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported ATS type: {job.ats_type}. Use Playwright fallback manually.")

        result = await connector.submit_application(payload)
        app.status = "submitted"
        app.submitted_at = datetime.utcnow()
        app.external_application_id = str(result.get("id", ""))

    except Exception as e:
        app.status = "error"
        app.error_message = str(e)
        db.add(AuditLog(action="application_error", entity="application", entity_id=app.id, note=str(e)))
        db.commit()
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

    db.add(AuditLog(action="application_submitted", entity="application", entity_id=app.id))
    db.commit()
    return {"message": "Application submitted", "id": application_id, "status": "submitted"}
