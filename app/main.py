from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import init_db
from app.routers import jobs, profiles, review, applications, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="JobSeeker Auto Apply",
    description="Automated job matching, ATS integration, and review-first auto-apply",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
