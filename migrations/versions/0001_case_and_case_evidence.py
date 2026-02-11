"""Phase 2 — Case and CaseEvidence schema

Revision ID: 0001
Revises: None
Create Date: 2026-02-10

Establishes:
  - legal_case table (case management)
  - organization table
  - case_party table
  - case_evidence association table (many-to-many)
  - EvidenceItem.origin_case_id (nullable workflow metadata)

Reversible: Yes (drops tables).
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Organization ---
    op.create_table(
        'organization',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(300), nullable=False, unique=True),
        sa.Column('org_type', sa.String(50), nullable=False),
        sa.Column('address', sa.Text()),
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(200)),
        sa.Column('website', sa.String(300)),
        sa.Column('max_cases', sa.Integer(), server_default='-1'),
        sa.Column('max_users', sa.Integer(), server_default='-1'),
        sa.Column('storage_gb', sa.Integer(), server_default='1000'),
        sa.Column('can_process_video', sa.Boolean(), server_default='1'),
        sa.Column('can_process_audio', sa.Boolean(), server_default='1'),
        sa.Column('can_use_ai_analysis', sa.Boolean(), server_default='1'),
        sa.Column('can_redact', sa.Boolean(), server_default='1'),
        sa.Column('created_at', sa.DateTime()),
    )

    # --- Legal Case ---
    op.create_table(
        'legal_case',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_number', sa.String(100), nullable=False, unique=True),
        sa.Column('case_name', sa.String(500), nullable=False),
        sa.Column('case_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('jurisdiction', sa.String(200)),
        sa.Column('court_name', sa.String(300)),
        sa.Column('judge_name', sa.String(200)),
        # Jurisdiction metadata (Phase 2)
        sa.Column('jurisdiction_state', sa.String(2)),
        sa.Column('jurisdiction_agency_type', sa.String(100)),
        sa.Column('retention_policy_ref', sa.String(500)),
        sa.Column('incident_number', sa.String(200)),
        sa.Column('incident_date', sa.DateTime()),
        # Dates
        sa.Column('filed_date', sa.DateTime()),
        sa.Column('discovery_deadline', sa.DateTime()),
        sa.Column('trial_date', sa.DateTime()),
        # Status
        sa.Column('status', sa.String(50), server_default='open'),
        sa.Column('is_legal_hold', sa.Boolean(), server_default='0'),
        sa.Column('legal_hold_date', sa.DateTime()),
        # Access
        sa.Column('lead_attorney_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organization.id')),
        # Audit
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id')),
    )
    op.create_index('ix_legal_case_case_number', 'legal_case', ['case_number'])
    op.create_index('ix_legal_case_incident_number', 'legal_case', ['incident_number'])
    op.create_index('ix_legal_case_created_at', 'legal_case', ['created_at'])

    # --- Case Party ---
    op.create_table(
        'case_party',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('party_type', sa.String(50)),
        sa.Column('role', sa.String(200)),
        sa.Column('contact_info', sa.String(300)),
        sa.Column('email', sa.String(200)),
        sa.Column('phone', sa.String(20)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    # --- Case Evidence (many-to-many) ---
    op.create_table(
        'case_evidence',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=False),
        sa.Column('linked_at', sa.DateTime(), nullable=False),
        sa.Column('linked_by_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('link_purpose', sa.String(50), server_default='intake'),
        sa.Column('unlinked_at', sa.DateTime()),
        sa.Column('unlinked_by_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.UniqueConstraint('case_id', 'evidence_id', name='uq_case_evidence'),
    )
    op.create_index('ix_case_evidence_case_id', 'case_evidence', ['case_id'])
    op.create_index('ix_case_evidence_evidence_id', 'case_evidence', ['evidence_id'])


def downgrade() -> None:
    op.drop_table('case_evidence')
    op.drop_table('case_party')
    op.drop_table('legal_case')
    op.drop_table('organization')
