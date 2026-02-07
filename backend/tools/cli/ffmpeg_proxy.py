"""Create proxies/derivatives using ffmpeg while preserving original SHA-256 references."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .hashing import compute_sha256
from .manifest import add_derivative


def create_video_proxy(
    case_dir: Path, original_rel_path: str, preset: str = "web"
) -> tuple[Path, str]:
    """Create a proxy video for the given original file.

    Returns (proxy_path, proxy_sha256)
    """
    originals_dir = case_dir / "originals"
    orig = case_dir / original_rel_path
    if not orig.exists():
        raise FileNotFoundError(f"Original not found: {orig}")

    orig_sha = compute_sha256(orig)
    proxies_dir = case_dir / "derivatives" / "proxies"
    proxies_dir.mkdir(parents=True, exist_ok=True)

    # create deterministic filename: <origsha>.<preset>.mp4
    out_name = f"{orig_sha}.{preset}.mp4"
    out_path = proxies_dir / out_name

    # ffmpeg command depending on preset
    if preset == "web":
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i",
            str(orig),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "28",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(out_path),
        ]
    else:
        # review preset: higher quality
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i",
            str(orig),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(out_path),
        ]

    # run ffmpeg (may be mocked in tests)
    subprocess.check_call(cmd)

    proxy_sha = compute_sha256(out_path)

    # register derivative in canonical manifest
    rel_out = str(out_path.relative_to(case_dir)).replace("\\", "/")
    # include tool information and a command fingerprint
    add_derivative(
        case_dir, rel_out, proxy_sha, kind="video_proxy", preset=preset, source_sha256=orig_sha
    )

    return out_path, proxy_sha
