# Barber Cam / BWC Platform Integration Roadmap

**Evident Legal Technologies → Barber Cam Evidence Platform**

**Date:** January 28, 2026  
**Mission:** Build trust, promote accountability, expand transparency through
citizen-led evidence documentation

--

## Current State Analysis

### ✅ Already Implemented (Strong Foundation)

**Evidence Processing Core:**

- ✓ `bwc_forensic_analyzer.py` - Full BWC video analysis with chain of custody
- ✓ SHA-256 hashing and integrity verification
- ✓ Audio transcription (Whisper integration)
- ✓ Speaker diarization (officer vs civilian)
- ✓ Metadata extraction (ffmpeg/ffprobe)
- ✓ Timeline synchronization
- ✓ Discrepancy detection
- ✓ Exports formatted for court submission (attorney review required)

**Infrastructure:**

- ✓ Flask web framework (established, well-tested)
- ✓ PostgreSQL database support
- ✓ User authentication & authorization
- ✓ Stripe payment integration (tiers: FREE, STARTER, PRO, ENTERPRISE)
- ✓ Upload management with size limits
- ✓ Watermarking service for free tier
- ✓ CORS configuration for cross-platform

**Branding Elements:**

- ✓ "Barber Cam" trademark established (LICENSE, FAQ)
- ✓ Faith Frontier Trust governance framework
- ✓ Privacy-first messaging
- ✓ Anti-confrontation policy documented

### ⚠️ Gaps vs. BWC Project Specification

**Architecture Alignment:**

- ❌ Uses Flask instead of FastAPI (but Flask is proven, works well)
- ❌ No Celery/Redis background workers (analysis runs synchronously)
- ❌ No S3-compatible object storage (uses local disk)
- ❌ Missing immutable storage layer (originals can be overwritten)
- ❌ No append-only audit log for access tracking

**Evidence Integrity:**

- ⚠️ Hashing exists but not enforced as immutable reference
- ⚠️ No derivative-to-original hash linking
- ⚠️ Admin access not logged (silent viewing possible)
- ⚠️ Export reproducibility not guaranteed

**User-Facing Features:**

- ❌ No drag-drop folder ingest
- ❌ No timeline viewer with markers/bookmarks
- ❌ No multi-camera alignment
- ❌ No attorney-specific sharing role
- ❌ No expiring share links
- ❌ No Evidence Report PDF generation
- ❌ No redaction tools (blur/mute)

**NJ Legal Compliance:**

- ⚠️ No "when to record" education pages
- ⚠️ No persistent "do not interfere" reminders
- ⚠️ No consent prompts for audio recording
- ⚠️ No user attestations against illegal recordings

**Mobile/Desktop:**

- ❌ No mobile app (capture side)
- ❌ No desktop app
- ❌ No offline-safe capture mode
- ❌ No one-tap recording interface

--

## Recommended Integration Strategy

### Phase 1: Core Evidence Integrity (1-2 weeks)

**Goal:** Make Evident backend truly evidence-grade

#### 1.1 Immutable Storage Layer

```python
# New: evidence_storage.py
class ImmutableEvidenceStore:
    """
    Ensures originals are never overwritten.
    All files stored with SHA-256 as filename.
    Audit log tracks every access.
    """
    def store_original(self, file_bytes, metadata):
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        # Store as: evidence/originals/{sha256[:2]}/{sha256}.ext
        # Create OriginalEvidence record in DB
        # Log ChainOfCustodyEvent

    def create_derivative(self, original_sha256, transform, output_bytes):
        derivative_sha256 = hashlib.sha256(output_bytes).hexdigest()
        # Store as: evidence/derivatives/{derivative_sha256}.ext
        # Create DerivativeEvidence record linking to original
        # Log transformation parameters

    def audit_access(self, sha256, user_id, action):
        # Append-only log: who accessed what, when, for what purpose
```

**Database Schema Updates:**

