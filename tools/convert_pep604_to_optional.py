#!/usr/bin/env python3
"""Convert occurrences of `X | None` to `Optional[X]` across the repository.

This is a conservative, regex-based helper intended to handle the common
cases where a type annotation uses the PEP 604 union with None (e.g.
`str | None`, `list[int] | None`). It will add `from typing import Optional`
to files that need it.

Run from the repository root:
    python tools/convert_pep604_to_optional.py

Review changes before committing.
"""
from __future__ import annotations

import re
from pathlib import Path

EXCLUDE_DIRS = {".git", "env", "venv", "_site", "builds", "node_modules"}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


PATTERN = re.compile(r"(?P<left>[^\n#]+?)\s*\|\s*None")


def convert_text(text: str) -> str:
    if "| None" not in text:
        return text

    def repl(m: re.Match) -> str:
        left = m.group("left").strip()
        # Don't attempt replacements inside string literals or comments.
        if left.startswith(('"', "'")):
            return m.group(0)
        return f"Optional[{left}]"

    new = PATTERN.sub(repl, text)

    # Add typing import if needed
    if "Optional[" in new and "from typing import Optional" not in new:
        # try to put after future imports or other imports
        lines = new.splitlines()
        insert_at = 0
        for i, ln in enumerate(lines[:30]):
            if ln.startswith("from __future__ import"):
                insert_at = i + 1
        # place after the first non-empty line in the header imports area
        lines.insert(insert_at, "from typing import Optional")
        new = "\n".join(lines)

    return new


def main() -> int:
    repo = Path(".")
    changed = []
    for p in repo.rglob("*.py"):
        if should_skip(p):
            continue
        # skip the conversion script itself
        if p.resolve() == Path(__file__).resolve():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new = convert_text(text)
        if new != text:
            p.write_text(new, encoding="utf-8")
            changed.append(p)
            print(f"Updated: {p}")

    if not changed:
        print("No files changed.")
        return 0
    print(f"Modified {len(changed)} files. Review and commit changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
