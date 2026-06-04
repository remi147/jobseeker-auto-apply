"""APScheduler-based background scheduler.

Runs the ingest+match+auto-submit pipeline every
`INGEST_INTERVAL_MINUTES` minutes (default 60).

Started/stopped from lifespan in main.py.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def _run_pipeline():
    """Async task: open a DB session and run the full apply pipeline."""
    from app.core.db import SessionLocal
    from app.services.apply_service import ApplyService

    db = SessionLocal()
    try:
        svc = ApplyService(db)
        result = await svc.run_pipeline()
        logger.info("Scheduled pipeline result: %s", result)
    except Exception as exc:
        logger.error("Scheduled pipeline error: %s", exc)
    finally:
        db.close()


def start_scheduler():
    scheduler = get_scheduler()
    if scheduler.running:
        return
    scheduler.add_job(
        _run_pipeline,
        trigger=IntervalTrigger(minutes=settings.ingest_interval_minutes),
        id="ingest_and_apply",
        replace_existing=True,
        misfire_grace_time=120,
    )
    scheduler.start()
    logger.info(
        "Scheduler started - pipeline every %s min (AUTO_APPLY=%s)",
        settings.ingest_interval_minutes,
        settings.auto_apply,
    )


def stop_scheduler():
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
