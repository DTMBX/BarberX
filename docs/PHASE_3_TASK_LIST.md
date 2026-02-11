# Phase 3 — Ticketized Task List

> All tasks carry explicit acceptance criteria.
> Non-negotiables: originals never overwritten, every artifact hashed,
> derivatives reference originals, audit log append-only, alignment is
> metadata-only, exports reproducible, no legal conclusions.

---

## EPX-201 — Case-Scoped Export Verification Hardening

**Priority:** P0 (blocking release)
**Component:** `services/case_export_service.py`, `services/evidence_export.py`
**Depends on:** Phase 2 (complete)

**Goal:** Guarantee case exports are reproducible and independently verifiable.

**Acceptance Criteria:**
- [ ] Two consecutive case exports of the same scope produce identical
      manifest hashes (excluding container-level timestamps; document
      reasoning if timestamps are included).
- [ ] Integrity statement PDF is included in every case export ZIP and its
      SHA-256 is recorded in the manifest.
- [ ] `case_export_generated` audit event includes: manifest hash, evidence
      list hash, and package SHA-256.
- [ ] Test: `test_export_reproducibility_hash_match` passes (byte-for-byte
      or hash-for-hash with documented exceptions).
- [ ] Test: `test_export_contains_integrity_statement` passes.

---

## EPX-202 — Sealed Event Immutability Enforcement

**Priority:** P0 (blocking release)
**Component:** `services/event_sync_service.py`, `models/case_event.py`
**Depends on:** Phase 2 (complete)

**Goal:** Sealed events cannot be modified without an auditable override path.

**Acceptance Criteria:**
- [ ] Offset updates fail when `event.is_sealed = True`, returning
      `SyncGroupResult(success=False, error=...)`.
- [ ] Denied mutation is logged as `event_mutation_denied` via SyncAuditAction
      (append-only).
- [ ] Tests cover: link denied, unlink denied, sync group creation denied,
      offset update denied — all on sealed events.
- [ ] Tests verify that unsealed events still accept all mutations.
- [ ] No override path exists unless explicitly designed and documented.

---

## EPX-203 — Timeline Alignment Artifact Generation

**Priority:** P1
**Component:** `services/event_timeline.py`, `services/event_sync_service.py`
**Depends on:** EPX-202

**Goal:** Produce a deterministic timeline JSON artifact per event that is
itself hashed and tracked as a derivative.

**Acceptance Criteria:**
- [ ] `/api/case-events/<event_id>/timeline` returns canonical timeline JSON.
- [ ] Timeline JSON has a SHA-256 stored as a derivative artifact on the
      event or in the case manifest.
- [ ] Audit entry `event_timeline_generated` appended with timeline hash.
- [ ] Test: same event data produces identical timeline hash across calls.
- [ ] Timeline entries are derived views only — they do not create new
      evidentiary state.

---

## EPX-204 — UI Event Timeline Alignment Viewer

**Priority:** P2
**Component:** `templates/events/`, `assets/js/`
**Depends on:** EPX-203

**Goal:** Synchronized proxy playback based on metadata offsets; no original
file modification.

**Acceptance Criteria:**
- [ ] Viewer shows tracks with labeled offsets per evidence stream.
- [ ] Playback sync uses `sync_offset_ms` metadata. No video transcoding or
      frame manipulation.
- [ ] UI contains explicit disclosure text: "Metadata-only alignment; originals
      unaltered."
- [ ] UI code is strictly separated from forensic logic (no direct DB access
      from templates/JS).
- [ ] Test: viewer renders without errors; disclosure text is present in DOM.

---

## EPX-205 — Alembic Migration Consolidation & CI Gate

**Priority:** P0 (blocking release)
**Component:** `migrations/`, CI configuration
**Depends on:** Phase 2 (complete)

**Goal:** Schema changes are fully represented in Alembic migrations and
enforced in CI.

**Acceptance Criteria:**
- [ ] `alembic upgrade head` succeeds from an empty database.
- [ ] `alembic downgrade -1` succeeds for the last revision (where feasible).
- [ ] CI includes a migration test job: create empty DB → upgrade head → run
      key tests.
- [ ] All four migration revisions (0001–0004) are ordered and reversible.
- [ ] Duplicate tablename collision (ediscovery vs. evidence) is resolved
      (ediscovery models prefixed with `ediscovery_`).

---

## EPX-206 — Jurisdiction Metadata UI + Validation

**Priority:** P1
**Component:** `templates/cases/`, `routes/case_routes.py`
**Depends on:** EPX-205

**Goal:** Enable jurisdiction metadata editing without legal conclusions.

**Acceptance Criteria:**
- [ ] UI supports editing: state (2-letter), agency type, retention policy
      reference, incident number, incident date.
- [ ] Validation is format-only (e.g., 2-letter state code, date format).
      No legal logic, no inference.
- [ ] Export includes jurisdiction fields as metadata only.
- [ ] Test: valid state code accepted; invalid rejected.
- [ ] Test: jurisdiction fields appear in export manifest.

---

## EPX-207 — Integrity Statement PDF Generator

**Priority:** P0 (blocking release)
**Component:** `services/integrity_statement.py`
**Depends on:** EPX-201

**Goal:** Deterministic PDF generation from the fixed verbatim template.

**Acceptance Criteria:**
- [ ] PDF generated for evidence, event, and case exports.
- [ ] PDF SHA-256 is logged and included in the export manifest.
- [ ] Text matches the verbatim template exactly (no AI variation, no
      paraphrasing).
- [ ] Bracketed fields are populated from system metadata at generation time.
- [ ] Test: `IntegrityStatementGenerator.generate_text()` produces stable
      output for same inputs.
- [ ] Fallback: if `reportlab` is not installed, UTF-8 text bytes are returned.

---

## EPX-208 — E-Discovery Model Reconciliation

**Priority:** P1
**Component:** `models/ediscovery.py`, `models/evidence.py`
**Depends on:** EPX-205

**Goal:** Eliminate duplicate model/table definitions between evidence and
e-discovery modules.

**Acceptance Criteria:**
- [ ] `ProductionSet`, `ProductionItem`, `PrivilegeLog` tablenames are unique
      across the entire ORM (`ediscovery_production_set`, etc.).
- [ ] All service imports resolve without collision.
- [ ] Migration for table renames is created if production data exists.
- [ ] No duplicate `Base` declarations — consolidate to `db.Model` only.

---

## EPX-209 — CI Test Pipeline

**Priority:** P1
**Component:** `.github/workflows/`
**Depends on:** EPX-205

**Goal:** Automated test execution on every push to `main` and on PRs.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow: install deps → run `pytest tests/` →
      report results.
- [ ] Migration test step: empty DB → `alembic upgrade head` → run
      forensic integrity tests.
- [ ] Minimum: all Phase 2 tests (34+) pass green.
- [ ] Badge added to README.

---

## EPX-210 — Audit Log Viewer (Admin)

**Priority:** P2
**Component:** `templates/admin/`, `auth/admin_routes.py`
**Depends on:** Phase 2

**Goal:** Admin UI for reviewing append-only audit log entries by case,
event, or evidence scope.

**Acceptance Criteria:**
- [ ] Admin route `/admin/audit-log` shows paginated audit entries.
- [ ] Filterable by: case_id, evidence_id, event_id, action type, date range.
- [ ] Entries are read-only in the UI. No edit or delete controls.
- [ ] Export as JSON slice for case-scoped audit.
