from __future__ import annotations
from dataclasses import dataclass, field
from app.models.job import Job
from app.models.profile import Profile


@dataclass
class MatchResult:
    score: float
    breakdown: dict
    reasons: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


class MatchingService:
    def score(self, profile: Profile, job: Job) -> MatchResult:
        breakdown = {}
        reasons = []
        blockers = []

        # Skills overlap
        profile_skills = set(s.strip().lower() for s in (profile.skills or "").split(",") if s.strip())
        job_skills = set(s.strip().lower() for s in (job.skills_raw or "").split(",") if s.strip())
        if profile_skills and job_skills:
            overlap = len(profile_skills & job_skills) / len(job_skills)
        else:
            overlap = 0.5
        breakdown["skills"] = round(overlap, 2)
        if overlap >= 0.5:
            reasons.append(f"Matched {int(overlap*100)}% of required skills")

        # Title match
        target_titles = [t.strip().lower() for t in (profile.target_titles or "").split(",") if t.strip()]
        job_title = job.title.lower()
        title_score = 1.0 if any(t in job_title for t in target_titles) else 0.3
        breakdown["title"] = title_score
        if title_score == 1.0:
            reasons.append("Job title matches target roles")

        # Location
        if job.remote and profile.remote_ok:
            location_score = 1.0
            reasons.append("Remote position - matches preference")
        else:
            target_locs = [l.strip().lower() for l in (profile.target_locations or "").split(",") if l.strip()]
            job_loc = (job.location or "").lower()
            location_score = 1.0 if any(l in job_loc for l in target_locs) else 0.3

        breakdown["location"] = location_score

        # Seniority
        allowed = [s.strip().lower() for s in (profile.allowed_seniority or "").split(",") if s.strip()]
        job_seniority = (job.seniority or "").lower()
        seniority_score = 1.0 if not allowed or any(s in job_seniority for s in allowed) else 0.4
        breakdown["seniority"] = seniority_score

        # Salary check
        if profile.salary_min and job.salary_max and job.salary_max < profile.salary_min:
            blockers.append(f"Salary max {job.salary_max} below your minimum {profile.salary_min}")

        total = (
            0.40 * breakdown["skills"]
            + 0.25 * breakdown["title"]
            + 0.20 * breakdown["location"]
            + 0.15 * breakdown["seniority"]
        )

        return MatchResult(
            score=round(total * 100, 2),
            breakdown=breakdown,
            reasons=reasons,
            blockers=blockers,
        )
