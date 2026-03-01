import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "evident_bwc",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

logger = logging.getLogger(__name__)


def _get_db():
    from app.core.database import SessionLocal
    return SessionLocal()


def _upload_artifact(s3_key: str, data: bytes) -> str:
    """Upload artifact to MinIO and return SHA-256."""
    from app.services.hashing import sha256_hex
    from app.services.s3 import get_s3_client
    from app.core.config import settings
    import io

    digest = sha256_hex(data)
    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=s3_key,
        Body=io.BytesIO(data),
        ContentLength=len(data),
        ContentType="application/json",
    )
    return digest


def _store_artifact(db, evidence_id, case_id, artifact_type, s3_key, content_json, preview=None):
    """Create an EvidenceArtifact row and upload JSON to MinIO."""
    from app.models.evidence_artifact import EvidenceArtifact

    data = json.dumps(content_json, separators=(",", ":"), sort_keys=True).encode()
    sha = _upload_artifact(s3_key, data)

    artifact = EvidenceArtifact(
        evidence_id=evidence_id,
        case_id=case_id,
        artifact_type=artifact_type,
        minio_object_key=s3_key,
        sha256=sha,
        content_preview=preview,
    )
    db.add(artifact)
    return artifact


@celery_app.task(name="evident.ping")
def ping():
    return {"ok": True}


