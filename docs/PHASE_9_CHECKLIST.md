# Phase 9 — Document Processing Engine

## Execution Checklist

Every item is binary: works / doesn't. Testable. Reproducible on a fresh machine.

**Scope freeze:** No Phase 10+ work until every item below is checked.

---

## Infrastructure Prerequisites

| # | Item | Verify Command | Pass Condition |
|---|------|----------------|----------------|
| P1 | FFmpeg on PATH | `ffmpeg -version` | Prints version string |
| P2 | FFprobe on PATH | `ffprobe -version` | Prints version string |
| P3 | Tesseract on PATH | `tesseract --version` | Prints `v5.x` |
| P4 | Redis running | `py -3.12 -c "import redis; r=redis.Redis(); print(r.ping())"` | Prints `True` |
| P5 | Celery importable | `py -3.12 -c "import celery; print(celery.__version__)"` | Prints version |
| P6 | pytesseract importable | `py -3.12 -c "import pytesseract; print('OK')"` | Prints `OK` |
| P7 | pdfplumber importable | `py -3.12 -c "import pdfplumber; print('OK')"` | Prints `OK` |
| P8 | python-docx importable | `py -3.12 -c "import docx; print('OK')"` | Prints `OK` |
| P9 | Pillow importable | `py -3.12 -c "from PIL import Image; print('OK')"` | Prints `OK` |

### Current Status (2026-02-10)

- [x] P1 — FFmpeg 8.0.1
- [x] P2 — FFprobe 8.0.1
- [x] P3 — Tesseract 5.4.0
- [x] P4 — Redis 5.0.14.1 (portable, C:\tools\redis\)
- [x] P5 — Celery 5.6.2
- [x] P6 — pytesseract OK
- [x] P7 — pdfplumber 0.11.8
- [x] P8 — python-docx OK
- [x] P9 — Pillow 12.0.0

### P4 Resolution Options

| Option | Effort | Notes |
|--------|--------|-------|
| A. Install Memurai (Redis for Windows) | `winget install Memurai.MemuraiDeveloper` | Free dev edition, Windows service |
| B. Docker Redis | `docker run -d -p 6379:6379 redis:7-alpine` | Requires Docker Desktop |
| C. WSL2 Redis | `wsl -- sudo apt install redis-server && wsl -- redis-server` | Requires WSL2 |
| D. Skip Redis/Celery for Phase 9 | Use synchronous processing | Defer queue to Phase 15 (deployment) |

**Decision required before proceeding.**

---

## Section A — PDF Text Extraction (Synchronous)

Existing models: `ContentExtractionIndex`, `OCRResult`
Existing service: `ContentIndexService`, `OCRService`
Existing processor: `MediaProcessor._process_pdf()`

| # | Item | Description | Verify |
|---|------|-------------|--------|
| A1 | Extract text from native PDF | pdfplumber → `full_text` | Run on any text PDF. Output is non-empty string. |
| A2 | OCR scanned PDF | pdfplumber → PIL → pytesseract per page | Run on `test_evidence.pdf`. Output contains "TOWNSHIP OF HAMILTON". |
| A3 | Page count extraction | pdfplumber page count → `ContentExtractionIndex.line_count` | Matches `pdfplumber.open().pages` length. |
| A4 | Word/char count | Count from extracted text | Non-zero integers stored in DB. |
| A5 | Store extraction in DB | `ContentIndexService.create_content_index()` | Row exists in `content_extraction_index` with correct `evidence_id`. |
| A6 | Processing task lifecycle | `ProcessingTaskService.create → update(completed)` | Task row status = `completed`, `processing_time_seconds > 0`. |
| A7 | Handle corrupt/empty PDF | Graceful error, task status = `failed` | No crash. Error message stored. |
| A8 | Script: `scripts/process_evidence.py` | CLI: `py -3.12 scripts/process_evidence.py --evidence-id <id>` | Runs end-to-end. Prints summary. Exit code 0. |

### Manual Proof (done 2026-02-10)

```
OCR page 1 of test_evidence.pdf: 699 chars
"TOWNSHIP OF HAMILTON POLICE DEPARTMENT 6101 THIRTEENTH STREET..."
```

---

## Section B — Video Metadata Extraction

Existing models: `ForensicVideoMetadata`
Existing service: `forensic_video_processor.py`

| # | Item | Description | Verify |
|---|------|-------------|--------|
| B1 | Extract video metadata via ffprobe | JSON: codec, resolution, fps, duration, bitrate | Run on `BWC_test.mp4`. All fields populated. |
| B2 | Generate thumbnail | ffmpeg single frame at t=10s | JPEG file > 0 bytes in derivatives folder. |
| B3 | Generate proxy video | ffmpeg transcode to 720p H.264 | MP4 file in derivatives, playable. |
| B4 | Store metadata in DB | `ForensicVideoMetadata` row | Row exists with correct `evidence_id`, resolution=1920x1080. |
| B5 | Store derivatives in evidence_store | `evidence_store/derivatives/<hash>/` | Thumbnail + proxy files exist under correct hash path. |
| B6 | Log processing in manifest | Append to evidence manifest JSON | Manifest `derivatives` array is non-empty. |
| B7 | Handle corrupt/missing video | Graceful error | No crash. Error in task record. |
| B8 | Script: extend `scripts/process_evidence.py` | Auto-detect video type, run B1-B6 | Exit code 0. Prints metadata summary. |

### Manual Proof (done 2026-02-10)

```
ffprobe BWC_test.mp4: H.264 1920x1080 30fps 134s 10Mbps
ffmpeg thumbnail: 384KB JPEG extracted at t=10s
```

---

## Section C — Document Type Handling

