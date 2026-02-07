# BWC Jobs: DB-backed persistence

This document describes the lightweight SQLite-backed job persistence added for the Body-Worn Camera (BWC) near-real-time batch pipeline.

Design summary
- Jobs are stored in a small SQLite database `instance/bwc_jobs.db` using SQLAlchemy ORM.
- The model is `JobModel` (defined in `backend/src/bwc_jobs.py`) with fields:
  - `job_id` (string, unique) — public job identifier
  - `case_id`, `user_id` — routing/context
  - `upload_ids`, `video_paths`, `options`, `artifacts`, `log` — JSON-serialized text fields
  - `status`, `progress`, `created_at`, `updated_at`

Migration / operational notes
- No external migration framework is required. The table is created automatically on first use via `Base.metadata.create_all(ENGINE)`.
- For production, run a maintenance step to back up `instance/bwc_jobs.db` before switching persistence implementations.
- To migrate existing filesystem job files (if present):

```py
import json
from pathlib import Path
from backend.src.bwc_jobs import enqueue_batch

JOBS_DIR = Path('instance/jobs')
for p in JOBS_DIR.glob('*.json'):
    state = json.loads(p.read_text())
    enqueue_batch(
        case_id=state.get('case_id'),
        user_id=state.get('user_id'),
        upload_ids=state.get('upload_ids', []),
        video_paths=state.get('video_paths', []),
        options=state.get('options', {}),
    )

```

API compatibility
- The module preserves the public functions: `enqueue_batch`, `get_job_status`, `run_job`.
- `get_job_status` returns a dictionary compatible with the previous filesystem-backed state.

Notes
- The SQLAlchemy usage here is intentionally minimal to avoid introducing large new dependencies or complexity. If you prefer a managed migration with Alembic, add a standard Alembic migration script.
