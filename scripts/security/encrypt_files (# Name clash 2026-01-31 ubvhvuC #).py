from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import argparse
import glob
import hashlib
import json
import os
import subprocess
from pathlib import Path

from cryptography.fernet import Fernet

KEY_ENV = "Evident_ENCRYPTION_KEY"
DEFAULT_CONFIG = Path("security/encryption_config.json")
MANIFEST_PATH = Path("secure/manifest.json")
SECURE_DIR = Path("secure")
KEY_PATH = Path(".secrets/Evident.key")


def load_key() -> bytes:
    if os.getenv(KEY_ENV):
        return os.getenv(KEY_ENV).encode()
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    raise SystemExit(
        "Encryption key not found. Run scripts/security/generate_key.py or set Evident_ENCRYPTION_KEY."
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode()).hexdigest()[:16]
    base = Path(relative_path).name
    return f"{base}.{digest}.enc"


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"files": []}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def collect_files(config: dict) -> list[Path]:
    include = config.get("encrypt_globs", [])
    exclude = config.get("exclude_globs", [])

    paths: list[Path] = []
    for pattern in include:
        for match in glob.glob(pattern, recursive=True):
            path = Path(match)
            if path.is_dir():
                continue
            paths.append(path)

    filtered: list[Path] = []
    for path in paths:
        rel = path.as_posix()
        if any(glob.fnmatch.fnmatch(rel, ex) for ex in exclude):
            continue
        filtered.append(path)

    return sorted(set(filtered))


Optional[def encrypt_file(fernet: Fernet, path: Path, manifest: dict) -> dict]:
    rel = path.as_posix()
    data = path.read_bytes()
    digest = sha256_bytes(data)

    existing = next((f for f in manifest["files"] if f["path"] == rel), None)
    if existing and existing.get("sha256") == digest:
        return None

    enc_name = safe_name(rel)
    enc_path = SECURE_DIR / enc_name
    enc_path.parent.mkdir(parents=True, exist_ok=True)
    enc_path.write_bytes(fernet.encrypt(data))

    record = {
        "path": rel,
        "enc_path": enc_path.as_posix(),
        "sha256": digest,
        "size": path.stat().st_size,
        "mtime": path.stat().st_mtime,
    }

    manifest["files"] = [f for f in manifest["files"] if f["path"] != rel]
    manifest["files"].append(record)
    return record


def stage_files(paths: list[Path]) -> None:
    for path in paths:
        try:
            subprocess.run(["git", "rm", "--cached", "-q", "--", str(path)], check=False)
        except Exception:
            pass


def stage_secure() -> None:
    subprocess.run(["git", "add", str(MANIFEST_PATH)], check=False)
    for enc in SECURE_DIR.glob("*.enc"):
        subprocess.run(["git", "add", str(enc)], check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    files = collect_files(config)

    if not files:
        return

    key = load_key()
    fernet = Fernet(key)
    manifest = load_manifest()

    updated = []
    for path in files:
        record = encrypt_file(fernet, path, manifest)
        if record:
            updated.append(path)

    if updated:
        save_manifest(manifest)

    if args.stage and updated:
        stage_files(updated)
        stage_secure()


if __name__ == "__main__":
    main()