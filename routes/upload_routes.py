"""
Evident Media Upload & Processing Routes
Handles batch and single file uploads with forensic evidence pipeline.

Every upload is:
  1. Saved to a staging area.
  2. Ingested into the canonical evidence store (hashed, verified).
  3. Recorded in the database (EvidenceItem + ChainOfCustody).
  4. Processed for derivatives (thumbnails, proxies for video).
  5. Audit-logged at every step.
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from flask import (
    Blueprint, request, jsonify, render_template,
    current_app, send_file, flash, redirect, url_for
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

# Import media processing service
from services.media_processor import (
    get_media_processor,
    get_batch_processor,
    MediaValidator,
    ProcessingStatus,
    MediaType,
)

# Forensic evidence pipeline
from services.evidence_store import EvidenceStore, compute_file_hash
from services.audit_stream import AuditStream, AuditAction

logger = logging.getLogger(__name__)

# Create blueprint
upload_bp = Blueprint('upload', __name__, url_prefix='/upload')


# ============================================================================
# UPLOAD CONFIGURATION
# ============================================================================

UPLOAD_DIR = 'uploads'
ALLOWED_EXTENSIONS = (
    # Video formats
    'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv',
    # Audio formats
    'mp3', 'wav', 'flac', 'aac', 'wma', 'm4a',
    # Image formats
    'jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'tiff',
    # PDF
    'pdf',
    # Documents
    'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'rtf'
)

MAX_FILE_SIZE = 2500 * 1024 * 1024  # 2.5 GB for BWC video evidence

# Singleton evidence store (initialised at module level, root relative to CWD)
_evidence_store = EvidenceStore(root="evidence_store")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_user_upload_dir(user_id: int) -> Path:
    """Create user-specific upload directory"""
    user_dir = Path(UPLOAD_DIR) / f"user_{user_id}" / datetime.utcnow().strftime("%Y%m%d")
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def save_upload_metadata(file_id: str, user_id: int, metadata: dict):
    """Save upload metadata to JSON"""
    metadata_dir = Path(UPLOAD_DIR) / f"user_{user_id}" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_file = metadata_dir / f"{file_id}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def get_upload_metadata(file_id: str, user_id: int) -> dict:
    """Get upload metadata from JSON"""
    metadata_file = Path(UPLOAD_DIR) / f"user_{user_id}" / "metadata" / f"{file_id}.json"
    
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    return {}


# ============================================================================
# ROUTES: Single File Upload
# ============================================================================

@upload_bp.route('/single', methods=['GET', 'POST'])
@login_required
def upload_single():
    """Upload and process a single file through the forensic evidence pipeline."""

    if request.method == 'GET':
        return render_template('upload/single.html', user=current_user)

    # Handle POST request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({
            'error': f'File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB'
        }), 400

    # Validate with media validator
    is_valid, error_msg = MediaValidator.validate_file(file.filename, file_size)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    try:
        # 1. Save to staging area (temp dir, cleaned up after ingest)
        staging_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)

        filename = secure_filename(file.filename)
        staging_path = staging_dir / filename
        file.save(str(staging_path))

        # 2. Ingest into the forensic evidence store
        device_label = request.form.get('device_label')
        case_id = request.form.get('case_id', type=int)

        ingest_result = _evidence_store.ingest(
            source_path=str(staging_path),
            original_filename=file.filename,
            ingested_by=current_user.email,
            device_label=device_label,
        )

        if not ingest_result.success:
            return jsonify({
                'error': f'Ingest failed: {ingest_result.error}'
            }), 500

        # 3. Create or find database record (EvidenceItem)
        #    If same hash already exists, reuse the existing record.
        from auth.models import db
        from models.evidence import EvidenceItem, CaseEvidence

        media_type = MediaValidator.get_media_type(file.filename)
        evidence_type_map = {
            MediaType.VIDEO: 'video',
            MediaType.AUDIO: 'audio',
            MediaType.IMAGE: 'image',
            MediaType.PDF: 'document',
            MediaType.DOCUMENT: 'document',
        }

        existing_item = EvidenceItem.query.filter_by(hash_sha256=ingest_result.sha256).first()

        if existing_item and ingest_result.duplicate:
            # Reuse existing EvidenceItem — do not create a new one
            evidence_item = existing_item
        else:
            evidence_item = EvidenceItem(
                original_filename=file.filename,
                stored_filename=Path(ingest_result.stored_path).name,
                file_type=Path(file.filename).suffix.lstrip('.').lower(),
                file_size_bytes=ingest_result.metadata.size_bytes,
                mime_type=ingest_result.metadata.mime_type,
                evidence_type=evidence_type_map.get(media_type, 'other'),
                evidence_store_id=ingest_result.evidence_id,
                hash_sha256=ingest_result.sha256,
                processing_status='processing',
                uploaded_by_id=current_user.id,
                created_at=datetime.now(timezone.utc),
            )

            if device_label:
                evidence_item.media_category = 'body_worn_camera'
                evidence_item.device_label = device_label
                evidence_item.collected_by = device_label

            db.session.add(evidence_item)
            db.session.commit()

        # 3b. Link to case via CaseEvidence if case_id provided
        if case_id:
            existing_link = CaseEvidence.query.filter_by(
                case_id=case_id, evidence_id=evidence_item.id
            ).first()
            if not existing_link:
                link = CaseEvidence(
                    case_id=case_id,
                    evidence_id=evidence_item.id,
                    linked_by_id=current_user.id,
                    link_purpose='intake',
                )
                db.session.add(link)
                db.session.commit()

        # 4. Audit: ingest event
        audit = AuditStream(db.session, _evidence_store)
        audit.record(
            evidence_id=ingest_result.evidence_id,
            db_evidence_id=evidence_item.id,
            action=AuditAction.INGEST_DUPLICATE if ingest_result.duplicate else AuditAction.INGEST,
            actor_id=current_user.id,
            actor_name=current_user.email,
            details={
                'sha256': ingest_result.sha256,
                'size_bytes': ingest_result.metadata.size_bytes,
                'mime_type': ingest_result.metadata.mime_type,
                'device_label': device_label,
            },
            hash_after=ingest_result.sha256,
        )

        # 5. Process derivatives (video: metadata + thumbnails + proxy)
        derivatives_result = {}
        if media_type == MediaType.VIDEO:
            derivatives_result = _process_video_derivatives(
                ingest_result, evidence_item, audit
            )
        elif media_type == MediaType.AUDIO:
            audit.record(
                evidence_id=ingest_result.evidence_id,
                db_evidence_id=evidence_item.id,
                action=AuditAction.METADATA_EXTRACTED,
                actor_id=current_user.id,
                actor_name=current_user.email,
                details={'note': 'Audio processing pending'},
            )

        # 6. Mark processing complete
        evidence_item.processing_status = 'completed'
        db.session.commit()

        # 7. Clean up staging file
        if staging_path.exists():
            staging_path.unlink()

        # 8. Also save JSON metadata for backward compatibility
        save_upload_metadata(
            ingest_result.evidence_id,
            current_user.id,
            {
                'evidence_id': ingest_result.evidence_id,
                'file_id': ingest_result.evidence_id,
                'filename': file.filename,
                'sha256': ingest_result.sha256,
                'size_bytes': ingest_result.metadata.size_bytes,
                'mime_type': ingest_result.metadata.mime_type,
                'db_id': evidence_item.id,
                'user_id': current_user.id,
                'upload_path': ingest_result.stored_path,
                'duplicate': ingest_result.duplicate,
                'derivatives': derivatives_result,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            },
        )

        return jsonify({
            'success': True,
            'evidence_id': ingest_result.evidence_id,
            'file_id': ingest_result.evidence_id,
            'filename': file.filename,
            'sha256': ingest_result.sha256,
            'size_bytes': ingest_result.metadata.size_bytes,
            'mime_type': ingest_result.metadata.mime_type,
            'duplicate': ingest_result.duplicate,
            'db_id': evidence_item.id,
            'processing_status': evidence_item.processing_status,
            'derivatives': derivatives_result,
        }), 200

    except Exception as e:
        current_app.logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


def _process_video_derivatives(ingest_result, evidence_item, audit):
    """
    Generate video derivatives (metadata, thumbnails, proxy) and store them.

    Returns a summary dict of what was generated.
    """
    from auth.models import db
    from services.forensic_video_processor import ForensicVideoProcessor

    result_summary = {'metadata': None, 'thumbnails': [], 'proxy': None, 'errors': []}
    derivative_records = []  # Collect for manifest update

    try:
        vp = ForensicVideoProcessor()
    except RuntimeError as e:
        result_summary['errors'].append(str(e))
        return result_summary

    original_path = ingest_result.stored_path

    # Temporary output directory for derivatives before storing canonically
    import tempfile
    with tempfile.TemporaryDirectory(prefix="evident_video_") as tmp_dir:
        proc_result = vp.process_video(original_path, tmp_dir, generate_proxy=True)

        # Store metadata as a derivative (JSON)
        if proc_result.get('metadata'):
            meta_json_path = os.path.join(tmp_dir, "metadata.json")
            with open(meta_json_path, "w") as f:
                json.dump(proc_result['metadata'], f, indent=2, default=str)
            rec = _evidence_store.store_derivative(
                ingest_result.sha256, "metadata", meta_json_path, "metadata.json"
            )
            derivative_records.append(rec)
            result_summary['metadata'] = rec.sha256

            # Update DB with duration
            meta = proc_result['metadata']
            evidence_item.duration_seconds = int(meta.get('duration_seconds', 0))
            db.session.commit()

            audit.record(
                evidence_id=ingest_result.evidence_id,
                db_evidence_id=evidence_item.id,
                action=AuditAction.METADATA_EXTRACTED,
                actor_id=None,
                actor_name="system",
                details={
                    'duration_seconds': meta.get('duration_seconds'),
                    'resolution': meta.get('video_streams', [{}])[0].get('width', '?'),
                    'codec': meta.get('video_streams', [{}])[0].get('codec', '?'),
                },
            )

        # Store thumbnails
        for thumb_path in proc_result.get('thumbnails', []):
            thumb_name = Path(thumb_path).name
            rec = _evidence_store.store_derivative(
                ingest_result.sha256, "thumbnail", thumb_path, thumb_name
            )
            derivative_records.append(rec)
            result_summary['thumbnails'].append(rec.sha256)

            audit.record(
                evidence_id=ingest_result.evidence_id,
                db_evidence_id=evidence_item.id,
                action=AuditAction.THUMBNAIL_GENERATED,
                actor_id=None,
                actor_name="system",
                details={'filename': thumb_name, 'sha256': rec.sha256},
            )

        # Store proxy
        if proc_result.get('proxy'):
            proxy_path = proc_result['proxy']
            proxy_name = Path(proxy_path).name
            rec = _evidence_store.store_derivative(
                ingest_result.sha256, "proxy", proxy_path, proxy_name
            )
            derivative_records.append(rec)
            result_summary['proxy'] = rec.sha256

            audit.record(
                evidence_id=ingest_result.evidence_id,
                db_evidence_id=evidence_item.id,
                action=AuditAction.PROXY_GENERATED,
                actor_id=None,
                actor_name="system",
                details={
                    'filename': proxy_name,
                    'sha256': rec.sha256,
                    'size_bytes': rec.size_bytes,
                },
            )

        # Update manifest with all derivative records
        manifest = _evidence_store.load_manifest(ingest_result.evidence_id)
        if manifest:
            manifest.derivatives.extend(derivative_records)
            _evidence_store.save_manifest(manifest)

        result_summary['errors'] = proc_result.get('errors', [])

    return result_summary


# ============================================================================
# ROUTES: Batch Upload
# ============================================================================

@upload_bp.route('/batch', methods=['GET', 'POST'])
@login_required
def upload_batch():
    """Batch upload and process multiple files"""
    
    if request.method == 'GET':
        return render_template('upload/batch.html', user=current_user)
    
    # Handle POST request
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400
    
    if len(files) > 50:
        return jsonify({'error': 'Maximum 50 files per batch'}), 400
    
    try:
        # Create user upload directory
        user_dir = create_user_upload_dir(current_user.id)
        
        # Validate and save files
        saved_files = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: File type not allowed")
                continue
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: File too large")
                continue
            
            # Validate with media validator
            is_valid, error_msg = MediaValidator.validate_file(file.filename, file_size)
            if not is_valid:
                errors.append(f"{file.filename}: {error_msg}")
                continue
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
            saved_filename = timestamp + filename
            file_path = user_dir / saved_filename
            
            file.save(str(file_path))
            saved_files.append(str(file_path))
        
        if not saved_files:
            return jsonify({
                'error': 'No files could be saved',
                'details': errors
            }), 400
        
        # Process batch
        batch_processor = get_batch_processor(UPLOAD_DIR)
        batch_result = batch_processor.process_batch(saved_files)
        
        # Save batch metadata
        batch_metadata = {
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'user_id': current_user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'file_count': len(saved_files),
            'errors': errors,
            'results': batch_result['results'],
        }
        
        user_batch_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "batches"
        user_batch_dir.mkdir(parents=True, exist_ok=True)
        
        batch_file = user_batch_dir / f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_file, 'w') as f:
            json.dump(batch_metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'batch_summary': batch_processor.get_summary(),
            'results': batch_result['results'],
            'errors': errors,
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Batch upload error: {e}", exc_info=True)
        return jsonify({'error': f'Batch upload failed: {str(e)}'}), 500


# ============================================================================
# ROUTES: Upload Management
# ============================================================================

@upload_bp.route('/history', methods=['GET'])
@login_required
def upload_history():
    """Get user's upload history"""
    
    batch_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "batches"
    
    if not batch_dir.exists():
        return render_template('upload/history.html', 
                             user=current_user,
                             batches=[])
    
    # Load all batch metadata files
    batches = []
    for batch_file in sorted(batch_dir.glob('*.json'), reverse=True)[:20]:  # Last 20
        try:
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
                batches.append(batch_data)
        except Exception as e:
            current_app.logger.error(f"Error reading batch file {batch_file}: {e}")
    
    return render_template('upload/history.html', 
                         user=current_user,
                         batches=batches)


