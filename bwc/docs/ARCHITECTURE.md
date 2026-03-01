# BWC Architecture

## Services & Ports

| Service  | Port | Protocol  | Description                      |
| -------- | ---- | --------- | -------------------------------- |
| postgres | 5432 | TCP       | PostgreSQL 16 — metadata store   |
| redis    | 6379 | TCP       | Redis 7 — Celery broker/result   |
| minio    | 9000 | HTTP/S3   | MinIO — object storage           |
| minio-ui | 9001 | HTTP      | MinIO console                    |
| backend  | 8000 | HTTP/REST | FastAPI app + Alembic migrations |
| worker   | —    | —         | Celery worker (same codebase)    |
| frontend | 3000 | HTTP      | Next.js 14 app                   |

## Environment Variables

### Backend (Settings)

```
APP_ENV, LOG_LEVEL, DATABASE_URL, REDIS_URL,
S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET, S3_REGION,
AUDIT_LOG_PATH, EVIDENCE_ORIGINALS_PREFIX,
MANIFEST_HMAC_KEY, S3_IMMUTABLE_POLICY, BWC_SUITE_ROOT,
COURTLISTENER_BASE_URL, COURTLISTENER_API_TOKEN,
LLM_PROVIDER (openai|anthropic|local|disabled),
OPENAI_API_KEY, ANTHROPIC_API_KEY,
EVIDENT_SAFE_MODE (0|1)
```

### Frontend

```
NEXT_PUBLIC_API_URL — backend base URL (default http://localhost:8000)
```

## Data Flow

```
                          ┌──────────┐
                          │ Frontend │
                          │ (Next.js)│
                          └────┬─────┘
                               │ REST
          ┌────────────────────▼──────────────────────┐
          │               Backend (FastAPI)            │
          │  routes → services → models → DB           │
          │  presigned URLs → MinIO                    │
          └───┬──────┬──────┬──────┬──────────────────┘
              │      │      │      │
         ┌────▼─┐ ┌──▼──┐ ┌▼────┐ ├──→ CourtListener API
         │Postgres│ │MinIO│ │Redis│ │
         │ meta  │ │files│ │queue│ │
         └───────┘ └─────┘ └──┬──┘ │
                               │    │
                          ┌────▼────▼─┐
                          │  Worker   │
                          │ (Celery)  │
                          │ OCR/Trans │
                          └───────────┘
```

### Upload Flow

1. Frontend computes local SHA-256
2. POST /evidence/init → returns presigned PUT URL + evidence_id
3. Frontend PUTs file directly to MinIO
4. POST /evidence/complete → backend downloads, re-hashes, checks dup
5. Job queued for OCR/transcription/metadata

### Manifest Export

1. GET /cases/{id}/export/manifest → canonical JSON + SHA-256 + HMAC
2. POST /verify/manifest → independent HMAC + hash check
3. GET /verify/cases/{id}/audit-replay → re-downloads from MinIO, re-hashes

## Forensic Invariants (MUST NEVER BREAK)

1. **SHA-256 integrity**: Every finalized evidence_file has sha256 computed from
   MinIO bytes
2. **HMAC signing**: Manifest exports use HMAC-SHA256 with server key
3. **Duplicate prevention**: unique(case_id, sha256) constraint (partial where
   sha256 IS NOT NULL)
4. **Audit dual-write**: Every sensitive action → audit_events DB +
   rag_context/audit_log.jsonl
5. **Immutable storage**: WORM-like deny-delete S3 policy when
   S3_IMMUTABLE_POLICY=true
6. **Audit replay**: Verifies every evidence file's hash from MinIO + monotonic
   timestamp ordering
7. **Integrity scripts**: Update-RagContext.ps1, Verify-Integrity.ps1,
   Test-RagContext.ps1 untouched

## Database Models

- **Project**: top-level grouping (NEW)
- **Case**: investigation case, belongs to a project
- **EvidenceFile**: uploaded file record
- **EvidenceArtifact**: derived outputs (transcript, OCR, metadata) (NEW)
- **Job**: background processing tracker
- **AuditEvent**: append-only forensic log
- **ChatMessage**: chat history with citations (NEW)
- **CourtListenerCache**: search result cache (NEW)

## API Endpoints

### Existing (preserved)

- POST /cases — create case
- POST /evidence/init — start upload
- POST /evidence/complete — finalize upload
- GET /cases/{id}/export/manifest — HMAC-signed manifest
- POST /verify/manifest — independent verification
- GET /verify/cases/{id}/audit-replay — full chain-of-custody replay
- GET /health — system health

### New

- GET /cases — list cases
- GET /cases/{id} — get case
- POST /projects — create project
- GET /projects — list projects
- POST /evidence/batch/init — batch presigned URLs
- POST /jobs/enqueue — enqueue OCR/transcribe/metadata
- GET /jobs?case_id=X — job status feed
- GET /cases/{id}/timeline — derived timeline events
- GET /chat/context?scope=X — context pack
- POST /chat/ask — grounded Q&A
- GET /chat/history?scope=X — chat history

## Frontend Routes

| Path                       | Component      | Description             |
| -------------------------- | -------------- | ----------------------- |
| /                          | Dashboard      | Health + quick actions  |
| /projects                  | ProjectList    | Project management      |
| /cases                     | CaseList       | Case browsing           |
| /cases/new                 | NewCase        | Create case form        |
| /cases/[id]                | CaseDetail     | Evidence + timeline     |
| /cases/[id]/evidence/[eid] | EvidenceViewer | PDF/video + artifacts   |
| /verify                    | VerifyPage     | Manifest + audit replay |
| /chat                      | ChatPage       | AI chat assistant       |
