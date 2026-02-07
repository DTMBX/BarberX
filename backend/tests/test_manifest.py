import hashlib
from pathlib import Path

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
    # canonical manifest contains `originals` list
    assert "originals" in manifest
    assert len(manifest["originals"]) == len(files)

    # Verify sha256s
    bypath = {it["path"]: it for it in manifest["originals"]}
    for name, data in files.items():
        rel = str((originals / name).relative_to(case)).replace("\\", "/")
        assert rel in bypath
        expected = hashlib.sha256(data).hexdigest()
        assert bypath[rel]["sha256"] == expected
