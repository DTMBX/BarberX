#!/usr/bin/env python
"""
Evident CLI
============
Court-defensible evidence management commands.

Usage:
    python -m cli.evident algorithms list
    python -m cli.evident algorithms run <algorithm_id> --case <id> [--tenant <id>]
    python -m cli.evident audit integrity --case <id> [--tenant <id>]
    python -m cli.evident export court-package --case <id> [--tenant <id>] [--output <dir>]

All commands run within a Flask app context, use the same database,
and emit proper audit events.
"""

import argparse
import json
import sys
import os

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_app():
    from app_config import create_app
    return create_app()


def _ensure_algorithms():
    """Import all algorithm modules to trigger registration."""
    import algorithms.bulk_dedup  # noqa: F401
    import algorithms.provenance_graph  # noqa: F401
    import algorithms.timeline_alignment  # noqa: F401
    import algorithms.integrity_sweep  # noqa: F401
    import algorithms.bates_generator  # noqa: F401
    import algorithms.redaction_verify  # noqa: F401
    import algorithms.access_anomaly  # noqa: F401


def cmd_algorithms_list(args):
    """List all registered algorithms."""
    app = _get_app()
    with app.app_context():
        from algorithms.registry import registry
        _ensure_algorithms()

        algos = registry.list_algorithms()
        print(f"\n  Registered Algorithms ({len(algos)}):")
        print(f"  {'ID':<25} {'Version':<10} Description")
        print(f"  {'-'*25} {'-'*10} {'-'*40}")
        for a in algos:
            print(f"  {a['algorithm_id']:<25} {a['version']:<10} {a['description'][:50]}")
        print()


