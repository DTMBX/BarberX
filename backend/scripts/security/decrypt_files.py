# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import argparse
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

KEY_ENV = "Evident_ENCRYPTION_KEY"
MANIFEST_PATH = Path("secure/manifest.json")
KEY_PATH = Path(".secrets/Evident.key")


def load_key() -> bytes:
    if os.getenv(KEY_ENV):
        return os.getenv(KEY_ENV).encode()
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    raise SystemExit(
        "Encryption key not found. Run scripts/security/generate_key.py or set Evident_ENCRYPTION_KEY."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit("Manifest not found. Nothing to decrypt.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    key = load_key()
    fernet = Fernet(key)

    for record in manifest.get("files", []):
        enc_path = Path(record["enc_path"])
        if not enc_path.exists():
            continue
        data = fernet.decrypt(enc_path.read_bytes())
        out_path = Path(record["path"])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)


if __name__ == "__main__":
    main()
