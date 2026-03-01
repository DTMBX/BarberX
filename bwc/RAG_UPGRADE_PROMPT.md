# RAG Upgrade Prompt — Evident Discovery Suite (Grounded)

You are upgrading an existing codebase into a defensible "discovery + evidence" suite.
You MUST rely on retrieved context from this repository. Do not hallucinate files or structure.

## Retrieval Anchors (use these as primary sources)
- Context tree: **bwc/rag_context/repo_tree.txt**
- File index (paths + sha256): **bwc/rag_context/file_index.json**
- Captured configs (if present): **bwc/rag_context/excerpts/**

## Operating Rules
1) Read what exists first. Assume nothing.
2) Prefer non-breaking, incremental changes: add missing wiring, do not remove working paths without justification.
3) Never overwrite originals: originals immutable keyed by SHA-256.
4) Every derivative references original hash and has its own hash.
5) Audit log append-only.
6) Exports reproducible (ZIP + manifest + hashes + audit events).
7) Secrets never committed; use .env.example.

## Your Task (do in this order)
### Phase 0 — Inventory
- Using repo_tree + file_index, identify:
  - backend framework and entrypoint(s)
  - database layer and migration tooling
  - queue/worker tooling
  - object storage adapter
  - media pipeline hooks (ffmpeg/ffprobe)
  - frontend framework and API integration
  - current CI workflows

Output: a short report listing what exists and what is missing.

### Phase 1 — Wire the Suite Together (Minimal Viable Integrity)
Implement or fix (using existing patterns where available):
- Upload flow:
  - Initiate upload -> presigned URL -> complete upload
  - Server verifies SHA-256 and stores immutable original object under:
    originals/<sha256>/<original_name>
  - DB record: EvidenceFile (case_id, sha256, size, mime, original_name, stored_key, created_at_utc)
  - Append audit events: UPLOAD_INIT, UPLOAD_COMPLETE, HASH_VERIFIED
- Worker flow:
  - ffprobe metadata extraction
  - proxy generation + thumbnails + waveform
  - store derivative hashes + relationship to original sha256
  - append audit events for each transform
- Case/timeline:
  - Case CRUD
  - Evidence listing per case, timestamp-aware
- Export:
  - ZIP + manifest.json (hashes, sizes, relationships, tool versions)
  - audit_log.json (append-only list)
  - download endpoint

### Phase 2 — Fill Gaps + Harden
- Add validation for file sizes/types, safe filenames, streaming handling.
- Ensure pinned versions and lockfiles.
- CI: lint/typecheck/tests for backend and frontend.
- Docs: CHAIN_OF_CUSTODY.md and LOCAL_DEV.md updated to match actual flows.

## Output Format
1) Checklist of changed/added files (paths).
2) Exact diffs or full file contents for key files.
3) Commands to run locally (PowerShell + Ubuntu).
4) Verification plan (how to prove hashing, immutability, audit log, export integrity).

IMPORTANT: If a file isn't present in retrieval, you must say "Not found in repository context" and propose the smallest addition that fits the existing structure.