def cmd_algorithms_run(args):
    """Run a specific algorithm on a case."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.base import AlgorithmParams
        from algorithms.registry import registry
        _ensure_algorithms()

        algo = registry.get(args.algorithm_id, getattr(args, "version", None))
        if not algo:
            print(f"  Error: Algorithm '{args.algorithm_id}' not found.")
            sys.exit(1)

        store = EvidenceStore()
        audit = AuditStream(db.session, store)

        extra = {}
        if hasattr(args, "params") and args.params:
            extra = json.loads(args.params)

        params = AlgorithmParams(
            case_id=args.case,
            tenant_id=args.tenant,
            actor_id=None,
            actor_name="cli",
            extra=extra,
        )
        context = {
            "db_session": db.session,
            "evidence_store": store,
            "audit_stream": audit,
        }

        print(f"\n  Running {algo.algorithm_id} v{algo.algorithm_version} on case {args.case}...")
        result = algo.run(params, context)

        if result.success:
            print(f"  Status: SUCCESS")
            print(f"  Run ID: {result.run_id}")
            print(f"  Duration: {result.duration_seconds}s")
            print(f"  Result hash: {result.result_hash}")
            print(f"  Integrity check: {result.integrity_check}")
        else:
            print(f"  Status: FAILED")
            print(f"  Error: {result.error}")

        if args.output:
            output_path = args.output
            with open(output_path, "w") as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            print(f"  Result written to: {output_path}")

        print()


def cmd_audit_integrity(args):
    """Run an integrity verification sweep."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.base import AlgorithmParams
        from algorithms.registry import registry
        _ensure_algorithms()

        algo = registry.get("integrity_sweep")
        if not algo:
            print("  Error: integrity_sweep algorithm not found.")
            sys.exit(1)

        store = EvidenceStore()
        audit = AuditStream(db.session, store)

        params = AlgorithmParams(
            case_id=args.case,
            tenant_id=args.tenant,
            actor_id=None,
            actor_name="cli:audit",
        )
        context = {
            "db_session": db.session,
            "evidence_store": store,
            "audit_stream": audit,
        }

        print(f"\n  Running integrity verification sweep on case {args.case}...")
        result = algo.run(params, context)

        if result.success:
            payload = result.payload
            summary = payload.get("summary", {})
            print(f"  Status: {'ALL PASSED' if payload.get('all_passed') else 'ISSUES FOUND'}")
            print(f"  Total items: {payload.get('total_items', 0)}")
            print(f"  Pass: {summary.get('pass', 0)}")
            print(f"  Fail: {summary.get('fail', 0)}")
            print(f"  Missing: {summary.get('missing', 0)}")
            print(f"  Errors: {summary.get('error', 0)}")
            print(f"  Report hash: {payload.get('report_hash', 'N/A')}")
        else:
            print(f"  FAILED: {result.error}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            print(f"  Full report written to: {args.output}")

        print()


def cmd_export_court_package(args):
    """Generate a court package with all supporting reports."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.base import AlgorithmParams, hash_json
        from algorithms.registry import registry
        _ensure_algorithms()

        store = EvidenceStore()
        audit = AuditStream(db.session, store)

        params = AlgorithmParams(
            case_id=args.case,
            tenant_id=args.tenant,
            actor_id=None,
            actor_name="cli:export",
        )
        context = {
            "db_session": db.session,
            "evidence_store": store,
            "audit_stream": audit,
        }

        algorithms_to_run = [
            "integrity_sweep",
            "provenance_graph",
            "timeline_alignment",
            "bates_generator",
        ]

        results = {}
        print(f"\n  Generating court package for case {args.case}...")

        for algo_id in algorithms_to_run:
            algo = registry.get(algo_id)
            if not algo:
                print(f"  Warning: Algorithm '{algo_id}' not found, skipping.")
                continue

            print(f"  Running {algo_id}...", end=" ")
            result = algo.run(params, context)
            results[algo_id] = result.to_dict()

            if result.success:
                print(f"OK ({result.duration_seconds}s)")
            else:
                print(f"FAILED: {result.error}")

        package_hash = hash_json(results)
        package = {
            "case_id": args.case,
            "algorithms_run": list(results.keys()),
            "results": results,
            "package_hash": package_hash,
        }

        output_dir = args.output or "exports"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"court_package_case_{args.case}.json")

        with open(output_path, "w") as f:
            json.dump(package, f, indent=2, default=str)

        print(f"\n  Court package written to: {output_path}")
        print(f"  Package hash: {package_hash}")
        print(f"  Algorithms run: {len(results)}")
        print()


def cmd_replay_case(args):
    """Re-run all recorded algorithm runs and verify reproducibility."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.replay import ReplayEngine

        store = EvidenceStore()
        audit = AuditStream(db.session, store)
        engine = ReplayEngine()

        print(f"\n  Replaying all algorithm runs for case {args.case}...")
        report = engine.replay_case(
            case_id=args.case,
            tenant_id=args.tenant,
            db_session=db.session,
            evidence_store=store,
            audit_stream=audit,
        )

        print(f"  Status: {'ALL REPRODUCIBLE' if report.all_reproducible else 'DELTAS DETECTED'}")
        print(f"  Total runs replayed: {report.total_runs}")
        print(f"  Matched: {report.matched}")
        print(f"  Mismatched: {report.mismatched}")
        print(f"  Errors: {report.errors}")
        print(f"  Report hash: {report.report_hash}")

        if not report.all_reproducible:
            print("\n  Deltas:")
            for v in report.verdicts:
                if not v.match or v.replay_error:
                    print(f"    Run {v.original_run_id[:8]}: {v.algorithm_id}")
                    if v.replay_error:
                        print(f"      Error: {v.replay_error}")
                    elif not v.match:
                        print(f"      Original hash: {v.original_result_hash[:16]}...")
                        print(f"      Replay hash:   {v.replay_result_hash[:16]}...")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            print(f"\n  Full report written to: {args.output}")

        print()


def cmd_export_sealed(args):
    """Generate an integrity-sealed court package."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.sealed_export import SealedCourtPackageBuilder

        store = EvidenceStore()
        audit = AuditStream(db.session, store)
        builder = SealedCourtPackageBuilder(
            export_base=args.output or "exports/sealed"
        )

        print(f"\n  Building integrity-sealed court package for case {args.case}...")
        result = builder.build(
            case_id=args.case,
            tenant_id=args.tenant,
            db_session=db.session,
            evidence_store=store,
            audit_stream=audit,
            actor_name="cli:sealed_export",
        )

        if result.success:
            print(f"  Status: SEALED")
            print(f"  Package: {result.package_path}")
            print(f"  Seal hash: {result.seal_hash}")
            print(f"  Exhibits: {result.exhibit_count}")
            print(f"  Files: {result.total_files}")
            print(f"  Algorithms: {', '.join(result.algorithms_run)}")
        else:
            print(f"  FAILED: {result.error}")

        print()


def main():
    parser = argparse.ArgumentParser(
        prog="evident",
        description="Evident Technologies CLI — Court-Defensible Evidence Management",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- algorithms ---
    algo_parser = subparsers.add_parser("algorithms", help="Algorithm management")
    algo_sub = algo_parser.add_subparsers(dest="algo_command")

    # algorithms list
    algo_sub.add_parser("list", help="List registered algorithms")

    # algorithms run
    algo_run = algo_sub.add_parser("run", help="Run an algorithm")
    algo_run.add_argument("algorithm_id", help="Algorithm ID to run")
    algo_run.add_argument("--case", type=int, required=True, help="Case ID")
    algo_run.add_argument("--tenant", type=int, default=1, help="Tenant (organization) ID")
    algo_run.add_argument("--version", help="Specific algorithm version")
    algo_run.add_argument("--params", help="JSON string of extra parameters")
    algo_run.add_argument("--output", "-o", help="Output file path for results")

    # --- audit ---
    audit_parser = subparsers.add_parser("audit", help="Audit and integrity")
    audit_sub = audit_parser.add_subparsers(dest="audit_command")

    integrity = audit_sub.add_parser("integrity", help="Run integrity sweep")
    integrity.add_argument("--case", type=int, required=True, help="Case ID")
    integrity.add_argument("--tenant", type=int, default=1, help="Tenant ID")
    integrity.add_argument("--output", "-o", help="Output file path")

    # --- replay ---
    replay_parser = subparsers.add_parser("replay-case", help="Replay and verify reproducibility")
    replay_parser.add_argument("--case", type=int, required=True, help="Case ID")
    replay_parser.add_argument("--tenant", type=int, default=1, help="Tenant ID")
    replay_parser.add_argument("--output", "-o", help="Output file path for delta report")

    # --- export ---
    export_parser = subparsers.add_parser("export", help="Export court packages")
    export_sub = export_parser.add_subparsers(dest="export_command")

    court_pkg = export_sub.add_parser("court-package", help="Generate court package")
    court_pkg.add_argument("--case", type=int, required=True, help="Case ID")
    court_pkg.add_argument("--tenant", type=int, default=1, help="Tenant ID")
    court_pkg.add_argument("--output", "-o", help="Output directory")

    sealed_pkg = export_sub.add_parser("sealed-package", help="Generate integrity-sealed court package")
    sealed_pkg.add_argument("--case", type=int, required=True, help="Case ID")
    sealed_pkg.add_argument("--tenant", type=int, default=1, help="Tenant ID")
    sealed_pkg.add_argument("--output", "-o", help="Output directory")

    args = parser.parse_args()

    if args.command == "algorithms":
        if args.algo_command == "list":
            cmd_algorithms_list(args)
        elif args.algo_command == "run":
            cmd_algorithms_run(args)
        else:
            algo_parser.print_help()
    elif args.command == "audit":
        if args.audit_command == "integrity":
            cmd_audit_integrity(args)
        else:
            audit_parser.print_help()
    elif args.command == "replay-case":
        cmd_replay_case(args)
    elif args.command == "export":
        if args.export_command == "court-package":
            cmd_export_court_package(args)
        elif args.export_command == "sealed-package":
            cmd_export_sealed(args)
        else:
            export_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
