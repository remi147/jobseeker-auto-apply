from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.db import Base


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    cv_id: Mapped[int | None] = mapped_column(ForeignKey("cv_versions.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending_review")
    ats_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_application_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    screening_answers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    submit_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
