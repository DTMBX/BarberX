from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
validate-docket.py - Validate docket entries against schema and verify file integrity

Usage:
    python scripts/validate-docket.py [--fix] [--case CASE_ID]

Options:
    --fix       Attempt to auto-fix common issues
    --case      Validate only a specific case
    --strict    Fail on warnings (not just errors)
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


# ANSI colors
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def load_schema(schema_path: Path) -> dict:
    """Load JSON Schema for validation."""
    if not schema_path.exists():
        print(
            f"{Colors.YELLOW}⚠ Schema not found at {schema_path}, using built-in schema{Colors.RESET}"
        )
        return get_builtin_schema()

    with open(schema_path) as f:
        return json.load(f)


def get_builtin_schema() -> dict:
    """Built-in schema for when external schema file is not available."""
    return {
        "type": "object",
        "required": ["id", "date", "type", "title", "file"],
        "properties": {
            "id": {"type": "string"},
            "date": {"type": "string"},
            "type": {
                "type": "string",
                "enum": [
                    "Order",
                    "Motion",
                    "Brief",
                    "Filing",
                    "Notice",
                    "Opinion",
                    "Judgment",
                    "Subpoena",
                    "Summons",
                    "Complaint",
                    "Answer",
                    "Discovery",
                    "Exhibit",
                    "Transcript",
                    "Other",
                ],
            },
            "title": {"type": "string"},
            "file": {"type": "string"},
            "notes": {"type": "string"},
            "court_stamp": {"type": ["string", "null"]},
            "checksum": {"type": "string"},
            "intake_date": {"type": "string"},
            "source": {"type": "string"},
        },
    }


def validate_entry(entry: dict, schema: dict, index: int) -> tuple[list[str], list[str]]:
    """Validate a single docket entry. Returns (errors, warnings)."""
    errors = []
    warnings = []

    # Schema validation
    try:
        jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error: {e.message}")

    # File path validation
    file_path = entry.get("file", "")
    if file_path:
        # Check for correct canonical path format
        if not file_path.startswith("/assets/cases/"):
            if file_path.startswith("/cases/"):
                errors.append(
                    f"Invalid path format: {file_path} (should start with /assets/cases/)"
                )
            else:
                errors.append(f"Invalid path format: {file_path}")

        # Check file exists (relative to repo root)
        abs_path = Path(file_path.lstrip("/"))
        if not abs_path.exists():
            errors.append(f"File not found: {file_path}")

    # Date validation
    date_str = entry.get("date", "")
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"Invalid date format: {date_str} (expected YYYY-MM-DD)")

    # ID format validation
    entry_id = entry.get("id", "")
    if entry_id:
        # Check if ID starts with date
        if not re.match(r"^\d{8}-", entry_id):
            warnings.append(f"ID '{entry_id}' doesn't follow YYYYMMDD-slug format")

    # Missing recommended fields
    if not entry.get("checksum"):
        warnings.append("Missing checksum for integrity verification")

    if not entry.get("source"):
        warnings.append("Missing source field (manual, ecf, mail, etc.)")

    return errors, warnings


def validate_docket_file(filepath: Path, schema: dict) -> dict:
    """Validate all entries in a docket YAML file."""
    result = {
        "file": filepath.name,
        "case_id": filepath.stem,
        "entries": 0,
        "errors": [],
        "warnings": [],
        "valid": True,
    }

    try:
        with open(filepath) as f:
            entries = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result["errors"].append(f"YAML parse error: {e}")
        result["valid"] = False
        return result

    if not isinstance(entries, list):
        result["errors"].append("Docket file must contain a list of entries")
        result["valid"] = False
        return result

    result["entries"] = len(entries)
    seen_ids = set()

    for i, entry in enumerate(entries):
        # Check for duplicate IDs
        entry_id = entry.get("id", f"index-{i}")
        if entry_id in seen_ids:
            result["errors"].append(f"[{i}] Duplicate ID: {entry_id}")
        seen_ids.add(entry_id)

        # Validate entry
        errors, warnings = validate_entry(entry, schema, i)

        for error in errors:
            result["errors"].append(f"[{i}] {entry_id}: {error}")

        for warning in warnings:
            result["warnings"].append(f"[{i}] {entry_id}: {warning}")

    result["valid"] = len(result["errors"]) == 0
    return result


