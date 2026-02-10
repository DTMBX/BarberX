"""
Case-Event API Routes
=====================
Ten endpoints for event management, evidence linking, sync groups,
timeline generation, and case export.

Blueprint: case_event_bp  (url_prefix: /api/case-events)

All routes assume a forensic context:
  - Events are factual; no inference of fault or intent.
  - Sync offsets are metadata only — evidence is never altered.
  - Exports are deterministic and reproducible.
"""

from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, render_template, request, send_file
from flask_login import login_required, current_user

from auth.models import db
from models.case_event import (
    CameraSyncGroup,
    CaseExportRecord,
    CaseTimelineEntry,
    Event,
    EventEvidence,
)
from services.event_sync_service import EventSyncService


case_event_bp = Blueprint('case_event', __name__, url_prefix='/api/case-events')
sync_service = EventSyncService()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _parse_datetime(value):
    """Parse ISO-8601 datetime string; return None on failure."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _serialize_event(event):
    """Serialize an Event to a JSON-safe dict."""
    return {
        'id': event.id,
        'case_id': event.case_id,
        'event_name': event.event_name,
        'event_type': event.event_type,
        'event_number': event.event_number,
        'event_start': event.event_start.isoformat() if event.event_start else None,
        'event_end': event.event_end.isoformat() if event.event_end else None,
        'description': event.description,
        'location_description': event.location_description,
        'location_address': event.location_address,
        'latitude': event.latitude,
        'longitude': event.longitude,
        'evidence_count': event.evidence_links.count(),
        'created_at': event.created_at.isoformat() if event.created_at else None,
    }


# ------------------------------------------------------------------
# 1. List events for a case
# ------------------------------------------------------------------

@case_event_bp.route('/cases/<int:case_id>/events', methods=['GET'])
@login_required
def list_events(case_id):
    events = Event.query.filter_by(case_id=case_id).order_by(
        Event.event_start,
    ).all()
    return jsonify([_serialize_event(e) for e in events])


# ------------------------------------------------------------------
# 2. Create event
# ------------------------------------------------------------------

@case_event_bp.route('/cases/<int:case_id>/events', methods=['POST'])
@login_required
def create_event(case_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    result = sync_service.create_event(
        case_id=case_id,
        event_name=data.get('event_name', ''),
        event_type=data.get('event_type'),
        event_number=data.get('event_number'),
        event_start=_parse_datetime(data.get('event_start')),
        event_end=_parse_datetime(data.get('event_end')),
        description=data.get('description'),
        location_description=data.get('location_description'),
        location_address=data.get('location_address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        created_by_user_id=current_user.id,
    )
    if not result.success:
        return jsonify({'error': result.error}), 400

    return jsonify(_serialize_event(result.data)), 201


# ------------------------------------------------------------------
# 3. Get event detail
# ------------------------------------------------------------------

@case_event_bp.route('/events/<event_id>', methods=['GET'])
@login_required
def get_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    links = event.evidence_links.all()
    evidence_data = [{
        'evidence_id': link.evidence_id,
        'sync_offset_ms': link.sync_offset_ms,
        'camera_label': link.camera_label,
        'is_sync_anchor': link.is_sync_anchor,
        'linked_at': link.linked_at.isoformat() if link.linked_at else None,
    } for link in links]

    resp = _serialize_event(event)
    resp['evidence'] = evidence_data
    return jsonify(resp)


# ------------------------------------------------------------------
# 4. Link evidence to event
# ------------------------------------------------------------------

@case_event_bp.route('/events/<event_id>/evidence', methods=['POST'])
@login_required
def link_evidence(event_id):
    data = request.get_json()
    if not data or 'evidence_id' not in data:
        return jsonify({'error': 'evidence_id is required'}), 400

    result = sync_service.link_evidence_to_event(
        event_id=event_id,
        evidence_id=data['evidence_id'],
        sync_offset_ms=data.get('sync_offset_ms'),
        camera_label=data.get('camera_label'),
        linked_by_user_id=current_user.id,
    )
    if not result.success:
        return jsonify({'error': result.error}), 400

    link = result.data
    return jsonify({
        'event_id': link.event_id,
        'evidence_id': link.evidence_id,
        'sync_offset_ms': link.sync_offset_ms,
        'linked_at': link.linked_at.isoformat() if link.linked_at else None,
    }), 201


# ------------------------------------------------------------------
# 5. Unlink evidence from event
# ------------------------------------------------------------------

@case_event_bp.route(
    '/events/<event_id>/evidence/<int:evidence_id>', methods=['DELETE'],
)
@login_required
def unlink_evidence(event_id, evidence_id):
    result = sync_service.unlink_evidence_from_event(event_id, evidence_id)
    if not result.success:
        return jsonify({'error': result.error}), 404
    return jsonify(result.data)


# ------------------------------------------------------------------
# 6. Create sync group
# ------------------------------------------------------------------

@case_event_bp.route('/events/<event_id>/sync-groups', methods=['POST'])
@login_required
def create_sync_group(event_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    evidence_ids = data.get('evidence_ids', [])
    offsets_ms = data.get('offsets_ms', {})
    # Normalize offset keys to int (JSON keys are always strings)
    offsets_ms = {int(k): v for k, v in offsets_ms.items()}

    result = sync_service.create_sync_group(
        event_id=event_id,
        evidence_ids=evidence_ids,
        offsets_ms=offsets_ms,
        reference_evidence_id=data.get('reference_evidence_id'),
        sync_label=data.get('sync_label', 'Untitled Sync Group'),
        sync_method=data.get('sync_method', 'manual'),
        created_by_user_id=current_user.id,
    )
    if not result.success:
        return jsonify({'error': result.error}), 400

    group = result.data
    return jsonify({
        'id': group.id,
        'event_id': group.event_id,
        'sync_label': group.sync_label,
        'integrity_hash': group.integrity_hash,
        'sync_method': group.sync_method,
    }), 201


# ------------------------------------------------------------------
# 7. Verify sync group
# ------------------------------------------------------------------

@case_event_bp.route('/sync-groups/<int:group_id>/verify', methods=['GET'])
@login_required
def verify_sync_group(group_id):
    result = sync_service.verify_sync_group(group_id)
    if not result.success:
        return jsonify({'error': result.error}), 404
    return jsonify(result.data)


# ------------------------------------------------------------------
# 8. Case timeline
# ------------------------------------------------------------------

@case_event_bp.route('/cases/<int:case_id>/timeline', methods=['GET'])
@login_required
def get_case_timeline(case_id):
    entries = sync_service.generate_case_timeline(case_id)
    return jsonify([{
        'timestamp': e.timestamp.isoformat(),
        'entry_type': e.entry_type,
        'label': e.label,
        'description': e.description,
        'event_id': e.event_id,
        'evidence_id': e.evidence_id,
        'source': e.source,
    } for e in entries])


# ------------------------------------------------------------------
# 9. Export case
# ------------------------------------------------------------------

@case_event_bp.route('/cases/<int:case_id>/export', methods=['POST'])
@login_required
def export_case(case_id):
    try:
        from services.case_export_service import CaseExporter
        exporter = CaseExporter()
        record = exporter.export_case(case_id, user_id=current_user.id)
        if not record:
            return jsonify({'error': 'Case not found'}), 404
        return jsonify({
            'export_id': record.id,
            'package_sha256': record.package_sha256,
            'file_count': record.file_count,
            'total_bytes': record.total_bytes,
            'export_path': record.export_path,
            'exported_at': record.exported_at.isoformat(),
        }), 201
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ------------------------------------------------------------------
# 10. List case exports
# ------------------------------------------------------------------

@case_event_bp.route('/cases/<int:case_id>/exports', methods=['GET'])
@login_required
def list_case_exports(case_id):
    records = CaseExportRecord.query.filter_by(
        case_id=case_id,
    ).order_by(CaseExportRecord.exported_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'export_type': r.export_type,
        'file_count': r.file_count,
        'total_bytes': r.total_bytes,
        'package_sha256': r.package_sha256,
        'exported_at': r.exported_at.isoformat() if r.exported_at else None,
    } for r in records])


# ------------------------------------------------------------------
# 11. Event alignment timeline (JSON)
# ------------------------------------------------------------------

@case_event_bp.route('/events/<event_id>/alignment-timeline', methods=['GET'])
@login_required
def get_alignment_timeline(event_id):
    """
    Build and return the canonical alignment timeline for an event.

    The response is a deterministic JSON structure.  Its SHA-256 hash is
    recorded in the audit log on every generation.
    """
    from services.event_timeline import EventTimelineBuilder

    builder = EventTimelineBuilder()
    result = builder.build(event_id, user_id=current_user.id)

    if not result.success:
        return jsonify({'error': result.error}), 404

    return jsonify(result.timeline)


# ------------------------------------------------------------------
# 12. Event alignment viewer (HTML page)
# ------------------------------------------------------------------

@case_event_bp.route('/events/<event_id>/viewer', methods=['GET'])
@login_required
def event_viewer(event_id):
    """Render the timeline alignment viewer for an event."""
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    return render_template(
        'cases/event_timeline_viewer.html',
        event=event,
        user=current_user,
    )


# ------------------------------------------------------------------
# 13. Serve evidence proxy for viewer playback
# ------------------------------------------------------------------

@case_event_bp.route('/evidence/<int:evidence_id>/proxy', methods=['GET'])
@login_required
def serve_evidence_proxy(evidence_id):
    """
    Serve the low-resolution proxy video for in-browser playback.

    Falls back to the original if no proxy exists.
    This endpoint does NOT modify any evidence files.
    """
    from models.evidence import EvidenceItem
    from services.evidence_store import EvidenceStore

    evidence = db.session.get(EvidenceItem, evidence_id)
    if not evidence:
        return jsonify({'error': 'Evidence not found'}), 404

    store = EvidenceStore()

    # Try proxy first
    if evidence.evidence_store_id:
        manifest = store.load_manifest(evidence.evidence_store_id)
        if manifest:
            for deriv in manifest.derivatives:
                if deriv.derivative_type == 'proxy':
                    proxy_path = store.get_derivative_path(
                        evidence.hash_sha256,
                        'proxy',
                        deriv.filename,
                    )
                    if proxy_path and Path(proxy_path).exists():
                        return send_file(
                            proxy_path,
                            mimetype=evidence.mime_type or 'video/mp4',
                        )

    # Fallback to original
    if evidence.hash_sha256:
        original_path = store.get_original_path(evidence.hash_sha256)
        if original_path and Path(original_path).exists():
            return send_file(
                original_path,
                mimetype=evidence.mime_type or 'application/octet-stream',
            )

    return jsonify({'error': 'No playable file found'}), 404
