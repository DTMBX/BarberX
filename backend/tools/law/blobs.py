from __future__ import annotations

import hashlib
from pathlib import Path

BASE = Path(__file__).parent / "blobs"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_blob(data: bytes, kind: str = "raw") -> dict:
    assert kind in ("raw", "canonical", "json"), "kind must be one of raw|canonical|json"
    base = BASE / kind
    base.mkdir(parents=True, exist_ok=True)
    sha = _sha256_bytes(data)
    fname = base / f"{sha}.bin"
    if not fname.exists():
        fname.write_bytes(data)
    return {"path": str(fname), "sha256": sha}
