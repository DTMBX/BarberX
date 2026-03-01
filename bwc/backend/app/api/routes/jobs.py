"""Jobs API — enqueue processing tasks and query status."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import JobEnqueueRequest, JobOut
from app.core.database import get_db
from app.models.evidence_file import EvidenceFile
from app.models.job import Job, JobStatus
from app.services.audit import append_audit_event
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/enqueue", response_model=list[JobOut], status_code=201)
def enqueue_jobs(body: JobEnqueueRequest, db: Session = Depends(get_db)):
    """Enqueue OCR/transcription/metadata jobs for a list of evidence IDs."""
    created_jobs: list[Job] = []

    for eid in body.evidence_ids:
        ef = db.get(EvidenceFile, eid)
        if ef is None:
            raise HTTPException(status_code=404, detail=f"Evidence {eid} not found")
        if ef.sha256 is None:
            raise HTTPException(
                status_code=400,
                detail=f"Evidence {eid} not yet finalized (sha256 missing)",
            )

        for task_type in body.tasks:
            job = Job(
                case_id=ef.case_id,
                evidence_id=ef.id,
                task_type=task_type,
                status=JobStatus.pending,
            )
            db.add(job)
            db.flush()

            append_audit_event(
                db,
                case_id=ef.case_id,
                event_type="job.enqueued",
                payload={
                    "job_id": str(job.id),
                    "evidence_id": str(eid),
                    "task_type": task_type,
                },
            )
            created_jobs.append(job)

            # Dispatch to Celery
            task_name_map = {
                "ocr": "evident.ocr_pdf",
                "transcribe": "evident.transcribe_media",
                "metadata": "evident.process_evidence_metadata",
            }
            celery_task = task_name_map.get(task_type, f"evident.{task_type}")
            celery_app.send_task(
                celery_task,
                kwargs={"evidence_id": str(ef.id), "job_id": str(job.id)},
            )

    db.commit()
    for j in created_jobs:
        db.refresh(j)
    return created_jobs


@router.get("", response_model=list[JobOut])
def list_jobs(
    case_id: Optional[uuid.UUID] = Query(None),
    evidence_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List jobs, optionally filtered by case_id, evidence_id, or status."""
    q = db.query(Job).order_by(Job.created_at.desc())
    if case_id is not None:
        q = q.filter(Job.case_id == case_id)
    if evidence_id is not None:
        q = q.filter(Job.evidence_id == evidence_id)
    if status is not None:
        q = q.filter(Job.status == status)
    return q.limit(200).all()