def check_for_duplicates(docket_dir: Path) -> list[str]:
    """Check for duplicate file references across all docket files."""
    all_files = {}
    duplicates = []

    for docket_file in docket_dir.glob("*.yml"):
        try:
            with open(docket_file) as f:
                entries = yaml.safe_load(f)

            if not isinstance(entries, list):
                continue

            for entry in entries:
                file_path = entry.get("file", "")
                if file_path:
                    if file_path in all_files:
                        duplicates.append(
                            f"Duplicate file reference: {file_path}\n"
                            f"  - First: {all_files[file_path]}\n"
                            f"  - Also: {docket_file.name}"
                        )
                    else:
                        all_files[file_path] = docket_file.name
        except Exception:
            continue

    return duplicates


Optional[def generate_checksum(filepath: Path) -> str]:
    """Generate SHA-256 checksum for a file."""
    if not filepath.exists():
        return None

    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def print_results(results: list[dict], duplicates: list[str], strict: bool = False):
    """Print validation results."""
    total_errors = 0
    total_warnings = 0
    total_entries = 0

    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}"
    )
    print(f"{Colors.BOLD}  DOCKET VALIDATION REPORT{Colors.RESET}")
    print(
        f"{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
    )

    for result in results:
        total_entries += result["entries"]
        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

        if result["valid"] and not result["warnings"]:
            status = f"{Colors.GREEN}✓{Colors.RESET}"
        elif result["valid"]:
            status = f"{Colors.YELLOW}⚠{Colors.RESET}"
        else:
            status = f"{Colors.RED}✗{Colors.RESET}"

        print(f"{status} {result['case_id']}: {result['entries']} entries")

        for error in result["errors"]:
            print(f"    {Colors.RED}✗ {error}{Colors.RESET}")

        for warning in result["warnings"][:3]:  # Limit warnings shown
            print(f"    {Colors.YELLOW}⚠ {warning}{Colors.RESET}")

        if len(result["warnings"]) > 3:
            print(
                f"    {Colors.YELLOW}  ... and {len(result['warnings']) - 3} more warnings{Colors.RESET}"
            )

    # Duplicates
    if duplicates:
        print(f"\n{Colors.RED}{Colors.BOLD}DUPLICATE FILE REFERENCES:{Colors.RESET}")
        for dup in duplicates:
            print(f"  {Colors.RED}{dup}{Colors.RESET}")
        total_errors += len(duplicates)

    # Summary
    print(
        f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )
    print(f"  Total files:    {len(results)}")
    print(f"  Total entries:  {total_entries}")
    print(
        f"  Errors:         {Colors.RED if total_errors else Colors.GREEN}{total_errors}{Colors.RESET}"
    )
    print(
        f"  Warnings:       {Colors.YELLOW if total_warnings else Colors.GREEN}{total_warnings}{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.RESET}"
    )

    if total_errors > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.RESET}")
        return False
    elif strict and total_warnings > 0:
        print(
            f"\n{Colors.YELLOW}{Colors.BOLD}⚠ VALIDATION PASSED WITH WARNINGS (strict mode){Colors.RESET}"
        )
        return False
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ VALIDATION PASSED{Colors.RESET}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate docket entries")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix issues")
    parser.add_argument("--case", type=str, help="Validate specific case only")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    # Find directories
    repo_root = Path(__file__).parent.parent
    docket_dir = repo_root / "_data" / "docket"
    schema_path = repo_root / "_data" / "schemas" / "docket-entry.schema.json"

    if not docket_dir.exists():
        print(f"{Colors.RED}❌ Docket directory not found: {docket_dir}{Colors.RESET}")
        sys.exit(1)

    # Load schema
    schema = load_schema(schema_path)

    # Get files to validate
    if args.case:
        files = [docket_dir / f"{args.case}.yml"]
        if not files[0].exists():
            print(f"{Colors.RED}❌ Case not found: {args.case}{Colors.RESET}")
            sys.exit(1)
    else:
        files = sorted(docket_dir.glob("*.yml"))

    if not files:
        print(f"{Colors.YELLOW}⚠ No docket files found{Colors.RESET}")
        sys.exit(0)

    # Validate
    results = []
    for filepath in files:
        result = validate_docket_file(filepath, schema)
        results.append(result)

    # Check for duplicates
    duplicates = check_for_duplicates(docket_dir) if not args.case else []

    # Print results
    if not args.quiet:
        success = print_results(results, duplicates, args.strict)
    else:
        success = all(r["valid"] for r in results) and not duplicates
        if not success:
            total_errors = sum(len(r["errors"]) for r in results)
            print(f"❌ {total_errors} errors found")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()