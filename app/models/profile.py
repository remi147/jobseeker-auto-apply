from sqlalchemy import String, Integer, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Job preferences
    target_titles: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    target_locations: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    remote_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_seniority: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated

    # Skills
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    languages: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Legal
    work_authorization: Mapped[str | None] = mapped_column(String(100), nullable=True)
    willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False)

    # Extra answers stored as JSON {question: answer}
    stock_answers: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
