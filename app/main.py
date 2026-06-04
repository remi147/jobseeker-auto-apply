from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import init_db
from app.routers import jobs, profiles, review, applications, health, cv, pipeline
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="JobSeeker Auto Apply",
    description=(
        "Automated job matching, ATS integration, and review-first auto-apply. "
        "Supports Greenhouse and Lever out of the box. "
        "Set AUTO_APPLY=true to submit approved applications automatically."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
app.include_router(cv.router, prefix="/cv", tags=["cv"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
