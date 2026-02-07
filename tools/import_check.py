import importlib
import sys
import traceback

print("sys.path (first 5):", sys.path[:5])

candidates = ["src.app", "app"]
for modname in candidates:
    try:
        importlib.import_module(modname)
        print("OK", modname)
    except Exception:
        print("FAILED", modname)
        traceback.print_exc()
