import zipfile
from pathlib import Path

from backend.tools.cli.exporter import export_case
from backend.tools.cli.manifest import create_manifest


def test_exporter_is_deterministic(tmp_path: Path):
    case = tmp_path / "CASE2"
    originals = case / "originals"
    originals.mkdir(parents=True)
    (originals / "one.txt").write_text("one")
    (originals / "two.txt").write_text("two")

    # create canonical manifest
    canonical = create_manifest(case)
    canonical_bytes = (case / "manifests" / "manifest.canonical.json").read_bytes()

    out1 = tmp_path / "export1.zip"
    out2 = tmp_path / "export2.zip"

    export_case(case, out1, normalize_mtime=True)
    export_case(case, out2, normalize_mtime=True)

    b1 = out1.read_bytes()
    b2 = out2.read_bytes()

    # At minimum, ensure embedded canonical manifest bytes match and ordering is identical
    assert b1 == b2

    # verify embedded canonical manifest equals source bytes
    with zipfile.ZipFile(out1, "r") as zf, zf.open("manifests/manifest.canonical.json") as mf:
        embedded = mf.read()
    assert embedded == canonical_bytes

    # check timestamps normalized
    with zipfile.ZipFile(out1, "r") as zf:
        infos = zf.infolist()
        for zi in infos:
            assert zi.date_time == (1980, 1, 1, 0, 0, 0)
