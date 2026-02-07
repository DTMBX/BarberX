# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
dedupe-docket-entries.py - Remove duplicate docket entries that reference the same file

Usage:
    python scripts/dedupe-docket-entries.py [--dry-run] [--case CASE_ID]
"""

import argparse
import sys
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


def dedupe_docket_file(docket_file: Path, dry_run: bool = False) -> dict:
    """Remove duplicate entries from a docket file."""
    result = {
        "case_id": docket_file.stem,
        "original_count": 0,
        "final_count": 0,
        "removed": [],
        "errors": [],
    }

    try:
        with open(docket_file, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
    except Exception as e:
        result["errors"].append(f"Failed to read: {e}")
        return result

    result["original_count"] = len(entries)

    # Track seen file paths
    seen_files = {}
    unique_entries = []

    for entry in entries:
        file_path = entry.get("file", "")
        entry_id = entry.get("id", "unknown")

        if file_path in seen_files:
            # This is a duplicate - record it
            result["removed"].append(
                {"entry_id": entry_id, "file": file_path, "kept_id": seen_files[file_path]}
            )
        else:
            # First occurrence - keep it
            seen_files[file_path] = entry_id
            unique_entries.append(entry)

    result["final_count"] = len(unique_entries)

    # Write back if we removed duplicates
    if len(unique_entries) < len(entries) and not dry_run:
        try:
            with open(docket_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    unique_entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False
                )
            result["written"] = True
        except Exception as e:
            result["errors"].append(f"Failed to write: {e}")
            result["written"] = False
    else:
        result["written"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="Remove duplicate docket entries")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--case", type=str, help="Process specific case only")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    docket_dir = repo_root / "_data" / "docket"

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET DEDUPLICATION{Colors.RESET}")
    if args.dry_run:
        print(f"{Colors.YELLOW}  (DRY RUN - No files will be modified){Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    # Get files to process
    if args.case:
        files = [docket_dir / f"{args.case}.yml"]
        if not files[0].exists():
            print(f"{Colors.RED}❌ Case not found: {args.case}{Colors.RESET}")
            sys.exit(1)
    else:
        files = sorted(docket_dir.glob("*.yml"))

    total_removed = 0

    for docket_file in files:
        result = dedupe_docket_file(docket_file, args.dry_run)

        if result["removed"]:
            status = (
                f"{Colors.GREEN}✓{Colors.RESET}"
                if result.get("written")
                else f"{Colors.CYAN}📝{Colors.RESET}"
            )
            print(
                f"{status} {result['case_id']}: {result['original_count']} → {result['final_count']} entries ({len(result['removed'])} duplicates removed)"
            )

            for dup in result["removed"][:3]:
                print(
                    f"    {Colors.RED}- {dup['entry_id']} (duplicate of {dup['kept_id']}){Colors.RESET}"
                )

            if len(result["removed"]) > 3:
                print(f"    {Colors.YELLOW}... and {len(result['removed']) - 3} more{Colors.RESET}")

            total_removed += len(result["removed"])
        else:
            print(f"{Colors.GREEN}✓{Colors.RESET} {result['case_id']}: No duplicates")

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Files processed:     {len(files)}")
    print(
        f"  Duplicates removed:  {Colors.GREEN if total_removed else ''}{total_removed}{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if args.dry_run and total_removed > 0:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif total_removed > 0:
        print(f"\n{Colors.GREEN}✅ {total_removed} duplicates removed successfully{Colors.RESET}")


if __name__ == "__main__":
    main()