@celery_app.task(name="evident.process_evidence_metadata", bind=True, max_retries=0)
def process_evidence_metadata(self, evidence_id: str, job_id: str | None = None):
    """Extract metadata from the uploaded evidence file using ffprobe."""
    from app.models.evidence_file import EvidenceFile
    from app.models.job import Job, JobStatus
    from app.services.audit import append_audit_event
    from app.services.s3 import download_bytes

    db = _get_db()
    try:
        eid = uuid.UUID(evidence_id)
        ef = db.get(EvidenceFile, eid)
        if ef is None:
            logger.error("EvidenceFile %s not found", evidence_id)
            return {"error": "not_found"}

        job = None
        if job_id:
            job = db.get(Job, uuid.UUID(job_id))
        if job is None:
            job = (
                db.query(Job)
                .filter(Job.evidence_id == eid, Job.status == JobStatus.pending)
                .first()
            )
        if job is None:
            logger.warning("No pending job for evidence %s", evidence_id)
            return {"error": "no_job"}

        job.status = JobStatus.running
        db.commit()

        # Check if ffprobe is available
        ffprobe_path = shutil.which("ffprobe")
        if ffprobe_path is None:
            logger.warning("ffprobe not installed — marking job failed for evidence %s", evidence_id)
            job.status = JobStatus.failed
            append_audit_event(
                db,
                case_id=ef.case_id,
                event_type="job.failed",
                payload={
                    "job_id": str(job.id),
                    "evidence_id": evidence_id,
                    "reason": "ffprobe not installed",
                },
            )
            db.commit()
            return {"status": "failed", "reason": "ffprobe_not_installed"}

        raw = download_bytes(ef.minio_object_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ef.original_filename) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [
                    ffprobe_path,
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    tmp_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            metadata = json.loads(result.stdout) if result.returncode == 0 else {"error": result.stderr[:500]}
        except Exception as exc:
            metadata = {"error": str(exc)[:500]}
        finally:
            os.unlink(tmp_path)

        # Store artifact
        s3_key = f"artifacts/{ef.case_id}/{ef.id}/metadata.json"
        _store_artifact(db, ef.id, ef.case_id, "metadata", s3_key, metadata)

        job.status = JobStatus.complete
        append_audit_event(
            db,
            case_id=ef.case_id,
            event_type="evidence.metadata_extracted",
            payload={
                "job_id": str(job.id),
                "evidence_id": evidence_id,
                "metadata": metadata,
            },
        )
        db.commit()
        return {"status": "complete", "metadata": metadata}
    except Exception as exc:
        logger.exception("process_evidence_metadata failed for %s", evidence_id)
        db.rollback()
        return {"error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="evident.transcribe_media", bind=True, max_retries=0)
def transcribe_media(self, evidence_id: str, job_id: str | None = None):
    """Transcribe audio/video evidence."""
    from app.models.evidence_file import EvidenceFile
    from app.models.job import Job, JobStatus
    from app.services.audit import append_audit_event
    from app.services.s3 import download_bytes
    from app.services.transcription import get_transcription_provider

    db = _get_db()
    try:
        eid = uuid.UUID(evidence_id)
        ef = db.get(EvidenceFile, eid)
        if ef is None:
            return {"error": "not_found"}

        job = None
        if job_id:
            job = db.get(Job, uuid.UUID(job_id))
        if job is None:
            job = db.query(Job).filter(Job.evidence_id == eid, Job.status == JobStatus.pending).first()
        if job is None:
            return {"error": "no_job"}

        job.status = JobStatus.running
        db.commit()

        raw = download_bytes(ef.minio_object_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ef.original_filename) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        try:
            provider = get_transcription_provider()
            transcript = provider.transcribe(tmp_path, ef.content_type)
        finally:
            os.unlink(tmp_path)

        # Store artifact
        s3_key = f"artifacts/{ef.case_id}/{ef.id}/transcript.json"
        preview = transcript.get("text", "")[:2000]
        _store_artifact(db, ef.id, ef.case_id, "transcript", s3_key, transcript, preview=preview)

        job.status = JobStatus.complete
        append_audit_event(
            db,
            case_id=ef.case_id,
            event_type="artifact.created",
            payload={
                "job_id": str(job.id),
                "evidence_id": evidence_id,
                "artifact_type": "transcript",
                "status": transcript.get("status", "complete"),
            },
        )
        db.commit()
        return {"status": "complete", "transcript_status": transcript.get("status", "complete")}
    except Exception as exc:
        logger.exception("transcribe_media failed for %s", evidence_id)
        db.rollback()
        return {"error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="evident.ocr_pdf", bind=True, max_retries=0)
def ocr_pdf(self, evidence_id: str, job_id: str | None = None):
    """OCR a PDF evidence file."""
    from app.models.evidence_file import EvidenceFile
    from app.models.job import Job, JobStatus
    from app.services.audit import append_audit_event
    from app.services.s3 import download_bytes
    from app.services.ocr import get_ocr_provider

    db = _get_db()
    try:
        eid = uuid.UUID(evidence_id)
        ef = db.get(EvidenceFile, eid)
        if ef is None:
            return {"error": "not_found"}

        job = None
        if job_id:
            job = db.get(Job, uuid.UUID(job_id))
        if job is None:
            job = db.query(Job).filter(Job.evidence_id == eid, Job.status == JobStatus.pending).first()
        if job is None:
            return {"error": "no_job"}

        job.status = JobStatus.running
        db.commit()

        raw = download_bytes(ef.minio_object_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ef.original_filename) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        try:
            provider = get_ocr_provider()
            ocr_result = provider.extract_text(tmp_path, ef.content_type)
        finally:
            os.unlink(tmp_path)

        # Store artifact
        s3_key = f"artifacts/{ef.case_id}/{ef.id}/ocr.json"
        preview = ocr_result.get("text", "")[:2000]
        _store_artifact(db, ef.id, ef.case_id, "ocr", s3_key, ocr_result, preview=preview)

        job.status = JobStatus.complete
        append_audit_event(
            db,
            case_id=ef.case_id,
            event_type="artifact.created",
            payload={
                "job_id": str(job.id),
                "evidence_id": evidence_id,
                "artifact_type": "ocr",
                "page_count": ocr_result.get("page_count", 0),
                "status": ocr_result.get("status", "complete"),
            },
        )
        db.commit()
        return {"status": "complete", "ocr_status": ocr_result.get("status", "complete")}
    except Exception as exc:
        logger.exception("ocr_pdf failed for %s", evidence_id)
        db.rollback()
        return {"error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="evident.index_case_for_chat", bind=True, max_retries=0)
def index_case_for_chat(self, case_id: str):
    """Build a searchable context pack for a case (aggregate artifacts)."""
    from app.models.evidence_artifact import EvidenceArtifact

    db = _get_db()
    try:
        cid = uuid.UUID(case_id)
        artifacts = db.query(EvidenceArtifact).filter(EvidenceArtifact.case_id == cid).all()

        context_pack = {
            "case_id": case_id,
            "artifact_count": len(artifacts),
            "summaries": [],
        }
        for a in artifacts:
            context_pack["summaries"].append({
                "artifact_type": a.artifact_type,
                "evidence_id": str(a.evidence_id),
                "preview": a.content_preview[:500] if a.content_preview else None,
            })

        s3_key = f"artifacts/{case_id}/context_pack.json"
        _upload_artifact(s3_key, json.dumps(context_pack).encode())

        logger.info("Indexed case %s for chat: %d artifacts", case_id, len(artifacts))
        return {"status": "complete", "artifact_count": len(artifacts)}
    except Exception as exc:
        logger.exception("index_case_for_chat failed for %s", case_id)
        return {"error": str(exc)}
    finally:
        db.close()
