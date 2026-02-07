import wave
import numpy as np
from pathlib import Path

from backend.src.bwc_sync import estimate_offset_seconds


def _write_sine(path: Path, freq=440.0, sr=16000, duration=1.0, delay=0.0):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * freq * t)
    # apply delay as zeros
    if delay > 0:
        pad = int(delay * sr)
        sig = np.concatenate((np.zeros(pad), sig))

    # write wav
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        int_data = (sig * 32767).astype("int16")
        wf.writeframes(int_data.tobytes())


def test_estimate_offset_seconds(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    _write_sine(a, duration=1.0, delay=0.0)
    _write_sine(b, duration=1.0, delay=0.25)

    offset, conf = estimate_offset_seconds(str(a), str(b), max_lag_seconds=1.0)
    # offset should be approx +0.25 (target later)
    assert abs(offset - 0.25) < 0.05
    assert 0.0 <= conf <= 1.0