```sql
CREATE TABLE original_evidence (
    id SERIAL PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT,
    acquired_at TIMESTAMP NOT NULL,
    acquired_by TEXT NOT NULL,
    source TEXT NOT NULL, - "OPRA #123", "User upload"
    storage_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE derivative_evidence (
    id SERIAL PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    original_sha256 TEXT REFERENCES original_evidence(sha256),
    transformation JSON NOT NULL, - {"type": "proxy", "codec": "h264"}
    storage_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE evidence_access_log (
    id SERIAL PRIMARY KEY,
    evidence_sha256 TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL, - "view", "download", "export"
    ip_address TEXT,
    user_agent TEXT,
    accessed_at TIMESTAMP DEFAULT NOW()
);
```

#### 1.2 Celery Background Workers

```bash
# Install
pip install celery redis

# Create worker/tasks.py
from celery import Celery
app = Celery('Evident', broker='redis://localhost:6379/0')

@app.task
def analyze_bwc_video(evidence_id):
    # Move bwc_forensic_analyzer logic here
    # Update database with results
    # Send notification when complete
```

**Run worker:**

```bash
celery -A worker.tasks worker --loglevel=info
```

#### 1.3 Export Reproducibility

```python
# New: evidence_exporter.py
class EvidenceExportPackage:
    """
    Creates ZIP with:
    - Original file
    - manifest.json (all hashes, metadata)
    - chain-of-custody.pdf
    - transcript.txt
    - analysis-report.json
    """
    def generate(self, case_id):
        # Collect all evidence for case
        # Verify all hashes match stored values
        # Generate manifest with audit trail
        # Create PDF report (use reportlab)
        # Bundle into timestamped ZIP
```

--

### Phase 2: Barber Cam Mobile App (2-3 weeks)

**Tech Stack:** React Native or Flutter

#### 2.1 Core Features

- One-tap record (video + optional audio)
- Persistent "Keep distance / Do not interfere" banner
- Offline capture with queue sync
- Client-side encryption before upload (libsodium)
- Location metadata (optional, user-controlled)
- Evidence mode: auto-hash, auto-timestamp, auto-upload to Evident backend

#### 2.2 NJ Legal Compliance UI

```javascript
// Before first recording
<ConsentScreen>
  <Checkbox>
    I understand NJ one-party consent rules
  </Checkbox>
  <Checkbox>
    I will not record conversations I'm not part of
  </Checkbox>
  <Checkbox>
    I will not interfere with police duties
  </Checkbox>
  <Link to="/legal-guide">Read full NJ recording guide</Link>
</ConsentScreen>

// During recording
<RecordingOverlay>
  <Banner color="yellow">
    🚨 Do not interfere • Keep safe distance • Comply with lawful orders
  </Banner>
</RecordingOverlay>
```

#### 2.3 Backend API Endpoints

```python
# app.py additions
@app.route("/api/v1/evidence/upload", methods=["POST"])
@login_required
def upload_evidence():
    """
    Accepts encrypted evidence from mobile app.
    Verifies hash, stores immutably, queues analysis.
    """
    encrypted_file = request.files['evidence']
    metadata = json.loads(request.form['metadata'])

    # Decrypt (client sends key separately)
    # Verify SHA-256 matches client-computed hash
    # Store immutably
    # Queue Celery analysis task
    # Return evidence_id + upload confirmation

@app.route("/api/v1/cases/<case_id>/timeline", methods=["GET"])
@login_required
def get_case_timeline(case_id):
    """
    Returns all evidence for a case with:
    - Timestamps
    - Thumbnails
    - Bookmark markers
    - Analysis status
    """
```

--

### Phase 3: Timeline Viewer & Case Management (2 weeks)

**Frontend:** React or Vue.js

#### 3.1 Timeline Component

