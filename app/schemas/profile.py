from pydantic import BaseModel, EmailStr
from typing import Optional


class ProfileCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    target_titles: Optional[str] = None
    target_locations: Optional[str] = None
    remote_ok: bool = True
    salary_min: Optional[int] = None
    allowed_seniority: Optional[str] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    work_authorization: Optional[str] = None
    willing_to_relocate: bool = False
    stock_answers: Optional[dict] = None
    is_active: bool = True


class ProfileOut(ProfileCreate):
    id: int

    model_config = {"from_attributes": True}
