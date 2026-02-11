"""
Evidence Processing CLI
========================
Process evidence items from the command line.

Usage:
  py -3.12 scripts/process_evidence.py --evidence-id <id>
  py -3.12 scripts/process_evidence.py --case-id <id>
  py -3.12 scripts/process_evidence.py --file <path> [--filename <name>]

Examples:
  # Process a specific evidence item by DB ID
  py -3.12 scripts/process_evidence.py --evidence-id 1

  # Process all unprocessed evidence in a case
  py -3.12 scripts/process_evidence.py --case-id 1

  # Process a raw file (no DB, prints extraction result)
  py -3.12 scripts/process_evidence.py --file evidence_store/originals/8e34/.../test_evidence.pdf
"""

import argparse
import json
import os
import sys
import time

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def process_by_evidence_id(evidence_id: int, user_id: int = 1) -> int:
    """Process a single evidence item by DB ID. Returns exit code."""
    from tasks.processing_tasks import process_evidence_sync

    print(f"Processing evidence ID {evidence_id}...")
    start = time.time()

    result = process_evidence_sync(evidence_id, user_id)
    elapsed = time.time() - start

    if result.get("success"):
        print(f"\n  Status:    completed")
        print(f"  Task ID:   {result.get('task_id')}")
        print(f"  Task Type: {result.get('task_type')}")
        print(f"  Time:      {elapsed:.1f}s")

        summary = result.get("summary", {})
        for key, value in summary.items():
            print(f"  {key}: {value}")

        print("\nDone.")
        return 0
    else:
        print(f"\n  Status: FAILED")
        print(f"  Error:  {result.get('error')}")
        return 1


def process_by_case_id(case_id: int, user_id: int = 1) -> int:
    """Process all unprocessed evidence in a case. Returns exit code."""
    from tasks.processing_tasks import process_case_batch

    print(f"Batch processing case ID {case_id}...")
    start = time.time()

    result = process_case_batch(case_id, user_id)
    elapsed = time.time() - start

    print(f"\n  Total:     {result.get('total')}")
    print(f"  Completed: {result.get('completed')}")
    print(f"  Failed:    {result.get('failed')}")
    print(f"  Time:      {elapsed:.1f}s")

    return 0 if result.get("success") else 1


def process_raw_file(file_path: str, filename: str = "") -> int:
    """Process a raw file without DB. Returns exit code."""
    from services.evidence_processor import process_evidence_file

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 1

    print(f"Processing file: {file_path}")
    start = time.time()

    result = process_evidence_file(
        file_path=file_path,
        original_filename=filename or os.path.basename(file_path),
    )
    elapsed = time.time() - start

    if result.success:
        print(f"\n  Status:     completed")
        print(f"  Task Type:  {result.task_type}")
        print(f"  Words:      {result.word_count}")
        print(f"  Characters: {result.character_count}")
        print(f"  Pages:      {result.page_count}")
        print(f"  Emails:     {result.email_addresses}")
        print(f"  Phones:     {result.phone_numbers}")
        print(f"  Time:       {elapsed:.1f}s")

        if result.full_text:
            preview = result.full_text[:500]
            print(f"\n  Text preview:\n  {preview}")
            if len(result.full_text) > 500:
                print(f"  ... ({result.character_count} total characters)")
    else:
        print(f"\n  Status: FAILED")
        print(f"  Error:  {result.error_message}")
        return 1

    print(f"\n  Metadata: {json.dumps(result.metadata, indent=2)}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Evident Evidence Processing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--evidence-id", type=int, help="Process a specific evidence item by DB ID")
    group.add_argument("--case-id", type=int, help="Batch-process all evidence in a case")
    group.add_argument("--file", type=str, help="Process a raw file (no DB)")

    parser.add_argument("--filename", type=str, default="", help="Original filename (for MIME detection with --file)")
    parser.add_argument("--user-id", type=int, default=1, help="User ID for DB operations (default: 1)")

    args = parser.parse_args()

    if args.evidence_id:
        sys.exit(process_by_evidence_id(args.evidence_id, args.user_id))
    elif args.case_id:
        sys.exit(process_by_case_id(args.case_id, args.user_id))
    elif args.file:
        sys.exit(process_raw_file(args.file, args.filename))


if __name__ == "__main__":
    main()
