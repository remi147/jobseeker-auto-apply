"""Apply service - orchestrates the full pipeline: ingest -> match -> auto-submit.

When AUTO_APPLY=true in .env, approved applications are submitted automatically
after the ingest+match cycle. Otherwise they remain as 'pending_review'.
"""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.models.application import Application
from app.models.job import Job
from app.models.audit_log import AuditLog
from app.services.ingest_service import IngestService
from app.services.matching_service import MatchingService
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector

logger = logging.getLogger(__name__)


class ApplyService:
    """High-level orchestrator for the automated application pipeline."""

    def __init__(self, db: Session):
        self.db = db
        self.matcher = MatchingService()
        self._connectors = [GreenhouseConnector(), LeverConnector()]

    async def run_pipeline(self) -> dict:
        """Full pipeline: ingest -> match -> optionally auto-submit."""
        ingest_result = await IngestService(self.db).ingest_all()
        match_result = self._match_all()
        submit_result = {"submitted": 0, "errors": 0}

        if settings.auto_apply:
            submit_result = await self._auto_submit_approved()

        return {
            "ingest": ingest_result,
            "match": match_result,
            "submit": submit_result,
        }

    def _match_all(self) -> dict:
        from app.models.profile import Profile

        profile = self.db.query(Profile).filter(Profile.is_active == True).first()
        if not profile:
            return {"queued": 0, "scored": 0, "error": "No active profile"}

        jobs = self.db.query(Job).filter(Job.status == "new").all()
        queued = 0
        for job in jobs:
            result = self.matcher.score(profile, job)
            job.match_score = result.score
            if result.score >= settings.min_match_score and not result.blockers:
                job.status = "matched"
                exists = self.db.query(Application).filter(
                    Application.job_id == job.id,
                    Application.profile_id == profile.id,
                ).first()
                if not exists:
                    app = Application(
                        job_id=job.id,
                        profile_id=profile.id,
                        status="pending_review",
                        match_score=result.score,
                        score_breakdown=result.breakdown,
                        ats_type=job.ats_type,
                    )
                    self.db.add(app)
                    queued += 1
            else:
                job.status = "below_threshold"
        self.db.commit()
        return {"queued": queued, "scored": len(jobs)}

    async def _auto_submit_approved(self) -> dict:
        """Submit all applications that are in 'approved' state."""
        approved = self.db.query(Application).filter(
            Application.status == "approved"
        ).all()
        submitted = 0
        errors = 0
        for app_obj in approved:
            try:
                await self._submit_one(app_obj)
                submitted += 1
            except Exception as exc:
                logger.error("Failed to submit application %s: %s", app_obj.id, exc)
                app_obj.status = "error"
                app_obj.error_message = str(exc)
                errors += 1
        self.db.commit()
        return {"submitted": submitted, "errors": errors}

    async def _submit_one(self, app_obj: Application) -> None:
        job = self.db.query(Job).filter(Job.id == app_obj.job_id).first()
        if not job:
            raise ValueError(f"Job {app_obj.job_id} not found")

        dupe = self.db.query(Application).filter(
            Application.job_id == job.id,
            Application.profile_id == app_obj.profile_id,
            Application.status == "submitted",
            Application.id != app_obj.id,
        ).first()
        if dupe:
            app_obj.status = "duplicate"
            return

        connector = self._get_connector(job.ats_type, job.url)
        if connector is None:
            raise ValueError(f"No connector for ATS type '{job.ats_type}'")

        payload = {
            "external_id": job.external_id,
            "url": job.url,
            "form": app_obj.submit_payload or {},
            "files": {},
        }
        result = await connector.submit_application(payload)

        app_obj.status = "submitted"
        app_obj.submitted_at = datetime.utcnow()
        app_obj.external_application_id = str(result.get("id", ""))
        job.status = "applied"

        log = AuditLog(
            action="application_submitted",
            entity="Application",
            entity_id=app_obj.id,
            payload={"job_id": job.id, "ats_type": job.ats_type, "result": result},
        )
        self.db.add(log)

    def _get_connector(self, ats_type: str, url: str):
        for c in self._connectors:
            if c.can_handle(url):
                return c
        if ats_type == "greenhouse":
            return GreenhouseConnector()
        if ats_type == "lever":
            return LeverConnector()
        return None
