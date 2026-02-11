"""Phase 2 — Jurisdiction metadata columns (no-op)

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-10

Originally intended to add jurisdiction metadata columns to legal_case.
These columns are already defined in migration 0001, making this revision
a no-op.  Retained to preserve the linear revision chain (0003 → 0004).

Reversible: Yes (no-op in both directions).
"""
from alembic import op

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NO-OP: These columns are already created by migration 0001 which
    # defines the full legal_case schema including all jurisdiction
    # metadata columns.
    #
    # This revision is retained (rather than deleted) to preserve the
    # linear revision chain.  Alembic stamps it as applied but emits
    # no DDL.
    #
    # For pre-Alembic databases that were bootstrapped via
    # db.create_all(), run `flask db stamp head` to mark all revisions
    # as applied without executing DDL.
    pass


def downgrade() -> None:
    # NO-OP: Corresponding upgrade is a no-op; nothing to reverse.
    pass
