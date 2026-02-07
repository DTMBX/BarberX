#!/usr/bin/env python3
# Copyright © 2024–2026 BARBER CAM, Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
svg_make_variants.py
Create .light.svg and .dark.svg variants from source SVGs by remapping
neutral fills/strokes and fixing low-contrast elements using brand tokens.

- Scans a directory (default: assets/img/logo)
- Skips *.bak, *.light.svg, *.dark.svg
- Writes <name>.light.svg and <name>.dark.svg next to original (or out dir)
- Produces a CSV report with per-file contrast score summary

This is intentionally conservative:
- Keeps gradients/patterns (fill="url(#...)") untouched
- Keeps 'none' untouched
- Only remaps simple color values (hex/rgb)
"""

from __future__ import annotations
from typing import Optional

import argparse
import csv
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_RE = re.compile(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$")
RGBA_RE = re.compile(r"^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)$")


@dataclass(frozen=True)
class ThemeTokens:
    name: str
    bg: str
    ink: str
    ink_soft: str
    accent: str
    accent_blue: str
    accent_gold: str


LIGHT = ThemeTokens(
    name="light",
    bg="#fafafa",
    ink="#0a0a0f",
    ink_soft="#1a1a2e",
    accent="#c41e3a",
    accent_blue="#1e40af",
    accent_gold="#d4a574",
)

DARK = ThemeTokens(
    name="dark",
    bg="#0a0a0f",
    ink="#f5f5f7",
    ink_soft="#e5e5e7",
    accent="#c41e3a",
    accent_blue="#3b82f6",
    accent_gold="#d4a574",
)


# Candidate palette used for "fix low contrast" substitutions
def palette_for(theme: ThemeTokens) -> tuple[str, ...]:
    return (theme.ink, theme.ink_soft, theme.accent, theme.accent_blue, theme.accent_gold)


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


Optional[def parse_color(s: str) -> tuple[int, int, int, float]]:
    """Return (r,g,b,a) or None if unsupported."""
    s = s.strip()
    if s.lower() in ("none", "transparent"):
        return None
    if s.startswith("url("):  # gradients/patterns
        return None

    m = HEX_RE.match(s)
    if m:
        hx = m.group(1)
        if len(hx) == 3:
            r = int(hx[0] * 2, 16)
            g = int(hx[1] * 2, 16)
            b = int(hx[2] * 2, 16)
            return (r, g, b, 1.0)
        if len(hx) == 6:
            r = int(hx[0:2], 16)
            g = int(hx[2:4], 16)
            b = int(hx[4:6], 16)
            return (r, g, b, 1.0)
        if len(hx) == 8:
            r = int(hx[0:2], 16)
            g = int(hx[2:4], 16)
            b = int(hx[4:6], 16)
            a = int(hx[6:8], 16) / 255.0
            return (r, g, b, a)

    m = RGB_RE.match(s)
    if m:
        r, g, b = map(int, m.groups())
        return (r, g, b, 1.0)

    m = RGBA_RE.match(s)
    if m:
        r, g, b = map(int, m.groups()[:3])
        a = float(m.group(4))
        return (r, g, b, clamp01(a))

    return None


def to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def srgb_to_lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    R = srgb_to_lin(r)
    G = srgb_to_lin(g)
    B = srgb_to_lin(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    L1 = rel_luminance(fg)
    L2 = rel_luminance(bg)
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)


def is_neutral(rgb: tuple[int, int, int], tol: int = 18) -> bool:
    r, g, b = rgb
    return (max(r, g, b) - min(r, g, b)) <= tol


def dist(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5


def rgb_of_hex(h: str) -> tuple[int, int, int]:
    c = parse_color(h)
    assert c is not None
    return (c[0], c[1], c[2])


def choose_best_color(
    current: tuple[int, int, int],
    theme: ThemeTokens,
    min_ratio: float = 4.5,
) -> tuple[tuple[int, int, int], float]:
    """Pick a palette token that maximizes contrast vs background; prefer close hue if already near a token."""
    bg = rgb_of_hex(theme.bg)

    candidates = [rgb_of_hex(x) for x in palette_for(theme)]
    scored = [(contrast_ratio(c, bg), c) for c in candidates]
    scored.sort(reverse=True, key=lambda x: x[0])

    # If current already meets target, keep it
    cur_ratio = contrast_ratio(current, bg)
    if cur_ratio >= min_ratio:
        return current, cur_ratio

    # Otherwise choose highest contrast
    best_ratio, best = scored[0]
    return best, best_ratio


def theme_map_neutral(rgb: tuple[int, int, int], theme: ThemeTokens) -> tuple[int, int, int]:
    """
    Neutral mapping:
    - In light theme, neutrals go dark (ink/ink_soft)
    - In dark theme, neutrals go light (ink/ink_soft)
    We decide "ink vs ink_soft" based on brightness.
    """
    # brightness proxy
    lum = rel_luminance(rgb)  # 0..1-ish
    ink = rgb_of_hex(theme.ink)
    ink_soft = rgb_of_hex(theme.ink_soft)

    # If element is very prominent light neutral in light theme, use ink_soft for softer look
    # In dark theme, both inks are light; choose softer for mid neutrals
    if theme.name == "light":
        return ink_soft if lum < 0.08 else ink
    else:
        return ink if lum < 0.25 else ink_soft


def update_style_attr(style: str, key: str, new_value: str) -> str:
    """
    Replace/insert key:value in inline style="...".
    Conservative: simple split by ; then rebuild.
    """
    parts = [p.strip() for p in style.split(";") if p.strip()]
    kv: dict[str, str] = {}
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            kv[k.strip()] = v.strip()
    kv[key] = new_value
    return "; ".join(f"{k}: {v}" for k, v in kv.items())


def process_svg(
    svg_path: Path, out_dir: Path, theme: ThemeTokens, min_ratio: float
) -> dict[str, Any]:
    ns = {"svg": "http://www.w3.org/2000/svg"}
    ET.register_namespace("", ns["svg"])

    tree = ET.parse(svg_path)
    root = tree.getroot()

    bg_rgb = rgb_of_hex(theme.bg)

    # Track ratios we see (best/worst)
    ratios = []

    def handle_attr(elem: ET.Element, attr: str) -> int:
        changed = 0
        val = elem.get(attr)
        if not val:
            return 0

        c = parse_color(val)
        if c is None:
            return 0

        r, g, b, a = c
        if a == 0.0:
            return 0

        cur = (r, g, b)
        cur_ratio = contrast_ratio(cur, bg_rgb)
        ratios.append(cur_ratio)

        new_rgb = cur

        # If neutral, map to theme ink/ink_soft
        if is_neutral(cur):
            new_rgb = theme_map_neutral(cur, theme)

        # Enforce contrast minimum by picking best token if needed
        new_rgb, new_ratio = choose_best_color(new_rgb, theme, min_ratio=min_ratio)
        ratios.append(new_ratio)

        new_hex = to_hex(new_rgb)
        if new_hex.lower() != val.lower():
            elem.set(attr, new_hex)
            changed += 1
        return changed

    # Walk all elements and update fill/stroke + style fill/stroke
    changed_count = 0
    for elem in root.iter():
        changed_count += handle_attr(elem, "fill")
        changed_count += handle_attr(elem, "stroke")

        style = elem.get("style")
        if style:
            # style fill/stroke
            for key in ("fill", "stroke"):
                m = re.search(rf"(?:^|;)\s*{key}\s*:\s*([^;]+)", style)
                if not m:
                    continue
                raw = m.group(1).strip()
                c = parse_color(raw)
                if c is None:
                    continue
                r, g, b, a = c
                if a == 0.0:
                    continue
                cur = (r, g, b)
                cur_ratio = contrast_ratio(cur, bg_rgb)
                ratios.append(cur_ratio)

                new_rgb = cur
                if is_neutral(cur):
                    new_rgb = theme_map_neutral(cur, theme)
                new_rgb, new_ratio = choose_best_color(new_rgb, theme, min_ratio=min_ratio)
                ratios.append(new_ratio)

                new_hex = to_hex(new_rgb)
                if new_hex.lower() != raw.lower():
                    style = update_style_attr(style, key, new_hex)
                    elem.set("style", style)
                    changed_count += 1

    # Output path
    out_name = svg_path.stem + f".{theme.name}.svg"
    out_path = out_dir / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)

    if ratios:
        worst = min(ratios)
        best = max(ratios)
        avg = sum(ratios) / len(ratios)
    else:
        worst = best = avg = 0.0

    return {
        "file": str(svg_path),
        "theme": theme.name,
        "out": str(out_path),
        "changed_props": changed_count,
        "contrast_min": round(worst, 2),
        "contrast_avg": round(avg, 2),
        "contrast_max": round(best, 2),
        "target_min": min_ratio,
        "bg": theme.bg,
    }


def iter_svgs(in_dir: Path):
    for p in in_dir.rglob("*.svg"):
        name = p.name.lower()
        if name.endswith(".bak"):
            continue
        if name.endswith(".light.svg") or name.endswith(".dark.svg"):
            continue
        yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="assets/img/logo", help="Directory to scan for source SVGs")
    ap.add_argument(
        "--out-dir", default="", help="Output directory (default: same as source file directory)"
    )
    ap.add_argument(
        "--min-contrast", type=float, default=4.5, help="Minimum contrast ratio to target"
    )
    ap.add_argument(
        "--report", default="scripts/svg_variants_report.csv", help="CSV report output path"
    )
    ap.add_argument("--dry-run", action="store_true", help="Analyze only, do not write files")
    args = ap.parse_args()

    repo_root = Path.cwd()
    in_dir = (repo_root / args.in_dir).resolve()
    if not in_dir.exists():
        raise SystemExit(f"Input directory not found: {in_dir}")

    report_path = (repo_root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for svg in iter_svgs(in_dir):
        src_dir = svg.parent
        out_dir = (repo_root / args.out_dir).resolve() if args.out_dir else src_dir

        if args.dry_run:
            # Still parse and score, but don't write
            for theme in (LIGHT, DARK):
                row = process_svg(svg, out_dir, theme, args.min_contrast)
                row["out"] = "(dry-run)"
                rows.append(row)
                print(
                    f"[DRY] {svg} -> {theme.name} | min {row['contrast_min']} avg {row['contrast_avg']} max {row['contrast_max']}"
                )
        else:
            for theme in (LIGHT, DARK):
                row = process_svg(svg, out_dir, theme, args.min_contrast)
                rows.append(row)
                print(
                    f"[OK] {svg.name} -> {Path(row['out']).name} | changed {row['changed_props']} | min {row['contrast_min']}"
                )

    # Write report
    if rows:
        fieldnames = list(rows[0].keys())
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()