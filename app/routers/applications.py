from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.db import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.audit_log import AuditLog
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector
from app.schemas.application import ApplicationOut

router = APIRouter()


@router.get("/", response_model=list[ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    if app_obj.status == "submitted":
        raise HTTPException(status_code=400, detail="Cannot delete a submitted application")
    db.delete(app_obj)
    db.commit()
    return {"message": "Deleted", "id": application_id}


@router.post("/{application_id}/submit", response_model=ApplicationOut)
async def submit_application(application_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    if app_obj.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Application must be approved first. Current status: {app_obj.status}",
        )

    job = db.query(Job).filter(Job.id == app_obj.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Associated job not found")

    duplicate = db.query(Application).filter(
        Application.job_id == app_obj.job_id,
        Application.profile_id == app_obj.profile_id,
        Application.status == "submitted",
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Duplicate application detected")

    payload = {
        "external_id": job.external_id,
        "url": job.url,
        "form": app_obj.submit_payload or {},
        "files": {},
    }

    try:
        if job.ats_type == "greenhouse":
            connector = GreenhouseConnector()
        elif job.ats_type == "lever":
            connector = LeverConnector()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported ATS type: {job.ats_type}")

        result = await connector.submit_application(payload)
        app_obj.status = "submitted"
        app_obj.submitted_at = datetime.utcnow()
        app_obj.external_application_id = str(result.get("id", ""))
        job.status = "applied"

        log = AuditLog(
            action="application_submitted",
            entity="Application",
            entity_id=application_id,
            payload={"job_id": job.id, "ats_type": job.ats_type, "result": result},
        )
        db.add(log)
        db.commit()
        db.refresh(app_obj)
        return app_obj

    except HTTPException:
        raise
    except Exception as exc:
        app_obj.status = "error"
        app_obj.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=502, detail=f"ATS submission failed: {exc}")
