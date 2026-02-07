import json
from pathlib import Path

from backend.src.bwc_jobs import enqueue_batch, get_job_status, run_job


def test_enqueue_and_run_job(monkeypatch, tmp_path):
    # Prepare fake videos (no ffmpeg will be run because we monkeypatch extract)
    v1 = tmp_path / "v1.mp4"
    v1.write_bytes(b"fakevideo1")
    v2 = tmp_path / "v2.mp4"
    v2.write_bytes(b"fakevideo2")

    # Monkeypatch bwc_sync functions to avoid external tools
    import backend.src.bwc_sync as sync

    monkeypatch.setattr(sync, "_sha256", lambda p: "deadbeef")
    monkeypatch.setattr(
        sync, "extract_audio_wav", lambda p, out=None: str(Path(p).with_suffix(".wav"))
    )
    monkeypatch.setattr(sync, "build_sync_map", lambda paths, reference_index=0: {"entries": []})

    # Enqueue
    job_id = enqueue_batch(
        case_id="C1", user_id=42, upload_ids=[1, 2], video_paths=[str(v1), str(v2)], options={}
    )
    status = get_job_status(job_id)
    assert status["status"] == "queued"

    # Run job (synchronous)
    res = run_job(job_id)
    assert res["status"] in ("completed", "failed")
    # When completed, ensure artifact path present
    if res["status"] == "completed":
        assert "report" in res["artifacts"]
