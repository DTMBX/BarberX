# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
generate-checksums.py - Generate SHA-256 checksums for all docket entries

This script:
1. Computes SHA-256 checksums for all PDF files referenced in docket YAML
2. Updates the YAML entries with checksum values
3. Optionally creates checksum manifest files

Usage:
    python scripts/generate-checksums.py [--dry-run] [--case CASE_ID] [--manifest]
"""

import argparse
import hashlib
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


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_docket_file(docket_file: Path, repo_root: Path, dry_run: bool = False) -> dict:
    """Process a docket YAML file and generate checksums."""
    result = {
        "case_id": docket_file.stem,
        "total": 0,
        "updated": 0,
        "missing_files": [],
        "already_set": 0,
        "errors": [],
    }

    try:
        with open(docket_file, encoding="utf-8") as f:
            entries = yaml.safe_load(f)
    except Exception as e:
        result["errors"].append(f"Failed to read: {e}")
        return result

    if not isinstance(entries, list):
        result["errors"].append("File does not contain a list")
        return result

    result["total"] = len(entries)
    modified = False

    for entry in entries:
        file_path = entry.get("file", "")
        existing_checksum = entry.get("checksum", "")

        if not file_path:
            continue

        # Convert web path to filesystem path
        # /assets/cases/case-id/docket/file.pdf → assets/cases/case-id/docket/file.pdf
        fs_path = repo_root / file_path.lstrip("/")

        if not fs_path.exists():
            result["missing_files"].append(file_path)
            continue

        # Compute checksum
        try:
            checksum = compute_sha256(fs_path)
        except Exception as e:
            result["errors"].append(f"Failed to hash {file_path}: {e}")
            continue

        # Update entry if different or missing
        if existing_checksum != checksum:
            entry["checksum"] = checksum
            result["updated"] += 1
            modified = True
        else:
            result["already_set"] += 1

    # Write back if modified
    if modified and not dry_run:
        try:
            with open(docket_file, "w", encoding="utf-8") as f:
                yaml.dump(entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            result["written"] = True
        except Exception as e:
            result["errors"].append(f"Failed to write: {e}")
            result["written"] = False
    else:
        result["written"] = False

    return result


def create_manifest(docket_file: Path, repo_root: Path, manifest_dir: Path) -> dict:
    """Create a checksum manifest file for a case."""
    result = {"case_id": docket_file.stem, "entries": 0}

    try:
        with open(docket_file, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
    except Exception:
        return result

    manifest_lines = [
        "# SHA-256 Checksum Manifest",
        f"# Case: {docket_file.stem}",
        f"# Generated: {datetime.now().isoformat()}",
        "# Format: checksum *filepath",
        "",
    ]

    for entry in entries:
        checksum = entry.get("checksum", "")
        file_path = entry.get("file", "")
        if checksum and file_path:
            # Use relative path from repo root
            rel_path = file_path.lstrip("/")
            manifest_lines.append(f"{checksum} *{rel_path}")
            result["entries"] += 1

    if result["entries"] > 0:
        manifest_file = manifest_dir / f"{docket_file.stem}.sha256"
        manifest_file.write_text("\n".join(manifest_lines), encoding="utf-8")
        result["manifest"] = str(manifest_file)

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate checksums for docket entries")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--case", type=str, help="Process specific case only")
    parser.add_argument(
        "--manifest", action="store_true", help="Also create checksum manifest files"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    docket_dir = repo_root / "_data" / "docket"
    checksum_dir = repo_root / "_data" / "checksums"

    if not docket_dir.exists():
        print(f"{Colors.RED}❌ Docket directory not found: {docket_dir}{Colors.RESET}")
        sys.exit(1)

    # Ensure checksum dir exists for manifests
    if args.manifest:
        checksum_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET CHECKSUM GENERATION{Colors.RESET}")
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

    total_entries = 0
    total_updated = 0
    total_missing = 0
    total_errors = 0
    files_modified = 0

    for docket_file in files:
        result = process_docket_file(docket_file, repo_root, args.dry_run)

        total_entries += result["total"]
        total_updated += result["updated"]
        total_missing += len(result["missing_files"])
        total_errors += len(result["errors"])

        if result["updated"] > 0:
            files_modified += 1
            status = (
                f"{Colors.YELLOW}⚡{Colors.RESET}"
                if result.get("written")
                else f"{Colors.CYAN}📝{Colors.RESET}"
            )
            print(
                f"{status} {result['case_id']}: {result['updated']}/{result['total']} checksums generated"
            )
        else:
            if result["already_set"] == result["total"]:
                print(
                    f"{Colors.GREEN}✓{Colors.RESET} {result['case_id']}: All {result['total']} checksums already set"
                )
            else:
                print(
                    f"{Colors.BLUE}○{Colors.RESET} {result['case_id']}: {result['total']} entries"
                )

        if result["missing_files"]:
            for mf in result["missing_files"][:2]:
                print(f"    {Colors.YELLOW}⚠ Missing: {mf}{Colors.RESET}")
            if len(result["missing_files"]) > 2:
                print(
                    f"    {Colors.YELLOW}... and {len(result['missing_files']) - 2} more missing{Colors.RESET}"
                )

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")

        # Create manifest if requested
        if args.manifest and not args.dry_run:
            manifest_result = create_manifest(docket_file, repo_root, checksum_dir)
            if manifest_result.get("entries", 0) > 0:
                print(
                    f"    {Colors.CYAN}📄 Manifest: {manifest_result['entries']} entries{Colors.RESET}"
                )

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Files processed:      {len(files)}")
    print(f"  Files modified:       {files_modified}")
    print(f"  Total entries:        {total_entries}")
    print(
        f"  Checksums generated:  {Colors.GREEN if total_updated else ''}{total_updated}{Colors.RESET}"
    )
    print(
        f"  Missing PDF files:    {Colors.YELLOW if total_missing else ''}{total_missing}{Colors.RESET}"
    )
    print(
        f"  Errors:               {Colors.RED if total_errors else ''}{total_errors}{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if args.dry_run and total_updated > 0:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif total_updated > 0:
        print(f"\n{Colors.GREEN}✅ {total_updated} checksums generated successfully{Colors.RESET}")
    else:
        print(f"\n{Colors.GREEN}✅ All checksums up to date{Colors.RESET}")


if __name__ == "__main__":
    main()
