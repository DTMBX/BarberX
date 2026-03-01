# Local Development — Evident BWC Discovery Suite

## Prerequisites

| Tool                    | Version         |
| ----------------------- | --------------- |
| Docker + Docker Compose | v2+             |
| Node.js                 | 20+ (frontend)  |
| Python                  | 3.12+ (backend) |
| Git                     | 2.40+           |

## Quick Start

```bash
# 1. Clone and enter project
cd bwc

# 2. Copy env template (review & edit before running)
cp .env.example .env

# 3. Start all services
docker compose -f ops/docker/docker-compose.yml up -d

# 4. Run database migrations
docker compose -f ops/docker/docker-compose.yml exec backend \
  alembic upgrade head

# 5. Open the app
#    Frontend:  http://localhost:3000
#    Backend:   http://localhost:8000
#    MinIO:     http://localhost:9001  (minioadmin / minioadmin)
```

## Dev Container (VS Code / Codespaces)

If using the devcontainer, the override file maps services to `localhost`:

```bash
docker compose -f ops/docker/docker-compose.yml \
               -f ops/docker/docker-compose.override.yml up -d
```

The override uses `network_mode: host` so all ports bind directly.

## Endpoints

| Service        | URL                            | Credentials             |
| -------------- | ------------------------------ | ----------------------- |
| Backend health | `http://localhost:8000/health` | —                       |
| Frontend       | `http://localhost:3000`        | —                       |
| MinIO console  | `http://localhost:9001`        | minioadmin / minioadmin |
| PostgreSQL     | `localhost:5432`               | evident / evident       |
| Redis          | `localhost:6379`               | —                       |

## Architecture

```
bwc/
├── backend/          FastAPI + SQLAlchemy + Celery
│   ├── app/
│   │   ├── api/      Routes, schemas
│   │   ├── core/     Config, security, audit
│   │   ├── models/   SQLAlchemy ORM models
│   │   ├── services/ CourtListener, LLM, OCR, Transcription
│   │   └── workers/  Celery tasks
│   └── alembic/      Database migrations
├── frontend/         Next.js 14 + React 18 + TanStack Query
│   ├── app/          Pages (app router)
│   ├── components/   Reusable UI components
│   └── lib/          API client, utilities
├── ops/docker/       Docker Compose configs
├── scripts/          Smoke tests, utilities
└── docs/             Architecture & dev docs
```

## Environment Variables

See `.env.example` for the full list. Critical variables:

| Variable                          | Purpose                             | Required                |
| --------------------------------- | ----------------------------------- | ----------------------- |
| `DATABASE_URL`                    | PostgreSQL connection string        | Yes                     |
| `REDIS_URL`                       | Redis for Celery broker             | Yes                     |
| `S3_ENDPOINT_URL`                 | MinIO / S3-compatible storage       | Yes                     |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Storage credentials                 | Yes                     |
| `MANIFEST_HMAC_KEY`               | HMAC key for manifest signing       | Yes (production)        |
| `COURTLISTENER_API_TOKEN`         | CourtListener API access            | Optional                |
| `LLM_PROVIDER`                    | `openai` / `anthropic` / `disabled` | Yes (default: disabled) |
| `EVIDENT_SAFE_MODE`               | Block destructive operations        | Recommended: true       |

## Running Migrations

```bash
# Inside the backend container:
alembic upgrade head

# Create a new migration after model changes:
alembic revision --autogenerate -m "describe_change"
```

Migration chain: `0001_initial` → `0002_forensic_hardening` →
`0003_extended_models`

## Running Tests

```bash
# Backend (from bwc/backend/)
pytest -xvs

# Frontend (from bwc/frontend/)
npm test

# Smoke test (health + basic endpoints)
bash scripts/smoke.sh
```

## Key API Endpoints

| Method   | Path                                      | Purpose                   |
| -------- | ----------------------------------------- | ------------------------- |
| GET      | `/health`                                 | Health check              |
| GET/POST | `/api/v1/projects`                        | Project CRUD              |
| GET/POST | `/api/v1/cases`                           | Case CRUD                 |
| POST     | `/api/v1/evidence/init-upload`            | Start presigned upload    |
| POST     | `/api/v1/evidence/{id}/complete`          | Verify + finalize upload  |
| GET      | `/api/v1/evidence?case_id=`               | List evidence for case    |
| POST     | `/api/v1/jobs/enqueue`                    | Start processing pipeline |
| GET      | `/api/v1/timeline/{case_id}`              | Audit timeline            |
| GET      | `/api/v1/manifest/{case_id}/export`       | Export signed manifest    |
| POST     | `/api/v1/manifest/verify`                 | Verify manifest integrity |
| POST     | `/api/v1/manifest/{case_id}/audit-replay` | Full audit replay         |
| POST     | `/api/v1/chat/ask`                        | Chat with AI assistant    |
| GET      | `/api/v1/artifacts`                       | List artifacts            |
| GET/POST | `/api/v1/issues`                          | Issue/violation CRUD      |
| GET      | `/api/v1/legal/search`                    | CourtListener search      |

## Forensic Invariants

These MUST be preserved in all changes:

1. **SHA-256 server-side verification** — Every uploaded file is hashed
   server-side. Client hash is informational only.
2. **HMAC-SHA256 manifest signing** — Manifests are signed with the HMAC key.
   Never expose the key client-side.
3. **Audit log dual-write** — Every mutation writes to both the database
   timeline and `audit_log.jsonl`.
4. **WORM storage** — MinIO bucket policy denies `s3:DeleteObject`. Evidence
   files are immutable.
5. **Partial unique index** — `uq_evidence_case_sha256` prevents duplicate
   uploads per case.
6. **No invented citations** — LLM responses must cite real sources.
   CourtListener results come from the Free Law Project API.

## RAG Context Pack

Rebuild after any file changes:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File bwc\Update-RagContext.ps1
```

## Troubleshooting

```bash
# Check service health
curl http://localhost:8000/health | jq

# View backend logs
docker compose -f ops/docker/docker-compose.yml logs backend -f

# View worker logs
docker compose -f ops/docker/docker-compose.yml logs worker -f

# Reset database
docker compose -f ops/docker/docker-compose.yml exec postgres \
  psql -U evident -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose -f ops/docker/docker-compose.yml exec backend alembic upgrade head
```
