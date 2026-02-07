import json
import subprocess
import sys
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kw)


def test_cli_hash_and_manifest(tmp_path: Path):
    src = tmp_path / "input"
    src.mkdir()
    (src / "one.txt").write_text("one")

    out = tmp_path / "out"
    out.mkdir()

    # Run hash via module
    r = run([sys.executable, "-m", "backend.tools.cli.cli", "hash", str(src), "--out", str(out)])
    assert r.returncode == 0, r.stderr

    hash_index = out / "hash_index.json"
    assert hash_index.exists()

    # Prepare a case_dir for manifest command
    case = tmp_path / "CASEX"
    originals = case / "originals"
    originals.mkdir(parents=True)
    (originals / "one.txt").write_text("one")

    r2 = run([sys.executable, "-m", "backend.tools.cli.cli", "manifest", str(case)])
    assert r2.returncode == 0, r2.stderr

    canonical = case / "manifests" / "manifest.canonical.json"
    assert canonical.exists()
    data = json.loads(canonical.read_text())
    assert "originals" in data and len(data["originals"]) == 1
