#!/usr/bin/env python
"""
ci_migration_smoke.py — CI gate for Alembic migration correctness
=================================================================

Runs as a standalone script (no pytest dependency).  Returns exit 0 on
success, exit 1 on any failure.  Suitable for GitHub Actions, Azure
Pipelines, or any shell-based CI.

Usage:
    python ci_migration_smoke.py

What it validates:
    1. upgrade head from a blank SQLite database
    2. Expected tables exist after upgrade
    3. Full downgrade chain back to base
    4. Round-trip (upgrade → downgrade → upgrade) is idempotent
    5. Revision chain is linear with a single head
"""

import os
import sys
import tempfile
import traceback

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    # ---------- Setup ----------
    tmp = tempfile.mktemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp}"

    try:
        from app_config import create_app
    except ImportError as exc:
        print(f"FAIL: Cannot import app_config: {exc}", file=sys.stderr)
        return 1

    app = create_app()
    failures = []

    with app.app_context():
        import sqlalchemy as sa
        from alembic.script import ScriptDirectory
        from auth.models import db
        from flask_migrate import downgrade, upgrade

        # Blank the database
        db.drop_all()
        db.session.execute(sa.text("DROP TABLE IF EXISTS alembic_version"))
        db.session.commit()

        cfg = app.extensions["migrate"].migrate.get_config()
        script = ScriptDirectory.from_config(cfg)

        # ----- 1. Revision chain is linear -----
        heads = script.get_heads()
        if len(heads) != 1:
            failures.append(f"Expected 1 head, found {len(heads)}: {heads}")
        else:
            print(f"OK  revision chain has single head: {heads[0]}")

        revisions = list(script.walk_revisions())
        rev_ids = [r.revision for r in revisions]
        print(f"    revisions: {' -> '.join(reversed(rev_ids))}")

        # ----- 2. upgrade head -----
        try:
            upgrade()
            inspector = sa.inspect(db.engine)
            tables = set(inspector.get_table_names())
            expected = {
                "organization",
                "legal_case",
                "case_party",
                "case_evidence",
                "events",
                "camera_sync_group",
                "event_evidence",
                "case_timeline_entry",
                "case_export_record",
                "alembic_version",
            }
            missing = expected - tables
            if missing:
                failures.append(f"Missing tables after upgrade: {missing}")
            else:
                print(f"OK  upgrade head — {len(tables)} tables created")
        except Exception:
            failures.append(f"upgrade head failed:\n{traceback.format_exc()}")

        # ----- 3. Check stamp -----
        try:
            row = db.session.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar()
            if row != heads[0]:
                failures.append(
                    f"Stamp mismatch: expected {heads[0]}, got {row}"
                )
            else:
                print(f"OK  stamp at head: {row}")
        except Exception:
            failures.append(
                f"Could not read alembic_version:\n{traceback.format_exc()}"
            )

        # ----- 4. Full downgrade chain -----
        try:
            for _ in revisions:
                downgrade(revision="-1")
            inspector = sa.inspect(db.engine)
            remaining = set(inspector.get_table_names())
            if remaining != {"alembic_version"}:
                failures.append(
                    f"Tables remaining after full downgrade: {remaining}"
                )
            else:
                print("OK  full downgrade chain — clean")
        except Exception:
            failures.append(
                f"downgrade chain failed:\n{traceback.format_exc()}"
            )

        # ----- 5. Round-trip -----
        try:
            upgrade()
            row = db.session.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar()
            if row != heads[0]:
                failures.append(
                    f"Round-trip stamp mismatch: expected {heads[0]}, got {row}"
                )
            else:
                print("OK  round-trip (upgrade → downgrade → upgrade) — clean")
        except Exception:
            failures.append(
                f"Round-trip upgrade failed:\n{traceback.format_exc()}"
            )

    # ---------- Cleanup ----------
    try:
        os.unlink(tmp)
    except OSError:
        pass  # Windows file-locking; harmless in CI

    # ---------- Report ----------
    if failures:
        print(f"\nFAILED — {len(failures)} issue(s):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nAll migration smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
