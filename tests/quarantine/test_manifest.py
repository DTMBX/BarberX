"""Quarantined: backend package removed from main branch.
Source modules (backend.tools.cli.hashing, backend.tools.cli.manifest)
no longer exist. Functions partially relocated to scripts/generate-checksums.py
with different signatures.
Tracked: Phase 10 gate — restore when CLI module is re-implemented.
Deadline: Phase 11 or remove permanently.
"""
import pytest

pytestmark = pytest.mark.skip(
    reason="quarantined — backend.tools.cli.hashing and .manifest removed from main; "
           "source modules do not exist (see Phase 10 gate)"
)

import hashlib
import tempfile
from pathlib import Path

from backend.tools.cli.hashing import compute_sha256
from backend.tools.cli.manifest import create_manifest


def test_manifest_matches_hashes(tmp_path: Path):
    case = tmp_path / "CASE123"
    originals = case / "originals"
    originals.mkdir(parents=True)

    files = {
        "a.txt": b"alpha",
        "b.bin": b"bravo",
    }

    for name, data in files.items():
        p = originals / name
        p.write_bytes(data)

    manifest = create_manifest(case)
    assert "items" in manifest
    assert len(manifest["items"]) == len(files)

    # Verify sha256s
    bypath = {it["path"]: it for it in manifest["items"]}
    for name, data in files.items():
        rel = str((originals / name).relative_to(case))
        assert rel in bypath
        expected = hashlib.sha256(data).hexdigest()
        assert bypath[rel]["sha256"] == expected
