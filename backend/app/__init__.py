# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Expose the Flask `app` object for tests that import `from app import app`.

Try multiple import paths so the package works whether tests run with
`backend` on PYTHONPATH or with the repository root on PYTHONPATH.
"""

import importlib
import os
import sys
import traceback

# Ensure backend/src and backend are on sys.path so tests can import the application
_here = os.path.dirname(__file__)
_candidates = [
    os.path.abspath(os.path.join(_here, "..", "src")),
    os.path.abspath(os.path.join(_here, "..")),
]
for _p in _candidates:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Ensure SECRET_KEY exists during tests to allow import-time config to pass.
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test-secret-key"

__all__ = ["app"]


def _load_app():
    # Standard import resolution: try package import paths in order.
    candidates = ["src.app", "app"]
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, "app"):
                return mod.app
        except Exception:
            continue
    raise ImportError(
        "Could not import Flask `app` from any candidate modules: " + ", ".join(candidates)
    )


app = _load_app()

# If running under tests, enable testing mode and disable CSRF checks to allow
# unit tests to exercise routes without browser CSRF tokens.
try:
    app.config.setdefault("TESTING", True)
    app.config.setdefault("WTF_CSRF_ENABLED", False)
except Exception:
    pass
