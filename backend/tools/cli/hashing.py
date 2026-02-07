"""Simple, dependency-free hashing utilities for evidence files."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path


def compute_sha256(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hex digest for a file.

    Args:
        path: Path to file
        chunk_size: bytes per read
    Returns:
        hex digest string
    """
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            yield p
