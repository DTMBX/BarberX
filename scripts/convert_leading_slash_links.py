#!/usr/bin/env python3
"""
Scan repository files (.html and .md) and replace leading-slash links
like href="/path" or src="/path" and Markdown links like](/path)
with Jekyll's `{{ '/path' | relative_url }}` helper.
Skips files under _site/ and builds/ and skips fenced code blocks in Markdown.

Usage: python scripts/convert_leading_slash_links.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
exclude_dirs = {"_site", "builds", "dist"}

html_src_pattern = re.compile(r'(href|src)="(/[^"\s]*)"')
md_link_pattern = re.compile(r'\]\((/[^)\s]*)\)')

modified_files = []

for path in root.rglob("*"):
    if not path.is_file():
        continue
    if path.match("*/_site/*") or path.match("*/builds/*") or path.match("*/dist/*"):
        continue
    if path.suffix.lower() not in {".html", ".md"}:
        continue
    text = path.read_text(encoding="utf-8")
    original = text

    if path.suffix.lower() == ".md":
        # Avoid replacements inside fenced code blocks (```)
        parts = re.split(r'(```)', text)
        out_parts = []
        in_code = False
        i = 0
        while i < len(parts):
            part = parts[i]
            if part == '```':
                # append delimiter and toggle
                out_parts.append('```')
                i += 1
                if i < len(parts):
                    out_parts.append(parts[i])
                i += 1
                continue
            # replace links in this non-fenced part
            replaced = md_link_pattern.sub(lambda m: f"]({{ '{m.group(1)}' | relative_url }})", part)
            replaced = html_src_pattern.sub(lambda m: f'{m.group(1)}="{{{{ \'{m.group(2)}\' | relative_url }}}}"', replaced)
            out_parts.append(replaced)
            i += 1
        text = ''.join(out_parts)
    else:
        # HTML file: simple replace for href/src
        text = md_link_pattern.sub(lambda m: f"]({{ '{m.group(1)}' | relative_url }})", text)
        text = html_src_pattern.sub(lambda m: f'{m.group(1)}="{{{{ \'{m.group(2)}\' | relative_url }}}}"', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        modified_files.append(str(path.relative_to(root)))

if modified_files:
    print("Modified files:")
    for f in modified_files:
        print(f)
else:
    print("No files modified.")
