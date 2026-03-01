"""Add projects, evidence_artifacts, chat_messages, courtlistener_cache, issues
tables; add project_id + task_type columns to existing tables.

Revision ID: 0003_extended_models
Revises: 0002_forensic_hardening
Create Date: 2026-02-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0003_extended_models"
down_revision: Union[str, None] = "0002_forensic_hardening"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── projects ─────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ── cases.project_id FK ──────────────────────────────────────────
    op.add_column("cases", sa.Column("project_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_cases_project_id",
        "cases",
        "projects",
        ["project_id"],
        ["id"],
    )

    # ── jobs.task_type + jobs.error_detail ───────────────────────────
    op.add_column("jobs", sa.Column("task_type", sa.String(64), nullable=True))
    op.add_column("jobs", sa.Column("error_detail", sa.Text, nullable=True))

    # ── evidence_artifacts ───────────────────────────────────────────
    op.create_table(
        "evidence_artifacts",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("evidence_id", UUID(as_uuid=True), sa.ForeignKey("evidence_files.id"), nullable=False),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("minio_object_key", sa.String(1024), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=True),
        sa.Column("content_preview", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_artifacts_case_id", "evidence_artifacts", ["case_id"])
    op.create_index("ix_artifacts_evidence_id", "evidence_artifacts", ["evidence_id"])

    # ── chat_messages ────────────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("scope", sa.String(32), nullable=False, server_default="global"),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("citations", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column("verification_status", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_chat_scope_case", "chat_messages", ["scope", "case_id"])

    # ── courtlistener_cache ──────────────────────────────────────────
    op.create_table(
        "courtlistener_cache",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("query_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("query_text", sa.Text, nullable=False),
        sa.Column("result_json", JSONB, nullable=False),
        sa.Column("result_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ── issues ───────────────────────────────────────────────────────
    op.create_table(
        "issues",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("narrative", sa.Text, nullable=False),
        sa.Column("jurisdiction", sa.String(128), nullable=True),
        sa.Column("code_reference", sa.String(512), nullable=True),
        sa.Column("courtlistener_cites", JSONB, nullable=True),
        sa.Column("supporting_sources", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("confidence", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("created_by", sa.String(256), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_issues_case_id", "issues", ["case_id"])


def downgrade() -> None:
    op.drop_table("issues")
    op.drop_table("courtlistener_cache")
    op.drop_table("chat_messages")
    op.drop_index("ix_artifacts_evidence_id", table_name="evidence_artifacts")
    op.drop_index("ix_artifacts_case_id", table_name="evidence_artifacts")
    op.drop_table("evidence_artifacts")
    op.drop_column("jobs", "error_detail")
    op.drop_column("jobs", "task_type")
    op.drop_constraint("fk_cases_project_id", "cases", type_="foreignkey")
    op.drop_column("cases", "project_id")
    op.drop_table("projects")
