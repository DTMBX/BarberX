import os
import sys
import traceback

_here = os.path.dirname(r"C:\web-dev\github-repos\Evident\backend\app")
_candidates = [
    os.path.abspath(os.path.join(_here, "..", "src")),
    os.path.abspath(os.path.join(_here, "..")),
]
_candidates = [
    os.path.abspath(os.path.join(_here, "..", "src")),
    os.path.abspath(os.path.join(_here, "..")),
]
for p in _candidates:
    print("candidate:", p, "exists?", os.path.exists(p))
    if p not in sys.path:
        sys.path.insert(0, p)
print("sys.path[0:6]=", sys.path[:6])
import pprint

print(
    "dir backend/src contains:",
    pprint.pformat(os.listdir(os.path.abspath(os.path.join(_here, "..", "src")))[:50]),
)
for name in ["src.app", "app"]:
    print("\nTrying", name)
    try:
        import importlib

        mod = importlib.import_module(name)
        print("OK ->", getattr(mod, "__file__", None))
    except Exception:
        traceback.print_exc()
