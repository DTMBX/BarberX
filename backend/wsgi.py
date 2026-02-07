# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""wsgi.py for production WSGI servers (e.g., gunicorn)

Keep a simple WSGI entry that imports the Flask `app` object defined
by the application packaging. Using the top-level `app` import keeps
compatibility with existing deploy scripts and Docker/Procfile setups.
"""

from app import app

if __name__ == "__main__":
    app.run()
