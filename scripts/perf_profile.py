#!/usr/bin/env python
"""
Large-Case Performance Profiler
=================================
CLI tool that measures query performance against cases with large evidence
counts, validating that the system remains responsive under load.

Usage:
    python scripts/perf_profile.py --evidence-count 5000

This script:
  1. Creates a temporary test case with N synthetic evidence items.
  2. Measures key query times (case load, evidence list, export manifest).
  3. Reports p50/p95/max timings.
  4. Cleans up all synthetic data.

Read-only against production — all data is created in a transaction that
is rolled back (or in an ephemeral test database).
"""

import argparse
import os
import statistics
import sys
import time
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _create_app():
    from app_config import create_app
    return create_app()


def _run_profile(evidence_count: int, iterations: int = 10):
    """Run performance profile with synthetic data."""
    app = _create_app()

    with app.app_context():
        from auth.models import db
        from models.evidence import CaseEvidence, EvidenceItem
        from models.legal_case import LegalCase

        # --- Setup: create synthetic case + evidence in a savepoint ---
        print(f"\n  Creating synthetic case with {evidence_count} evidence items...")
        t0 = time.perf_counter()

        case = LegalCase(
            case_number=f"PERF-{uuid.uuid4().hex[:8]}",
            case_name="Performance Profile (Synthetic)",
            case_type="civil",
            status="open",
        )
        db.session.add(case)
        db.session.flush()

        items = []
        for i in range(evidence_count):
            item = EvidenceItem(
                original_filename=f"evidence_{i:06d}.pdf",
                evidence_type="document",
                file_size_bytes=1024 * (i + 1),
                hash_sha256=f"{i:064x}",
                processing_status="complete",
            )
            items.append(item)
        db.session.add_all(items)
        db.session.flush()

        for item in items:
            link = CaseEvidence(
                case_id=case.id,
                evidence_id=item.id,
                link_purpose="intake",
            )
            db.session.add(link)
        db.session.flush()

        setup_time = time.perf_counter() - t0
        print(f"  Setup complete in {setup_time:.2f}s")

        # --- Benchmark queries ---
        results = {}

        # 1. Load case with evidence count
        timings = []
        for _ in range(iterations):
            t = time.perf_counter()
            c = LegalCase.query.get(case.id)
            _ = c.evidence_count
            timings.append(time.perf_counter() - t)
        results["case_load_with_count"] = timings

        # 2. Load full evidence list
        timings = []
        for _ in range(iterations):
            t = time.perf_counter()
            c = LegalCase.query.get(case.id)
            _ = c.evidence_items
            timings.append(time.perf_counter() - t)
        results["full_evidence_list"] = timings

        # 3. Filtered evidence query (by type)
        timings = []
        for _ in range(iterations):
            t = time.perf_counter()
            _ = (
                EvidenceItem.query
                .join(CaseEvidence)
                .filter(CaseEvidence.case_id == case.id)
                .filter(CaseEvidence.unlinked_at.is_(None))
                .filter(EvidenceItem.evidence_type == "document")
                .count()
            )
            timings.append(time.perf_counter() - t)
        results["filtered_evidence_count"] = timings

        # 4. Hash lookup (indexed)
        sample_hash = f"{evidence_count // 2:064x}"
        timings = []
        for _ in range(iterations):
            t = time.perf_counter()
            _ = EvidenceItem.query.filter_by(hash_sha256=sample_hash).first()
            timings.append(time.perf_counter() - t)
        results["hash_lookup"] = timings

        # --- Cleanup ---
        db.session.rollback()

        # --- Report ---
        print(f"\n  Performance Profile Results ({evidence_count} items, {iterations} iterations)")
        print("  " + "=" * 70)
        print(f"  {'Query':<30} {'p50 (ms)':>10} {'p95 (ms)':>10} {'max (ms)':>10}")
        print("  " + "-" * 70)

        for name, timings in results.items():
            ms = [t * 1000 for t in timings]
            p50 = statistics.median(ms)
            p95 = sorted(ms)[int(len(ms) * 0.95)]
            mx = max(ms)
            print(f"  {name:<30} {p50:>10.2f} {p95:>10.2f} {mx:>10.2f}")

        print("  " + "=" * 70)

        # Return results for programmatic use
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Evident — Large-Case Performance Profiler",
    )
    parser.add_argument(
        "--evidence-count",
        type=int,
        default=1000,
        help="Number of synthetic evidence items (default: 1000)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Iterations per query (default: 10)",
    )
    args = parser.parse_args()
    _run_profile(args.evidence_count, args.iterations)


if __name__ == "__main__":
    main()
