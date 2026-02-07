from pathlib import Path

from backend.tools.cli.manifest import add_derivative, create_manifest
from backend.tools.cli.verifier import verify_manifest


def test_verifier_detects_missing_and_mismatch(tmp_path: Path):
    case = tmp_path / "CASE3"
    originals = case / "originals"
    originals.mkdir(parents=True)
    f = originals / "doc.txt"
    f.write_text("hello")

    create_manifest(case)

    # simulate derivative that points to non-existent source
    add_derivative(
        case,
        "derivatives/proxies/fake.mp4",
        "deadbeef",
        kind="video_proxy",
        preset="web",
        source_sha256="nope",
    )

    res = verify_manifest(case)
    assert "nope" in " ".join(
        res.get("missing", []) + [d.get("path", "") for d in res.get("mismatches", [])]
    ) or res.get("missing")
