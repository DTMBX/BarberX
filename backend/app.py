# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

from app.root_legacy.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

# Gunicorn entrypoint
app = create_app()
