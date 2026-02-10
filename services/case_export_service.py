"""
Case Export Service
===================
Generates court-ready ZIP packages for case materials.

Export packages include:
  - Original evidence files with SHA-256 verification
  - Derivative files (thumbnails, transcripts, etc.)
  - Event metadata (JSON)
  - Sync group data (JSON) — if any
  - Timeline data (JSON) — if generated
  - Evidence Integrity Statement (deterministic text + optional PDF)
  - Package manifest and integrity report

Exports are deterministic and reproducible from originals.
Each export is recorded as a CaseExportRecord.
"""

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from auth.models import db
from models.case_event import (
    CameraSyncGroup,
    CaseExportRecord,
    CaseTimelineEntry,
    Event,
)
from models.legal_case import LegalCase


class CaseExporter:
    """Generates court-ready ZIP export packages for cases."""

    def __init__(self, export_base_path='exports'):
        self._export_base = Path(export_base_path)
        self._export_base.mkdir(parents=True, exist_ok=True)
        self._store = self._load_evidence_store()

    @staticmethod
    def _load_evidence_store():
        try:
            from services.evidence_store import EvidenceStore
            return EvidenceStore()
        except Exception:
            return None

    def export_case(self, case_id, user_id=None):
        """Export all case materials to a court-ready ZIP package.

        The export includes an Evidence Integrity Statement generated
        deterministically from export metadata.  The statement's SHA-256
        is recorded in the manifest and in the audit stream.
        """
        case = db.session.get(LegalCase, case_id)
        if not case:
            return None

        evidence_items = case.evidence_items  # active items via property
        events = Event.query.filter_by(case_id=case_id).all()

        export_time = datetime.now(timezone.utc)
        timestamp = export_time.strftime('%Y%m%d_%H%M%S')
        zip_name = f'case_{case.case_number}_{timestamp}.zip'
        zip_path = self._export_base / zip_name

        file_manifest = []
        total_bytes = 0

        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            # --- Originals ---
            for item in evidence_items:
                total_bytes += self._pack_original(zf, item, file_manifest)
                total_bytes += self._pack_derivatives(zf, item, file_manifest)

            # --- Events JSON ---
            event_data = [self._serialize_event(e) for e in events]
            zf.writestr('events.json', json.dumps(event_data, indent=2))

            # --- Sync groups ---
            sync_groups = CameraSyncGroup.query.filter(
                CameraSyncGroup.event_id.in_([e.id for e in events]),
            ).all()
            if sync_groups:
                sg_data = [self._serialize_sync_group(sg) for sg in sync_groups]
                zf.writestr('sync_groups.json', json.dumps(sg_data, indent=2))

            # --- Timeline ---
            timeline = CaseTimelineEntry.query.filter_by(
                case_id=case_id,
            ).order_by(CaseTimelineEntry.timestamp).all()
            if timeline:
                tl_data = [self._serialize_timeline_entry(t) for t in timeline]
                zf.writestr('timeline.json', json.dumps(tl_data, indent=2))

            # --- Pre-manifest (without integrity statement entry) ---
            pre_manifest = {
                'case_number': case.case_number,
                'case_name': case.case_name,
                'exported_at': export_time.isoformat(),
                'evidence_count': len(evidence_items),
                'event_count': len(events),
                'files': list(file_manifest),
            }
            pre_manifest_sha256 = hashlib.sha256(
                json.dumps(pre_manifest, sort_keys=True).encode('utf-8'),
            ).hexdigest()

            # --- Evidence Integrity Statement ---
            stmt_result = self._generate_integrity_statement(
                case=case,
                manifest_sha256=pre_manifest_sha256,
                export_time=export_time,
            )

            # Write text statement (authoritative, deterministic)
            zf.writestr(
                'evidence_integrity_statement.txt',
                stmt_result.text_bytes,
            )
            file_manifest.append({
                'path': 'evidence_integrity_statement.txt',
                'sha256': stmt_result.text_sha256,
                'type': 'integrity_statement',
                'format': 'text',
            })
            total_bytes += len(stmt_result.text_bytes)

            # Write PDF statement if available (convenience derivative)
            if stmt_result.pdf_bytes is not None:
                zf.writestr(
                    'evidence_integrity_statement.pdf',
                    stmt_result.pdf_bytes,
                )
                file_manifest.append({
                    'path': 'evidence_integrity_statement.pdf',
                    'sha256': stmt_result.pdf_sha256,
                    'type': 'integrity_statement',
                    'format': 'pdf',
                })
                total_bytes += len(stmt_result.pdf_bytes)

            # --- Final manifest (includes integrity statement entries) ---
            manifest = {
                'case_number': case.case_number,
                'case_name': case.case_name,
                'exported_at': export_time.isoformat(),
                'evidence_count': len(evidence_items),
                'event_count': len(events),
                'files': file_manifest,
                'integrity_statement': {
                    'statement_id': stmt_result.statement_id,
                    'text_sha256': stmt_result.text_sha256,
                    'pdf_sha256': stmt_result.pdf_sha256,
                    'pre_manifest_sha256': pre_manifest_sha256,
                },
            }
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))

            # --- Integrity report ---
            integrity = self._compute_integrity(manifest, file_manifest, total_bytes)
            zf.writestr('integrity_report.json', json.dumps(integrity, indent=2))

        # Package hash
        pkg_sha256 = self._hash_file(zip_path)

        # Record export
        record = CaseExportRecord(
            case_id=case_id,
            export_type='full',
            included_event_ids=json.dumps([e.id for e in events]),
            included_evidence_ids=json.dumps([e.id for e in evidence_items]),
            file_count=len(file_manifest),
            total_bytes=total_bytes,
            package_sha256=pkg_sha256,
            export_path=str(zip_path),
            manifest_json=json.dumps(manifest),
            exported_by_id=user_id,
        )
        db.session.add(record)
        db.session.commit()

        self._audit_export(case_id, record, evidence_items, user_id,
                           stmt_result=stmt_result)

        return record

    # ------------------------------------------------------------------
    # Integrity Statement generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_integrity_statement(case, manifest_sha256, export_time):
        """Generate the Evidence Integrity Statement for this export.

        Uses an explicit timestamp and deterministic statement ID so
        that the text output is byte-reproducible from the same inputs.
        """
        from services.integrity_statement import IntegrityStatementGenerator

        gen = IntegrityStatementGenerator()
        statement_id = (
            f"IS-{case.case_number}-"
            f"{export_time.strftime('%Y%m%d%H%M%S')}"
        )
        return gen.generate(
            scope="CASE",
            scope_id=case.case_number,
            manifest_sha256=manifest_sha256,
            manifest_filename="manifest.json",
            generated_at=export_time,
            statement_id=statement_id,
            render_pdf=True,
        )

    # ------------------------------------------------------------------
    # Packaging helpers
    # ------------------------------------------------------------------

    def _pack_original(self, zf, item, manifest):
        """Pack original evidence file into ZIP; return bytes packed."""
        if not self._store or not item.hash_sha256:
            return 0
        orig_path = self._store.get_original_path(item.hash_sha256)
        if not orig_path or not Path(orig_path).exists():
            return 0
        arc_name = f'originals/{item.original_filename}'
        zf.write(str(orig_path), arc_name)
        size = Path(orig_path).stat().st_size
        manifest.append({
            'path': arc_name,
            'sha256': item.hash_sha256,
            'evidence_id': item.id,
            'type': 'original',
        })
        return size

    def _pack_derivatives(self, zf, item, manifest):
        """Pack derivative files for an evidence item; return bytes packed."""
        if not self._store or not item.evidence_store_id:
            return 0
        try:
            evidence_manifest = self._store.load_manifest(item.evidence_store_id)
        except Exception:
            return 0
        if not evidence_manifest or 'derivatives' not in evidence_manifest:
            return 0

        total = 0
        for deriv in evidence_manifest['derivatives']:
            try:
                d_path = self._store.get_derivative_path(
                    item.hash_sha256,
                    deriv.get('type', 'unknown'),
                    deriv.get('filename', ''),
                )
                if d_path and Path(d_path).exists():
                    arc_name = f"derivatives/{item.id}/{deriv.get('filename', 'unknown')}"
                    zf.write(str(d_path), arc_name)
                    size = Path(d_path).stat().st_size
                    manifest.append({
                        'path': arc_name,
                        'sha256': deriv.get('sha256', ''),
                        'evidence_id': item.id,
                        'type': 'derivative',
                    })
                    total += size
            except Exception:
                continue
        return total

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_event(event):
        links = event.evidence_links.all()
        return {
            'id': event.id,
            'event_name': event.event_name,
            'event_start': event.event_start.isoformat() if event.event_start else None,
            'event_end': event.event_end.isoformat() if event.event_end else None,
            'description': event.description,
            'evidence_links': [{
                'evidence_id': link.evidence_id,
                'sync_offset_ms': link.sync_offset_ms,
                'camera_label': link.camera_label,
            } for link in links],
        }

    @staticmethod
    def _serialize_sync_group(sg):
        return {
            'id': sg.id,
            'event_id': sg.event_id,
            'sync_label': sg.sync_label,
            'integrity_hash': sg.integrity_hash,
            'sync_method': sg.sync_method,
            'members': [{
                'evidence_id': m.evidence_id,
                'sync_offset_ms': m.sync_offset_ms,
                'camera_label': m.camera_label,
            } for m in sg.members],
        }

    @staticmethod
    def _serialize_timeline_entry(entry):
        return {
            'timestamp': entry.timestamp.isoformat(),
            'entry_type': entry.entry_type,
            'label': entry.label,
            'description': entry.description,
        }

    # ------------------------------------------------------------------
    # Integrity
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_integrity(manifest, file_manifest, total_bytes):
        file_hash = hashlib.sha256()
        for fi in sorted(file_manifest, key=lambda x: x['path']):
            if fi.get('sha256'):
                file_hash.update(fi['sha256'].encode('utf-8'))
        return {
            'manifest_hash': hashlib.sha256(
                json.dumps(manifest, sort_keys=True).encode('utf-8'),
            ).hexdigest(),
            'file_count': len(file_manifest),
            'total_bytes': total_bytes,
            'files_hash': file_hash.hexdigest(),
        }

    @staticmethod
    def _hash_file(path):
        sha = hashlib.sha256()
        with open(str(path), 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha.update(chunk)
        return sha.hexdigest()

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    @staticmethod
    def _audit_export(case_id, record, evidence_items, user_id,
                      stmt_result=None):
        try:
            from services.audit_stream import AuditStream
            audit = AuditStream()
            metadata = {
                'case_id': case_id,
                'export_id': record.id,
                'package_sha256': record.package_sha256,
            }
            if stmt_result is not None:
                metadata['integrity_statement_id'] = stmt_result.statement_id
                metadata['integrity_statement_text_sha256'] = stmt_result.text_sha256
                if stmt_result.pdf_sha256 is not None:
                    metadata['integrity_statement_pdf_sha256'] = stmt_result.pdf_sha256
            for item in evidence_items:
                audit.record(
                    action='EXPORT',
                    evidence_id=item.evidence_store_id,
                    metadata=metadata,
                    user_id=user_id,
                )
        except Exception:
            pass
