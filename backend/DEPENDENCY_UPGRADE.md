Dependency upgrade summary

This file documents the dependency adjustments performed on branch `chore/add-tokens-core-and-ci`.

Changes made:

- Pinned `Werkzeug` to `==3.1.5` (matches local venv) to avoid resolver drift and ensure compatibility with Flask 3.1.2.
- Upgraded `Flask-WTF` to `==1.2.2` (fixes imports that relied on Flask->Markup and Werkzeug url helpers).
- Added/pinned test/runtime dependencies used by the backend test-suite: `Flask-Compress==1.14`, `Flask-Cors==4.0.0`, `Flask-Bcrypt==1.0.1`, `bcrypt==4.0.1`, `pypdf==3.12.0` (already included in `requirements-local-dev.txt`).

Temporary fallback removed:

- A file-based import fallback loader (`backend/app/__init__.py`) that attempted to import `backend/src/app.py` directly has been removed. The repository now relies on standard import resolution (`src.app` or `app`).

Why:

- These adjustments stabilize the local test environment and remove runtime shims in favor of compatible library versions.
- Pinning exact minor versions reduces surprises across CI agents and developer machines.

Next recommended actions:

1. Allow CI on PR #50 to run and observe any environment-specific failures.
2. If CI is green, consider applying the same pinned versions to `requirements.txt`/production manifests where appropriate.
3. Run an automated dependency audit (e.g., `pip-audit`) and update transitive packages where security advisories exist.

If you want, I will open (or update) the PR body with this summary and wait for CI results.
