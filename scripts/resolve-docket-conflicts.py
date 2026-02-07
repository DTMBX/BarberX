# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Resolve Git merge conflicts in docket YAML files
Chooses the newer format and removes duplicate /assets/ prefix
"""

import os
import re
from pathlib import Path


def resolve_conflicts(file_path):
    """Resolve merge conflicts in a YAML file"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    if "<<<<<<< HEAD" not in content:
        return False, 0

    original_content = content
    conflict_count = 0

    # Pattern 1: Simple conflict (most common)
    # Choose the newer version (after =======) and fix double /assets/
    pattern1 = re.compile(
        r"<<<<<<< HEAD\n"
        r"  file: /assets/assets/(.*?)\n"
        r"=======\n"
        r"  file: /assets/assets/(.*?)\n"
        r">>>>>>> [^\n]+\n",
        re.MULTILINE,
    )

    def replace1(match):
        nonlocal conflict_count
        conflict_count += 1
        newer_path = match.group(2)
        return f"  file: /assets/{newer_path}\n"

    content = pattern1.sub(replace1, content)

    # Pattern 2: Nested conflict (three-way merge)
    pattern2 = re.compile(
        r"<<<<<<< HEAD\n"
        r"<<<<<<< HEAD\n"
        r"  file: /assets/assets/(.*?)\n"
        r"=======\n"
        r"  file: /assets/assets/(.*?)\n"
        r">>>>>>> [^\n]+\n"
        r"=======\n"
        r"  file: /assets/assets/(.*?)\n"
        r">>>>>>> [^\n]+\n",
        re.MULTILINE,
    )

    def replace2(match):
        nonlocal conflict_count
        conflict_count += 1
        # Use the third (most recent) path
        newest_path = match.group(3)
        return f"  file: /assets/{newest_path}\n"

    content = pattern2.sub(replace2, content)

    # Pattern 3: Identical conflicts (both sides same, just remove markers)
    pattern3 = re.compile(
        r"<<<<<<< HEAD\n"
        r"(  file: /assets/assets/.*?)\n"
        r"=======\n"
        r"\1\n"
        r">>>>>>> [^\n]+\n",
        re.MULTILINE,
    )

    def replace3(match):
        nonlocal conflict_count
        conflict_count += 1
        file_line = match.group(1)
        # Fix double /assets/ if present
        fixed_line = file_line.replace("/assets/assets/", "/assets/")
        return f"{fixed_line}\n"

    content = pattern3.sub(replace3, content)

    # Write back if changes were made
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, conflict_count

    return False, 0


def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    docket_dir = root_dir / "_data" / "docket"

    print("🔧 Resolving merge conflicts in docket YAML files...\n")

    total_files = 0
    total_conflicts = 0

    for yaml_file in sorted(docket_dir.glob("*.yml")):
        changed, conflicts = resolve_conflicts(yaml_file)
        if changed:
            total_files += 1
            total_conflicts += conflicts
            print(f"✅ Fixed {yaml_file.name}: {conflicts} conflicts resolved")

    print(f"\n✨ Complete! Fixed {total_conflicts} conflicts in {total_files} files.")

    if total_files == 0:
        print("   No conflicts found.")


if __name__ == "__main__":
    main()
