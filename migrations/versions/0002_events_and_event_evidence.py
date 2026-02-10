"""Phase 2 — Events and EventEvidence schema

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-10

Establishes:
  - events table (UUID string PK)
  - event_evidence association table (surrogate PK + unique constraint)
  - camera_sync_group table (integrity hashing)

Reversible: Yes (drops tables).
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Events ---
    op.create_table(
        'events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(100)),
        sa.Column('event_number', sa.String(100)),
        sa.Column('event_start', sa.DateTime()),
        sa.Column('event_end', sa.DateTime()),
        sa.Column('description', sa.Text()),
        sa.Column('location_description', sa.String(500)),
        sa.Column('location_address', sa.String(500)),
        sa.Column('latitude', sa.Float()),
        sa.Column('longitude', sa.Float()),
        sa.Column('is_sealed', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id')),
    )
    op.create_index('ix_events_case_id', 'events', ['case_id'])
    op.create_index('ix_events_event_number', 'events', ['event_number'])

    # --- Camera Sync Group ---
    op.create_table(
        'camera_sync_group',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('sync_label', sa.String(300), nullable=False),
        sa.Column('reference_evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=False),
        sa.Column('sync_method', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('sync_verified', sa.Boolean(), server_default='0'),
        sa.Column('sync_verified_by_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('sync_verified_at', sa.DateTime()),
        sa.Column('integrity_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id')),
    )
    op.create_index('ix_camera_sync_group_event_id', 'camera_sync_group', ['event_id'])
    op.create_index('ix_camera_sync_group_integrity_hash', 'camera_sync_group', ['integrity_hash'])

    # --- Event Evidence (many-to-many with sync metadata) ---
    op.create_table(
        'event_evidence',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id'), nullable=False),
        sa.Column('sync_offset_ms', sa.Integer()),
        sa.Column('camera_label', sa.String(200)),
        sa.Column('camera_position', sa.String(200)),
        sa.Column('is_sync_anchor', sa.Boolean(), server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('sync_group_id', sa.Integer(), sa.ForeignKey('camera_sync_group.id')),
        sa.Column('linked_at', sa.DateTime(), nullable=False),
        sa.Column('linked_by_user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.UniqueConstraint('event_id', 'evidence_id', name='uq_event_evidence'),
    )
    op.create_index('ix_event_evidence_event_id', 'event_evidence', ['event_id'])
    op.create_index('ix_event_evidence_evidence_id', 'event_evidence', ['evidence_id'])


def downgrade() -> None:
    op.drop_table('event_evidence')
    op.drop_table('camera_sync_group')
    op.drop_table('events')
