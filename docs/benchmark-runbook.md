# Review Platform — Benchmark Runbook

Throughput proof for Phase 10 "Done" confirmation.

---

## Objective

Demonstrate that the Search & Review Platform handles a realistic
corpus (5 000 documents / ~50 000 pages) within acceptable latency
under standard deployment conditions.

---

## Prerequisites

| Item | Requirement |
|------|-------------|
| Python | 3.9+ (test runner), 3.12 (application) |
| Database | SQLite (test) or PostgreSQL 15+ (production) |
| Test suite | `tests/test_review_performance.py` |
| Seed count | 5 000 evidence items × ~10 pages each |

---

## 1. Run the automated benchmark

```bash
py -3.9 -m pytest tests/test_review_performance.py -v --tb=short -W ignore
```

**Expected output:** All `TestSearchThroughput` tests pass with wall-clock
times printed in assertion messages.  All `TestIndexCoverage` tests confirm
that every search-hot column has a database index.

---

## 2. Index verification checklist

| Model | Column(s) | Index Name |
|-------|-----------|------------|
| `EvidenceItem` | `file_type` | `ix_evidence_item_file_type` |
| `EvidenceItem` | `collected_date` | `ix_evidence_item_collected_date` |
| `EvidenceItem` | `evidence_type` | `ix_evidence_item_evidence_type` |
| `EvidenceItem` | `processing_status` | `ix_evidence_item_processing_status` |
| `ContentExtractionIndex` | `case_id` | `ix_content_extraction_case_id` |
| `ReviewDecision` | `(case_id, evidence_id, is_current)` | `ix_review_decision_lookup` |
| `ReviewAnnotation` | `(case_id, evidence_id)` | `ix_review_annotation_lookup` |
| `CaseEvidence` | `case_id` | inline `index=True` |
| `CaseEvidence` | `evidence_id` | inline `index=True` |
| `CaseEvidence` | `(case_id, evidence_id)` | `uq_case_evidence` (unique) |

---

## 3. Manual throughput estimate

For a human reviewer session:

1. **Seed a test case** with 5 000 evidence items (the automated test
   does this in `_seed_data`).
2. Open the Review Workspace at `/review/<case_id>`.
3. Execute a series of searches and coding actions over 10 minutes.
4. Record:
   - Number of documents reviewed (coded)
   - Number of searches executed
   - Subjective responsiveness (acceptable / sluggish)
5. Extrapolate: `(documents coded / minutes) × 60 = docs/hour`.

**Target:** ≥ 60 documents reviewed per hour with no perceptible lag
on search or code-apply operations.

---

## 4. Production PostgreSQL query plans

When deploying to PostgreSQL, verify query plans with:

```sql
-- Unfiltered search (most common)
EXPLAIN ANALYZE
SELECT ei.id, ei.original_filename, ei.file_type
FROM evidence_item ei
JOIN case_evidence ce ON ce.evidence_id = ei.id
JOIN content_extraction_index ci ON ci.evidence_id = ei.id
WHERE ce.case_id = :case_id AND ce.unlinked_at IS NULL
ORDER BY ei.created_at DESC
LIMIT 50 OFFSET 0;

-- Text search (ILIKE)
EXPLAIN ANALYZE
SELECT ei.id
FROM evidence_item ei
JOIN content_extraction_index ci ON ci.evidence_id = ei.id
JOIN case_evidence ce ON ce.evidence_id = ei.id
WHERE ce.case_id = :case_id AND ce.unlinked_at IS NULL
  AND (ci.full_text ILIKE '%contract%' OR ci.persons ILIKE '%contract%');
```

Confirm that:
- Index scans are used on `case_evidence.case_id`.
- No sequential scans on `evidence_item` for filtered queries.
- Pagination does not regress beyond `O(page * page_size)`.

---

## 5. Success criteria

| Metric | Threshold |
|--------|-----------|
| Unfiltered search (5k docs) | < 2 s (SQLite), < 200 ms (PostgreSQL) |
| Text search (ILIKE, 5k docs) | < 2 s (SQLite), < 500 ms (PostgreSQL) |
| All index coverage tests | PASS |
| Deep pagination (page 50) | < 2 s |
| Batch coding (50 items) | < 1 s |

---

## 6. Sign-off

| Role | Name | Date | Result |
|------|------|------|--------|
| Developer | | | |
| Reviewer | | | |

> Phase 10 is considered **Done** when all tests pass and the manual
> throughput estimate meets the target above.
