# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
normalize-docket-files.py - Rename PDF files to match YYYYMMDD-slug.pdf format

This script normalizes PDF filenames in docket directories:
- "2026-01-10_Order_filename.pdf" → "20260110-filename.pdf"
- "11-26-25-njta's-motion.pdf" → "20251126-njtas-motion.pdf"

Also updates the corresponding YAML entries to point to new filenames.

Usage:
    python scripts/normalize-docket-files.py [--dry-run] [--case CASE_ID]
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def slugify(text: str) -> str:
    """Convert text to lowercase slug format."""
    text = text.lower()
    text = re.sub(r"[''`']", "", text)  # Remove apostrophes
    text = re.sub(r"[^a-z0-9-]", "-", text)  # Replace non-alphanumeric with hyphen
    text = re.sub(r"-+", "-", text)  # Collapse multiple hyphens
    text = text.strip("-")  # Remove leading/trailing hyphens
    return text


def normalize_filename(filename: str) -> tuple[str, bool]:
    """
    Normalize a PDF filename to YYYYMMDD-slug.pdf format.
    Returns (normalized_filename, was_changed)
    """
    original = filename

    # Remove .pdf extension for processing
    if filename.lower().endswith(".pdf"):
        base = filename[:-4]
    else:
        return filename, False

    # Pattern 1: YYYY-MM-DD_Type_slug (e.g., "2026-01-10_Order_motion-name")
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_[A-Za-z]+_(.+)$", base)
    if match:
        year, month, day, slug = match.groups()
        normalized = f"{year}{month}{day}-{slugify(slug)}.pdf"
        return normalized, normalized != original

    # Pattern 2: MM-DD-YY-slug (e.g., "11-26-25-njta's-motion")
    match = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{2})-(.+)$", base)
    if match:
        month, day, year, slug = match.groups()
        year = f"20{year}"
        normalized = f"{year}{month.zfill(2)}{day.zfill(2)}-{slugify(slug)}.pdf"
        return normalized, normalized != original

    # Pattern 3: MM-DD-YYYY-slug (e.g., "12-15-2025-order")
    match = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})-(.+)$", base)
    if match:
        month, day, year, slug = match.groups()
        normalized = f"{year}{month.zfill(2)}{day.zfill(2)}-{slugify(slug)}.pdf"
        return normalized, normalized != original

    # Pattern 4: Already normalized YYYYMMDD-slug.pdf - just slugify
    match = re.match(r"^(\d{8})-(.+)$", base)
    if match:
        date_part, slug = match.groups()
        normalized = f"{date_part}-{slugify(slug)}.pdf"
        return normalized, normalized != original

    # Pattern 5: Has special chars but no date pattern - just slugify
    slugified = slugify(base)
    if slugified != base:
        return f"{slugified}.pdf", True

    return filename, False


