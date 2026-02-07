from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Auto-associate OPRA records to case pages (Option B: case tags)

What it does
------------
1) Ensures every case page has: case_slug: <slug>
   - Uses existing front matter 'slug' if present, else derives from filename/permalink.

2) Updates each OPRA record (_opra/**/index.md) to include:
   related_cases:
     - <case_slug_1>
     - <case_slug_2>

How it decides which OPRA belongs to which case
-----------------------------------------------
A) Preferred (deterministic): uses a mapping file if present:
   _data/opra_case_map.yml

   Example:
   opra:
     atlantic-county-acjf-vendors-2025:
       - atl-l-003252-25
       - mer-l-002371-25
     hamilton-township-bodycam-oaths-2024:
       - atl-l-003252-25

B) Heuristic fallback (best-effort): scans OPRA record folder text for case tokens:
   - case slugs (e.g., atl-l-003252-25)
   - common docket patterns (ATL-L-003252-25, MER-L-002371-25, etc.)
   - if found, maps to the matching case_slug

Safe behavior
-------------
- Never deletes existing related_cases entries; it merges.
- Leaves files unchanged if no associations are found.
- Preserves existing front matter formatting as best as possible.

Run
---
From repo root:
  python3 scripts/opra_case_autotag.py

Optional:
  python3 scripts/opra_case_autotag.py --write-map-template
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import yaml  # PyYAML
except ImportError as e:
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from e


REPO_ROOT = Path.cwd()

CASES_DIR_CANDIDATES = ["_cases", "cases"]  # your repo likely uses _cases
OPRA_DIR = "_opra"
DATA_MAP_PATH = Path("_data") / "opra_case_map.yml"

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

