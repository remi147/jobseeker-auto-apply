from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
from app.core.db import get_db
from app.models.cv import CVVersion

router = APIRouter()
CV_UPLOAD_DIR = os.getenv("CV_UPLOAD_DIR", "./uploads/cv")
os.makedirs(CV_UPLOAD_DIR, exist_ok=True)


@router.get("/")
def list_cvs(profile_id: int, db: Session = Depends(get_db)):
    return db.query(CVVersion).filter(CVVersion.profile_id == profile_id).all()


@router.post("/")
def upload_cv(
    profile_id: int = Form(...),
    name: str = Form(...),
    tags: str = Form(default=""),
    cover_letter_template: str = Form(default=""),
    is_default: bool = Form(default=False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    dest = os.path.join(CV_UPLOAD_DIR, f"{profile_id}_{name}_{file.filename}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if is_default:
        db.query(CVVersion).filter(
            CVVersion.profile_id == profile_id, CVVersion.is_default == True
        ).update({"is_default": False})

    cv = CVVersion(
        profile_id=profile_id,
        name=name,
        filename=file.filename,
        file_path=dest,
        tags=tags,
        cover_letter_template=cover_letter_template or None,
        is_default=is_default,
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv


@router.delete("/{cv_id}")
def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVVersion).filter(CVVersion.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    if os.path.exists(cv.file_path):
        os.remove(cv.file_path)
    db.delete(cv)
    db.commit()
    return {"message": "CV deleted", "id": cv_id}
