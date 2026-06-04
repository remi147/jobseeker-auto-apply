from abc import ABC, abstractmethod


class ATSConnector(ABC):
    """Abstract base class for ATS (Applicant Tracking System) connectors."""

    @abstractmethod
    def can_handle(self, job_url: str) -> bool:
        """Return True if this connector handles the given job URL."""
        ...

    @abstractmethod
    async def fetch_jobs(self, **kwargs) -> list[dict]:
        """Fetch available job postings and return normalised list of dicts."""
        ...

    @abstractmethod
    async def submit_application(self, payload: dict) -> dict:
        """Submit an application via the ATS API and return the response."""
        ...
