# JobSeeker Auto Apply

Automated job matching and ATS application engine built with **FastAPI + SQLAlchemy + APScheduler**.

## Architecture

```
Greenhouse API --\
                 +--> IngestService --> DB (jobs)
   Lever API ----/
                           |
                    MatchingService  (skills / title / location / seniority)
                           |
                    Applications  (pending_review -> approved -> submitted)
                           |
                    ApplyService  --> ATS connector.submit_application()
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env - add your Greenhouse / Lever tokens
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

## Typical Workflow

| Step | Endpoint | Description |
|------|----------|-----------|
| 1 | `POST /profiles/seed` | Create a default profile |
| 2 | `POST /jobs/ingest` | Pull live jobs from Greenhouse + Lever |
| 3 | `POST /jobs/match` | Score jobs, queue matches as `pending_review` |
| 4 | `GET /review/pending` | Review applications awaiting approval |
| 5 | `POST /review/{id}/approve` | Approve an application |
| 6 | `POST /applications/{id}/submit` | Submit to the ATS |

**Shortcuts:**
- `POST /jobs/ingest-and-match` — steps 2+3 in one call
- `POST /pipeline/run` — steps 2+3+6 in one call (with `AUTO_APPLY=true`)

Set `AUTO_APPLY=true` in `.env` for the scheduler to auto-submit every `INGEST_INTERVAL_MINUTES` minutes.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./jobseeker.db` | SQLAlchemy DB URL |
| `GREENHOUSE_BOARD_TOKEN` | `` | Greenhouse board slug |
| `GREENHOUSE_API_KEY` | `` | Greenhouse API key |
| `LEVER_SITE` | `` | Lever company slug |
| `LEVER_API_KEY` | `` | Lever API key |
| `MIN_MATCH_SCORE` | `70.0` | Min score (0-100) to queue a job |
| `AUTO_APPLY` | `false` | Auto-submit approved applications |
| `INGEST_INTERVAL_MINUTES` | `60` | Scheduler interval |
| `CV_UPLOAD_DIR` | `./uploads/cv` | CV file storage directory |

## Matching Algorithm

| Dimension | Weight | Logic |
|-----------|--------|-------|
| Skills overlap | 40% | `len(profile_skills & job_skills) / len(job_skills)` |
| Title match | 25% | Any target title substring in job title |
| Location / Remote | 20% | Remote preference or location substring match |
| Seniority | 15% | Allowed seniority list matches job seniority |

Blockers (e.g. salary below minimum) prevent queuing regardless of score.

## Project Structure

```
app/
  connectors/
    base.py            # ATSConnector abstract base class
    greenhouse.py      # Greenhouse API connector
    lever.py           # Lever API connector
  core/
    config.py          # Settings (pydantic-settings + .env)
    db.py              # SQLAlchemy engine + session factory
  models/
    job.py / profile.py / application.py / cv.py / audit_log.py
  routers/
    health.py          # GET /health
    profiles.py        # CRUD /profiles
    cv.py              # Upload/list/delete /cv
    jobs.py            # Ingest/match/list /jobs
    review.py          # Approve/reject /review
    applications.py    # Submit/list /applications
    pipeline.py        # POST /pipeline/run
  schemas/
    profile.py / job.py / application.py
  services/
    ingest_service.py  # Fetches jobs from connectors
    matching_service.py # Scores jobs against profile
    apply_service.py   # Full pipeline orchestrator
    scheduler.py       # APScheduler background task
  main.py              # FastAPI app + lifespan
```

## Adding a New ATS Connector

1. Create `app/connectors/myats.py` extending `ATSConnector`
2. Implement `can_handle()`, `fetch_jobs()`, `submit_application()`
3. Add an instance to `IngestService.__init__` and `ApplyService.__init__`

## License

MIT
