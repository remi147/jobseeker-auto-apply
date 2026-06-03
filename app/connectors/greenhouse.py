import httpx
from app.connectors.base import ATSConnector
from app.core.config import settings


class GreenhouseConnector(ATSConnector):
    def __init__(self):
        self.board_token = settings.greenhouse_board_token
        self.api_key = settings.greenhouse_api_key
        self.base_url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}"

    def can_handle(self, job_url: str) -> bool:
        return "greenhouse" in job_url.lower()

    async def fetch_jobs(self, **kwargs) -> list[dict]:
        if not self.board_token:
            return []
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{self.base_url}/jobs?content=true")
            r.raise_for_status()
            jobs = r.json().get("jobs", [])
            return [self._normalize(j) for j in jobs]

    def _normalize(self, raw: dict) -> dict:
        loc = raw.get("location", {})
        return {
            "title": raw.get("title", ""),
            "company": self.board_token,
            "url": raw.get("absolute_url", ""),
            "ats_type": "greenhouse",
            "external_id": str(raw.get("id", "")),
            "location": loc.get("name") if isinstance(loc, dict) else str(loc),
            "remote": "remote" in str(loc).lower(),
            "description": raw.get("content", ""),
        }

    async def submit_application(self, payload: dict) -> dict:
        job_id = payload["external_id"]
        auth = (self.api_key, "") if self.api_key else None
        async with httpx.AsyncClient(timeout=60, auth=auth) as client:
            r = await client.post(
                f"{self.base_url}/jobs/{job_id}",
                data=payload.get("form", {}),
                files=payload.get("files", {}),
            )
            r.raise_for_status()
            return r.json() if r.content else {"status": "submitted"}
