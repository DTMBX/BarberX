# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
reconcile-docket-paths.py - Fix YAML paths to match actual files on disk

This script:
1. Scans each case's docket directory for actual PDF files
2. Updates YAML entries to point to existing files
3. Reports any entries with no matching file

Usage:
    python scripts/reconcile-docket-paths.py [--dry-run] [--case CASE_ID]
"""

import argparse
import re
import sys
from difflib import SequenceMatcher
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


def normalize_for_comparison(filename: str) -> str:
    """Normalize filename for fuzzy matching."""
    # Remove extension
    name = filename.lower().replace(".pdf", "")
    # Remove numeric suffixes like -2, -3
    name = re.sub(r"-\d+$", "", name)
    # Remove date prefixes for comparison
    name = re.sub(r"^\d{8}-", "", name)
    return name


def find_best_match(yaml_path: str, existing_files: list, case_id: str) -> str:
    """Find the best matching file on disk for a YAML path."""
    yaml_filename = Path(yaml_path).name
    yaml_base = normalize_for_comparison(yaml_filename)

    # Extract date from YAML filename
    date_match = re.match(r"^(\d{8})-", yaml_filename)
    yaml_date = date_match.group(1) if date_match else None

    best_match = None
    best_score = 0

    for existing in existing_files:
        existing_base = normalize_for_comparison(existing)

        # Check date match first
        existing_date_match = re.match(r"^(\d{8})-", existing)
        existing_date = existing_date_match.group(1) if existing_date_match else None

        # Calculate similarity
        score = SequenceMatcher(None, yaml_base, existing_base).ratio()

        # Boost score if dates match
        if yaml_date and existing_date and yaml_date == existing_date:
            score += 0.3

        # Exact base match (ignoring suffixes)
        if yaml_base == existing_base:
            score += 0.5

        if score > best_score:
            best_score = score
            best_match = existing

    # Only return if we have a good match (threshold 0.7)
    if best_score >= 0.7:
        return f"/assets/cases/{case_id}/docket/{best_match}"

    return None


def reconcile_case(docket_file: Path, case_dir: Path, dry_run: bool = False) -> dict:
    """Reconcile YAML paths with actual files on disk."""
    case_id = docket_file.stem
    result = {"case_id": case_id, "fixes": [], "unmatched": [], "errors": []}

    # Get list of actual files on disk
    docket_dir = case_dir / "docket"
    if not docket_dir.exists():
        result["errors"].append(f"Docket directory not found: {docket_dir}")
        return result

    existing_files = [f.name for f in docket_dir.glob("*.pdf")]
    existing_files_lower = {f.lower(): f for f in existing_files}

    # Load YAML
    try:
        with open(docket_file, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
    except Exception as e:
        result["errors"].append(f"Failed to read YAML: {e}")
        return result

    modified = False

    for entry in entries:
        yaml_path = entry.get("file", "")
        if not yaml_path:
            continue

        yaml_filename = Path(yaml_path).name

        # Check if file exists as-is
        full_path = case_dir.parent.parent.parent / yaml_path.lstrip("/")
        if full_path.exists():
            continue

        # Try exact match (case-insensitive)
        if yaml_filename.lower() in existing_files_lower:
            actual_filename = existing_files_lower[yaml_filename.lower()]
            new_path = f"/assets/cases/{case_id}/docket/{actual_filename}"
            if new_path != yaml_path:
                result["fixes"].append(
                    {
                        "entry_id": entry.get("id", "unknown"),
                        "old_path": yaml_path,
                        "new_path": new_path,
                        "reason": "exact match",
                    }
                )
                entry["file"] = new_path
                modified = True
            continue

        # Try removing suffix (-2, -3) from YAML path
        base_name = re.sub(r"-(\d+)\.pdf$", ".pdf", yaml_filename)
        if base_name.lower() in existing_files_lower:
            actual_filename = existing_files_lower[base_name.lower()]
            new_path = f"/assets/cases/{case_id}/docket/{actual_filename}"
            result["fixes"].append(
                {
                    "entry_id": entry.get("id", "unknown"),
                    "old_path": yaml_path,
                    "new_path": new_path,
                    "reason": "removed numeric suffix",
                }
            )
            entry["file"] = new_path
            modified = True
            continue

        # Try fuzzy match
        best_match = find_best_match(yaml_path, existing_files, case_id)
        if best_match:
            result["fixes"].append(
                {
                    "entry_id": entry.get("id", "unknown"),
                    "old_path": yaml_path,
                    "new_path": best_match,
                    "reason": "fuzzy match",
                }
            )
            entry["file"] = best_match
            modified = True
            continue

        # No match found
        result["unmatched"].append({"entry_id": entry.get("id", "unknown"), "path": yaml_path})

    # Write back if modified
    if modified and not dry_run:
        try:
            with open(docket_file, "w", encoding="utf-8") as f:
                yaml.dump(entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            result["written"] = True
        except Exception as e:
            result["errors"].append(f"Failed to write YAML: {e}")
            result["written"] = False
    else:
        result["written"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="Reconcile docket YAML paths with actual files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--case", type=str, help="Process specific case only")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    docket_data_dir = repo_root / "_data" / "docket"
    cases_dir = repo_root / "assets" / "cases"

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET PATH RECONCILIATION{Colors.RESET}")
    if args.dry_run:
        print(f"{Colors.YELLOW}  (DRY RUN - No files will be modified){Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    # Get files to process
    if args.case:
        docket_files = [docket_data_dir / f"{args.case}.yml"]
        if not docket_files[0].exists():
            print(f"{Colors.RED}❌ Case not found: {args.case}{Colors.RESET}")
            sys.exit(1)
    else:
        docket_files = sorted(docket_data_dir.glob("*.yml"))

    total_fixes = 0
    total_unmatched = 0
    total_errors = 0

    for docket_file in docket_files:
        case_id = docket_file.stem
        case_dir = cases_dir / case_id

        if not case_dir.exists():
            print(f"{Colors.YELLOW}⚠{Colors.RESET} {case_id}: Case directory not found")
            continue

        result = reconcile_case(docket_file, case_dir, args.dry_run)

        if result["fixes"]:
            status = (
                f"{Colors.GREEN}✓{Colors.RESET}"
                if result.get("written")
                else f"{Colors.CYAN}📝{Colors.RESET}"
            )
            print(f"{status} {case_id}: {len(result['fixes'])} paths fixed")

            for fix in result["fixes"][:3]:
                print(f"    {Colors.RED}- {Path(fix['old_path']).name}{Colors.RESET}")
                print(f"    {Colors.GREEN}+ {Path(fix['new_path']).name}{Colors.RESET}")
                print(f"    {Colors.BLUE}  ({fix['reason']}){Colors.RESET}")

            if len(result["fixes"]) > 3:
                print(f"    {Colors.YELLOW}... and {len(result['fixes']) - 3} more{Colors.RESET}")

            total_fixes += len(result["fixes"])
        else:
            print(f"{Colors.GREEN}✓{Colors.RESET} {case_id}: All paths valid")

        if result["unmatched"]:
            print(
                f"    {Colors.RED}⚠ {len(result['unmatched'])} entries have no matching file{Colors.RESET}"
            )
            total_unmatched += len(result["unmatched"])

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")
            total_errors += 1

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Cases processed:   {len(docket_files)}")
    print(f"  Paths fixed:       {Colors.GREEN if total_fixes else ''}{total_fixes}{Colors.RESET}")
    print(
        f"  Still unmatched:   {Colors.RED if total_unmatched else ''}{total_unmatched}{Colors.RESET}"
    )
    print(f"  Errors:            {Colors.RED if total_errors else ''}{total_errors}{Colors.RESET}")
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if args.dry_run and total_fixes > 0:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif total_fixes > 0:
        print(f"\n{Colors.GREEN}✅ {total_fixes} paths reconciled successfully{Colors.RESET}")


if __name__ == "__main__":
    main()