@upload_bp.route('/api/detail/<file_id>', methods=['GET'])
@login_required
def get_upload_detail(file_id: str):
    """Get detailed information about an upload"""
    
    try:
        metadata = get_upload_metadata(file_id, current_user.id)
        
        if not metadata:
            return jsonify({'error': 'Upload not found'}), 404
        
        return jsonify(metadata), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting upload detail: {e}")
        return jsonify({'error': 'Failed to retrieve details'}), 500


@upload_bp.route('/api/status/<file_id>', methods=['GET'])
@login_required
def get_upload_status(file_id: str):
    """Get processing status of an upload"""
    
    try:
        metadata = get_upload_metadata(file_id, current_user.id)
        
        if not metadata:
            return jsonify({'error': 'Upload not found'}), 404
        
        return jsonify({
            'file_id': file_id,
            'status': metadata.get('status', 'unknown'),
            'processing_time': metadata.get('processing_time', 0),
            'filename': metadata.get('filename'),
            'media_type': metadata.get('media_type'),
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting upload status: {e}")
        return jsonify({'error': 'Failed to get status'}), 500


@upload_bp.route('/api/delete/<file_id>', methods=['DELETE'])
@login_required
def delete_upload(file_id: str):
    """Delete an uploaded file"""
    
    try:
        metadata = get_upload_metadata(file_id, current_user.id)
        
        if not metadata:
            return jsonify({'error': 'Upload not found'}), 404
        
        # Delete the file
        file_path = Path(metadata.get('upload_path', ''))
        if file_path.exists():
            file_path.unlink()
        
        # Delete metadata
        metadata_file = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "metadata" / f"{file_id}.json"
        if metadata_file.exists():
            metadata_file.unlink()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting upload: {e}")
        return jsonify({'error': 'Failed to delete'}), 500


# ============================================================================
# ROUTES: Status & Statistics
# ============================================================================

@upload_bp.route('/api/stats', methods=['GET'])
@login_required
def get_upload_stats():
    """Get upload statistics for current user"""
    
    try:
        metadata_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "metadata"
        batch_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}" / "batches"
        
        # Count uploads
        upload_count = len(list(metadata_dir.glob('*.json'))) if metadata_dir.exists() else 0
        batch_count = len(list(batch_dir.glob('*.json'))) if batch_dir.exists() else 0
        
        # Calculate total size
        user_dir = Path(UPLOAD_DIR) / f"user_{current_user.id}"
        total_size = sum(f.stat().st_size for f in user_dir.rglob('*') if f.is_file())
        
        return jsonify({
            'total_uploads': upload_count,
            'total_batches': batch_count,
            'total_size_mb': total_size / (1024 * 1024),
            'quota_mb': 1000,  # Example: 1GB quota
            'quota_usage_percent': (total_size / (1024 * 1024)) / 1000 * 100,
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting upload stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500


# ============================================================================
# ROUTES: Evidence Integrity & Export
# ============================================================================

@upload_bp.route('/api/verify/<evidence_id>', methods=['GET'])
@login_required
def verify_evidence(evidence_id: str):
    """Verify the integrity of stored evidence by recomputing its hash."""
    from auth.models import db

    manifest = _evidence_store.load_manifest(evidence_id)
    if manifest is None:
        return jsonify({'error': 'Evidence not found'}), 404

    passed, message = _evidence_store.verify_original(manifest.ingest.sha256)

    audit = AuditStream(db.session, _evidence_store)
    audit.record(
        evidence_id=evidence_id,
        action=AuditAction.INTEGRITY_VERIFIED if passed else AuditAction.INTEGRITY_FAILED,
        actor_id=current_user.id,
        actor_name=current_user.email,
        details={'passed': passed, 'message': message},
    )

    return jsonify({
        'evidence_id': evidence_id,
        'integrity_passed': passed,
        'message': message,
        'sha256': manifest.ingest.sha256,
    }), 200 if passed else 409


@upload_bp.route('/api/export/<evidence_id>', methods=['POST'])
@login_required
def export_evidence(evidence_id: str):
    """Generate a court-ready evidence export package (ZIP)."""
    from services.evidence_export import EvidenceExporter
    from auth.models import db

    include_derivatives = request.json.get('include_derivatives', True) if request.is_json else True

    exporter = EvidenceExporter(_evidence_store, export_dir="exports")
    result = exporter.export(
        evidence_id=evidence_id,
        include_derivatives=include_derivatives,
        exported_by=current_user.email,
    )

    if not result.success:
        return jsonify({'error': result.error}), 500

    # Audit the export
    audit = AuditStream(db.session, _evidence_store)
    audit.record(
        evidence_id=evidence_id,
        action=AuditAction.EXPORTED,
        actor_id=current_user.id,
        actor_name=current_user.email,
        details={
            'package_sha256': result.package_sha256,
            'file_count': result.file_count,
            'total_bytes': result.total_bytes,
        },
    )

    return jsonify(result.to_dict()), 200


@upload_bp.route('/api/export/<evidence_id>/download', methods=['GET'])
@login_required
def download_export(evidence_id: str):
    """Download the most recent export package for evidence."""
    export_dir = Path("exports").resolve()
    if not export_dir.exists():
        return jsonify({'error': 'No exports available'}), 404

    # Find the most recent package for this evidence_id
    prefix = f"evidence_package_{evidence_id[:8]}_"
    candidates = sorted(
        [f for f in export_dir.glob(f"{prefix}*.zip")],
        reverse=True,
    )
    if not candidates:
        return jsonify({'error': 'No export package found for this evidence'}), 404

    return send_file(
        str(candidates[0]),
        mimetype='application/zip',
        as_attachment=True,
        download_name=candidates[0].name,
    )