from pathlib import Path
from unittest.mock import patch

from backend.tools.cli.ffmpeg_proxy import create_video_proxy
from backend.tools.cli.hashing import compute_sha256
from backend.tools.cli.manifest import create_manifest, load_canonical


def _fake_ffmpeg_write(out_path: Path):
    # write predictable bytes so hash is deterministic
    out_path.write_bytes(b"proxy-bytes")


def test_ffmpeg_proxy_creates_derivative(tmp_path: Path):
    case = tmp_path / "CASE1"
    originals = case / "originals"
    originals.mkdir(parents=True)
    orig = originals / "video.mp4"
    orig.write_bytes(b"original-bytes")

    # create canonical manifest first
    create_manifest(case)

    # mock subprocess.check_call to create the output file instead of running ffmpeg
    with patch("subprocess.check_call") as fake_call:

        def side_effect(cmd):
            # compute expected out_path from code behavior: filename will be <origsha>.<preset>.mp4
            orig_sha = compute_sha256(orig)
            out = case / "derivatives" / "proxies" / f"{orig_sha}.web.mp4"
            out.parent.mkdir(parents=True, exist_ok=True)
            _fake_ffmpeg_write(out)

        fake_call.side_effect = side_effect
        out_path, proxy_sha = create_video_proxy(case, str(orig.relative_to(case)), preset="web")

    assert out_path.exists()
    assert proxy_sha == compute_sha256(out_path)

    # verify derivative recorded in canonical manifest
    canonical = load_canonical(case)
    derivs = canonical.get("derivatives", [])
    assert len(derivs) == 1
    d = derivs[0]
    assert d["source_sha256"] == compute_sha256(orig)
    assert d["sha256"] == proxy_sha
