"""Create deterministic export ZIP packages containing originals, derivatives, manifest, and audit excerpt."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

from .hashing import compute_sha256, iter_files


def _norm_path(p: Path) -> str:
    return str(p).replace("\\", "/")


def export_case(case_dir: Path, out_zip: Path, normalize_mtime: bool = True) -> Path:
    """Export a case folder to a reproducible ZIP.

    - Orders entries deterministically
    - Normalizes timestamps in ZIP entries when `normalize_mtime` is True
    """
    case_dir = case_dir.resolve()
    items = []
    for p in iter_files(case_dir):
        rel = p.relative_to(case_dir)
        items.append((str(rel).replace("\\", "/"), p))

    # stabilize ordering
    items.sort(key=lambda t: t[0])

    # exclude manifests we add explicitly below to avoid duplicate entries
    items = [
        it
        for it in items
        if it[0] not in ("manifests/manifest.canonical.json", "manifests/manifest.meta.json")
    ]

    # Ensure manifest exists
    # Prefer canonical manifest for deterministic exports
    canonical_path = case_dir / "manifests" / "manifest.canonical.json"
    meta_path = case_dir / "manifests" / "manifest.meta.json"
    if not canonical_path.exists():
        raise FileNotFoundError("manifest.canonical.json not found; run manifest command first")

    # Build audit excerpt (simple): list of items and sha256
    audit = []
    for rel, p in items:
        audit.append({"path": rel, "sha256": compute_sha256(p)})

    # Write ZIP with normalized timestamps
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # fixed timestamp: 1980-01-01 00:00:00 per ZIP spec minimum
        dt = (1980, 1, 1, 0, 0, 0) if normalize_mtime else datetime.utcnow().timetuple()[:6]
        for rel, p in items:
            zi = zipfile.ZipInfo(rel)
            zi.date_time = dt
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(zi, p.read_bytes())

        # include canonical manifest and meta manifest for reproducibility and auditability
        canonical_bytes = canonical_path.read_bytes()
        zi = zipfile.ZipInfo("manifests/manifest.canonical.json")
        zi.date_time = dt
        zf.writestr(zi, canonical_bytes)

        if meta_path.exists():
            meta_bytes = meta_path.read_bytes()
            zi = zipfile.ZipInfo("manifests/manifest.meta.json")
            zi.date_time = dt
            zf.writestr(zi, meta_bytes)

        # add audit excerpt
        audit_bytes = json.dumps(audit, sort_keys=True, separators=(",", ":")).encode("utf-8")
        zi = zipfile.ZipInfo("audit/audit.json")
        zi.date_time = dt
        zf.writestr(zi, audit_bytes)

    return out_zip
