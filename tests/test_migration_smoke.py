"""
Migration Smoke Tests
=====================
Validates that Alembic migrations can apply cleanly to a blank database
and fully reverse.  Designed to run in CI as a gate before merge.

Tests:
  1. upgrade head from blank DB      — all revisions apply without error
  2. downgrade -1 (full chain)       — every revision reverses cleanly
  3. upgrade → downgrade → upgrade   — round-trip is idempotent
  4. revision chain is linear        — no forks, no orphans
  5. head matches model metadata     — no un-migrated schema drift

These tests use a temporary SQLite file so the production database is
never touched.
"""

import os
import tempfile

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.script import ScriptDirectory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def migration_app(tmp_path):
    """Create a Flask app pointed at a fresh temp database."""
    db_path = tmp_path / "test_migrate.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from app_config import create_app
    app = create_app()

    with app.app_context():
        from auth.models import db
        # create_app() calls db.create_all(), so we must nuke every table
        # including non-Alembic tables so upgrade() starts from blank.
        inspector = sa.inspect(db.engine)
        # Disable FK checks so drops don't fail on references
        db.session.execute(sa.text("PRAGMA foreign_keys = OFF"))
        for table_name in inspector.get_table_names():
            db.session.execute(sa.text(f'DROP TABLE IF EXISTS "{table_name}"'))
        db.session.commit()
        db.session.execute(sa.text("PRAGMA foreign_keys = ON"))

    yield app

    # Restore env (optional — tests are isolated by tmp_path)
    os.environ.pop("DATABASE_URL", None)


def _get_config(app):
    """Return the Alembic Config wired through Flask-Migrate."""
    return app.extensions["migrate"].migrate.get_config()


def _get_script(app):
    """Return the Alembic ScriptDirectory."""
    return ScriptDirectory.from_config(_get_config(app))


# ---------------------------------------------------------------------------
# 1. upgrade head from blank
# ---------------------------------------------------------------------------

class TestUpgradeHead:
    """Ensure all migrations apply to a clean database."""

    def test_upgrade_head_creates_expected_tables(self, migration_app):
        with migration_app.app_context():
            from flask_migrate import upgrade
            from auth.models import db

            upgrade()

            inspector = sa.inspect(db.engine)
            tables = set(inspector.get_table_names())

            # Tables introduced by migrations 0001–0003
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
            assert not missing, f"Missing tables after upgrade head: {missing}"

    def test_upgrade_head_stamps_latest_revision(self, migration_app):
        with migration_app.app_context():
            from flask_migrate import upgrade
            from auth.models import db

            upgrade()

            row = db.session.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar()
            assert row == "0005", f"Expected head=0005, got {row}"


# ---------------------------------------------------------------------------
# 2. downgrade -1 (full chain back to base)
# ---------------------------------------------------------------------------

class TestDowngradeChain:
    """Ensure every revision can be reversed."""

    def test_full_downgrade_leaves_only_alembic_version(self, migration_app):
        with migration_app.app_context():
            from flask_migrate import upgrade, downgrade
            from auth.models import db

            upgrade()

            # Walk back one revision at a time
            script = _get_script(migration_app)
            revisions = list(script.walk_revisions())
            for _ in revisions:
                downgrade(revision="-1")

            inspector = sa.inspect(db.engine)
            tables = set(inspector.get_table_names())
            assert tables == {"alembic_version"}, (
                f"Tables remaining after full downgrade: {tables}"
            )

    def test_downgrade_stamps_correct_revisions(self, migration_app):
        with migration_app.app_context():
            from flask_migrate import upgrade, downgrade
            from auth.models import db

            upgrade()

            expected_chain = ["0004", "0003", "0002", "0001", None]
            for expected_rev in expected_chain:
                downgrade(revision="-1")
                row = db.session.execute(
                    sa.text("SELECT version_num FROM alembic_version")
                ).scalar()
                assert row == expected_rev, (
                    f"Expected revision {expected_rev}, got {row}"
                )


# ---------------------------------------------------------------------------
# 3. Round-trip: upgrade → downgrade → upgrade
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """Upgrade, fully downgrade, then upgrade again — must be idempotent."""

    def test_double_upgrade_is_idempotent(self, migration_app):
        with migration_app.app_context():
            from flask_migrate import upgrade, downgrade
            from auth.models import db

            # First pass
            upgrade()
            # Full rollback
            script = _get_script(migration_app)
            for _ in list(script.walk_revisions()):
                downgrade(revision="-1")
            # Second pass — must not raise
            upgrade()

            row = db.session.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar()
            assert row == "0005"


# ---------------------------------------------------------------------------
# 4. Revision chain integrity
# ---------------------------------------------------------------------------

class TestRevisionChain:
    """Validate the migration revision graph is linear and complete."""

    def test_no_branch_heads(self, migration_app):
        with migration_app.app_context():
            script = _get_script(migration_app)
            heads = script.get_heads()
            assert len(heads) == 1, f"Expected 1 head, found {len(heads)}: {heads}"

    def test_revisions_form_linear_chain(self, migration_app):
        with migration_app.app_context():
            script = _get_script(migration_app)
            revisions = list(script.walk_revisions())
            ids = [r.revision for r in revisions]
            # walk_revisions returns newest-first
            assert ids == ["0005", "0004", "0003", "0002", "0001"], (
                f"Unexpected revision order: {ids}"
            )

    def test_no_orphan_revisions(self, migration_app):
        """Every revision except the first must have a valid down_revision."""
        with migration_app.app_context():
            script = _get_script(migration_app)
            revisions = list(script.walk_revisions())
            all_ids = {r.revision for r in revisions}
            for rev in revisions:
                if rev.down_revision is not None:
                    assert rev.down_revision in all_ids, (
                        f"Orphan: {rev.revision} points to missing "
                        f"down_revision {rev.down_revision}"
                    )


# ---------------------------------------------------------------------------
# 5. Head matches model metadata (drift detection)
# ---------------------------------------------------------------------------

class TestSchemaDrift:
    """
    After upgrade head + db.create_all(), compare the actual schema against
    the declared model metadata.  Any mismatch indicates un-migrated drift.
    """

    MIGRATION_MANAGED_TABLES = {
        "organization",
        "legal_case",
        "case_party",
        "case_evidence",
        "events",
        "camera_sync_group",
        "event_evidence",
        "case_timeline_entry",
        "case_export_record",
    }

    def test_migration_tables_have_all_model_columns(self, migration_app):
        """
        For each migration-managed table, verify that the columns declared
        in the ORM model exist in the schema produced by migrations alone.
        """
        with migration_app.app_context():
            from flask_migrate import upgrade
            from auth.models import db

            upgrade()

            inspector = sa.inspect(db.engine)
            issues = []
            for tbl_name in self.MIGRATION_MANAGED_TABLES:
                if tbl_name not in inspector.get_table_names():
                    continue
                db_cols = {c["name"] for c in inspector.get_columns(tbl_name)}
                model_table = db.metadata.tables.get(tbl_name)
                if model_table is None:
                    continue
                model_cols = {c.name for c in model_table.columns}
                missing = model_cols - db_cols
                if missing:
                    issues.append(f"{tbl_name}: missing {missing}")
            assert not issues, (
                "Schema drift detected — columns in models but not in "
                f"migrations:\n" + "\n".join(issues)
            )