| # | Item | Description | Verify |
|---|------|-------------|--------|
| C1 | DOCX text extraction | python-docx → paragraphs → full_text | Non-empty text from any .docx file. |
| C2 | Image OCR | PIL + pytesseract on JPEG/PNG/TIFF | Non-empty text from image containing text. |
| C3 | Plain text passthrough | Read file → store as-is | Exact content match. |
| C4 | MIME type detection | `mimetypes` + magic bytes check | Correct type for PDF, DOCX, JPEG, MP4, TXT. |
| C5 | Unsupported file type | Graceful skip with reason | Task status = `skipped`, message explains why. |

---

## Section D — Content Indexing & Search

Existing model: `ContentExtractionIndex` (has `full_text` column)
Existing service: `ContentIndexService.search_content()`

| # | Item | Description | Verify |
|---|------|-------------|--------|
| D1 | Full-text stored in ContentExtractionIndex | After A1/A2/C1, `full_text` column populated | `SELECT full_text FROM content_extraction_index WHERE evidence_id = ?` returns text. |
| D2 | Keyword search works | `ContentIndexService.search_content(case_id, "HAMILTON")` | Returns the evidence item containing that word. |
| D3 | Search returns nothing for absent term | Search for `"XYZNONEXISTENT"` | Empty result list. |
| D4 | Entity extraction (basic) | Regex: emails, phone numbers from text | `email_addresses` or `phone_numbers` field populated for `test_evidence.pdf`. |
| D5 | Route: `GET /api/v1/search?q=<term>` | Bearer-token-gated search endpoint | Returns JSON with matching evidence IDs + snippets. |

---

## Section E — Processing Route & UI

| # | Item | Description | Verify |
|---|------|-------------|--------|
| E1 | Route: `POST /api/v1/evidence/<id>/process` | Trigger processing for an evidence item | Returns 202 with task_id. |
| E2 | Route: `GET /api/v1/evidence/<id>/text` | Return extracted text for evidence | Returns JSON with `full_text`, `word_count`, `page_count`. |
| E3 | Route: `GET /api/v1/tasks/<id>` | Poll processing task status | Returns JSON with `status`, `progress`, `error_message`. |
| E4 | Route: `POST /api/v1/cases/<id>/process-all` | Batch-process all evidence in a case | Returns 202 with batch_id. |
| E5 | Route: `GET /api/v1/batches/<id>` | Poll batch processing status | Returns JSON with counts (total, completed, failed). |

---

## Section F — Celery Worker (conditional on P4)

| # | Item | Description | Verify |
|---|------|-------------|--------|
| F1 | Celery app config | `celery_app.py` with broker URL | `celery -A celery_app inspect ping` returns `pong`. |
| F2 | OCR task definition | `@celery_app.task` wrapping A1/A2 | Send task, poll result, text appears in DB. |
| F3 | Video task definition | `@celery_app.task` wrapping B1-B6 | Send task, poll result, metadata + derivatives appear. |
| F4 | Batch task definition | Fans out sub-tasks per evidence item | All items processed, batch status = completed. |
| F5 | Failure logging | Failed task → task status = `failed`, error stored | Kill FFmpeg mid-process, observe logged error. |
| F6 | Worker startup script | `scripts/start_worker.ps1` | Worker connects to Redis, processes queued task. |

**Section F is blocked by P4 (Redis).** If Redis is not available, Sections A-E
execute synchronously and F is deferred.

---

## Section G — Tests (written LAST)

Written only after A-E are manually verified and scripted.

| # | Test | Depends On |
|---|------|------------|
| G1 | `test_pdf_text_extraction` — native PDF → text | A1, A5 |
| G2 | `test_pdf_ocr_extraction` — scanned PDF → OCR text | A2, A5 |
| G3 | `test_video_metadata_extraction` — ffprobe → DB | B1, B4 |
| G4 | `test_thumbnail_generation` — ffmpeg → JPEG | B2, B5 |
| G5 | `test_content_search` — keyword → results | D2, D3 |
| G6 | `test_entity_extraction` — regex → emails/phones | D4 |
| G7 | `test_processing_task_lifecycle` — create → complete | A6 |
| G8 | `test_processing_task_failure` — corrupt file → failed | A7 |
| G9 | `test_api_process_evidence` — POST trigger → 202 | E1 |
| G10 | `test_api_get_text` — GET text → JSON | E2 |
| G11 | `test_api_search` — GET search → results | D5 |
| G12 | `test_unsupported_file_type` — skip with reason | C5 |

---

## Execution Order

```
1. Resolve P4 (Redis decision)
2. A1-A7  (PDF extraction — manual, then scripted)
3. B1-B7  (Video metadata — manual, then scripted)
4. A8+B8  (CLI script)
5. C1-C5  (Document types)
6. D1-D5  (Search indexing + route)
7. E1-E5  (API routes)
8. F1-F6  (Celery — if Redis available)
9. G1-G12 (Tests — last)
10. Regression (288 existing + new)
11. Version bump → 0.8.0
```

---

## Done Criteria

Phase 9 is complete when:

1. ~~`scripts/process_evidence.py --evidence-id <id>` produces text + metadata for
   any PDF or video in the evidence store~~ ✅
2. ~~`GET /api/v1/search?q=HAMILTON` returns the matching evidence item~~ ✅
3. ~~`GET /api/v1/evidence/<id>/text` returns extracted text~~ ✅
4. ~~All G-section tests pass~~ ✅ 52 tests passing
5. ~~Full regression (288 + new) green~~ ✅ 362 passed (310 existing + 52 new)
6. ~~Failures are observable: corrupt files produce logged errors, not crashes~~ ✅

### Phase 9 Complete — v0.8.0
