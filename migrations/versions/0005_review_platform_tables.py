"""Phase 10 — Review platform tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-10

Establishes:
  - review_decision table (append-only coding decisions)
  - review_annotation table (non-destructive sticky notes)
  - saved_search table (persisted search queries)
  - review_audit_event table (fine-grained review action log)

Reversible: Yes (drops tables).
"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ReviewDecision ---
    op.create_table(
        'review_decision',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=False),
        sa.Column('review_code', sa.String(50), nullable=False),
        sa.Column('confidence', sa.String(20), server_default='confirmed'),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reviewer_note', sa.Text()),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('superseded_by_id', sa.Integer(), sa.ForeignKey('review_decision.id'), nullable=True),
        sa.Column('batch_action_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_review_decision_case_id', 'review_decision', ['case_id'])
    op.create_index('ix_review_decision_evidence_id', 'review_decision', ['evidence_id'])
    op.create_index('ix_review_decision_reviewer_id', 'review_decision', ['reviewer_id'])
    op.create_index('ix_review_decision_is_current', 'review_decision', ['is_current'])
    op.create_index('ix_review_decision_batch_action_id', 'review_decision', ['batch_action_id'])
    op.create_index('ix_review_decision_created_at', 'review_decision', ['created_at'])
    op.create_index('ix_review_decision_lookup', 'review_decision', ['case_id', 'evidence_id', 'is_current'])

    # --- ReviewAnnotation ---
    op.create_table(
        'review_annotation',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('annotation_type', sa.String(30), server_default='note'),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('x_position', sa.Float(), nullable=True),
        sa.Column('y_position', sa.Float(), nullable=True),
        sa.Column('color', sa.String(7), server_default='#fbbf24'),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_review_annotation_case_id', 'review_annotation', ['case_id'])
    op.create_index('ix_review_annotation_evidence_id', 'review_annotation', ['evidence_id'])
    op.create_index('ix_review_annotation_author_id', 'review_annotation', ['author_id'])
    op.create_index('ix_review_annotation_lookup', 'review_annotation', ['case_id', 'evidence_id'])

    # --- SavedSearch ---
    op.create_table(
        'saved_search',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('query_text', sa.String(500), nullable=True),
        sa.Column('filters_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_saved_search_case_id', 'saved_search', ['case_id'])
    op.create_index('ix_saved_search_user_id', 'saved_search', ['user_id'])

    # --- ReviewAuditEvent ---
    op.create_table(
        'review_audit_event',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=True),
        sa.Column('action', sa.String(80), nullable=False),
        sa.Column('actor_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_review_audit_event_case_id', 'review_audit_event', ['case_id'])
    op.create_index('ix_review_audit_event_evidence_id', 'review_audit_event', ['evidence_id'])
    op.create_index('ix_review_audit_event_created_at', 'review_audit_event', ['created_at'])


def downgrade() -> None:
    op.drop_table('review_audit_event')
    op.drop_table('saved_search')
    op.drop_table('review_annotation')
    op.drop_table('review_decision')
