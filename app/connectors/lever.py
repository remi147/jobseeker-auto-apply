import httpx
from app.connectors.base import ATSConnector
from app.core.config import settings


class LeverConnector(ATSConnector):
    def __init__(self):
        self.site = settings.lever_site
        self.api_key = settings.lever_api_key
        self.base_url = f"https://api.lever.co/v0/postings/{self.site}"

    def can_handle(self, job_url: str) -> bool:
        return "lever.co" in job_url.lower()

    async def fetch_jobs(self, **kwargs) -> list[dict]:
        if not self.site:
            return []
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(self.base_url, params={"mode": "json"})
            r.raise_for_status()
            return [self._normalize(j) for j in r.json()]

    def _normalize(self, raw: dict) -> dict:
        cats = raw.get("categories", {})
        return {
            "title": raw.get("text", ""),
            "company": self.site,
            "url": raw.get("hostedUrl", ""),
            "ats_type": "lever",
            "external_id": raw.get("id", ""),
            "location": cats.get("location", ""),
            "remote": "remote" in str(cats.get("location", "")).lower(),
            "seniority": cats.get("commitment", ""),
            "description": raw.get("descriptionPlain", ""),
        }

    async def submit_application(self, payload: dict) -> dict:
        posting_id = payload["external_id"]
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"https://jobs.lever.co/{self.site}/{posting_id}/apply",
                data=payload.get("form", {}),
                files=payload.get("files", {}),
            )
            r.raise_for_status()
            return {"status": "submitted", "posting_id": posting_id}
