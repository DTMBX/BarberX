# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Expose the Flask `app` object for tests that import `from app import app`.

Try multiple import paths so the package works whether tests run with
`backend` on PYTHONPATH or with the repository root on PYTHONPATH.
"""
import importlib
import traceback
import os
import sys

# Ensure backend/src and backend are on sys.path so tests can import the application
_here = os.path.dirname(__file__)
_candidates = [os.path.abspath(os.path.join(_here, "..", "src")), os.path.abspath(os.path.join(_here, ".."))]
for _p in _candidates:
	if _p not in sys.path:
		sys.path.insert(0, _p)

# Ensure SECRET_KEY exists during tests to allow import-time config to pass.
if not os.environ.get("SECRET_KEY"):
	os.environ["SECRET_KEY"] = "test-secret-key"

__all__ = ["app"]

def _load_app():
	# Try importing top-level `app` first, then `src.app` for environments
	# where `backend/src` is not a package. This order is more robust when
	# tests add `backend/src` to sys.path (so `app.py` is importable as `app`).
	candidates = ["app", "src.app"]
	# Debug info to help diagnose import resolution in CI/test environments
	try:
		print("[DEBUG] sys.path[0:6]=", sys.path[0:6])
		print("[DEBUG] import candidates=", candidates)
	except Exception:
		pass
	for modname in candidates:
		try:
			mod = importlib.import_module(modname)
			if hasattr(mod, "app"):
				return getattr(mod, "app")
		except Exception:
			# Print per-candidate traceback to help diagnose import failures
			try:
				print(f"[DEBUG] failed importing {modname}: \n", traceback.format_exc())
			except Exception:
				pass
			# try next candidate
			continue
	# Fallback: try loading backend/src/app.py directly by path. This makes
	# the import robust when `backend/src` isn't a package and tests run from
	# different working directories.
	src_app_path = os.path.abspath(os.path.join(_here, "..", "src", "app.py"))
	if os.path.exists(src_app_path):
		try:
			spec = importlib.util.spec_from_file_location("app", src_app_path)
			mod = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(mod)
			if hasattr(mod, "app"):
				return getattr(mod, "app")
		except Exception:
			pass

	raise ImportError("Could not import Flask `app` from any candidate modules: " + \
					  ", ".join(candidates) + " or file: " + src_app_path + "\n" + traceback.format_exc())


app = _load_app()

# If running under tests, enable testing mode and disable CSRF checks to allow
# unit tests to exercise routes without browser CSRF tokens.
try:
	app.config.setdefault("TESTING", True)
	app.config.setdefault("WTF_CSRF_ENABLED", False)
except Exception:
	pass

