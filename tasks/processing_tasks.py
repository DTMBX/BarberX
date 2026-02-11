"""
Processing Tasks — Celery + Synchronous Evidence Processing
=============================================================
Orchestrates evidence processing through the database task lifecycle.

Each public function:
  1. Creates a DocumentProcessingTask record (status='processing').
  2. Resolves the evidence file path from EvidenceStore.
  3. Invokes the appropriate processor from evidence_processor.
  4. Stores results in ContentExtractionIndex / OCRResult / ForensicVideoMetadata.
  5. Updates the task record (status='completed' or 'failed').
  6. Appends an audit entry to the evidence manifest.

These functions can be called directly (sync mode) or dispatched via Celery.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync-compatible task wrapper
# ---------------------------------------------------------------------------


def _get_flask_app():
    """Import and return the Flask app for DB context."""
    from app_config import create_app
    return create_app()


def process_evidence_sync(evidence_id: int, user_id: int, generate_proxy: bool = False) -> Dict:
    """
    Process a single evidence item synchronously.

    This is the core orchestration function. It:
      - Looks up the EvidenceItem by ID
      - Resolves the file on disk via EvidenceStore
      - Detects file type and dispatches to the appropriate processor
      - Stores extracted text / metadata in the database
      - Returns a summary dict

    Args:
        evidence_id: Database ID of the EvidenceItem.
        user_id: Database ID of the requesting user.
        generate_proxy: Whether to generate proxy video (default False).

    Returns:
        Dict with keys: success, task_id, task_type, summary, error
    """
    app = _get_flask_app()

    with app.app_context():
        from auth.models import db, User
        from models.document_processing import DocumentProcessingTask, ContentExtractionIndex, OCRResult
        from models.evidence import EvidenceItem, ChainOfCustody
        from services.evidence_store import EvidenceStore
        from services.evidence_processor import (
            process_evidence_file,
            process_video_evidence,
            detect_file_type,
            extract_entities,
        )

        # 1. Look up evidence
        evidence = EvidenceItem.query.get(evidence_id)
        if not evidence:
            return {"success": False, "error": f"Evidence ID {evidence_id} not found"}

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": f"User ID {user_id} not found"}

        # 2. Resolve file path
        store = EvidenceStore()
        sha256 = evidence.hash_sha256
        if not sha256:
            return {"success": False, "error": "Evidence has no SHA-256 hash"}

        file_path = store.get_original_path(sha256)
        if not file_path:
            return {"success": False, "error": f"Original file not found for hash {sha256[:16]}..."}

        # 3. Detect file type
        file_type = detect_file_type(file_path, evidence.original_filename or "")

        # Determine task type mapping
        task_type_map = {
            "pdf": "ocr",
            "image": "ocr",
            "video": "video_metadata",
            "audio": "audio_metadata",
            "docx": "text_extraction",
            "plaintext": "text_extraction",
        }
        task_type = task_type_map.get(file_type, "unknown")

        if file_type == "unsupported":
            return {
                "success": False,
                "error": f"Unsupported file type for {evidence.original_filename}",
                "task_type": "skipped",
            }

        # Determine case_id from first linked case or origin_case_id
        case_id = evidence.origin_case_id
        if not case_id and evidence.case_evidence_links:
            active_links = [l for l in evidence.case_evidence_links if l.is_active]
            if active_links:
                case_id = active_links[0].case_id

        if not case_id:
            return {"success": False, "error": "Evidence is not linked to any case"}

        # 4. Create processing task
        task = DocumentProcessingTask(
            evidence_id=evidence_id,
            case_id=case_id,
            task_type=task_type,
            task_uuid=__import__("uuid").uuid4().hex,
            status="processing",
            started_at=datetime.now(timezone.utc),
            requested_by_id=user_id,
        )
        db.session.add(task)
        db.session.commit()

        start_time = time.time()

        try:
            # 5. Process based on file type
            if file_type == "video":
                vresult = process_video_evidence(
                    file_path=file_path,
                    evidence_store=store,
                    original_sha256=sha256,
                    generate_proxy=generate_proxy,
                )

                if not vresult.success:
                    raise RuntimeError(vresult.error_message or "Video processing failed")

                # Store video metadata in evidence item
                evidence.duration_seconds = int(vresult.metadata.get("duration_seconds", 0))
                evidence.processing_status = "completed"

                # Create content index for video metadata (searchable)
                meta_text = json.dumps(vresult.metadata, indent=2)
                _store_content_index(
                    db=db,
                    evidence_id=evidence_id,
                    case_id=case_id,
                    content_type="video_metadata",
                    full_text=meta_text,
                    word_count=0,
                    character_count=len(meta_text),
                    metadata=vresult.metadata,
                )

                summary = {
                    "duration_seconds": evidence.duration_seconds,
                    "thumbnail": vresult.thumbnail_path is not None,
                    "proxy": vresult.proxy_path is not None,
                    "resolution": vresult.metadata.get("video", {}).get("width", 0),
                }

            else:
                # Text-bearing file types
                result = process_evidence_file(
                    file_path=file_path,
                    original_filename=evidence.original_filename or "",
                    evidence_store=store,
                    original_sha256=sha256,
                )

                if not result.success:
                    raise RuntimeError(result.error_message or "Processing failed")

                # Store extracted text on evidence item
                if result.full_text:
                    evidence.text_content = result.full_text
                    evidence.processing_status = "completed"
                    if result.task_type in ("pdf_ocr", "image_ocr"):
                        evidence.has_ocr = True

                # Store in ContentExtractionIndex
                _store_content_index(
                    db=db,
                    evidence_id=evidence_id,
                    case_id=case_id,
                    content_type=result.task_type,
                    full_text=result.full_text,
                    word_count=result.word_count,
                    character_count=result.character_count,
                    page_count=result.page_count,
                    emails=result.email_addresses,
                    phones=result.phone_numbers,
                    metadata=result.metadata,
                )

                # Store OCR result if applicable
                if result.task_type in ("pdf_ocr", "image_ocr"):
                    _store_ocr_result(
                        db=db,
                        evidence_id=evidence_id,
                        task_id=task.id,
                        text=result.full_text or "",
                        page_count=result.page_count,
                        confidence=result.metadata.get("average_confidence"),
                    )

                summary = {
                    "task_type": result.task_type,
                    "word_count": result.word_count,
                    "character_count": result.character_count,
                    "page_count": result.page_count,
                    "emails_found": len(result.email_addresses),
                    "phones_found": len(result.phone_numbers),
                }

            # 6. Mark task completed
            elapsed = time.time() - start_time
            task.status = "completed"
            task.completed_at = datetime.now(timezone.utc)
            task.processing_time_seconds = int(elapsed)
            task.processing_engine = result.metadata.get("processing_engine", "evident") if file_type != "video" else "ffprobe+ffmpeg"
            db.session.commit()

            # 7. Audit log
            store.append_audit(
                evidence_id=evidence.evidence_store_id or sha256[:36],
                action="processed",
                actor=user.username if hasattr(user, 'username') else str(user_id),
                details={
                    "task_type": task_type,
                    "task_id": task.id,
                    "processing_seconds": round(elapsed, 2),
                },
            )

            # 8. Chain of custody entry
            coc = ChainOfCustody(
                evidence_id=evidence_id,
                action="processed",
                actor_id=user_id,
                actor_name=user.username if hasattr(user, 'username') else str(user_id),
                action_details=json.dumps({
                    "task_type": task_type,
                    "task_id": task.id,
                }),
                hash_before=sha256,
                hash_after=sha256,  # Originals are never modified
            )
            db.session.add(coc)
            db.session.commit()

            return {
                "success": True,
                "task_id": task.id,
                "task_uuid": task.task_uuid,
                "task_type": task_type,
                "summary": summary,
                "processing_seconds": round(elapsed, 2),
            }

        except Exception as exc:
            elapsed = time.time() - start_time
            logger.error(
                "Processing failed for evidence %d: %s", evidence_id, exc, exc_info=True
            )

            task.status = "failed"
            task.completed_at = datetime.now(timezone.utc)
            task.processing_time_seconds = int(elapsed)
            task.error_message = str(exc)
            evidence.processing_status = "failed"
            db.session.commit()

            return {
                "success": False,
                "task_id": task.id,
                "task_uuid": task.task_uuid,
                "task_type": task_type,
                "error": str(exc),
                "processing_seconds": round(elapsed, 2),
            }


def process_case_batch(case_id: int, user_id: int) -> Dict:
    """
    Process all unprocessed evidence items in a case.

    Returns a summary dict with total, completed, failed counts.
    """
    app = _get_flask_app()

    with app.app_context():
        from auth.models import db
        from models.evidence import EvidenceItem, CaseEvidence
        from models.document_processing import BatchProcessingQueue
        from uuid import uuid4

        # Find all active evidence links for this case
        links = CaseEvidence.query.filter_by(case_id=case_id).filter(
            CaseEvidence.unlinked_at.is_(None)
        ).all()

        evidence_ids = [link.evidence_id for link in links]

        # Filter to only unprocessed items
        items = EvidenceItem.query.filter(
            EvidenceItem.id.in_(evidence_ids),
            EvidenceItem.processing_status.in_(["pending", "failed"]),
        ).all()

        if not items:
            return {
                "success": True,
                "total": 0,
                "completed": 0,
                "failed": 0,
                "message": "No unprocessed evidence items found",
            }

        # Create batch record
        batch = BatchProcessingQueue(
            case_id=case_id,
            batch_name=f"Case {case_id} batch processing",
            batch_uuid=uuid4().hex,
            processing_type="full_extraction",
            document_count=len(items),
            status="processing",
            started_at=datetime.now(timezone.utc),
            created_by_id=user_id,
        )
        db.session.add(batch)
        db.session.commit()

        completed = 0
        failed = 0

        for item in items:
            result = process_evidence_sync(item.id, user_id)
            if result.get("success"):
                completed += 1
            else:
                failed += 1

            # Update batch progress
            batch.successful_count = completed
            batch.failed_count = failed
            total_done = completed + failed
            batch.progress_percentage = int((total_done / len(items)) * 100)
            db.session.commit()

        # Mark batch complete
        batch.status = "completed"
        batch.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        return {
            "success": True,
            "batch_id": batch.id,
            "batch_uuid": batch.batch_uuid,
            "total": len(items),
            "completed": completed,
            "failed": failed,
        }


# ---------------------------------------------------------------------------
# Celery task wrappers (only registered if Celery is available)
# ---------------------------------------------------------------------------


try:
    from celery_app import celery_app, is_async

    if celery_app is not None:

        @celery_app.task(name="evident.process_evidence", bind=True, max_retries=2)
        def process_evidence_task(self, evidence_id: int, user_id: int, generate_proxy: bool = False):
            """Celery task wrapper for process_evidence_sync."""
            try:
                return process_evidence_sync(evidence_id, user_id, generate_proxy)
            except Exception as exc:
                logger.error("Celery task failed for evidence %d: %s", evidence_id, exc)
                raise self.retry(exc=exc, countdown=30)

        @celery_app.task(name="evident.process_case_batch", bind=True, max_retries=1)
        def process_case_batch_task(self, case_id: int, user_id: int):
            """Celery task wrapper for process_case_batch."""
            try:
                return process_case_batch(case_id, user_id)
            except Exception as exc:
                logger.error("Celery batch task failed for case %d: %s", case_id, exc)
                raise self.retry(exc=exc, countdown=60)

except ImportError:
    pass


# ---------------------------------------------------------------------------
# Helper: dispatch (async if available, else sync)
# ---------------------------------------------------------------------------


def dispatch_process_evidence(evidence_id: int, user_id: int, generate_proxy: bool = False) -> Dict:
    """
    Dispatch evidence processing — async via Celery if available, else sync.

    Returns:
        Dict with 'async' flag and either 'task_id' (Celery) or the sync result.
    """
    try:
        from celery_app import is_async
        if is_async():
            result = process_evidence_task.delay(evidence_id, user_id, generate_proxy)
            return {
                "async": True,
                "celery_task_id": result.id,
                "message": "Processing queued",
            }
    except (ImportError, NameError):
        pass

    # Sync fallback
    sync_result = process_evidence_sync(evidence_id, user_id, generate_proxy)
    sync_result["async"] = False
    return sync_result


def dispatch_process_case(case_id: int, user_id: int) -> Dict:
    """
    Dispatch batch case processing — async if available, else sync.
    """
    try:
        from celery_app import is_async
        if is_async():
            result = process_case_batch_task.delay(case_id, user_id)
            return {
                "async": True,
                "celery_task_id": result.id,
                "message": "Batch processing queued",
            }
    except (ImportError, NameError):
        pass

    sync_result = process_case_batch(case_id, user_id)
    sync_result["async"] = False
    return sync_result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _store_content_index(
    db, evidence_id, case_id, content_type, full_text,
    word_count=0, character_count=0, page_count=None,
    emails=None, phones=None, metadata=None,
):
    """Create or update a ContentExtractionIndex entry."""
    from models.document_processing import ContentExtractionIndex

    existing = ContentExtractionIndex.query.filter_by(evidence_id=evidence_id).first()

    if existing:
        existing.full_text = full_text
        existing.content_type = content_type
        existing.word_count = word_count
        existing.character_count = character_count
        existing.line_count = page_count
        existing.email_addresses = ",".join(emails) if emails else ""
        existing.phone_numbers = ",".join(phones) if phones else ""
        existing.is_indexed = True
        existing.last_indexed = datetime.now(timezone.utc)
    else:
        idx = ContentExtractionIndex(
            evidence_id=evidence_id,
            case_id=case_id,
            content_type=content_type,
            word_count=word_count,
            character_count=character_count,
            line_count=page_count,
            full_text=full_text,
            email_addresses=",".join(emails) if emails else "",
            phone_numbers=",".join(phones) if phones else "",
            is_indexed=True,
            last_indexed=datetime.now(timezone.utc),
        )
        db.session.add(idx)

    db.session.flush()


def _store_ocr_result(db, evidence_id, task_id, text, page_count=None, confidence=None):
    """Create or update an OCRResult entry."""
    from models.document_processing import OCRResult

    existing = OCRResult.query.filter_by(evidence_id=evidence_id).first()

    if existing:
        existing.extracted_text = text
        existing.processing_task_id = task_id
        existing.total_pages = page_count
        existing.pages_processed = page_count
        if confidence:
            existing.average_confidence = confidence
    else:
        ocr = OCRResult(
            evidence_id=evidence_id,
            processing_task_id=task_id,
            extracted_text=text,
            total_pages=page_count,
            pages_processed=page_count,
            average_confidence=confidence,
            confidence_per_line="[]",
            is_searchable=True,
        )
        db.session.add(ocr)

    db.session.flush()
