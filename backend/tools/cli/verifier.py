"""Verify manifests and the integrity of case exports."""

from __future__ import annotations

import json
from pathlib import Path

from .hashing import compute_sha256


def verify_manifest(case_dir: Path) -> dict:
    canonical_path = case_dir / "manifests" / "manifest.canonical.json"
    if not canonical_path.exists():
        raise FileNotFoundError("manifest.canonical.json not found")

    m = json.loads(canonical_path.read_text(encoding="utf-8"))
    results = {"missing": [], "mismatches": []}

    # check originals
    for item in m.get("originals", []):
        p = case_dir / item["path"]
        if not p.exists():
            results["missing"].append(item["path"])
            continue
        sha = compute_sha256(p)
        if sha != item["sha256"]:
            results["mismatches"].append(
                {"path": item["path"], "expected": item["sha256"], "got": sha}
            )

    # check derivatives
    for d in m.get("derivatives", []):
        p = case_dir / d["path"]
        if not p.exists():
            results["missing"].append(d["path"])
            continue
        sha = compute_sha256(p)
        if sha != d["sha256"]:
            results["mismatches"].append({"path": d["path"], "expected": d["sha256"], "got": sha})

    return results