# Detect docket-like tokens, then normalize to slug-ish lower-case form.
DOCKET_TOKEN_RE = re.compile(
    r"\b([A-Z]{2,4})\s*-\s*([A-Z])\s*-\s*(\d{3,7})\s*-\s*(\d{2})\b", re.IGNORECASE
)
# Also catch already-slugged case ids like atl-l-003252-25
SLUG_TOKEN_RE = re.compile(r"\b([a-z]{2,4}-[a-z]-\d{3,7}-\d{2})\b", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def split_front_matter(md: str) -> tuple[dict, str]:
    """
    Returns (front_matter_dict, body).
    If no front matter exists, returns ({}, full_text_as_body).
    """
    m = FRONT_MATTER_RE.match(md)
    if not m:
        return {}, md
    fm_raw, body = m.group(1), m.group(2)
    fm = yaml.safe_load(fm_raw) or {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, body


def join_front_matter(fm: dict, body: str) -> str:
    fm_yaml = yaml.safe_dump(
        fm,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    ).strip()
    return f"---\n{fm_yaml}\n---\n{body.lstrip()}"


def find_cases_dir() -> Path:
    for c in CASES_DIR_CANDIDATES:
        p = REPO_ROOT / c
        if p.exists() and p.is_dir():
            return p
    raise SystemExit("Could not find a cases directory. Expected one of: _cases/, cases/")


def normalize_docket_to_slug(prefix: str, letter: str, num: str, year2: str) -> str:
    return f"{prefix.lower()}-{letter.lower()}-{num}-{year2}"


def extract_tokens_from_text(text: str) -> set[str]:
    tokens: set[str] = set()
    for m in DOCKET_TOKEN_RE.finditer(text):
        tokens.add(normalize_docket_to_slug(m.group(1), m.group(2), m.group(3), m.group(4)))
    for m in SLUG_TOKEN_RE.finditer(text):
        tokens.add(m.group(1).lower())
    return tokens


def list_markdown_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.md") if p.is_file()]


def list_opra_record_dirs(opra_root: Path) -> list[Path]:
    dirs = []
    if not opra_root.exists():
        return dirs
    for p in opra_root.iterdir():
        if p.is_dir() and (p / "index.md").exists():
            dirs.append(p)
    return sorted(dirs)


Optional[def load_yaml_if_exists(path: Path) -> dict]:
    if not path.exists():
        return None
    data = yaml.safe_load(read_text(path)) or {}
    return data if isinstance(data, dict) else None


def write_map_template(path: Path) -> None:
    tpl = {
        "opra": {
            "example-opra-record-slug-2025": ["atl-l-003252-25", "mer-l-002371-25"],
        }
    }
    content = yaml.safe_dump(tpl, sort_keys=False, allow_unicode=True, width=120)
    write_text(path, content)


Optional[def ensure_case_slug(case_file: Path) -> str]:
    md = read_text(case_file)
    fm, body = split_front_matter(md)

    # Determine slug
    slug = fm.get("slug")
    if not slug:
        # Try to derive from permalink like /cases/atl-l-003252-25/
        permalink = fm.get("permalink", "")
        m = re.search(r"/cases/([^/]+)/", str(permalink))
        if m:
            slug = m.group(1)
        else:
            # Fallback to filename without extension
            slug = case_file.stem

    slug = str(slug).strip().lower()
    if not slug:
        return None

    changed = False
    if fm.get("case_slug") != slug:
        fm["case_slug"] = slug
        changed = True

    # Keep existing slug field if present; if absent, optionally set it to match
    if not fm.get("slug"):
        fm["slug"] = slug
        changed = True

    if changed:
        write_text(case_file, join_front_matter(fm, body))
    return slug


def build_case_index(cases_dir: Path) -> dict[str, Path]:
    """
    Returns mapping: case_slug -> file path
    """
    idx: dict[str, Path] = {}
    for md_file in list_markdown_files(cases_dir):
        slug = ensure_case_slug(md_file)
        if slug:
            idx[slug] = md_file
    return idx


def opra_dir_slug(opra_record_dir: Path) -> str:
    return opra_record_dir.name.strip().lower()


def gather_opra_text_blob(opra_record_dir: Path) -> str:
    """
    Gather text from index.md + notes.md + timeline.yml (and any .md/.txt in the record dir),
    but avoids heavy binary.
    """
    parts: list[str] = []
    for rel in ["index.md", "notes.md", "timeline.yml"]:
        p = opra_record_dir / rel
        if p.exists():
            parts.append(read_text(p))

    # Also include any exported .txt or .md in subfolders
    for p in opra_record_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in [".md", ".txt", ".yml", ".yaml"]:
            # Skip huge files > 2MB
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            parts.append(read_text(p))
    return "\n\n".join(parts)


Optional[def merge_unique_list(existing: list], add: list[str]) -> list[str]:
    out: list[str] = []
    seen = set()
    for x in existing or []:
        sx = str(x).strip().lower()
        if sx and sx not in seen:
            out.append(sx)
            seen.add(sx)
    for x in add:
        sx = str(x).strip().lower()
        if sx and sx not in seen:
            out.append(sx)
            seen.add(sx)
    return out


def update_opra_related_cases(opra_record_dir: Path, related_slugs: list[str]) -> bool:
    index_path = opra_record_dir / "index.md"
    if not index_path.exists():
        return False

    md = read_text(index_path)
    fm, body = split_front_matter(md)

    current = fm.get("related_cases")
    merged = merge_unique_list(current if isinstance(current, list) else [], related_slugs)
    if merged == (current if isinstance(current, list) else []):
        return False

    fm["related_cases"] = merged
    write_text(index_path, join_front_matter(fm, body))
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--write-map-template", action="store_true", help="Create _data/opra_case_map.yml template"
    )
    args = ap.parse_args()

    if args.write_map_template:
        write_map_template(DATA_MAP_PATH)
        print(f"Wrote template: {DATA_MAP_PATH}")
        return

    cases_dir = find_cases_dir()
    opra_root = REPO_ROOT / OPRA_DIR
    if not opra_root.exists():
        raise SystemExit("No _opra/ folder found at repo root.")

    case_index = build_case_index(cases_dir)
    all_case_slugs = set(case_index.keys())

    mapping_data = load_yaml_if_exists(DATA_MAP_PATH)
    opra_map = {}
    if mapping_data and "opra" in mapping_data and isinstance(mapping_data["opra"], dict):
        # normalize keys/values
        for k, v in mapping_data["opra"].items():
            if not isinstance(v, list):
                continue
            opra_map[str(k).strip().lower()] = [str(x).strip().lower() for x in v if str(x).strip()]

    opra_dirs = list_opra_record_dirs(opra_root)

    changed_any = False
    for od in opra_dirs:
        slug = opra_dir_slug(od)

        # A) deterministic mapping
        if slug in opra_map:
            related = [s for s in opra_map[slug] if s in all_case_slugs]
        else:
            # B) heuristic scan
            blob = gather_opra_text_blob(od)
            tokens = extract_tokens_from_text(blob)
            related = [t for t in sorted(tokens) if t in all_case_slugs]

        if not related:
            continue

        changed = update_opra_related_cases(od, related)
        if changed:
            changed_any = True
            print(f"Updated OPRA related_cases: {slug} -> {related}")

    if not changed_any:
        print("No OPRA records updated (no associations found, or already up to date).")
    else:
        print("Done.")


if __name__ == "__main__":
    main()