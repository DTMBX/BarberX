# Schema Governance — Alembic Migration Policy

## Revision Chain

| Revision | Description | Reversible |
|----------|-------------|------------|
| 0001 | Case, Organization, CaseParty, CaseEvidence | Yes |
| 0002 | Events (UUID PK), CameraSyncGroup, EventEvidence | Yes |
| 0003 | CaseTimelineEntry, CaseExportRecord, SHA-256 index | Yes |
| 0004 | (no-op) Jurisdiction metadata — superseded by 0001 | Yes |

## Table Ownership

Tables fall into two categories:

### Migration-managed (created by Alembic revisions)

`organization`, `legal_case`, `case_party`, `case_evidence`, `events`,
`camera_sync_group`, `event_evidence`, `case_timeline_entry`,
`case_export_record`

These tables are created, altered, and dropped exclusively by Alembic
migrations.  `db.create_all()` will also create them (from ORM metadata),
but the authoritative schema is the migration chain.

### ORM-managed (created by `db.create_all()`)

All other tables — `users`, `evidence_item`, `chain_of_custody`,
`evidence_analysis`, `evidence_tag`, `production_set`, `production_item`,
`privilege_log`, and the e-discovery / legal-violation / document-processing
families.

These tables are **not** governed by migrations today.  Future phases may
bring them under Alembic control.  Until then, `db.create_all()` is the
canonical path.

## ForeignKey Dependencies

Migrations 0001–0003 reference `users.id` and `evidence_item.id` via
ForeignKey constraints.  These tables are ORM-managed, not migration-managed.

- On **SQLite** (current): FK references are stored as schema text and are
  not enforced at DDL time (`PRAGMA foreign_keys` defaults to OFF).
  Migrations apply cleanly even if the referenced tables do not yet exist.
- On **PostgreSQL / MySQL** (future): These FKs would fail unless the
  referenced tables exist first.  A baseline migration (or
  `db.create_all()`) would be required before `upgrade head`.

The CI smoke test (`ci_migration_smoke.py`) validates against a blank
SQLite database without calling `db.create_all()` first.  This works
because SQLite does not enforce FK existence at table creation time.

## Table Rename Strategy (Phase 2)

### Problem

Three tablenames collided between `models/evidence.py` and
`models/ediscovery.py`:

| Table | evidence.py | ediscovery.py |
|-------|-------------|---------------|
| production_set | `production_set` | `production_set` (collision) |
| production_item | `production_item` | `production_item` (collision) |
| privilege_log | `privilege_log` | `privilege_log` (collision) |

### Resolution

The **ediscovery.py** models were renamed with an `ediscovery_` prefix:

| Model | Old tablename | New tablename |
|-------|---------------|---------------|
| `ediscovery.ProductionSet` | `production_set` | `ediscovery_production_set` |
| `ediscovery.ProductionItem` | `production_item` | `ediscovery_production_item` |
| `ediscovery.PrivilegeLog` | `privilege_log` | `ediscovery_privilege_log` |

The **evidence.py** models retain their original tablenames (`production_set`,
`production_item`, `privilege_log`).

### Migration coverage

No Alembic migration performs a `RENAME TABLE` operation.  The rename was
applied at the ORM level only (changing `__tablename__`).  Since these
tables are ORM-managed (via `db.create_all()`), the rename takes effect on
fresh databases automatically.

For existing databases that already have data in the old tablenames, a
data-migration script would be needed.  This is tracked as a future task.

### ForeignKey audit

After the rename, all ForeignKey references in `ediscovery.py` were updated
to point to the new `ediscovery_` prefixed tablenames.  The
`court_grade_discovery.py` model intentionally references
`production_set.id` (the evidence.py table), which is correct.

## CI Migration Smoke Test

Two entry points are provided:

1. **pytest**: `tests/test_migration_smoke.py` — 9 tests covering upgrade,
   downgrade, round-trip, chain integrity, and schema drift detection.
2. **Standalone script**: `ci_migration_smoke.py` — zero-dependency gate
   suitable for any CI pipeline.  Returns exit 0 on success, 1 on failure.

### Recommended CI step

```yaml
# GitHub Actions example
- name: Migration smoke test
  run: python ci_migration_smoke.py
```

```yaml
# Or via pytest
- name: Migration smoke test (pytest)
  run: python -m pytest tests/test_migration_smoke.py -v
```

## Rules for New Migrations

1. Every revision must have a `downgrade()` that fully reverses `upgrade()`.
2. Use `render_as_batch=True` (already configured in `env.py`) for SQLite
   ALTER TABLE support.
3. Guard operations on ORM-managed tables (e.g., `evidence_item`) with
   `inspector.get_table_names()` checks.
4. Do not use Unicode characters in `server_default` values — use ASCII
   only.
5. Run `python ci_migration_smoke.py` before merging any migration.
6. Keep the revision chain linear — no branch heads.
