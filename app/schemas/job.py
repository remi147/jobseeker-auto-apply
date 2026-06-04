from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    url: str
    ats_type: str
    location: Optional[str] = None
    remote: bool
    seniority: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    skills_raw: Optional[str] = None
    status: str
    match_score: Optional[float] = None
    ingested_at: datetime

    model_config = {"from_attributes": True}