```javascript
<CaseTimeline>
  <TimelineHeader>
    <DateFilter />
    <AddBookmarkButton />
    <ExportButton />
  </TimelineHeader>

  <TimelineTrack>
    {evidence.map((item) => (
      <EvidenceCard
        thumbnail={item.thumbnail}
        duration={item.duration}
        markers={item.bookmarks}
        onClick={() => playVideo(item.id)}
      />
    ))}
  </TimelineTrack>

  <VideoPlayer>
    <BookmarksList />
    <TranscriptPanel />
  </VideoPlayer>
</CaseTimeline>
```

#### 3.2 Database Schema

```sql
CREATE TABLE case_bookmarks (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    evidence_id INTEGER REFERENCES original_evidence(id),
    timestamp FLOAT NOT NULL, - seconds into video
    note TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE case_notes (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    content TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

--

### Phase 4: Attorney Sharing & Collaboration (1 week)

#### 4.1 Secure Share Links

```python
# New: share_links.py
class ShareLink:
    """
    Expiring, revocable links for attorney access.
    No login required, but access is logged.
    """
    def create(self, case_id, expires_hours=72):
        token = secrets.token_urlsafe(32)
        # Store: share_links table with case_id, token, expires_at
        # Return: https://Evident.info/share/{token}

    def verify(self, token):
        # Check expiration
        # Log access
        # Return case data (read-only)
