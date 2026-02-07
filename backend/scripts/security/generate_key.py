# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import os
from pathlib import Path

from cryptography.fernet import Fernet

KEY_ENV = "Evident_ENCRYPTION_KEY"
KEY_PATH = Path(".secrets/Evident.key")


def main() -> None:
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if KEY_PATH.exists():
        print("Key already exists at .secrets/Evident.key")
        print("Use it via environment variable Evident_ENCRYPTION_KEY or keep the file locally.")
        return

    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    print("Generated new encryption key at .secrets/Evident.key")
    print("Export for CI or local use:")
    print(
        f"setx {KEY_ENV} {key.decode()}" if os.name == "nt" else f"export {KEY_ENV}={key.decode()}"
    )


if __name__ == "__main__":
    main()
