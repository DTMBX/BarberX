# Dependency pinning and license notes (Phase 1)

This document records dependencies introduced by Phase 1 scaffolding and recommended pinning strategy.

Added in Phase 1:

- None (the Phase 1 CLI uses only the Python standard library and PowerShell scripts).

Recommended review & pins for future phases:

- `requests` — MIT or Apache-2.0; pin exact version in `requirements.txt` or `requirements-dev.txt`.
- `PyMuPDF` (fitz) — GPL-compatible; pin to a known stable version if used for PDF extraction.
- `pdfminer.six` — permissive license; pin exact version.
- `pypdf` — BSD/MIT-like; pin exact version.
- `pytest` — for tests; pin in dev requirements.
- `ruff` — optional linter; pin in dev requirements.

Pinning approach:

- Use `requirements.txt` with exact versions and hashes (`pip hash` or `pip-compile`) for production dependencies.
- Use `requirements-dev.txt` for test/dev tools (pytest, ruff, black) also pinned.
- Record license and source for each pinned dependency in this document.

Security & secrets:

- Do not store secrets or API keys in the repo. Use environment variables and `.env.example`.