```

**Database:**

```sql
CREATE TABLE share_links (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    token TEXT UNIQUE NOT NULL,
    created_by INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE share_link_access (
    id SERIAL PRIMARY KEY,
    share_link_id INTEGER REFERENCES share_links(id),
    ip_address TEXT,
    user_agent TEXT,
    accessed_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.2 Attorney Role

```python
# Update: models_auth.py
class UserRole(enum.Enum):
    USER = "user"
    ATTORNEY = "attorney"  # New
    ADMIN = "admin"

# Attorney features:
# - Read-only case access (never edit originals)
# - Export packages
# - Add legal notes
# - Request additional evidence
```

--

### Phase 5: Evidence Report PDF (1 week)

```python
# New: report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class EvidenceReportGenerator:
    """
    Generates PDFs formatted for court submission with:
    - Case summary
    - Chain of custody table
    - Evidence manifest (all hashes)
    - Timeline summary
    - Audit log excerpt
    - Signature/certification page
    """
    def generate(self, case_id):
        pdf = canvas.Canvas(f"evidence_report_{case_id}.pdf", pagesize=letter)

        # Title page
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, f"Evidence Report - Case #{case_id}")

        # Chain of custody table
        # Evidence manifest with SHA-256 hashes
        # Timeline with bookmarks
        # Audit log summary
        # Certification statement

        pdf.save()
```

--

## File Structure Alignment

**Recommended Directory Layout:**

```
Evident.info/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   │   ├── auth.py
│   │   │   ├── evidence.py    # NEW
│   │   │   ├── cases.py       # NEW
│   │   │   ├── share.py       # NEW
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   ├── models/
│   │   │   ├── auth.py
│   │   │   ├── evidence.py    # NEW
│   │   │   ├── cases.py       # NEW
│   │   ├── services/
│   │   │   ├── evidence_storage.py  # NEW
│   │   │   ├── bwc_analyzer.py      # MOVE from root
│   │   │   ├── report_generator.py  # NEW
│   │   ├── workers/
│   │   │   ├── tasks.py       # NEW (Celery)
│   ├── app.py                 # Keep as main entry
│   ├── requirements.txt
├── mobile/                     # NEW (React Native / Flutter)
│   ├── src/
│   │   ├── screens/
│   │   │   ├── RecordScreen.js
│   │   │   ├── CaseListScreen.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── crypto.js
├── frontend/                   # NEW (React timeline viewer)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Timeline.jsx
│   │   │   ├── VideoPlayer.jsx
├── static/                     # Keep existing
├── templates/                  # Keep existing
├── docs/
│   ├── nj-legal-guide.md      # NEW
│   ├── safety-guidelines.md   # NEW
```

--

## Quick Wins (Next 48 Hours)

### 1. Add Evidence Integrity Page

**File:** `templates/evidence-integrity.html`

Show users:

- How SHA-256 hashing works (plain language)
- What "immutable storage" means
- Why audit logs matter
- How to verify file integrity

### 2. Create NJ Legal Guide

**File:** `docs/nj-recording-laws.md`

Content:

- One-party consent explanation
- When you can record police (public, official duties)
- When you CANNOT record (private property, conversations you're not in)
- Interfering with duties = separate crime
- Case law citations

### 3. Update Homepage Mission

**File:** `templates/index.html`

Replace "Evident Legal Technologies" messaging with:

> **"Record clean. Store safe. Share fair."**
>
> Barber Cam helps New Jersey residents lawfully document events, preserve
> evidence with verifiable integrity, and share it credibly with counsel—without
> confrontation.

### 4. Add Safety Banner to BWC Upload

**File:** `templates/bwc_upload.html`

```html
<div
  class="safety-banner"
  style="background: #fff3cd; padding: 1rem; margin-bottom: 1rem;"
>
  <h4>⚠️ Before You Upload</h4>
  <ul>
    <li>Only upload recordings you made lawfully</li>
    <li>Do not upload recordings made to harass or intimidate</li>
    <li>NJ law protects your right to record police in public</li>
    <li>Interfering with official duties is a separate offense</li>
  </ul>
  <a href="/legal-guide">Read full NJ recording guidelines →</a>
</div>
```

--

## Migration Strategy (Flask → FastAPI Discussion)

**Recommendation: Keep Flask**

**Why:**

- ✅ Flask is working, tested, deployed
- ✅ Team knows it well
- ✅ Async can be added with `async def` routes (Flask 2.0+)
- ✅ Migration risk is high for little gain

**If you must switch to FastAPI:**

1. Run both in parallel (Flask on :5000, FastAPI on :8000)
2. Migrate routes incrementally
3. Use shared database/models
4. Switch DNS when confidence high

**Verdict:** Focus on features, not framework swaps.

--

## Success Metrics

**Phase 1 (Evidence Integrity):**

- ✓ 100% of uploads tracked with SHA-256
- ✓ Zero original file overwrites
- ✓ All admin access logged

**Phase 2 (Mobile App):**

- ✓ One-tap recording works offline
- ✓ 95%+ of users complete consent flow
- ✓ Average upload time < 30 seconds

**Phase 3 (Timeline):**

- ✓ Users can bookmark 3+ moments per case
- ✓ Timeline loads < 2 seconds
- ✓ Export package generates < 10 seconds

**Phase 4 (Attorney Sharing):**

- ✓ Share links expire automatically
- ✓ 100% of attorney access logged
- ✓ Zero unauthorized case views

**Phase 5 (Reports):**

- ✓ PDF generates < 5 seconds
- ✓ Includes all required chain-of-custody elements
- ✓ Attorney feedback: "formatted for court submission"

--

## Next Steps (Action Plan)

### This Week:

1. ✅ Create this roadmap document
2. ⏳ Add safety banner to BWC upload page
3. ⏳ Write NJ legal guide (docs/nj-recording-laws.md)
4. ⏳ Update homepage mission statement
5. ⏳ Add evidence integrity explainer page

### Next Week:

1. Implement immutable storage layer
2. Set up Celery + Redis
3. Add evidence_access_log table
4. Test export reproducibility

### Month 1:

1. Complete Phase 1 (Evidence Integrity)
2. Start mobile app prototype
3. Design timeline viewer UI
4. Write attorney sharing spec

### Month 2:

1. Beta test mobile app (10 users)
2. Launch timeline viewer
3. Implement attorney roles
4. Generate first Evidence Report PDF

### Month 3:

1. Public beta (100 users)
2. Monitor for bugs/feedback
3. Launch FaithFrontier.org/barbercam landing page
4. Announce on social media

--

**Status:** Ready to implement ✅  
**Blocker:** None  
**Risk:** Low (incremental changes, no breaking migrations)  
**Confidence:** High (builds on proven codebase)
