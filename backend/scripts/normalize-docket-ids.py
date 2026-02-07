# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
normalize-docket-ids.py - Fix docket entry ID format to YYYYMMDD-slug standard

This script normalizes various ID formats to the canonical YYYYMMDD-slug format:
- "12-15-2025-order" → "20251215-order"
- "2025-12-15_Order_order-name" → "20251215-order-name"
- "order-granted" (no date) → uses entry date field

Usage:
    python scripts/normalize-docket-ids.py [--dry-run] [--case CASE_ID]
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

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


def normalize_id(entry_id: str, entry_date: str) -> tuple[str, bool]:
    """
    Normalize an entry ID to YYYYMMDD-slug format.
    Returns (normalized_id, was_changed)
    """
    original = entry_id

    # Pattern 1: MM-DD-YYYY-slug or MM-DD-YY-slug (e.g., "12-15-2025-order" or "11-26-25-order")
    match = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{2,4})-(.+)$", entry_id)
    if match:
        month, day, year, slug = match.groups()
        if len(year) == 2:
            year = f"20{year}"
        normalized = f"{year}{month.zfill(2)}{day.zfill(2)}-{slug}"
        return normalized, normalized != original

    # Pattern 2: YYYY-MM-DD_Type_slug (e.g., "2025-12-15_Order_order-name")
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_[A-Za-z]+_(.+)$", entry_id)
    if match:
        year, month, day, slug = match.groups()
        normalized = f"{year}{month}{day}-{slug}"
        return normalized, normalized != original

    # Pattern 3: YYYY-MM-DD_Type_YYYY-MM-DD-slug (redundant date in slug)
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_[A-Za-z]+_\d{4}-\d{2}-\d{2}-(.+)$", entry_id)
    if match:
        year, month, day, slug = match.groups()
        normalized = f"{year}{month}{day}-{slug}"
        return normalized, normalized != original

    # Pattern 4: Already correct YYYYMMDD-slug format
    if re.match(r"^\d{8}-[a-z0-9-]+$", entry_id):
        return entry_id, False

    # Pattern 5: No date prefix at all (e.g., "order-granted")
    # Use the entry's date field to construct ID
    if entry_date and not re.match(r"^\d", entry_id):
        try:
            dt = datetime.strptime(entry_date, "%Y-%m-%d")
            date_prefix = dt.strftime("%Y%m%d")
            normalized = f"{date_prefix}-{entry_id}"
            return normalized, True
        except ValueError:
            pass

    # Pattern 6: Partial date like "11-15-slug" (assume current/recent year)
    match = re.match(r"^(\d{1,2})-(\d{1,2})-([a-z].+)$", entry_id)
    if match:
        month, day, slug = match.groups()
        # Use entry date year if available
        if entry_date:
            try:
                dt = datetime.strptime(entry_date, "%Y-%m-%d")
                year = dt.year
            except ValueError:
                year = 2025
        else:
            year = 2025
        normalized = f"{year}{month.zfill(2)}{day.zfill(2)}-{slug}"
        return normalized, normalized != original

    # Cannot normalize - return as-is with warning
    return entry_id, False


def slugify(text: str) -> str:
    """Convert text to lowercase slug format."""
    # Remove apostrophes and special chars, convert to lowercase
    text = text.lower()
    text = re.sub(r"[''`]", "", text)  # Remove apostrophes
    text = re.sub(r"[^a-z0-9-]", "-", text)  # Replace non-alphanumeric with hyphen
    text = re.sub(r"-+", "-", text)  # Collapse multiple hyphens
    text = text.strip("-")  # Remove leading/trailing hyphens
    return text


def process_docket_file(filepath: Path, dry_run: bool = False) -> dict:
    """Process a single docket file and normalize IDs."""
    result = {"file": filepath.name, "case_id": filepath.stem, "changes": [], "errors": []}

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
            entries = yaml.safe_load(content)
    except Exception as e:
        result["errors"].append(f"Failed to read: {e}")
        return result

    if not isinstance(entries, list):
        result["errors"].append("File does not contain a list")
        return result

    modified = False
    seen_ids = {}

    for i, entry in enumerate(entries):
        old_id = entry.get("id", "")
        entry_date = entry.get("date", "")

        # Normalize the ID
        new_id, changed = normalize_id(old_id, entry_date)

        # Also slugify to ensure lowercase and no special chars
        new_id = slugify(new_id) if changed else new_id

        # Handle duplicates by appending index
        if new_id in seen_ids:
            base_id = new_id
            counter = 2
            while new_id in seen_ids:
                new_id = f"{base_id}-{counter}"
                counter += 1
            result["changes"].append(
                {
                    "index": i,
                    "old": old_id,
                    "new": new_id,
                    "reason": f"duplicate resolved (originally {base_id})",
                }
            )
            changed = True

        if changed:
            result["changes"].append(
                {"index": i, "old": old_id, "new": new_id, "reason": "format normalized"}
            )
            entry["id"] = new_id
            modified = True

        seen_ids[new_id] = i

    # Write back if modified and not dry run
    if modified and not dry_run:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            result["written"] = True
        except Exception as e:
            result["errors"].append(f"Failed to write: {e}")
            result["written"] = False
    else:
        result["written"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="Normalize docket entry IDs")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--case", type=str, help="Process specific case only")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    docket_dir = repo_root / "_data" / "docket"

    if not docket_dir.exists():
        print(f"{Colors.RED}❌ Docket directory not found: {docket_dir}{Colors.RESET}")
        sys.exit(1)

    # Get files to process
    if args.case:
        files = [docket_dir / f"{args.case}.yml"]
        if not files[0].exists():
            print(f"{Colors.RED}❌ Case not found: {args.case}{Colors.RESET}")
            sys.exit(1)
    else:
        files = sorted(docket_dir.glob("*.yml"))

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET ID NORMALIZATION{Colors.RESET}")
    if args.dry_run:
        print(f"{Colors.YELLOW}  (DRY RUN - No files will be modified){Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    total_changes = 0
    total_errors = 0
    files_modified = 0

    for filepath in files:
        result = process_docket_file(filepath, args.dry_run)

        if result["changes"]:
            files_modified += 1
            status = (
                f"{Colors.YELLOW}⚡{Colors.RESET}"
                if result.get("written")
                else f"{Colors.CYAN}📝{Colors.RESET}"
            )
            print(f"{status} {result['case_id']}: {len(result['changes'])} changes")

            for change in result["changes"][:5]:  # Show first 5
                print(f"    {Colors.RED}- {change['old']}{Colors.RESET}")
                print(f"    {Colors.GREEN}+ {change['new']}{Colors.RESET}")

            if len(result["changes"]) > 5:
                print(f"    {Colors.YELLOW}... and {len(result['changes']) - 5} more{Colors.RESET}")

            total_changes += len(result["changes"])
        else:
            print(f"{Colors.GREEN}✓{Colors.RESET} {result['case_id']}: No changes needed")

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")
            total_errors += 1

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Files processed:  {len(files)}")
    print(f"  Files modified:   {files_modified}")
    print(
        f"  Total changes:    {Colors.GREEN if total_changes else ''}{total_changes}{Colors.RESET}"
    )
    print(f"  Errors:           {Colors.RED if total_errors else ''}{total_errors}{Colors.RESET}")
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if args.dry_run and total_changes > 0:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif total_changes > 0:
        print(f"\n{Colors.GREEN}✅ {total_changes} IDs normalized successfully{Colors.RESET}")
    else:
        print(f"\n{Colors.GREEN}✅ All IDs already in correct format{Colors.RESET}")


if __name__ == "__main__":
    main()
