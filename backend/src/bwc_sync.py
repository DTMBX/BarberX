import hashlib
import logging
import subprocess
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8192), b""):
            h.update(b)
    return h.hexdigest()


def ffmpeg_version() -> str:
    try:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        return out.stdout.splitlines()[0]
    except Exception:
        return "ffmpeg:unknown"


def extract_audio_wav(video_path: str, out_wav: str | None = None) -> str:
    """Extract mono 16k PCM WAV for downstream processing."""
    video = Path(video_path)
    if out_wav is None:
        out_wav = str(video.with_suffix(".wav"))

    cmd = [
        "ffmpeg",
        "-i",
        str(video),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-y",
        out_wav,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out_wav
    except Exception as e:
        logger.warning(f"ffmpeg extract failed: {e}")
        raise


def _read_wav_mono(path: Path) -> np.ndarray:
    # Minimal wav reader using numpy and wave module to avoid heavy deps
    import wave

    with wave.open(str(path), "rb") as wf:
        assert wf.getnchannels() == 1
        frames = wf.readframes(wf.getnframes())
        dtype = np.int16 if wf.getsampwidth() == 2 else np.int16
        arr = np.frombuffer(frames, dtype=dtype).astype(float)
        # normalize
        if arr.size == 0:
            return np.zeros(0)
        return arr / np.max(np.abs(arr))


def estimate_offset_seconds(
    reference_wav: str, target_wav: str, max_lag_seconds: float = 30.0
) -> tuple[float, float]:
    """Estimate offset of target relative to reference using cross-correlation.

    Returns (offset_seconds, confidence(0..1)). Positive offset means target is later than reference.
    """
    ref = Path(reference_wav)
    tgt = Path(target_wav)
    ref_arr = _read_wav_mono(ref)
    tgt_arr = _read_wav_mono(tgt)

    if ref_arr.size == 0 or tgt_arr.size == 0:
        return 0.0, 0.0

    # sample rate is 16000 per extraction contract
    sr = 16000
    max_lag = int(min(len(ref_arr), len(tgt_arr), int(max_lag_seconds * sr)))

    # Full cross-correlation using numpy
    corr = np.correlate(ref_arr, tgt_arr, mode="full")
    # lags range from -(len(tgt)-1) .. len(ref)-1
    lags = np.arange(-len(tgt_arr) + 1, len(ref_arr))

    # Limit search to max_lag around zero
    center_idx = np.where(lags == 0)[0][0]
    low = max(0, center_idx - max_lag)
    high = min(len(corr), center_idx + max_lag + 1)
    sub = corr[low:high]
    rel_idx = int(np.argmax(np.abs(sub)))
    lag = lags[low + rel_idx]

    # Positive lag from np.correlate corresponds to reference delayed relative to target,
    # so target is later by -lag samples. Invert sign to return target offset relative to reference.
    offset_seconds = -float(lag) / float(sr)

    # Confidence: normalized correlation peak
    peak = float(np.max(np.abs(sub)))
    energy = float(np.linalg.norm(ref_arr) * np.linalg.norm(tgt_arr))
    confidence = peak / (energy + 1e-9)
    confidence = max(0.0, min(1.0, confidence))

    return offset_seconds, confidence


def build_sync_map(video_paths: list[str], reference_index: int = 0) -> dict:
    """Build sync map for list of video paths. Returns dict with offsets and metadata."""
    paths = [Path(p) for p in video_paths]
    sync = {
        "reference_index": reference_index,
        "entries": [],
        "ffmpeg_version": ffmpeg_version(),
    }

    # Extract wavs to temporary .wav next to files (non-destructive)
    wavs = []
    for p in paths:
        wav = str(p.with_suffix(".wav"))
        try:
            extract_audio_wav(str(p), wav)
        except Exception:
            # if extraction fails, continue with None
            wav = None
        wavs.append(wav)

    ref_wav = wavs[reference_index]
    for i, wav in enumerate(wavs):
        entry = {"pov_index": i, "video_path": str(paths[i]), "sha256": _sha256(paths[i])}
        if wav and ref_wav and i != reference_index:
            try:
                offset, conf = estimate_offset_seconds(ref_wav, wav)
                entry.update({"offset_seconds": offset, "confidence": conf})
            except Exception:
                entry.update({"offset_seconds": 0.0, "confidence": 0.0})
        else:
            entry.update({"offset_seconds": 0.0, "confidence": 0.0})

        sync["entries"].append(entry)

    return sync
