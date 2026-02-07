import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from . import bwc_flags, bwc_sync

logger = logging.getLogger(__name__)

# SQLite DB for jobs
DB_PATH = Path("instance/bwc_jobs.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=ENGINE))
Base = declarative_base()


class JobModel(Base):
    __tablename__ = "bwc_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), unique=True, index=True, nullable=False)
    case_id = Column(String(128), nullable=True)
    user_id = Column(Integer, nullable=True)
    upload_ids = Column(Text, nullable=True)
    video_paths = Column(Text, nullable=True)
    options = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="queued")
    created_at = Column(String(64), nullable=False)
    updated_at = Column(String(64), nullable=False)
    progress = Column(Integer, nullable=False, default=0)
    artifacts = Column(Text, nullable=True)
    log = Column(Text, nullable=True)


Base.metadata.create_all(ENGINE)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _to_json(obj: Any) -> str:
    try:
        return json.dumps(obj)
    except Exception:
        return json.dumps(str(obj))


def _from_json(s: str | None) -> Any:
    if s is None:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def enqueue_batch(
    case_id: str | None,
    user_id: int,
    upload_ids: list[Any],
    video_paths: list[str],
    options: dict | None = None,
) -> str:
    job_id = uuid.uuid4().hex
    now = _now_iso()
    session = Session()
    job = JobModel(
        job_id=job_id,
        case_id=case_id,
        user_id=user_id,
        upload_ids=_to_json(upload_ids),
        video_paths=_to_json(video_paths),
        options=_to_json(options or {}),
        status="queued",
        created_at=now,
        updated_at=now,
        progress=0,
        artifacts=_to_json({}),
        log=_to_json([]),
    )
    session.add(job)
    session.commit()
    session.close()
    return job_id


def _update_job(job: JobModel, session) -> dict[str, Any]:
    job.updated_at = _now_iso()
    session.add(job)
    session.commit()
    return get_job_status(job.job_id)


def get_job_status(job_id: str) -> dict:
    session = Session()
    job = session.query(JobModel).filter_by(job_id=job_id).one_or_none()
    if job is None:
        session.close()
        return {"error": "not_found"}
    state = {
        "job_id": job.job_id,
        "case_id": job.case_id,
        "user_id": job.user_id,
        "upload_ids": _from_json(job.upload_ids),
        "video_paths": _from_json(job.video_paths),
        "options": _from_json(job.options),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "progress": job.progress,
        "artifacts": _from_json(job.artifacts),
        "log": _from_json(job.log),
    }
    session.close()
    return state


def run_job(job_id: str) -> dict:
    """Run the job synchronously (caller may run in background worker)."""
    session = Session()
    job = session.query(JobModel).filter_by(job_id=job_id).one_or_none()
    if job is None:
        session.close()
        raise RuntimeError("Job not found")

    try:
        job.status = "running"
        job.progress = 1
        _update_job(job, session)

        manifests = []
        video_paths = _from_json(job.video_paths) or []
        for p in video_paths:
            try:
                sha = bwc_sync._sha256(Path(p))
            except Exception:
                sha = None
            manifests.append({"path": p, "sha256": sha})

        job.artifacts = _to_json({"manifests": manifests})
        job.progress = 10
        _update_job(job, session)

        audio_paths = []
        for p in video_paths:
            try:
                wav = bwc_sync.extract_audio_wav(p, str(Path(p).with_suffix(".wav")))
            except Exception as e:
                wav = None
                logger.warning("Audio extract failed for %s: %s", p, e)
            audio_paths.append(wav)

        job.options = _to_json({"audio_paths": audio_paths})
        job.progress = 30
        _update_job(job, session)

        try:
            sync = bwc_sync.build_sync_map([p for p in video_paths])
        except Exception as e:
            sync = {"error": str(e)}
        # merge sync into artifacts
        artifacts = _from_json(job.artifacts) or {}
        artifacts["sync_map"] = sync
        job.artifacts = _to_json(artifacts)
        job.progress = 45
        _update_job(job, session)

        transcripts = []
        try:
            from whisper_transcription import WhisperTranscriptionService

            svc = WhisperTranscriptionService()
            for wav in audio_paths:
                if not wav:
                    transcripts.append([])
                    continue
                try:
                    result = svc.transcribe_batch([wav])
                    transcripts.append(result[0] if isinstance(result, list) and result else [])
                except Exception as e:
                    logger.warning("Transcription failed for %s: %s", wav, e)
                    transcripts.append([])
        except Exception:
            transcripts = [[] for _ in audio_paths]

        artifacts["transcripts"] = transcripts
        job.artifacts = _to_json(artifacts)
        job.progress = 75
        _update_job(job, session)

        flags = bwc_flags.analyze_transcript_for_flags(transcripts)
        artifacts["flags"] = [f.__dict__ for f in flags]
        job.artifacts = _to_json(artifacts)
        job.progress = 90
        _update_job(job, session)

        artifacts_dir = Path("instance/jobs") / job.job_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        bundle = {
            "job_id": job.job_id,
            "manifests": manifests,
            "sync_map": sync,
            "transcripts": transcripts,
            "flags": artifacts.get("flags", []),
        }
        bundle_path = artifacts_dir / "report.json"
        with open(bundle_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        artifacts["report"] = str(bundle_path)
        job.artifacts = _to_json(artifacts)
        job.progress = 100
        job.status = "completed"
        _update_job(job, session)

        session.close()
        return get_job_status(job.job_id)

    except Exception as e:
        logger.error("Job %s failed: %s", job_id, e)
        job.status = "failed"
        job.progress = 0
        session.add(job)
        session.commit()
        session.close()
        return get_job_status(job.job_id)
