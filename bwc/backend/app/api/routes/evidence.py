"""Evidence upload endpoints — init + complete."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import (
    EvidenceBatchInitRequest,
    EvidenceBatchInitResponse,
    EvidenceCompleteRequest,
    EvidenceInitRequest,
    EvidenceInitResponse,
    EvidenceOut,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.case import Case
from app.models.evidence_file import EvidenceFile
from app.models.job import Job, JobStatus
from app.services.audit import append_audit_event
from app.services.hashing import sha256_hex
from app.services.s3 import download_bytes, presigned_put_url
from app.workers.celery_app import celery_app

import re

_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")

# Allowed MIME types for upload
_ALLOWED_MIME_PREFIXES = ("video/", "audio/", "image/", "application/pdf")

router = APIRouter(prefix="/evidence", tags=["evidence"])


def _validate_mime(content_type: str) -> None:
    """Reject disallowed MIME types."""
    if not any(content_type.startswith(prefix) for prefix in _ALLOWED_MIME_PREFIXES):
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported content type: {content_type}. "
            f"Allowed: {', '.join(_ALLOWED_MIME_PREFIXES)}",
        )


@router.post("/init", response_model=EvidenceInitResponse, status_code=201)
def evidence_init(body: EvidenceInitRequest, db: Session = Depends(get_db)):
    # Verify case exists
    case = db.get(Case, body.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # Validate MIME type
    _validate_mime(body.content_type)

    # ── Enforce object key naming scheme ─────────────────────────────
    # Key pattern: originals/<case_id>/<evidence_id>/<filename>
    # Reject path-traversal or shell-injection filenames
    safe_name = body.filename.replace("/", "_").replace("\\", "_")
    if not _SAFE_FILENAME_RE.match(safe_name):
        raise HTTPException(
            status_code=422,
            detail="Filename contains disallowed characters.",
        )

    evidence_id = uuid.uuid4()
    object_key = (
        f"{settings.evidence_originals_prefix}{body.case_id}/{evidence_id}/{safe_name}"
    )

    # Create evidence row (sha256 pending)
    ef = EvidenceFile(
        id=evidence_id,
        case_id=body.case_id,
        original_filename=safe_name,
        content_type=body.content_type,
        size_bytes=body.size_bytes,
        sha256=None,
        minio_object_key=object_key,
    )
    db.add(ef)

    append_audit_event(
        db,
        case_id=body.case_id,
        event_type="evidence.init",
        payload={
            "evidence_id": str(evidence_id),
            "filename": body.filename,
            "content_type": body.content_type,
            "size_bytes": body.size_bytes,
        },
    )

    db.commit()

    upload_url = presigned_put_url(object_key, body.content_type)
    return EvidenceInitResponse(evidence_id=evidence_id, upload_url=upload_url)


@router.post("/complete", response_model=EvidenceOut)
def evidence_complete(body: EvidenceCompleteRequest, db: Session = Depends(get_db)):
    ef = db.get(EvidenceFile, body.evidence_id)
    if ef is None:
        raise HTTPException(status_code=404, detail="Evidence file not found")

    if ef.sha256 is not None:
        raise HTTPException(status_code=409, detail="Evidence already finalized")

    # Download from MinIO and compute SHA-256
    raw = download_bytes(ef.minio_object_key)
    digest = sha256_hex(raw)

    # ── Enforce uniqueness: (case_id, sha256) ────────────────────────
    duplicate = (
        db.query(EvidenceFile)
        .filter(
            EvidenceFile.case_id == ef.case_id,
            EvidenceFile.sha256 == digest,
        )
        .first()
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate evidence: SHA-256 {digest} already exists in this case.",
        )

    ef.sha256 = digest
    db.add(ef)

    # Create a background job for metadata extraction
    job = Job(
        case_id=ef.case_id,
        evidence_id=ef.id,
        status=JobStatus.pending,
    )
    db.add(job)

    append_audit_event(
        db,
        case_id=ef.case_id,
        event_type="evidence.complete",
        payload={
            "evidence_id": str(ef.id),
            "sha256": digest,
            "size_bytes": ef.size_bytes,
            "filename": ef.original_filename,
        },
    )

    db.commit()
    db.refresh(ef)

    # Queue Celery task (after commit so the job row is visible)
    celery_app.send_task(
        "evident.process_evidence_metadata",
        kwargs={"evidence_id": str(ef.id)},
    )

    return ef


@router.post("/batch/init", response_model=EvidenceBatchInitResponse, status_code=201)
def evidence_batch_init(body: EvidenceBatchInitRequest, db: Session = Depends(get_db)):
    """Initialize batch upload — returns N presigned URLs."""
    case = db.get(Case, body.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    items: list[EvidenceInitResponse] = []
    for file_info in body.files:
        _validate_mime(file_info.content_type)
        safe_name = file_info.filename.replace("/", "_").replace("\\", "_")
        if not _SAFE_FILENAME_RE.match(safe_name):
            raise HTTPException(
                status_code=422,
                detail=f"Filename contains disallowed characters: {file_info.filename}",
            )

        evidence_id = uuid.uuid4()
        object_key = (
            f"{settings.evidence_originals_prefix}{body.case_id}/{evidence_id}/{safe_name}"
        )

        ef = EvidenceFile(
            id=evidence_id,
            case_id=body.case_id,
            original_filename=safe_name,
            content_type=file_info.content_type,
            size_bytes=file_info.size_bytes,
            sha256=None,
            minio_object_key=object_key,
        )
        db.add(ef)

        append_audit_event(
            db,
            case_id=body.case_id,
            event_type="evidence.init",
            payload={
                "evidence_id": str(evidence_id),
                "filename": file_info.filename,
                "content_type": file_info.content_type,
                "size_bytes": file_info.size_bytes,
                "batch": True,
            },
        )

        upload_url = presigned_put_url(object_key, file_info.content_type)
        items.append(EvidenceInitResponse(evidence_id=evidence_id, upload_url=upload_url))

    db.commit()
    return EvidenceBatchInitResponse(items=items)


@router.get("", response_model=list[EvidenceOut])
def list_evidence(
    case_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    """List evidence files, optionally filtered by case_id."""
    q = db.query(EvidenceFile).order_by(EvidenceFile.uploaded_at.desc())
    if case_id is not None:
        q = q.filter(EvidenceFile.case_id == case_id)
    return q.limit(500).all()
