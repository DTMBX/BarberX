"""Add unique constraint (case_id, sha256) on evidence_files

Revision ID: 0002_forensic_hardening
Revises: 0001_initial
Create Date: 2026-02-28
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_forensic_hardening"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Partial unique constraint: only applies when sha256 IS NOT NULL
    # This allows multiple rows with sha256=NULL (pending uploads)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_evidence_case_sha256
        ON evidence_files (case_id, sha256)
        WHERE sha256 IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_evidence_case_sha256")
