# Test Status Report — v0.8.0 (Phase 9 Gate)

**Date:** 2026-02-10  
**Version:** 0.8.0  
**Runner:** `py -3.9 -m pytest tests/ --tb=no`  
**Exit Code:** 0

## Normalized Metrics

| Metric              | Count |
|---------------------|-------|
| **Passed**          | 380   |
| **Failed**          | 0     |
| **Errors**          | 0     |
| **Skipped**         | 0     |
| **Quarantined**     | 3     |
| **Warnings**        | 20    |
| **CI Green**        | Yes   |

## Quarantined Suites (excluded from collection)

| File | Reason | Tracked In |
|------|--------|-----------|
| `test_cli_end_to_end.py` | `backend.tools.cli.cli` removed | `tests/quarantine/QUARANTINE.md` |
| `test_courtlistener_client.py` | `backend.src.verified_legal_sources` removed | `tests/quarantine/QUARANTINE.md` |
| `test_manifest.py` | `backend.tools.cli.hashing` / `.manifest` removed | `tests/quarantine/QUARANTINE.md` |

**Deadline:** Phase 11 — restore when modules are re-implemented, or remove permanently.

## Test File Breakdown

| File | Tests |
|------|-------|
| `tests/phase9/unit/batch_processing/test_pdf_batch_loader.py` | 20 |
| `tests/test_access_controls.py` | 21 |
| `tests/test_api_and_webhooks.py` | 50 |
| `tests/test_case_event_invariants.py` | 22 |
| `tests/test_case_management.py` | 17 |
| `tests/test_court_package.py` | 15 |
| `tests/test_document_processing.py` | 52 |
| `tests/test_event_timeline.py` | 20 |
| `tests/test_forensic_integrity.py` | 17 |
| `tests/test_health_and_logging.py` | 19 |
| `tests/test_integrity_statement.py` | 29 |
| `tests/test_login_now.py` | 1 |
| `tests/test_migration_smoke.py` | 9 |
| `tests/test_phase2_defensibility.py` | 17 |
| `tests/test_share_and_transparency.py` | 47 |
| `tests/test_storage_backend.py` | 25 |
| **Total** | **380** |

## Version Source of Truth

- **Canonical:** `version.py` → `__version__ = "0.8.0"`
- **Propagated to:** `package.json` (manual sync), `app_config.py` (imported)

## Warnings (non-blocking)

1. `MovedIn20Warning` — `declarative_base()` deprecated in SQLAlchemy 2.0 (in `batch_document_processing.py`)
2. `DeprecationWarning` — PyPDF2 deprecated, migrate to pypdf
3. `LegacyAPIWarning` — `Query.get()` deprecated in SQLAlchemy 2.0 (multiple locations)

These are informational. None block CI. Address during Phase 10+ maintenance.

## Phase 10 Gate: PASSED

Default test invocation (`py -3.9 -m pytest tests/`) exits green.  
All quarantined suites are tracked with documented deadlines.  
No unresolved failures or collection errors.
