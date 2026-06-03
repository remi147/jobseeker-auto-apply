from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileOut

router = APIRouter()


@router.post("/", response_model=ProfileOut)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(Profile).filter(Profile.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile with this email already exists")
    profile = Profile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/", response_model=list[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(Profile).all()


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/seed")
def seed_default_profile(db: Session = Depends(get_db)):
    existing = db.query(Profile).first()
    if existing:
        return {"message": "Profile already exists", "id": existing.id}
    profile = Profile(
        full_name="Your Name",
        email="your@email.com",
        location="Poland",
        target_titles="Security Analyst,Penetration Tester,SOC Analyst,Cybersecurity Engineer",
        target_locations="Warsaw,Krakow,Poznan,remote",
        remote_ok=True,
        salary_min=8000,
        allowed_seniority="junior,mid,senior",
        skills="python,penetration testing,nmap,burpsuite,linux,networking,siem,splunk,wireshark",
        languages="Polish,English",
        work_authorization="EU citizen",
        willing_to_relocate=False,
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Default profile seeded", "id": profile.id, "note": "Update your details at PUT /profiles/{id}"}
