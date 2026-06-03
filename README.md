# JobSeeker Auto Apply

AI-powered automated job application system built with **FastAPI + Python 3.11+**

> Ingest jobs from Greenhouse & Lever → Score & match against your profile → Review queue → Auto-submit

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/remi147/jobseeker-auto-apply.git
cd jobseeker-auto-apply

# 2. Configure
cp .env.example .env
# Edit .env with your credentials

# 3. Install
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 4. Run
uvicorn app.main:app --reload
```

Open: **http://127.0.0.1:8000/docs**

---

## Workflow

1. `POST /profiles/seed` - Create your cybersecurity profile
2. `POST /jobs/ingest` - Pull jobs from Greenhouse + Lever
3. `POST /jobs/match` - Score jobs against your profile
4. `GET /review/pending` - See matched jobs waiting for approval
5. `POST /review/{id}/approve` - Approve the ones you want
6. `POST /applications/{id}/submit` - Submit to ATS

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /profiles/ | Create profile |
| POST | /profiles/seed | Seed default cybersecurity profile |
| GET | /profiles/ | List profiles |
| POST | /jobs/ingest | Ingest jobs from all ATS |
| POST | /jobs/match | Match & score jobs |
| GET | /jobs/ | List all jobs |
| GET | /review/pending | Pending review queue |
| POST | /review/{id}/approve | Approve application |
| POST | /review/{id}/reject | Reject application |
| GET | /applications/ | List all applications |
| POST | /applications/{id}/submit | Submit approved application |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GREENHOUSE_BOARD_TOKEN` | Greenhouse board token |
| `GREENHOUSE_API_KEY` | Greenhouse API key |
| `LEVER_SITE` | Lever company site name |
| `LEVER_API_KEY` | Lever API key |
| `MIN_MATCH_SCORE` | Minimum match score 0-100 (default: 70) |
| `AUTO_APPLY` | Skip review queue - keep false! |

---

## Project Structure

```
app/
├── main.py              FastAPI entry point
├── core/                Config + Database
├── models/              SQLAlchemy ORM (Job, Profile, CV, Application, AuditLog)
├── schemas/             Pydantic schemas
├── routers/             API routes (jobs, profiles, review, applications)
├── services/            Business logic (matching, ingest)
├── connectors/          Greenhouse, Lever, Playwright fallback
cvs/                     Put your CV PDFs here
```

---

## License

MIT
