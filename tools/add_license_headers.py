#!/usr/bin/env python3
"""
One-time helper to add the required proprietary header to source files.
This is NOT a pre-commit hook. Run manually when needed.

Usage:
  python tools/add_license_headers.py
"""

from __future__ import annotations

from pathlib import Path

HEADER_LINE = "Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.\nPROPRIETARY — See LICENSE.\n"

COMMENT_PREFIX = {
    ".py": "# ",
    ".sh": "# ",
    ".js": "// ",
    ".ts": "// ",
    ".tsx": "// ",
    ".jsx": "// ",
    ".go": "// ",
    ".rs": "// ",
    ".java": "// ",
    ".kt": "// ",
    ".yml": "# ",
    ".yaml": "# ",
}

EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}

INCLUDE_EXTS = set(COMMENT_PREFIX.keys())


def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in EXCLUDE_DIRS)


def has_header(text: str) -> bool:
    return "PROPRIETARY — See LICENSE." in text[:400]


def add_header(path: Path) -> bool:
    ext = path.suffix.lower()
    prefix = COMMENT_PREFIX.get(ext)
    if not prefix:
        return False

    content = path.read_text(encoding="utf-8", errors="ignore")
    if has_header(content):
        return False

    header = "".join(prefix + line if line.strip() else prefix.rstrip() + "\n"
                     for line in HEADER_LINE.splitlines(True))
    new_content = header + "\n" + content
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    changed = 0

    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue
        if should_exclude(p):
            continue
        if p.suffix.lower() not in INCLUDE_EXTS:
            continue

        try:
            if add_header(p):
                changed += 1
        except Exception:
            # Skip files we can't safely edit
            continue

    print(f"Done. Updated {changed} file(s).")


if __name__ == "__main__":
    main()
