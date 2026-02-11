# Evident Algorithms — Court-Defensible Evidence Processing

> **Version:** 1.0.0  
> **Last Updated:** 2025-07-11  
> **Classification:** Technical Reference — Not Legal Advice

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Architecture Overview](#architecture-overview)
3. [Algorithm Catalogue](#algorithm-catalogue)
   - [A — Bulk Deduplication](#a--bulk-deduplication)
   - [B — Provenance Graph](#b--provenance-graph)
   - [C — Timeline Alignment](#c--timeline-alignment)
   - [D — Integrity Sweep](#d--integrity-sweep)
   - [E — Bates Generator](#e--bates-generator)
   - [F — Redaction Verification](#f--redaction-verification)
   - [G — Access Anomaly Detector](#g--access-anomaly-detector)
4. [API Reference](#api-reference)
5. [CLI Reference](#cli-reference)
6. [Data Model](#data-model)
7. [Testing & Verification](#testing--verification)
8. [Forensic Defensibility Notes](#forensic-defensibility-notes)

---

## Design Principles

Every algorithm in this package is governed by the following non-negotiable
constraints:

| Principle | Implementation |
|---|---|
| **Immutability** | Originals are never modified. All outputs are new derivative records. |
| **Determinism** | Given identical inputs, every algorithm produces identical outputs. No randomness, no non-deterministic ordering. |
| **Provenance** | Every run records: input hashes, output hashes, parameter hash, result hash, algorithm version, actor identity, and wall-clock timing. |
| **Auditability** | Every run emits an append-only audit event via `AuditStream`. Events include the full `AlgorithmResult` envelope. |
| **Reproducibility** | Any result can be independently verified by re-running the same algorithm version against the same inputs with the same parameters. |
| **Explainability** | Algorithm logic uses standard, well-documented techniques. No opaque ML pipelines. |
| **Tenant Isolation** | All queries are scoped to `organization_id`. Cross-tenant data access is structurally impossible. |

These principles exist so that algorithm outputs are **admissible** in
evidentiary proceedings and withstand adversarial cross-examination.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                    Entry Points                        │
│  REST API (/api/v1/algorithms/*)                       │
│  CLI (evident algorithms run | audit integrity | ...)  │
│  Celery Tasks (async dispatch)                         │
└──────────────┬─────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│       AlgorithmRegistry          │
│  register() / get() / list()     │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│        AlgorithmBase.run()       │
│  1. Hash inputs                  │
│  2. Hash parameters              │
│  3. Execute _execute()           │
│  4. Hash outputs                 │
│  5. Build AlgorithmResult        │
│  6. Emit audit event             │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  AlgorithmResult (frozen)        │
│  - algorithm_id, version         │
│  - run_id (UUID)                 │
│  - input_hashes, output_hashes   │
│  - params_hash, result_hash      │
│  - payload (algorithm-specific)  │
│  - timing (start, end, elapsed)  │
│  - integrity_check (bool)        │
└──────────────────────────────────┘
```

### Key Files

| File | Purpose |
|---|---|
| `algorithms/base.py` | `AlgorithmBase`, `AlgorithmResult`, `AlgorithmParams`, `canonical_json()` |
| `algorithms/registry.py` | Singleton `AlgorithmRegistry`, `@registry.register()` decorator |
| `algorithms/manifest.py` | Hash verification, derivative record building, provenance linking |
| `algorithms/bulk_dedup.py` | Algorithm A |
| `algorithms/provenance_graph.py` | Algorithm B |
| `algorithms/timeline_alignment.py` | Algorithm C |
| `algorithms/integrity_sweep.py` | Algorithm D |
| `algorithms/bates_generator.py` | Algorithm E |
| `algorithms/redaction_verify.py` | Algorithm F |
| `algorithms/access_anomaly.py` | Algorithm G |
| `routes/algorithms_api.py` | REST API blueprint |
| `tasks/algorithm_tasks.py` | Celery task wrappers |
| `cli/evident.py` | Command-line interface |
| `models/algorithm_models.py` | SQLAlchemy models |

---

## Algorithm Catalogue

### A — Bulk Deduplication

**ID:** `bulk_dedup` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Identify exact and near-duplicate evidence items within a case to
reduce review volume and expose redundant material.

**Technique:**

- **Exact duplicates:** SHA-256 hash comparison. Items sharing the same hash are
  grouped.
- **Near duplicates (images):** Average-hash (aHash) perceptual hashing with
  configurable Hamming-distance threshold.

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `similarity_threshold` | float | 0.9 | Minimum similarity score (0.0–1.0) for near-duplicate grouping. |

**Output Payload:**

```json
{
  "exact_groups": [
    { "hash": "abc123...", "item_ids": ["ev-001", "ev-003"] }
  ],
  "near_groups": [
    {
      "anchor": "ev-002",
      "members": [
        { "item_id": "ev-005", "similarity": 0.94 }
      ]
    }
  ],
  "total_items": 100,
  "exact_duplicate_count": 12,
  "near_duplicate_count": 5
}
```

**Forensic Notes:**

- Exact dedup is based solely on cryptographic hash identity — no interpretation.
- Near-dedup similarity scores are explained (Hamming distance / 64 bits).
- Groupings do not delete or hide items — they annotate.

---

### B — Provenance Graph

**ID:** `provenance_graph` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Build a directed acyclic graph (DAG) tracing every evidence item
from ingestion through all derivatives and exports.

**Technique:**

- Walks evidence manifests and `ChainOfCustody` audit entries.
- Constructs nodes (type: `original`, `derivative`, `export`) and directed edges
  (type: `derived_from`, `exported_from`, `ingested`, `transformed`, `accessed`).
- Detects orphaned nodes (items with no provenance link).

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `include_access_events` | bool | `true` | Include access/view events as edges. |

**Output Payload:**

```json
{
  "nodes": [
    { "id": "ev-001", "type": "original", "label": "photo_001.jpg" }
  ],
  "edges": [
    { "source": "ev-001", "target": "ev-001-d1", "type": "derived_from" }
  ],
  "orphans": [],
  "stats": {
    "total_nodes": 42,
    "total_edges": 67,
    "originals": 20,
    "derivatives": 18,
    "exports": 4,
    "orphans": 0
  }
}
```

**Forensic Notes:**

- The graph is purely structural — it does not infer intent.
- Orphan detection surfaces items whose chain of custody may be incomplete.
- Suitable for inclusion in court packages as a provenance exhibit.

---

### C — Timeline Alignment

**ID:** `timeline_alignment` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Normalize timestamps across multiple devices and sources onto a
unified timeline, detecting clock drift between capture devices.

**Technique:**

- Parses multiple timestamp formats (ISO 8601, epoch seconds, epoch
  milliseconds, common date strings).
- Assigns confidence labels: `exact` (authoritative server-stamped), `derived`
  (computed from offset correction), `unknown` (unparseable or missing).
- Detects clock drift by computing median inter-device offsets from overlapping
  events.
- Records all assumptions explicitly in the result.

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `drift_threshold_seconds` | float | 5.0 | Minimum offset (seconds) to flag as clock drift. |

**Output Payload:**

```json
{
  "timeline": [
    {
      "item_id": "ev-001",
      "original_timestamp": "2024-01-15T09:30:00Z",
      "normalized_timestamp": "2024-01-15T09:30:00+00:00",
      "confidence": "exact",
      "device_id": "phone-A",
      "offset_applied_seconds": 0.0
    }
  ],
  "drift_pairs": [
    {
      "device_a": "phone-A",
      "device_b": "camera-B",
      "median_offset_seconds": 12.5
    }
  ],
  "assumptions": [
    "Items without timestamps assigned confidence='unknown'."
  ],
  "stats": {
    "total_items": 50,
    "exact": 30,
    "derived": 15,
    "unknown": 5
  }
}
```

**Forensic Notes:**

- No timestamp is fabricated. Missing timestamps are labeled `unknown`, not
  guessed.
- Drift detection is statistical (median offset), not assumed.
- All assumptions are explicitly declared and included in the audit record.

---

### D — Integrity Sweep

**ID:** `integrity_sweep` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Verify the cryptographic integrity of every evidence item in a case
by recomputing SHA-256 hashes and comparing against stored records.

**Technique:**

- For each evidence item, reads the file from the evidence store, computes
  SHA-256, and compares against the hash recorded at ingestion.
- Emits per-item audit events for traceability.
- Status values: `pass`, `fail`, `missing`, `error`.

**Parameters:** None (operates on full case).

**Output Payload:**

```json
{
  "results": [
    {
      "item_id": "ev-001",
      "status": "pass",
      "expected_hash": "abc123...",
      "actual_hash": "abc123..."
    }
  ],
  "summary": {
    "total": 100,
    "passed": 98,
    "failed": 1,
    "missing": 1,
    "errors": 0
  }
}
```

**Forensic Notes:**

- A single `fail` result indicates potential tampering or corruption and must be
  investigated.
- `missing` means the file was not found at its expected store path.
- Every verification event is individually audit-logged.

---

### E — Bates Generator

**ID:** `bates_generator` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Produce Bates-stamped derivative copies of evidence items for
court-ready exhibit numbering.

**Technique:**

- Generates sequential Bates numbers in the format `PREFIX-000001`.
- For PDF content: stamps the Bates number onto each page using ReportLab
  overlays merged via PyPDF2. Falls back to a text-marker prefix when libraries
  are unavailable or input is not valid PDF.
- Stores each derivative in the evidence store with its own SHA-256 hash.
- Records provenance linking each derivative to its original.

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `prefix` | string | `"EVD"` | Bates number prefix. |
| `start_number` | int | `1` | First Bates number in the sequence. |
| `position` | string | `"bottom_right"` | Stamp position on PDF pages. |
| `include_types` | list | all types | Filter evidence items by `file_type`. |

**Output Payload:**

```json
{
  "exhibits": [
    {
      "original_id": "ev-001",
      "bates_number": "EVD-000001",
      "derivative_hash": "def456...",
      "store_path": "derivatives/ev-001-bates-EVD-000001"
    }
  ],
  "range": { "first": "EVD-000001", "last": "EVD-000042" },
  "count": 42
}
```

**Forensic Notes:**

- Originals are never modified. Bates-stamped copies are new derivative records.
- Each derivative is independently hashed and linked to its source via
  provenance edge.
- The stamping method (PDF overlay or text marker) is recorded in the audit
  trail.

---

### F — Redaction Verification

**ID:** `redaction_verify` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Verify that redacted documents are properly sanitized — no hidden
text layers, no recoverable content beneath redaction annotations.

**Technique:**

- **Text-layer check:** Extracts text from PDF pages; flags pages where
  extractable text overlaps with redaction regions.
- **Annotation check:** Inspects PDF annotation objects for redaction-type
  annotations.
- **Byte-leakage check:** Scans raw PDF bytes for patterns suggesting residual
  content (e.g., embedded fonts referencing redacted terms).

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `check_text_layer` | bool | `true` | Run text-layer extraction check. |
| `check_annotations` | bool | `true` | Run annotation-based check. |
| `check_byte_leakage` | bool | `true` | Run raw byte-pattern check. |

**Output Payload:**

```json
{
  "items": [
    {
      "item_id": "ev-010",
      "checks": {
        "text_layer": { "status": "pass", "details": {} },
        "annotations": { "status": "warning", "details": { "redaction_annotations_found": 3 } },
        "byte_leakage": { "status": "pass", "details": {} }
      },
      "overall": "warning"
    }
  ],
  "summary": {
    "total": 5,
    "clean": 3,
    "warnings": 2,
    "failures": 0
  }
}
```

**Forensic Notes:**

- This algorithm does not perform redaction — it verifies existing redactions.
- A `warning` status requires human review. The system does not decide whether
  the redaction is adequate.
- Results are suitable for inclusion in a privilege-review log.

---

### G — Access Anomaly Detector

**ID:** `access_anomaly` &nbsp;|&nbsp; **Version:** 1.0.0

**Purpose:** Detect suspicious access patterns in audit logs — download bursts,
share-link abuse, authentication failures, and off-hours activity.

**Technique:**

- **Download bursts:** Identifies actors who downloaded more than a threshold
  number of items within a configurable time window.
- **Share-link abuse:** Flags items shared more than a threshold number of times.
- **Authentication failures:** Counts failed authentication attempts by actor.
- **Off-hours access:** Flags access events occurring outside configurable
  business hours (default 06:00–22:00 UTC).

**Parameters:**

| Key | Type | Default | Description |
|---|---|---|---|
| `burst_threshold` | int | `10` | Downloads within window → burst flag. |
| `burst_window_minutes` | int | `5` | Time window for burst detection. |
| `share_threshold` | int | `5` | Share events per item → abuse flag. |
| `business_hours_start` | int | `6` | UTC hour business hours begin. |
| `business_hours_end` | int | `22` | UTC hour business hours end. |

**Output Payload:**

```json
{
  "anomalies": [
    {
      "type": "download_burst",
      "severity": "warning",
      "actor": "user-42",
      "details": { "count": 15, "window_minutes": 5, "threshold": 10 },
      "timestamp": "2024-01-15T03:22:00Z"
    }
  ],
  "summary": {
    "total_anomalies": 4,
    "by_type": {
      "download_burst": 1,
      "share_link_abuse": 1,
      "auth_failure": 1,
      "off_hours_access": 1
    },
    "by_severity": {
      "info": 1,
      "warning": 2,
      "alert": 1
    }
  }
}
```

**Forensic Notes:**

- This algorithm detects patterns — it does **not** infer intent, guilt, or
  liability.
- Anomaly severity is descriptive, not prescriptive. All flagged events require
  human review.
- The detection thresholds are explicit and documented in every result.

---

## API Reference

All endpoints require Bearer-token authentication and are scoped to the
authenticated user's `organization_id`.

**Base path:** `/api/v1/algorithms/`

### List Algorithms

```
GET /api/v1/algorithms/
```

Returns all registered algorithms with their IDs, versions, and descriptions.

### Run Algorithm

```
POST /api/v1/algorithms/run
Content-Type: application/json

{
  "algorithm_id": "bulk_dedup",
  "case_id": "case-001",
  "params": {
    "similarity_threshold": 0.9
  }
}
```

Returns the full `AlgorithmResult` envelope.

### List Runs

```
GET /api/v1/algorithms/runs?case_id=case-001
```

Returns previous algorithm runs for a case.

### Get Run

```
GET /api/v1/algorithms/runs/<run_id>
```

Returns a specific run by its UUID.

### Integrity Sweep (Shortcut)

```
POST /api/v1/algorithms/integrity-sweep
Content-Type: application/json

{ "case_id": "case-001" }
```

### Timeline Alignment (Shortcut)

```
POST /api/v1/algorithms/timeline
Content-Type: application/json

{ "case_id": "case-001" }
```

### Court Package

```
POST /api/v1/algorithms/court-package
Content-Type: application/json

{ "case_id": "case-001" }
```

Runs integrity sweep, timeline alignment, provenance graph, and Bates stamping
in sequence. Returns a unified court package with manifest hash.

---

## CLI Reference

```bash
# List all available algorithms
evident algorithms list

# Run a specific algorithm
evident algorithms run bulk_dedup --case case-001

# Run an integrity sweep
evident audit integrity --case case-001

# Export a court package
evident export court-package --case case-001 --output ./court_pkg/
```

All CLI commands produce JSON output on stdout, suitable for piping to other
tools or archival.

---

## Data Model

### AlgorithmRun

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique run identifier. |
| `algorithm_id` | String | Algorithm identifier (e.g., `"bulk_dedup"`). |
| `algorithm_version` | String | Semantic version (e.g., `"1.0.0"`). |
| `case_id` | String | Case identifier. |
| `organization_id` | String | Tenant scope. |
| `actor_id` | String | User who initiated the run. |
| `params_hash` | String | SHA-256 of canonical parameters. |
| `result_hash` | String | SHA-256 of canonical result payload. |
| `input_hashes` | JSON | List of input content hashes. |
| `output_hashes` | JSON | List of output content hashes. |
| `status` | String | `"completed"` or `"failed"`. |
| `payload` | JSON | Full algorithm-specific output. |
| `started_at` | DateTime | Run start (UTC). |
| `completed_at` | DateTime | Run end (UTC). |
| `elapsed_seconds` | Float | Wall-clock duration. |

### ProvenanceEdge

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Edge identifier. |
| `source_id` | String | Source evidence item. |
| `target_id` | String | Target evidence item. |
| `edge_type` | String | `"derived_from"`, `"exported_from"`, etc. |
| `algorithm_run_id` | UUID (FK) | Run that produced this edge. |
| `case_id` | String | Case scope. |
| `organization_id` | String | Tenant scope. |
| `created_at` | DateTime | Creation timestamp (UTC). |

### VerificationReport

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Report identifier. |
| `algorithm_run_id` | UUID (FK) | Associated integrity sweep run. |
| `item_id` | String | Evidence item verified. |
| `expected_hash` | String | Hash at ingestion. |
| `actual_hash` | String | Hash at verification time. |
| `status` | String | `"pass"`, `"fail"`, `"missing"`, `"error"`. |
| `case_id` | String | Case scope. |
| `organization_id` | String | Tenant scope. |
| `verified_at` | DateTime | Verification timestamp (UTC). |

### RedactionReport

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Report identifier. |
| `algorithm_run_id` | UUID (FK) | Associated redaction-verify run. |
| `item_id` | String | Evidence item checked. |
| `text_layer_status` | String | Text-layer check result. |
| `annotation_status` | String | Annotation check result. |
| `byte_leakage_status` | String | Byte-leakage check result. |
| `overall_status` | String | Aggregate status. |
| `details` | JSON | Full check details. |
| `case_id` | String | Case scope. |
| `organization_id` | String | Tenant scope. |
| `checked_at` | DateTime | Check timestamp (UTC). |

Migration: `migrations/versions/0006_algorithm_tables.py` (revision `0006`,
down-revision `0005`).

---

## Testing & Verification

### Test Suites

| Suite | File | Tests | Coverage |
|---|---|---|---|
| Base framework | `tests/test_algorithm_base.py` | 17 | `AlgorithmBase`, `AlgorithmResult`, `AlgorithmParams`, `canonical_json`, `hash_json` |
| Registry | `tests/test_algorithm_registry.py` | 7 | Registration, versioning, listing, decorator |
| Manifest utilities | `tests/test_algorithm_manifest.py` | 10 | Hash verification, derivative records, provenance linking |
| Integration (all algorithms) | `tests/test_algorithms_integration.py` | 19 | All 7 algorithms, cross-cutting concerns |

**Total: 53 tests**

### Running Tests

```bash
# All algorithm tests
python -m pytest tests/test_algorithm_base.py tests/test_algorithm_registry.py \
  tests/test_algorithm_manifest.py tests/test_algorithms_integration.py -v

# With coverage
python -m pytest tests/test_algorithm_base.py tests/test_algorithm_registry.py \
  tests/test_algorithm_manifest.py tests/test_algorithms_integration.py \
  --cov=algorithms --cov-report=term-missing
```

### Golden Fixture

The test suite uses `tests/fixtures/golden_case.json`, which contains:

- 6 evidence items (photos, documents, video, including exact duplicates and a
  redacted document)
- 6 audit entries (ingestion, access, export, download burst)
- Known properties: predictable hashes, deliberate duplicates, missing
  timestamps, off-hours access patterns

### Cross-Cutting Verifications

The integration test suite verifies properties that apply to all algorithms:

1. **Immutability:** Original evidence data is never modified.
2. **Integrity check:** Every result includes `integrity_check = True`.
3. **Determinism:** Running the same algorithm twice on the same input produces
   identical `result_hash` values.

---

## Forensic Defensibility Notes

### Chain of Custody

Every algorithm run creates an unbroken chain from input to output:

```
Input Evidence → (hashed) → Algorithm Execution → (hashed) → Output
                                   ↓
                            Audit Event (append-only)
                                   ↓
                            AlgorithmRun Record (immutable)
```

### Admissibility Considerations

This system is designed to support, not replace, expert testimony. Algorithm
outputs provide:

- **Authenticity support:** Hash verification and provenance graphs demonstrate
  that evidence has not been altered since ingestion.
- **Completeness evidence:** Deduplication reports and timeline alignments help
  demonstrate thorough review.
- **Process evidence:** Audit logs demonstrate who ran what analysis, when, with
  what parameters.

### What This System Does Not Do

- It does not render legal conclusions.
- It does not determine admissibility (that is a judicial function).
- It does not infer intent, guilt, or liability.
- It does not provide legal advice.

### Independent Verification

Any result can be independently verified:

1. Retrieve the `AlgorithmRun` record.
2. Confirm the `params_hash` matches the stated parameters.
3. Confirm the `input_hashes` match the evidence items.
4. Re-run the same algorithm version with the same inputs and parameters.
5. Confirm the `result_hash` matches.

If any hash does not match, the discrepancy must be investigated and explained.

---

*This document is technical reference material. It is not legal advice and does
not constitute a legal opinion on the admissibility of any evidence or the
adequacy of any process.*
