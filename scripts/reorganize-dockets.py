# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Reorganize docket files and update YAML paths
Copies files from cases/<slug>/filings/ to assets/cases/<slug>/docket/
and updates _data/docket/<slug>.yml files with correct paths
"""

import os
import re
import shutil
from pathlib import Path

CASES_DIR = Path("cases")
ASSETS_CASES_DIR = Path("assets/cases")
DOCKET_DATA_DIR = Path("_data/docket")


def copy_pdf_files():
    """Copy PDF files from cases/<slug>/filings to assets/cases/<slug>/docket"""
    stats = {"copied": 0, "skipped": 0, "errors": 0}

    for case_dir in sorted(CASES_DIR.glob("*/")):
        if not case_dir.is_dir():
            continue

        slug = case_dir.name
        filings_dir = case_dir / "filings"

        if not filings_dir.exists():
            print(f"⊘ No filings directory for {slug}")
            continue

        docket_dir = ASSETS_CASES_DIR / slug / "docket"
        docket_dir.mkdir(parents=True, exist_ok=True)

        pdf_files = list(filings_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"⊘ No PDF files in {slug}/filings")
            continue

        print(f"\n📁 Processing {slug}... ({len(pdf_files)} files)")

        for pdf_file in pdf_files:
            dest_file = docket_dir / pdf_file.name

            try:
                if dest_file.exists():
                    print(f"  ⊘ Skipped (exists): {pdf_file.name}")
                    stats["skipped"] += 1
                else:
                    shutil.copy2(pdf_file, dest_file)
                    print(f"  ✓ Copied: {pdf_file.name}")
                    stats["copied"] += 1
            except Exception as e:
                print(f"  ✗ Error copying {pdf_file.name}: {e}")
                stats["errors"] += 1

    return stats


def update_docket_yaml():
    """Update YAML files to use correct paths"""
    stats = {"files_updated": 0, "paths_updated": 0}

    for yaml_file in sorted(DOCKET_DATA_DIR.glob("*.yml")):
        slug = yaml_file.stem
        print(f"\n📝 Updating YAML for {slug}...")

        with open(yaml_file, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        update_count = 0

        # Replace various old path formats with the correct one
        patterns = [
            (rf'file: /cases/{slug}/filings/([^"\n]+)', rf"file: /assets/cases/{slug}/docket/\1"),
            (rf"file: /cases/{slug}/([^/\n]+\.pdf)", rf"file: /assets/cases/{slug}/docket/\1"),
            (rf'file: /cases/{slug}/pcr/([^"\n]+)', rf"file: /assets/cases/{slug}/docket/\1"),
            (rf'file: /cases/{slug}/docket/([^"\n]+)', rf"file: /assets/cases/{slug}/docket/\1"),
            (
                r'file: /cases/atl-24-001934/pcr/([^"\n]+)',
                rf"file: /assets/cases/{slug}/docket/\1",
            ),  # Special case for old docket
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                matches = len(re.findall(pattern, content))
                update_count += matches
                content = new_content
                print(f"  ✓ Updated {matches} paths matching pattern")

        if content != original_content:
            with open(yaml_file, "w", encoding="utf-8") as f:
                f.write(content)
            stats["files_updated"] += 1
            stats["paths_updated"] += update_count
            print(f"  ✓ Saved {yaml_file.name} with {update_count} updates")
        else:
            print(f"  → No changes needed for {yaml_file.name}")

    return stats


def main():
    print("=== Reorganizing Docket Files ===\n")

    # Step 1: Copy files
    print("Step 1: Copying PDF files...")
    copy_stats = copy_pdf_files()

    print("\n📊 Copy Summary:")
    print(f"  • Copied: {copy_stats['copied']}")
    print(f"  • Skipped (already exist): {copy_stats['skipped']}")
    print(f"  • Errors: {copy_stats['errors']}")

    # Step 2: Update YAML files
    print("\n" + "=" * 50)
    print("Step 2: Updating YAML files...")
    yaml_stats = update_docket_yaml()

    print("\n📊 YAML Update Summary:")
    print(f"  • Files updated: {yaml_stats['files_updated']}")
    print(f"  • Paths updated: {yaml_stats['paths_updated']}")

    print("\n" + "=" * 50)
    print("✅ Reorganization complete!")
    print("\nNext steps:")
    print("1. Review changes: git status")
    print("2. Test Jekyll build: bundle exec jekyll build")
    print("3. Verify case pages display correctly")
    print("4. Commit changes if everything looks good")


if __name__ == "__main__":
    # Change to repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    os.chdir(repo_root)

    main()
