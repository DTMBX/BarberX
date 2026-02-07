#!/usr/bin/env python3
# Copyright © 2024–2026 BARBER CAM, Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Strip common white-background "canvas" artifacts from SVG files.

What it does (safe-ish defaults):
- Removes root <svg> style background declarations when they're white.
- Removes <rect> elements that:
  * look like a full-artboard background (x=0,y=0 and width/height match viewBox or 100%),
  * and are filled white (direct fill or via style).
- Creates .bak backups before modifying.

Usage:
  python strip_svg_white_bg.py "C:\\path\\to\\your\\repo"
  python strip_svg_white_bg.py ./ --dry-run
"""

from __future__ import annotations
from typing import Optional

import argparse
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

WHITE_VALUES = {"white", "#fff", "#ffffff", "rgb(255,255,255)", "rgb(255, 255, 255)"}


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().lower())


def parse_style(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def is_white_color(v: str) -> bool:
    return norm(v) in {norm(x) for x in WHITE_VALUES}


Optional[def get_attr(el: ET.Element, name: str) -> str]:
    return el.attrib.get(name)


def strip_root_white_background(svg: ET.Element) -> bool:
    """Remove root style background declarations if white."""
    style = svg.attrib.get("style")
    if not style:
        return False
    styles = parse_style(style)
    changed = False

    # background / background-color
    for key in ("background", "background-color"):
        if key in styles and is_white_color(styles[key]):
            del styles[key]
            changed = True

    if changed:
        # rebuild style string
        new_style = "; ".join(f"{k}: {v}" for k, v in styles.items())
        if new_style.strip():
            svg.attrib["style"] = new_style
        else:
            del svg.attrib["style"]
    return changed


Optional[def parse_viewbox(svg: ET.Element) -> tuple[float, float, float, float]]:
    vb = svg.attrib.get("viewBox") or svg.attrib.get("viewbox")
    if not vb:
        return None
    parts = re.split(r"[,\s]+", vb.strip())
    if len(parts) != 4:
        return None
    try:
        return tuple(float(p) for p in parts)  # minx, miny, w, h
    except ValueError:
        return None


Optional[def to_float(v: str]Optional[) -> float]:
    if v is None:
        return None
    v = v.strip()
    if v.endswith("%"):
        return None
    # strip common units
    v = re.sub(r"(px|pt|pc|mm|cm|in)$", "", v)
    try:
        return float(v)
    except ValueError:
        return None


def looks_like_full_canvas_rect(rect: ET.Element, svg: ET.Element) -> bool:
    """
    Identify a <rect> that likely represents the artboard background.
    Heuristics:
    - x,y are 0 or missing
    - width/height match:
      * 100% or
      * viewBox w/h or
      * svg width/height
    """
    x = rect.attrib.get("x", "0").strip()
    y = rect.attrib.get("y", "0").strip()

    if norm(x) not in {"0", "0.0"}:
        return False
    if norm(y) not in {"0", "0.0"}:
        return False

    w = rect.attrib.get("width")
    h = rect.attrib.get("height")
    if not w or not h:
        return False

    w_n = norm(w)
    h_n = norm(h)

    # obvious full canvas
    if w_n == "100%" and h_n == "100%":
        return True

    vb = parse_viewbox(svg)
    if vb:
        _, _, vb_w, vb_h = vb
        rw = to_float(w)
        rh = to_float(h)
        if rw is not None and rh is not None:
            # allow tiny tolerance
            if abs(rw - vb_w) < 0.01 and abs(rh - vb_h) < 0.01:
                return True

    # fallback to svg width/height attributes if numeric
    svg_w = to_float(svg.attrib.get("width"))
    svg_h = to_float(svg.attrib.get("height"))
    rw = to_float(w)
    rh = to_float(h)
    if svg_w is not None and svg_h is not None and rw is not None and rh is not None:
        if abs(rw - svg_w) < 0.01 and abs(rh - svg_h) < 0.01:
            return True

    return False


def rect_is_white(rect: ET.Element) -> bool:
    fill = rect.attrib.get("fill")
    if fill and is_white_color(fill):
        return True

    style = rect.attrib.get("style", "")
    if style:
        styles = parse_style(style)
        if "fill" in styles and is_white_color(styles["fill"]):
            return True

    # Some exports use opacity + white via rgb
    if fill and norm(fill).startswith("rgb(") and is_white_color(fill):
        return True

    return False


def remove_white_bg_rects(tree: ET.ElementTree) -> int:
    """
    Remove white full-canvas rects.
    xml.etree doesn't provide parent pointers, so we walk and remove from known parents.
    """
    root = tree.getroot()
    removed = 0

    # Iterate all parents and check their direct children
    for parent in root.iter():
        children = list(parent)
        for child in children:
            tag = child.tag.split("}")[-1]  # handle namespaces
            if tag != "rect":
                continue
            if looks_like_full_canvas_rect(child, root) and rect_is_white(child):
                parent.remove(child)
                removed += 1
    return removed


def process_svg(path: Path, dry_run: bool = False) -> tuple[bool, str]:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        return False, f"ERROR parse: {e}"

    changed = False
    notes = []

    if strip_root_white_background(root):
        changed = True
        notes.append("removed root white background style")

    removed_rects = remove_white_bg_rects(tree)
    if removed_rects:
        changed = True
        notes.append(f"removed {removed_rects} white canvas rect(s)")

    if not changed:
        return False, "no change"

    if dry_run:
        return True, "DRY-RUN: " + "; ".join(notes)

    # backup
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(path, bak)

    # write back
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return True, "; ".join(notes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Folder to scan recursively for .svg")
    ap.add_argument("--dry-run", action="store_true", help="Don't modify files")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 2

    svg_files = list(root.rglob("*.svg"))
    if not svg_files:
        print("No .svg files found.")
        return 0

    changed_count = 0
    for f in svg_files:
        changed, msg = process_svg(f, dry_run=args.dry_run)
        if changed:
            changed_count += 1
        print(f"[{'CHANGED' if changed else 'SKIP'}] {f} :: {msg}")

    print(f"\nDone. Files changed: {changed_count} / {len(svg_files)}")
    if not args.dry_run:
        print("Backups: *.svg.bak (only created once per file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())