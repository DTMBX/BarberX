import os
import sys
import traceback

_here = os.path.dirname(r"C:\web-dev\github-repos\Evident\backend\app")
_candidates = [
    os.path.abspath(os.path.join(_here, "..", "src")),
    os.path.abspath(os.path.join(_here, "..")),
]
print("candidates:", _candidates)
for p in _candidates:
    if p not in sys.path:
        sys.path.insert(0, p)
print("sys.path[0:6]=", sys.path[:6])
print("\nTrying import app:")
try:
    import app

    print("imported app module:", getattr(app, "__file__", None))
except Exception:
    traceback.print_exc()
print("\nTrying import src.app:")
try:
    import importlib

    importlib.import_module("src.app")
    print("imported src.app")
except Exception:
    traceback.print_exc()
