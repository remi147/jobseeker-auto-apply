from sqlalchemy.orm import Session
from app.models.job import Job
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector


class IngestService:
    def __init__(self, db: Session):
        self.db = db
        self.connectors = [GreenhouseConnector(), LeverConnector()]

    async def ingest_all(self) -> dict:
        total_new = 0
        total_skipped = 0
        for connector in self.connectors:
            jobs = await connector.fetch_jobs()
            for job_data in jobs:
                url = job_data.get("url", "")
                if not url:
                    continue
                existing = self.db.query(Job).filter(Job.url == url).first()
                if existing:
                    total_skipped += 1
                    continue
                job = Job(
                    title=job_data.get("title", ""),
                    company=job_data.get("company", ""),
                    url=url,
                    ats_type=job_data.get("ats_type", "unknown"),
                    external_id=job_data.get("external_id"),
                    location=job_data.get("location"),
                    remote=job_data.get("remote", False),
                    seniority=job_data.get("seniority"),
                    description=job_data.get("description"),
                    status="new",
                )
                self.db.add(job)
                total_new += 1
        self.db.commit()
        return {"new": total_new, "skipped": total_skipped}
