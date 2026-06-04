from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    profile_id: int
    cv_id: Optional[int] = None
    status: str
    ats_type: Optional[str] = None
    external_application_id: Optional[str] = None
    match_score: Optional[float] = None
    score_breakdown: Optional[dict] = None
    screening_answers: Optional[dict] = None
    error_message: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
