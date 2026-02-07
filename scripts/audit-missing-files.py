# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
audit-missing-files.py - Generate a comprehensive report of missing docket files

This script:
1. Identifies all PDF files referenced in YAML but missing from disk
2. Generates a CSV report for easy tracking
3. Creates a shell script to help with file organization
4. Optionally adds default 'source' field to entries missing it

Usage:
    python scripts/audit-missing-files.py [--fix-source] [--output-dir DIR]
"""

import argparse
import csv
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


def audit_docket_files(repo_root: Path) -> dict:
    """Audit all docket files and identify missing PDFs."""
    docket_dir = repo_root / "_data" / "docket"
    results = {"missing": [], "found": [], "no_source": [], "by_case": {}}

    for docket_file in sorted(docket_dir.glob("*.yml")):
        case_id = docket_file.stem
        results["by_case"][case_id] = {"missing": [], "found": [], "no_source": []}

        try:
            with open(docket_file, encoding="utf-8") as f:
                entries = yaml.safe_load(f) or []
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to read {docket_file}: {e}{Colors.RESET}")
            continue

        for entry in entries:
            file_path = entry.get("file", "")
            entry_id = entry.get("id", "unknown")
            entry_date = entry.get("date", "")
            entry_title = entry.get("title", "")
            entry_type = entry.get("type", "")

            if not file_path:
                continue

            # Check if file exists
            fs_path = repo_root / file_path.lstrip("/")

            record = {
                "case_id": case_id,
                "entry_id": entry_id,
                "date": entry_date,
                "title": entry_title,
                "type": entry_type,
                "yaml_path": file_path,
                "fs_path": str(fs_path),
            }

            if fs_path.exists():
                results["found"].append(record)
                results["by_case"][case_id]["found"].append(record)
            else:
                results["missing"].append(record)
                results["by_case"][case_id]["missing"].append(record)

            # Check for missing source
            if "source" not in entry:
                results["no_source"].append(record)
                results["by_case"][case_id]["no_source"].append(record)

    return results


def add_default_source(repo_root: Path, default_source: str = "manual") -> int:
    """Add default source field to entries missing it."""
    docket_dir = repo_root / "_data" / "docket"
    updated_count = 0

    for docket_file in sorted(docket_dir.glob("*.yml")):
        try:
            with open(docket_file, encoding="utf-8") as f:
                entries = yaml.safe_load(f) or []
        except Exception:
            continue

        modified = False
        for entry in entries:
            if "source" not in entry:
                entry["source"] = default_source
                modified = True
                updated_count += 1

        if modified:
            with open(docket_file, "w", encoding="utf-8") as f:
                yaml.dump(entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return updated_count


def generate_csv_report(results: dict, output_path: Path):
    """Generate a CSV report of missing files."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Case ID", "Entry ID", "Date", "Type", "Title", "Expected Path", "Status"])

        for record in results["missing"]:
            writer.writerow(
                [
                    record["case_id"],
                    record["entry_id"],
                    record["date"],
                    record["type"],
                    record["title"],
                    record["yaml_path"],
                    "MISSING",
                ]
            )


def generate_directory_structure(results: dict, output_path: Path):
    """Generate a script to create required directory structure."""
    cases = set(r["case_id"] for r in results["missing"])

    lines = [
        "#!/bin/bash",
        "# Auto-generated script to create docket directory structure",
        f"# Generated: {datetime.now().isoformat()}",
        "",
        "# Create docket directories for cases with missing files",
    ]

    for case_id in sorted(cases):
        lines.append(f'mkdir -p "assets/cases/{case_id}/docket"')

    lines.extend(
        [
            "",
            "# Missing files to upload:",
            "# ========================",
        ]
    )

    for record in sorted(results["missing"], key=lambda r: (r["case_id"], r["date"])):
        lines.append(f"# {record['case_id']}: {record['entry_id']} ({record['date']})")
        lines.append(f"#   -> {record['yaml_path']}")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_missing_files_list(results: dict, output_path: Path):
    """Generate a simple text list of missing files grouped by case."""
    lines = [
        "# MISSING DOCKET FILES REPORT",
        f"# Generated: {datetime.now().isoformat()}",
        f"# Total missing: {len(results['missing'])}",
        "",
    ]

    for case_id, case_data in sorted(results["by_case"].items()):
        if case_data["missing"]:
            lines.append(f"\n## {case_id} ({len(case_data['missing'])} missing)")
            lines.append("-" * 60)

            for record in sorted(case_data["missing"], key=lambda r: r["date"]):
                lines.append(f"  [{record['date']}] {record['entry_id']}")
                lines.append(f"    Type: {record['type']}")
                lines.append(f"    Title: {record['title'][:60]}...")
                lines.append(f"    Path: {record['yaml_path']}")
                lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Audit missing docket files")
    parser.add_argument(
        "--fix-source",
        action="store_true",
        help='Add default source="manual" to entries missing it',
    )
    parser.add_argument(
        "--output-dir", type=str, default="_data/audit", help="Output directory for reports"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET FILE AUDIT{Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    # Run audit
    print(f"{Colors.CYAN}Scanning docket files...{Colors.RESET}")
    results = audit_docket_files(repo_root)

    # Display summary by case
    print(f"\n{Colors.BOLD}Files by Case:{Colors.RESET}")
    for case_id, case_data in sorted(results["by_case"].items()):
        found = len(case_data["found"])
        missing = len(case_data["missing"])
        total = found + missing

        if missing == 0:
            status = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            status = f"{Colors.RED}✗{Colors.RESET}"

        print(f"  {status} {case_id}: {found}/{total} files found", end="")
        if missing > 0:
            print(f" ({Colors.RED}{missing} missing{Colors.RESET})")
        else:
            print()

    # Generate reports
    print(f"\n{Colors.BOLD}Generating reports...{Colors.RESET}")

    csv_path = output_dir / "missing-files.csv"
    generate_csv_report(results, csv_path)
    print(f"  {Colors.GREEN}✓{Colors.RESET} CSV report: {csv_path}")

    txt_path = output_dir / "missing-files.txt"
    generate_missing_files_list(results, txt_path)
    print(f"  {Colors.GREEN}✓{Colors.RESET} Text report: {txt_path}")

    sh_path = output_dir / "setup-directories.sh"
    generate_directory_structure(results, sh_path)
    print(f"  {Colors.GREEN}✓{Colors.RESET} Setup script: {sh_path}")

    # Fix source fields if requested
    if args.fix_source:
        print(f"\n{Colors.CYAN}Adding default source field...{Colors.RESET}")
        count = add_default_source(repo_root)
        print(f"  {Colors.GREEN}✓{Colors.RESET} Added source='manual' to {count} entries")

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Total entries:     {len(results['found']) + len(results['missing'])}")
    print(f"  Files found:       {Colors.GREEN}{len(results['found'])}{Colors.RESET}")
    print(f"  Files missing:     {Colors.RED}{len(results['missing'])}{Colors.RESET}")
    print(f"  Missing source:    {Colors.YELLOW}{len(results['no_source'])}{Colors.RESET}")
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if results["missing"]:
        print(
            f"\n{Colors.YELLOW}⚠ {len(results['missing'])} files need to be uploaded{Colors.RESET}"
        )
        print(f"  See: {txt_path}")
    else:
        print(f"\n{Colors.GREEN}✅ All referenced files exist on disk{Colors.RESET}")


if __name__ == "__main__":
    main()
