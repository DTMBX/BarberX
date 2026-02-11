# Database Operations Guide

This document covers schema baseline management, backup/restore procedures, and
the SQLite-to-PostgreSQL migration path.

---

## 1. Schema Baseline (Alembic)

### Stamp an existing database at the current head

If a database was created via `db.create_all()` (not Alembic) and already matches
the schema at head, stamp it so Alembic considers it up to date:

```bash
# Activate your virtualenv / ensure correct Python
flask db stamp head
```

This writes the current head revision (`0004`) into the `alembic_version` table
without executing any migration code.

### Verify the current revision

```bash
flask db current
```

Expected output: `0004_jurisdiction_metadata (head)`

### Run pending migrations

```bash
flask db upgrade
```

### Downgrade one step

```bash
flask db downgrade -1
```

### Full downgrade to base (empty schema)

```bash
flask db downgrade base
```

---

## 2. Backup and Restore (SQLite)

### Backup

SQLite databases are single files. A reliable backup is a file copy while no
write transactions are in progress.

```powershell
# Windows — stop the Flask process first
Copy-Item "instance\Evident.db" "backups\Evident_$(Get-Date -Format yyyyMMdd_HHmmss).db"
```

```bash
# Linux/macOS
cp instance/Evident.db "backups/Evident_$(date +%Y%m%d_%H%M%S).db"
```

For online backup without downtime (requires `sqlite3` CLI):

```bash
sqlite3 instance/Evident.db ".backup 'backups/Evident_online.db'"
```

### Restore

```powershell
# Stop the Flask process, then:
Copy-Item "backups\Evident_20260210_120000.db" "instance\Evident.db" -Force
```

### Evidence store backup

The evidence store directory (`evidence_store/`) contains originals, derivatives,
and manifests. Back it up alongside the database:

```powershell
# Archive the complete evidence store
Compress-Archive -Path "evidence_store\*" -DestinationPath "backups\evidence_store_$(Get-Date -Format yyyyMMdd).zip"
```

---

## 3. SQLite → PostgreSQL Migration Path

### Prerequisites

- PostgreSQL 15+ installed and running.
- `psycopg2-binary` (or `psycopg2`) installed in your Python environment.
- A target database created: `CREATE DATABASE evident;`

### Step 1: Export data from SQLite

```bash
# Dump all table data (not schema — Alembic creates that)
sqlite3 instance/Evident.db .dump > backups/evident_data.sql
```

Or use `pgloader` for automated conversion:

```bash
pgloader sqlite:///instance/Evident.db postgresql://user:pass@localhost/evident
```

### Step 2: Update configuration

Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/evident"
```

Or in a `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/evident
```

### Step 3: Create schema via Alembic

```bash
flask db upgrade
```

This applies all migrations (0001–0004) against PostgreSQL.

### Step 4: Import data

If using `pgloader`, data is already loaded. If using manual SQL:

1. Strip SQLite-specific syntax from the dump (`BEGIN TRANSACTION`, `COMMIT`,
   `CREATE TABLE` statements — keep only `INSERT INTO`).
2. Run the filtered inserts against PostgreSQL:

```bash
psql -U user -d evident -f backups/evident_inserts.sql
```

### Step 5: Stamp Alembic

If the schema was created by `flask db upgrade`, this is already done. If you
used `pgloader` (which copies the `alembic_version` table), verify:

```bash
flask db current
# Should show: 0004_jurisdiction_metadata (head)
```

### Step 6: Verify integrity

```bash
# Run the migration smoke tests against the new database
DATABASE_URL="postgresql://..." python -m pytest tests/test_migration_smoke.py -v
```

---

## 4. Schema Version History

| Revision | Name | Key Changes |
|----------|------|-------------|
| 0001 | `case_and_case_evidence` | `legal_case`, `case_evidence`, `case_party`, `case_event`, `event_officer`, `sync_group`, `case_export_record` tables |
| 0002 | `add_chain_of_custody_table` | `chain_of_custody` table for append-only audit |
| 0003 | `timeline_export_indexes` | Indexes on `case_event.event_date`, `case_export_record.created_at`; conditional SHA-256 index on `evidence_item` |
| 0004 | `jurisdiction_metadata` | No-op (columns already in 0001); retained for chain integrity |

---

## 5. CI Migration Gate

The CI pipeline runs `ci_migration_smoke.py` on every push. This script:

1. Creates a temporary in-memory SQLite database.
2. Upgrades to head.
3. Downgrades to base.
4. Round-trips (upgrade → downgrade → upgrade).
5. Checks for model/migration drift.

Failure blocks the build. See `docs/SCHEMA_GOVERNANCE.md` for the full policy.

---

## 6. Operational Backup Schedule

### Recommended Cadence

| Frequency | Target | Retention |
|-----------|--------|-----------|
| Hourly | WAL archive (PostgreSQL) | 48 hours |
| Daily | Full `pg_dump -Fc` | 30 days |
| Weekly | Evidence store rsync | 90 days |
| Monthly | Full system snapshot | 1 year |

### Automated Daily Backup (cron example)

```cron
# /etc/cron.d/evident-backup
0 3 * * * evident /opt/evident/scripts/backup.sh >> /var/log/evident-backup.log 2>&1
```

```bash
#!/bin/bash
# scripts/backup.sh
set -euo pipefail
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backup/evident

# Database
pg_dump -Fc evident > "$BACKUP_DIR/db_${TIMESTAMP}.dump"

# Evidence store (incremental)
rsync -a --checksum /opt/evident/evidence_store/ "$BACKUP_DIR/evidence_store/"

# Prune old database dumps (>30 days)
find "$BACKUP_DIR" -name 'db_*.dump' -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

### Backup Verification

Test restores quarterly:

```bash
createdb evident_restore_test
pg_restore -d evident_restore_test /backup/evident/db_YYYYMMDD_HHMMSS.dump
DATABASE_URL="postgresql://...evident_restore_test" flask db current
dropdb evident_restore_test
```

