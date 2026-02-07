"""Manifest generation for evidence cases.

Produces a JSON manifest listing originals with size, mtime, and sha256.
"""

from __future__ import annotations
from typing import Optional

import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .hashing import compute_sha256, iter_files


def _detect_ffmpeg_version() -> str:
    try:
        out = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT)
        first = out.decode("utf-8", errors="ignore").splitlines()[0]
        return first.strip()
    except Exception:
        return "ffmpeg: not found"


def create_manifest(
    case_dir: Path,
    originals_subdir: str = "originals",
    tool_versions: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Create canonical manifest and meta manifest.

    Produces two files under `manifests/`:
    - `manifest.canonical.json`: deterministic listing of `originals` and empty `derivatives` (no timestamps)
    - `manifest.meta.json`: operational metadata including `generated_at` and `tool_versions`.
    """
    originals_dir = case_dir / originals_subdir
    if not originals_dir.exists():
        raise FileNotFoundError(f"Originals directory not found: {originals_dir}")

    if tool_versions is None:
        tool_versions = {
            "python": platform.python_version(),
            "ffmpeg": _detect_ffmpeg_version(),
        }

    originals: list[dict[str, Any]] = []
    for p in sorted(iter_files(originals_dir), key=lambda p: str(p.relative_to(case_dir)).lower()):
        rel = p.relative_to(case_dir)
        st = p.stat()
        originals.append(
            {
                "path": str(rel).replace("\\", "/"),
                "size": st.st_size,
                "mtime": int(st.st_mtime),
                "sha256": compute_sha256(p),
            }
        )

    canonical = {
        "schema_version": "1.1.0",
        "case_dir": str(case_dir).replace("\\", "/"),
        "originals": originals,
        "derivatives": [],
    }

    manifests_dir = case_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    canonical_path = manifests_dir / "manifest.canonical.json"
    with canonical_path.open("w", encoding="utf-8") as fh:
        # stable JSON representation without timestamps
        json.dump(canonical, fh, indent=2, sort_keys=True, separators=(",", ":"))

    meta = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool_versions": tool_versions,
        "schema_version": canonical["schema_version"],
    }
    meta_path = manifests_dir / "manifest.meta.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True, separators=(",", ": "))

    return canonical


def load_canonical(case_dir: Path) -> dict[str, Any]:
    p = case_dir / "manifests" / "manifest.canonical.json"
    if not p.exists():
        raise FileNotFoundError("manifest.canonical.json not found; run manifest command")
    return json.loads(p.read_text(encoding="utf-8"))


def add_derivative(
    case_dir: Path, path: str, sha256: str, kind: str, preset: str, source_sha256: str
) -> dict[str, Any]:
    """Append a derivative record to the canonical manifest deterministically.

    Returns the derivative record added.
    """
    manifests_dir = case_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    canonical_path = manifests_dir / "manifest.canonical.json"
    canonical = {}
    if canonical_path.exists():
        canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    else:
        canonical = create_manifest(case_dir)

    deriv = {
        "path": path.replace("\\", "/"),
        "sha256": sha256,
        "kind": kind,
        "preset": preset,
        "source_sha256": source_sha256,
        "tool": "ffmpeg",
        "tool_version": _detect_ffmpeg_version(),
        "command_fingerprint": "",
    }

    # compute a simple command fingerprint (sha256 of the command line)
    try:
        import hashlib

        cmd_str = " ".join([kind, preset, source_sha256])
        deriv["command_fingerprint"] = hashlib.sha256(cmd_str.encode("utf-8")).hexdigest()
    except Exception:
        deriv["command_fingerprint"] = ""

    # append then stable-sort by path
    canonical.setdefault("derivatives", []).append(deriv)
    canonical["derivatives"] = sorted(canonical["derivatives"], key=lambda d: d["path"].lower())

    with canonical_path.open("w", encoding="utf-8") as fh:
        json.dump(canonical, fh, indent=2, sort_keys=True, separators=(",", ":"))

    # refresh meta
    meta_path = manifests_dir / "manifest.meta.json"
    meta = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool_versions": {"python": platform.python_version(), "ffmpeg": _detect_ffmpeg_version()},
        "schema_version": canonical["schema_version"],
    }
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True, separators=(",", ": "))

    return deriv
