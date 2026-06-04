from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileOut

router = APIRouter()


@router.post("/", response_model=ProfileOut, status_code=201)
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


@router.put("/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: int, data: ProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "Profile deleted", "id": profile_id}


@router.post("/seed", response_model=ProfileOut)
def seed_default_profile(db: Session = Depends(get_db)):
    """Seed a default cybersecurity-focused profile for quick testing."""
    existing = db.query(Profile).first()
    if existing:
        return existing
    profile = Profile(
        full_name="Remigiusz Ungeheuer",
        email="your@email.com",
        location="Warsaw, Poland",
        target_titles="Security Analyst,Penetration Tester,SOC Analyst,Cybersecurity Engineer,Red Team",
        target_locations="Warsaw,Krakow,Poznan,Gdansk,remote",
        remote_ok=True,
        salary_min=8000,
        allowed_seniority="junior,mid,senior",
        skills="python,penetration testing,nmap,burpsuite,linux,networking,siem,splunk,wireshark,metasploit,owasp,kali",
        languages="Polish,English",
        work_authorization="EU citizen",
        willing_to_relocate=False,
        stock_answers={
            "Are you authorized to work in Poland?": "Yes",
            "Do you require visa sponsorship?": "No",
            "Are you willing to work remotely?": "Yes",
        },
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
