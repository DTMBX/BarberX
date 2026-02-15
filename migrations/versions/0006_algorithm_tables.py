"""Add algorithm tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-02-10

Tables created:
  - algorithm_run: Tracks every algorithm execution with full provenance.
  - provenance_edge: Directed edges in the evidence provenance graph.
  - verification_report: Integrity verification reports per case.
  - redaction_report: Redaction verification reports per case.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    # --- algorithm_run ---
    op.create_table(
        "algorithm_run",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(36), unique=True, nullable=False),
        sa.Column("algorithm_id", sa.String(100), nullable=False),
        sa.Column("algorithm_version", sa.String(20), nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("legal_case.id"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("params_hash", sa.String(64), nullable=True),
        sa.Column("result_hash", sa.String(64), nullable=True),
        sa.Column("integrity_check", sa.String(64), nullable=True),
        sa.Column("input_hashes_json", sa.Text(), nullable=True),
        sa.Column("output_hashes_json", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_algorithm_run_run_id", "algorithm_run", ["run_id"])
    op.create_index("ix_algorithm_run_algorithm_id", "algorithm_run", ["algorithm_id"])
    op.create_index("ix_algorithm_run_case_id", "algorithm_run", ["case_id"])
    op.create_index("ix_algorithm_run_tenant_id", "algorithm_run", ["tenant_id"])
    op.create_index("ix_algorithm_run_case_algo", "algorithm_run", ["case_id", "algorithm_id"])
    op.create_index("ix_algorithm_run_created", "algorithm_run", ["created_at"])

    # --- provenance_edge ---
    op.create_table(
        "provenance_edge",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("target_hash", sa.String(64), nullable=False),
        sa.Column("transformation", sa.String(100), nullable=False),
        sa.Column("algorithm_id", sa.String(100), nullable=False),
        sa.Column("algorithm_version", sa.String(20), nullable=False),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("algorithm_run.run_id"), nullable=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("legal_case.id"), nullable=True),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_provenance_edge_source", "provenance_edge", ["source_hash"])
    op.create_index("ix_provenance_edge_target", "provenance_edge", ["target_hash"])
    op.create_index("ix_provenance_edge_case", "provenance_edge", ["case_id"])

    # --- verification_report ---
    op.create_table(
        "verification_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("algorithm_run.run_id"), nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("legal_case.id"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_missing", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_error", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("all_passed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("report_json", sa.Text(), nullable=True),
        sa.Column("report_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_verification_report_run_id", "verification_report", ["run_id"])
    op.create_index("ix_verification_report_case", "verification_report", ["case_id"])

    # --- redaction_report ---
    op.create_table(
        "redaction_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("algorithm_run.run_id"), nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("legal_case.id"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("total_checked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_warning", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("report_json", sa.Text(), nullable=True),
        sa.Column("report_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_redaction_report_run_id", "redaction_report", ["run_id"])
    op.create_index("ix_redaction_report_case", "redaction_report", ["case_id"])


def downgrade():
    op.drop_table("redaction_report")
    op.drop_table("verification_report")
    op.drop_table("provenance_edge")
    op.drop_table("algorithm_run")
