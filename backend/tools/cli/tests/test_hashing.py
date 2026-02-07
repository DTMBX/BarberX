import hashlib
from pathlib import Path

from backend.tools.cli.hashing import compute_sha256


def test_compute_sha256(tmp_path: Path):
    p = tmp_path / "sample.txt"
    data = b"hello-evident"
    p.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    got = compute_sha256(p)
    assert got == expected
