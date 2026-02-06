# Barber Cam - GPT Project Instructions

**Evident Legal Tech → Barber Cam Citizen Evidence Platform**

## Mission

Build trust, promote accountability, expand transparency through NJ citizen-led evidence documentation. Brand: "Barber Cam" (FaithFrontier Trust). Promise: "Record clean. Store safe. Share fair."

## Tech Stack

- **Backend:** Flask + PostgreSQL + Celery/Redis (NOT FastAPI - keep proven stack)
- **Frontend:** React/Vue.js timeline viewer
- **Mobile:** React Native/Flutter with offline capture
- **Storage:** SHA-256 immutable evidence storage
- **Analysis:** Whisper transcription + PyAnnote speaker diarization

## Current State

**✅ Working:** `bwc_forensic_analyzer.py` (920 lines), SHA-256 hashing, transcription, chain of custody, exports formatted for court submission, Stripe tiers, user auth, PostgreSQL, Flask web app

**❌ Missing:** Immutable storage layer, Celery workers, audit logs, mobile app, timeline viewer, attorney sharing, expiring links, PDF reports, drag-drop folder ingest, redaction tools

## NJ Legal Compliance (Critical)

- **One-party consent:** NJ allows recording conversations you participate in (N.J.S.A. 2A:156A-3)
- **Police in public:** First Amendment protects recording officers on duty in public (_Fields v. Philadelphia_, 3rd Cir. 2017)
- **Prohibited:** Recording to harass/intimidate, interfering with duties, private property without consent
- **UI Requirements:** Consent screens before first recording, persistent "Do not interfere" banner during recording, safety warnings on upload

## Integration Phases

### Phase 1: Evidence Integrity (Weeks 1-2)

**Goal:** Immutable storage + audit logs

- **DB:** `original_evidence` (sha256, file_size, acquired_at, storage_path), `derivative_evidence` (links to original), `evidence_access_log` (user_id, action, timestamp)
- **Storage:** `/evidence/originals/{hash[:2]}/{hash}.ext` (never overwrite)
- **Celery:** Background video analysis, queue notifications
- **Export:** ZIP with manifest.json (all hashes), chain-of-custody.pdf, transcript, analysis-report.json

### Phase 2: Mobile App (Weeks 3-5)

**Features:** One-tap record, offline queue sync, client-side encryption (libsodium), location metadata (optional), auto-hash before upload
**API:** `/api/v1/evidence/upload` (verify hash, store immutably), `/api/v1/cases/<id>/timeline` (thumbnails, bookmarks, status)

### Phase 3: Timeline Viewer (Weeks 6-7)

**Components:** Timeline track with evidence cards, video player with bookmarks panel, transcript sync, drag-drop folder ingest
**DB:** `case_bookmarks` (evidence_id, timestamp, note), `case_notes` (case_id, content)

### Phase 4: Attorney Sharing (Week 8)

**Features:** Expiring share links (72h default), read-only access, no login required, access logging
**DB:** `share_links` (case_id, token, expires_at, revoked), `share_link_access` (ip_address, accessed_at)
**Role:** Add `ATTORNEY` role (read-only case access, export packages, legal notes)

### Phase 5: Evidence Report PDF (Week 9)

**reportlab generator:** Title page, chain of custody table, evidence manifest (SHA-256 hashes), timeline summary, audit log excerpt, certification page

## File Structure

```
backend/
  app/
    api/ (evidence.py, cases.py, share.py)
    models/ (evidence.py, cases.py)
    services/ (evidence_storage.py, bwc_analyzer.py, report_generator.py)
    workers/ (tasks.py - Celery)
mobile/ (React Native/Flutter)
frontend/ (React timeline viewer)
docs/ (NJ-RECORDING-LAWS.md, EVIDENCE-INTEGRITY.md)
```

## Quick Wins (Next 48h)

1. ✅ Add safety banner to `templates/bwc-analyzer.html` (NJ legal warnings)
2. ✅ Create `docs/NJ-RECORDING-LAWS.md` (one-party consent, police recording rights, prohibited uses)
3. Create `docs/EVIDENCE-INTEGRITY.md` (SHA-256 explanation, immutable storage, audit logs)
4. Update homepage: "Record clean. Store safe. Share fair."

## Database Schemas (Key Tables)

```sql
- Immutable originals
CREATE TABLE original_evidence (
    id SERIAL PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    file_size BIGINT,
    acquired_at TIMESTAMP,
    storage_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

- Derivatives link to originals
CREATE TABLE derivative_evidence (
    id SERIAL PRIMARY KEY,
    sha256 TEXT UNIQUE,
    original_sha256 TEXT REFERENCES original_evidence(sha256),
    transformation JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

- Append-only audit log
CREATE TABLE evidence_access_log (
    id SERIAL PRIMARY KEY,
    evidence_sha256 TEXT,
    user_id INTEGER,
    action TEXT, - "view", "download", "export"
    accessed_at TIMESTAMP DEFAULT NOW()
);

- Attorney sharing
CREATE TABLE share_links (
    id SERIAL PRIMARY KEY,
    case_id INTEGER,
    token TEXT UNIQUE,
    expires_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);
```

## Python Service Pattern

```python
class ImmutableEvidenceStore:
    def store_original(self, file_bytes, metadata):
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        path = f"evidence/originals/{sha256[:2]}/{sha256}.ext"
        # Save file, create DB record, log custody event

    def create_derivative(self, original_sha256, transform, output):
        derivative_sha256 = hashlib.sha256(output).hexdigest()
        # Link to original, store transform params

    def audit_access(self, sha256, user_id, action):
        # Append to evidence_access_log
```

## Celery Tasks

```python
@app.task
def analyze_bwc_video(evidence_id):
    # Move bwc_forensic_analyzer logic here
    # Update DB with transcript, discrepancies
    # Notify user when complete
```

## Success Criteria

- Phase 1: 100% uploads SHA-256 tracked, zero overwrites, all admin access logged
- Phase 2: One-tap recording works offline, 95%+ consent completion, <30s upload
- Phase 3: Timeline loads <2s, bookmark support, export <10s
- Phase 4: Auto-expiring links, 100% attorney access logged
- Phase 5: PDF generates <5s, formatting for court submission

## Next Actions

**Week 1-2:** Implement immutable storage + Celery + audit logs + export reproducibility  
**Week 3-5:** Mobile app prototype (consent screens, offline recording, encrypted upload)  
**Week 6-7:** Timeline viewer (React, bookmarks, video player sync)  
**Week 8:** Attorney sharing (expiring tokens, read-only access)  
**Week 9:** Evidence Report PDF (reportlab, chain of custody, certification)

**Blockers:** None  
**Risk:** Low (incremental, no breaking changes)  
**Status:** ✅ Ready to implement

--

**Character Count:** ~5,800 (fits GPT 8000 limit)
