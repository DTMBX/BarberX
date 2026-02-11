# Changelog

All notable changes to the Evident Technologies platform are documented here.
This project uses [Semantic Versioning](https://semver.org/).

---

## [0.7.0] — 2026-02-10

**Phase 8 — API Hardening & Webhook Notifications**

### Added

- **Bearer token authentication middleware** (`auth/api_auth.py`):
  `api_token_required` and `api_admin_required` decorators for programmatic API
  access. Extracts `Authorization: Bearer <token>` header, validates against
  `ApiToken` model (expiration, active state, user active), sets `g.api_token`
  and `g.api_user`, updates `last_used_at` on every request.
- **Versioned REST API** (`routes/api_v1.py`): Blueprint at `/api/v1/` with 15+
  endpoints:
  - **Cases:** `GET /cases` (paginated, filterable by status/case_type),
    `GET /cases/<id>` (with evidence list).
  - **Evidence:** `GET /evidence` (paginated), `GET /evidence/<id>`,
    `GET /evidence/<id>/audit` (chain of custody), `GET /evidence/verify/<hash>`
    (SHA-256 lookup).
  - **Audit:** `GET /audit` (global, paginated, filterable by action/since).
  - **Tokens:** `GET /tokens`, `POST /tokens` (create, returns raw once),
    `DELETE /tokens/<id>` (revoke).
  - **Webhooks:** `GET /webhooks`, `POST /webhooks` (HTTPS required, returns
    secret once), `DELETE /webhooks/<id>`.
  - **Health:** `GET /health` (no auth, returns status + api_version + version).
  Pagination helper with max 100 per page. All serializers return metadata only —
  no PII, no content bytes, no transcripts.
- **Webhook subscription model** (`models/webhook.py`): `WebhookSubscription`
  with HMAC-SHA256 signing, comma-separated event type filtering (11 valid
  events or `*` wildcard), auto-disable after 10 consecutive delivery failures,
  delivery health tracking (consecutive_failures, last_failure_at/reason,
  last_success_at, total_deliveries). `WebhookDeliveryLog` — append-only delivery
  audit records (event type, payload hash, response status, duration, success).
- **Webhook service** (`services/webhook_service.py`): `WebhookService.dispatch()`
  finds matching active subscriptions, builds JSON envelope with SHA-256 payload
  hash, delivers with HMAC-signed headers (`X-Evident-Event`,
  `X-Evident-Signature`, `X-Evident-Delivery`). 10-second timeout per delivery.
  `create_subscription()`, `delete_subscription()` (soft-deactivate),
  `list_subscriptions()`.
- **Phase 8 test suite** (`tests/test_api_and_webhooks.py`): 50 tests covering
  bearer token auth (missing, invalid, expired, inactive, valid, usage tracking),
  all REST endpoints (cases, evidence, audit, tokens, webhooks, health),
  pagination, webhook model (HMAC sign/verify, event matching, auto-disable,
  success reset), webhook service (create, delete, dispatch, access control),
  delivery log (append-only).

### Changed

- `app_config.py`: Registered `api_v1_bp` blueprint.

### Test Results

- **288 tests passing** (238 existing + 50 new), 0 failures.

---

## [0.6.0] — 2026-02-10

**Phase 7 — Controlled External Trust & Scale**

### Added

- **Share-link model** (`models/share_link.py`): Expiring, revocable, audited
  share tokens. SHA-256 hashed storage, configurable scopes (read_only, export),
  recipient roles (attorney, co_counsel, expert_witness, auditor,
  opposing_counsel, insurance_adjuster), max 90-day expiry, access-count limits.
  SQLite-safe datetime handling via `_ensure_aware()`.
- **Share-link service** (`services/share_link_service.py`): Create, resolve,
  revoke, list operations. Raw token returned exactly once on creation; only the
  hash is stored. Revocation is immediate and irreversible.
- **Share routes** (`routes/share_routes.py`): Authenticated management endpoints
  (`POST /share/links`, `POST /share/links/<id>/revoke`,
  `GET /share/links/case/<case_id>`) and unauthenticated external portal
  (`GET /share/portal?token=`, `GET /share/portal/verify?token=`). Portal returns
  case metadata and evidence hashes only — no content bytes served.
- **Transparency blueprint** (`routes/transparency.py`):
  `GET /transparency/report` — public, no-auth, returns aggregate counts only
  (cases, evidence items, audit entries, type distributions, version). Explicitly
  no PII. `GET /transparency/verify` — verification instructions with CLI
  commands for Linux/macOS/Windows/Python and legal disclaimer.
- **Multi-tenant isolation** (`auth/tenant_isolation.py`): `tenant_case_access`
  decorator enforces organization-level case boundaries. `tenant_filter_cases()`
  applies WHERE filter to case queries. Admin bypass for oversight.
- **Performance profiler** (`scripts/perf_profile.py`): CLI benchmarking for
  large-case query performance (case load, evidence list, filtered count, hash
  lookup). Reports p50/p95/max. Synthetic data rolled back after profiling.
- **Change-control policy** (`docs/CHANGE_CONTROL_POLICY.md`): Phase-locking
  rules (phases 1–6 locked), branch naming conventions, commit message format,
  pre-merge forensic checklist, release process, incident response protocol.
- **47 new tests** (`tests/test_share_and_transparency.py`): ShareLink model (11),
  ShareLinkService (8), Share routes (10), Transparency report (9),
  Tenant isolation (4), Governance docs (3), Audit logging (2).

### Changed

- Replaced deprecated `Query.get()` calls with `Session.get()` in
  `services/share_link_service.py`, `routes/share_routes.py`,
  `auth/tenant_isolation.py`.
- Registered `share_bp` and `transparency_bp` blueprints in `app_config.py`.

### Test totals

| Suite | Count |
| ----- | ----- |
| Phases 1–6 (existing) | 191 |
| Phase 7 (share, transparency, tenant, governance) | 47 |
| **Total** | **238** |

---

## [0.5.0] — 2026-02-10

**Phase 5 + 6 — Productionization & Deployment Baseline**

### Added (Phase 5)

- Release discipline: `VERSION` file (semver), `CHANGELOG.md`, `package.json`
  version alignment.
- Purpose-required access controls (`auth/access_control.py`): every evidence
  download requires an explicit access purpose from a governed list.
- Security hardening (`auth/security.py`): Flask-Talisman (CSP, HSTS,
  X-Frame-Options), Flask-Limiter (rate limits on auth routes), session
  hardening.
- Pluggable storage backend (`services/storage_backend.py`): `LocalFSStore`
  (default) and `S3Store` interface with atomic writes, SHA-256 verification,
  immutability enforcement, and directory-traversal prevention.
- Chunked upload service (`services/chunked_upload.py`): server-side staging for
  large BWC files (10 MiB chunks, 4 hr timeout, SHA-256 on finalize).
- Court-package exporter (`services/court_package.py`): Exhibit_NNN directories,
  INDEX.csv, INDEX.json with per-file SHA-256, PACKAGE_HASH.txt, optional
  derivative viewer notice.
- Technical brief for investors/counsel (`docs/TECHNICAL_BRIEF.md`).
- Database operations guide (`docs/DATABASE_OPERATIONS.md`).
- 61 new tests across 3 suites (access controls, storage backend, court package).

### Added (Phase 6)

- Health-check endpoints (`routes/health.py`): `/health/live`, `/health/ready`,
  `/health/info` — unauthenticated, JSON-only, suitable for load-balancer probes.
- Structured JSON logging (`services/structured_logging.py`): per-request UUID,
  `X-Request-ID` response header, JSON format in production, human-readable in
  development.
- Gunicorn production configuration (`deploy/gunicorn.conf.py`): CPU-scaled
  workers, 120 s timeout, forwarded-header trust, stdout logging.
- nginx reverse-proxy template (`deploy/nginx.conf`): TLS termination, 3 GB
  upload passthrough, health-check routing, static asset serving.
- systemd service unit (`deploy/evident.service`): restart policy, filesystem
  hardening (NoNewPrivileges, ProtectSystem=strict).
- Environment template (`deploy/.env.template`): all production variables
  documented.
- Production deployment guide (`docs/PRODUCTION_DEPLOYMENT.md`): end-to-end
  setup, tuning, monitoring, operational runbook.
- Audit transparency report script (`scripts/audit_report.py`): CLI tool with
  `activity`, `evidence`, `actors`, `exports` sub-commands. Read-only, supports
  JSON/CSV output with date range filters.
- Key management guide (`docs/KEY_MANAGEMENT.md`): SECRET_KEY rotation,
  database credential lifecycle, S3 IAM guidance, incident response.
- Operational backup schedule added to `docs/DATABASE_OPERATIONS.md`.
- 19 new tests (`tests/test_health_and_logging.py`).

### Test totals

- 10 suites, **191 tests**, 0 failures.

---

## [0.4.0] — 2026-02-10

**Phase 4 — Deterministic Integrity Statements**

### Added

- Deterministic Evidence Integrity Statement generator with two-pass self-hash
  embedding (`services/integrity_statement.py` rewritten).
- Integrity statement (text + optional PDF) included in every case export ZIP.
- `integrity_statement` section in export `manifest.json` records `text_sha256`,
  `pdf_sha256`, `statement_id`, and `pre_manifest_sha256`.
- Statement SHA-256 hashes propagated to `AuditStream` on export.
- 29 tests covering determinism, input-variation sensitivity, self-hash
  round-trip, manifest recording, export-record persistence, no-legal-conclusions
  guard, legacy API compatibility, and result immutability
  (`tests/test_integrity_statement.py`).

### Design decisions

- Text output is the authoritative forensic artifact (byte-deterministic).
  PDF is a convenience derivative (not byte-reproducible due to reportlab
  internals).
- `generated_at` is an explicit parameter — not sourced from `datetime.now()` —
  enabling deterministic re-generation from identical inputs.
- Two-pass hash: render with placeholder → SHA-256 → embed. The embedded
  hash is the pass-1 hash; `text_sha256` is the hash of the final bytes.

---

## [0.3.0] — 2026-02-10

**Phase 3 — Schema Governance and Migration Correctness**

### Fixed

- Flask-Migrate not initialized in `create_app()` — added
  `Migrate(app, db, directory='migrations')` after `db.init_app(app)`.
- Unicode minus signs (U+2212) in migration 0001 `server_default='-1'` replaced
  with ASCII hyphen-minus.
- Migration 0004 converted to documented no-op (retained for chain integrity).
- Missing `notes`, `created_at`, `updated_at` columns added to `case_party` in
  migration 0001.
- SHA-256 index on `evidence_item` in migration 0003 guarded with
  `inspector.get_table_names()` check.
- Stale FK in `models/ediscovery.py` corrected from `ForeignKey('production_set.id')`
  to `ForeignKey('ediscovery_production_set.id')`.
- Deprecated `get_engine()` call in `migrations/env.py` replaced with `.engine`
  property.

### Added

- Full migration validation: upgrade head from blank DB, full downgrade chain,
  round-trip (upgrade → downgrade → upgrade) — all pass.
- `tests/test_migration_smoke.py` — 9 pytest tests (upgrade, downgrade,
  round-trip, chain integrity, drift detection).
- `ci_migration_smoke.py` — standalone CI gate script (exit 0 / 1).
- `docs/SCHEMA_GOVERNANCE.md` — migration policy, table ownership, rename
  strategy, CI instructions.

---

## [0.2.0] — 2026-02-09

**Phase 2 — Operational Excellence**

### Added

- Case management models: `LegalCase`, `CaseEvidence`, `CaseParty`,
  `CaseExportRecord` with full CRUD and linking.
- Body-worn camera (BWC) event sync model and service
  (`services/event_sync_service.py`, `models/case_event.py`).
- Jurisdiction and incident metadata on `LegalCase`.
- Case event timeline viewer (`templates/cases/event_timeline_viewer.html`).
- Event sealing: sealed events record `sealed_by`, `sealed_at`, and originating
  `sync_group_id`. Sealed events cannot be mutated.
- Court-grade discovery service (`services/court_grade_discovery_service.py`).
- `tests/test_case_event_invariants.py` — 22 tests for event sealing,
  sync-group fidelity, and metadata-only updates.
- `tests/test_case_management.py` — 17 tests for case lifecycle and linking.
- `tests/test_phase2_defensibility.py` — 17 tests for audit append-only
  behavior and chain-of-custody integrity.
- `tests/test_forensic_integrity.py` — 17 tests for evidence hashing,
  immutability, and ingest invariants.

---

## [0.1.0] — 2026-02-08

**Phase 1 — Forensic Evidence Pipeline**

### Added

- `services/evidence_store.py` — canonical evidence storage with SHA-256 at
  ingest, immutable originals, streaming hashing, duplicate detection, and
  post-copy integrity verification.
- `services/audit_stream.py` — append-only dual-write audit (database +
  manifest JSON) for the full evidence lifecycle.
- `services/case_export_service.py` — court-ready ZIP export with integrity
  report and manifest.
- `services/evidence_export.py` — single-evidence self-verifying export.
- `models/evidence.py` — `EvidenceItem`, `CaseEvidence`, `ChainOfCustody`,
  `EvidenceDerivative`.
- Flask application factory with SQLAlchemy, Flask-Login, and CSRF protection.
- Authentication system: `User`, `ApiToken`, `AuditLog`, `UsageRecord` with
  role-based (ADMIN, MODERATOR, PRO_USER, USER) and tier-based (FREE, PRO,
  ENTERPRISE, ADMIN) access.
- Alembic migration chain (0001 → 0004) for case-management and evidence
  tables.

---

## [0.0.1] — 2026-02-07

**Initial Repository Setup**

### Added

- Repository structure, CI pipeline, GitHub Pages deployment.
- Modern design system with Tailwind CSS.
- Static site (11ty) for public-facing pages.
- Base Flask backend scaffold.