def process_case_directory(case_dir: Path, docket_file: Path, dry_run: bool = False) -> dict:
    """Process a case directory and rename files."""
    result = {"case_id": case_dir.name, "renames": [], "yaml_updates": [], "errors": []}

    docket_dir = case_dir / "docket"
    if not docket_dir.exists():
        result["errors"].append(f"Docket directory not found: {docket_dir}")
        return result

    # Load YAML data
    yaml_entries = []
    if docket_file.exists():
        try:
            with open(docket_file, encoding="utf-8") as f:
                yaml_entries = yaml.safe_load(f) or []
        except Exception as e:
            result["errors"].append(f"Failed to load YAML: {e}")

    # Build map of old paths to entries
    path_to_entry = {}
    for entry in yaml_entries:
        if "file" in entry:
            path_to_entry[entry["file"]] = entry

    # Process all PDF files
    pdf_files = list(docket_dir.glob("*.pdf")) + list(docket_dir.glob("*.PDF"))

    for pdf_path in pdf_files:
        old_name = pdf_path.name
        new_name, changed = normalize_filename(old_name)

        if changed:
            new_path = pdf_path.parent / new_name

            # Check for collision
            if new_path.exists() and new_path != pdf_path:
                # Add suffix to avoid collision
                base, ext = os.path.splitext(new_name)
                counter = 2
                while new_path.exists():
                    new_name = f"{base}-{counter}{ext}"
                    new_path = pdf_path.parent / new_name
                    counter += 1

            result["renames"].append(
                {
                    "old": old_name,
                    "new": new_name,
                    "old_path": str(pdf_path),
                    "new_path": str(new_path),
                }
            )

            # Update YAML entry if exists
            old_yaml_path = f"/assets/cases/{case_dir.name}/docket/{old_name}"
            new_yaml_path = f"/assets/cases/{case_dir.name}/docket/{new_name}"

            if old_yaml_path in path_to_entry:
                result["yaml_updates"].append(
                    {"old_path": old_yaml_path, "new_path": new_yaml_path}
                )
                if not dry_run:
                    path_to_entry[old_yaml_path]["file"] = new_yaml_path

            # Perform rename
            if not dry_run:
                try:
                    pdf_path.rename(new_path)
                except Exception as e:
                    result["errors"].append(f"Failed to rename {old_name}: {e}")

    # Write updated YAML
    if result["yaml_updates"] and not dry_run and docket_file.exists():
        try:
            with open(docket_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    yaml_entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False
                )
        except Exception as e:
            result["errors"].append(f"Failed to update YAML: {e}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Normalize docket PDF filenames")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming")
    parser.add_argument("--case", type=str, help="Process specific case only")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    cases_dir = repo_root / "assets" / "cases"
    docket_data_dir = repo_root / "_data" / "docket"

    if not cases_dir.exists():
        print(f"{Colors.RED}❌ Cases directory not found: {cases_dir}{Colors.RESET}")
        sys.exit(1)

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET FILE NORMALIZATION{Colors.RESET}")
    if args.dry_run:
        print(f"{Colors.YELLOW}  (DRY RUN - No files will be renamed){Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    # Get case directories
    if args.case:
        case_dirs = [cases_dir / args.case]
        if not case_dirs[0].exists():
            print(f"{Colors.RED}❌ Case not found: {args.case}{Colors.RESET}")
            sys.exit(1)
    else:
        case_dirs = sorted([d for d in cases_dir.iterdir() if d.is_dir()])

    total_renames = 0
    total_yaml_updates = 0
    total_errors = 0
    cases_modified = 0

    for case_dir in case_dirs:
        docket_file = docket_data_dir / f"{case_dir.name}.yml"
        result = process_case_directory(case_dir, docket_file, args.dry_run)

        if result["renames"]:
            cases_modified += 1
            status = (
                f"{Colors.YELLOW}⚡{Colors.RESET}"
                if not args.dry_run
                else f"{Colors.CYAN}📝{Colors.RESET}"
            )
            print(f"{status} {result['case_id']}: {len(result['renames'])} files")

            for rename in result["renames"][:3]:  # Show first 3
                print(f"    {Colors.RED}- {rename['old']}{Colors.RESET}")
                print(f"    {Colors.GREEN}+ {rename['new']}{Colors.RESET}")

            if len(result["renames"]) > 3:
                print(f"    {Colors.YELLOW}... and {len(result['renames']) - 3} more{Colors.RESET}")

            total_renames += len(result["renames"])
            total_yaml_updates += len(result["yaml_updates"])
        else:
            print(f"{Colors.GREEN}✓{Colors.RESET} {result['case_id']}: No changes needed")

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")
            total_errors += 1

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Cases processed:    {len(case_dirs)}")
    print(f"  Cases modified:     {cases_modified}")
    print(
        f"  Files renamed:      {Colors.GREEN if total_renames else ''}{total_renames}{Colors.RESET}"
    )
    print(
        f"  YAML paths updated: {Colors.GREEN if total_yaml_updates else ''}{total_yaml_updates}{Colors.RESET}"
    )
    print(f"  Errors:             {Colors.RED if total_errors else ''}{total_errors}{Colors.RESET}")
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if args.dry_run and total_renames > 0:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif total_renames > 0:
        print(f"\n{Colors.GREEN}✅ {total_renames} files normalized successfully{Colors.RESET}")
    else:
        print(f"\n{Colors.GREEN}✅ All filenames already in correct format{Colors.RESET}")


if __name__ == "__main__":
    main()
