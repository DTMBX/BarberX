"""Phase 2 — Timeline, Export Records, and supporting indexes

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-10

Establishes:
  - case_timeline_entry table (derived views)
  - case_export_record table (export audit trail)
  - SHA-256 unique index on evidence_item

Reversible: Yes (drops tables and indexes).
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Case Timeline Entry ---
    op.create_table(
        'case_timeline_entry',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id')),
        sa.Column('evidence_id', sa.Integer(), sa.ForeignKey('evidence_item.id')),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('entry_type', sa.String(50), nullable=False, server_default='annotation'),
        sa.Column('label', sa.String(300), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('source', sa.String(200)),
        sa.Column('source_reference', sa.String(300)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id')),
    )
    op.create_index('ix_case_timeline_entry_case_id', 'case_timeline_entry', ['case_id'])
    op.create_index('ix_case_timeline_entry_event_id', 'case_timeline_entry', ['event_id'])
    op.create_index('ix_case_timeline_entry_timestamp', 'case_timeline_entry', ['timestamp'])

    # --- Case Export Record ---
    op.create_table(
        'case_export_record',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_id', sa.Integer(), sa.ForeignKey('legal_case.id'), nullable=False),
        sa.Column('export_type', sa.String(50), nullable=False, server_default='full'),
        sa.Column('included_event_ids', sa.Text()),
        sa.Column('included_evidence_ids', sa.Text()),
        sa.Column('file_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('package_sha256', sa.String(64)),
        sa.Column('export_path', sa.String(500)),
        sa.Column('manifest_json', sa.Text(), nullable=False),
        sa.Column('exported_at', sa.DateTime(), nullable=False),
        sa.Column('exported_by_id', sa.Integer(), sa.ForeignKey('users.id')),
    )
    op.create_index('ix_case_export_record_case_id', 'case_export_record', ['case_id'])
    op.create_index('ix_case_export_record_package_sha256', 'case_export_record', ['package_sha256'])

    # --- SHA-256 unique index on evidence_item ---
    # evidence_item is managed by db.create_all() (not by migrations).
    # Guard against the table not yet existing — it will be absent in
    # pure-migration-only environments (e.g. CI smoke tests that start
    # from a blank DB without calling db.create_all() first).
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'evidence_item' in inspector.get_table_names():
        existing = {idx['name'] for idx in inspector.get_indexes('evidence_item')}
        if 'ix_evidence_item_sha256_unique' not in existing:
            with op.batch_alter_table('evidence_item') as batch_op:
                batch_op.create_index(
                    'ix_evidence_item_sha256_unique',
                    ['hash_sha256'],
                    unique=True,
                )


def downgrade() -> None:
    # Guard: evidence_item may not exist in migration-only environments
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'evidence_item' in inspector.get_table_names():
        existing = {idx['name'] for idx in inspector.get_indexes('evidence_item')}
        if 'ix_evidence_item_sha256_unique' in existing:
            with op.batch_alter_table('evidence_item') as batch_op:
                batch_op.drop_index('ix_evidence_item_sha256_unique')
    op.drop_table('case_export_record')
    op.drop_table('case_timeline_entry')
