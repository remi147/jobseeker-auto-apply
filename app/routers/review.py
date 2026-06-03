from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.db import get_db
from app.models.application import Application

router = APIRouter()


@router.get("/pending")
def get_pending(db: Session = Depends(get_db)):
    apps = db.query(Application).filter(Application.status == "pending_review").all()
    return apps


@router.post("/{application_id}/approve")
def approve(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != "pending_review":
        raise HTTPException(status_code=400, detail=f"Cannot approve application with status '{app.status}'")
    app.status = "approved"
    app.approved_at = datetime.utcnow()
    app.approved_by = "user"
    db.commit()
    return {"message": "Application approved", "id": application_id, "next": f"POST /applications/{application_id}/submit"}


@router.post("/{application_id}/reject")
def reject(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "rejected"
    db.commit()
    return {"message": "Application rejected", "id": application_id}
