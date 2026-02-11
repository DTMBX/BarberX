# Evident Technologies — Technical Brief

**For: Investor and counsel review**
**Version: 0.4.0**
**Date: 2026-02-10**

This document summarizes the technical guarantees and design constraints of the
Evident platform as of v0.4.0. Every claim below is backed by automated tests
that run on every commit. No claim is aspirational; each describes implemented,
tested behavior.

---

## 1. Evidence Integrity Invariants

**Tested by:** `tests/test_forensic_integrity.py` (17 tests)

| Guarantee | Mechanism |
|-----------|-----------|
| Originals are never overwritten | `EvidenceStore.store_original()` raises `FileExistsError` on duplicate path. Immutability enforced at both application and storage-backend level. |
| Every artifact is SHA-256 hashed at ingest | Streaming 64 KiB-block hashing (`services/evidence_store.py`). Post-copy verification compares recomputed hash against expected. |
| Duplicate detection | If an ingested file's SHA-256 matches an existing original, the system references the existing file and records a `INGEST_DUPLICATE` audit entry. No data is lost or silently merged. |
| Hash verification on retrieval | `verify_original(sha256)` recomputes the hash and compares. Any mismatch is logged as `INTEGRITY_FAILED`. |

**Storage backend abstraction** (`services/storage_backend.py`): `LocalFSStore`
and `S3Store` implement the same `StorageBackend` interface. Immutability and
SHA-256 verification are enforced at the interface level, not per-backend. 25
tests cover the abstraction (`tests/test_storage_backend.py`).

---

## 2. Audit Model

**Tested by:** `tests/test_phase2_defensibility.py` (17 tests)

| Guarantee | Mechanism |
|-----------|-----------|
| Append-only audit log | `AuditStream` dual-writes to DB (`ChainOfCustody` table) and evidence manifest JSON. No update or delete operations exist on the `ChainOfCustody` model. |
| Every access is recorded | Download endpoints require a stated purpose (`auth/access_control.py`). The audit record captures actor, purpose, IP, user agent, and timestamp. |
| Cascade-safe | Deleting a parent `EvidenceItem` does not delete its `ChainOfCustody` entries — tested explicitly. |
| Structured action vocabulary | `AuditAction` constants (`INGEST`, `HASH_COMPUTED`, `DERIVATIVE_CREATED`, `ACCESSED`, `DOWNLOADED`, `EXPORTED`, etc.) prevent ad-hoc strings. |

---

## 3. Export Reproducibility

**Tested by:** `tests/test_integrity_statement.py` (29 tests)

| Guarantee | Mechanism |
|-----------|-----------|
| Deterministic text output | `IntegrityStatementGenerator.generate()` accepts explicit `generated_at` and `statement_id` parameters. Same inputs produce byte-identical output. |
| Two-pass self-hash | Text is rendered with a placeholder, hashed, then the hash is embedded. The embedded hash is independently verifiable. |
| Manifest records statement hashes | `manifest.json` inside every export ZIP contains `text_sha256`, `pdf_sha256`, `statement_id`, and `pre_manifest_sha256`. |
| Court package with exhibit index | `CourtPackageExporter` produces `INDEX.csv` + `INDEX.json` with per-file SHA-256 hashes, verified against actual file contents. 15 tests cover the package (`tests/test_court_package.py`). |

---

## 4. Event Sealing and Sync Metadata-Only Policy

**Tested by:** `tests/test_case_event_invariants.py` (22 tests)

| Guarantee | Mechanism |
|-----------|-----------|
| Event sealing | Once an event's `is_sealed` flag is set, the event records `sealed_by`, `sealed_at`, and originating `sync_group_id`. Sealed events cannot be mutated. |
| Sync groups are metadata-only | BWC sync creates `SyncGroup` records that reference events by ID. No evidence bytes are modified during sync. |
| Conflict detection | Overlapping sync groups that reference the same event are detected and flagged. |

---

## 5. Migration Governance and CI Gates

**Tested by:** `tests/test_migration_smoke.py` (9 tests), `ci_migration_smoke.py`

| Guarantee | Mechanism |
|-----------|-----------|
| Full upgrade/downgrade reversibility | Tested: upgrade from blank DB to head (4 revisions, 10 tables), full downgrade to base, round-trip (upgrade → downgrade → upgrade). |
| Linear migration chain | Alembic revisions 0001 → 0002 → 0003 → 0004, single head, no branches. Enforced by CI. |
| Drift detection | CI compares model metadata against migration-created schema. Divergence blocks the build. |
| Schema baseline documented | `docs/DATABASE_OPERATIONS.md` covers stamp, backup/restore, and SQLite → PostgreSQL migration path. |

---

## 6. Access Control

**Tested by:** `tests/test_access_controls.py` (21 tests)

| Guarantee | Mechanism |
|-----------|-----------|
| Purpose-required access | Evidence downloads require a `purpose` parameter from a controlled vocabulary — denied with 400/422 otherwise. |
| Secure headers | Flask-Talisman enforces CSP, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, HSTS. |
| Rate limiting | Auth endpoints (login, register, forgot-password, reset-password) are rate-limited via Flask-Limiter. |
| Session hardening | HTTPOnly, SameSite=Lax, Secure (production). |

---

## 7. Test Coverage Summary

| Suite | Tests | Scope |
|-------|-------|-------|
| `test_forensic_integrity` | 17 | Hashing, immutability, ingest invariants |
| `test_phase2_defensibility` | 17 | Audit append-only, chain of custody |
| `test_case_event_invariants` | 22 | Event sealing, sync fidelity |
| `test_case_management` | 17 | Case lifecycle, linking |
| `test_migration_smoke` | 9 | Schema upgrade/downgrade/round-trip |
| `test_integrity_statement` | 29 | Export determinism, manifest recording |
| `test_access_controls` | 21 | Purpose-required access, secure headers |
| `test_storage_backend` | 25 | Storage abstraction, chunked uploads |
| `test_court_package` | 15 | Court exhibit packaging, index integrity |

**Total automated tests: 172**

All tests run against an in-memory SQLite database. No external services
required. No mocked integrity checks — hashes are computed and compared in every
relevant test.

---

## 8. Architecture Constraints (by design)

- **No AI inference on evidence content.** The platform processes, stores, and
  exports evidence. It does not infer guilt, liability, intent, or credibility.
- **No nondeterministic processing.** All transforms are reproducible from
  originals and recorded parameters.
- **No silent side effects.** Every state change is logged. Every file
  operation is hashed.
- **UI is separated from forensic logic.** Templates render data; services
  enforce invariants.
- **Audit logs are append-only.** No API, model method, or administrative
  function deletes or modifies audit entries.

---

## 9. Deployment Model

| Environment | Database | Storage | Notes |
|-------------|----------|---------|-------|
| Development | SQLite | Local filesystem | Single-node, default |
| Production | PostgreSQL 15+ | S3 / S3-compatible | Multi-node, via `STORAGE_BACKEND=s3` |

Migration path from SQLite to PostgreSQL is documented in
`docs/DATABASE_OPERATIONS.md`. The storage backend is selected by configuration
(`STORAGE_BACKEND`, `S3_BUCKET`), not by code changes.

---

*This document was generated from the Evident codebase at commit HEAD on
2026-02-10. It reflects implemented, tested behavior — not roadmap items.*
