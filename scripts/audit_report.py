#!/usr/bin/env python
"""
Audit Transparency Report Generator
=====================================
Produces deterministic, read-only reports from the ChainOfCustody table.

Usage:
    # Full activity report (JSON to stdout)
    python scripts/audit_report.py activity

    # Evidence access history for a specific item
    python scripts/audit_report.py evidence --id 42

    # Actor summary (who did what, how many times)
    python scripts/audit_report.py actors

    # Export history (all export-related actions)
    python scripts/audit_report.py exports

    # Write any report to file
    python scripts/audit_report.py activity --output report.json

Options:
    --since YYYY-MM-DD   Filter records after this date
    --until YYYY-MM-DD   Filter records before this date
    --format json|csv    Output format (default: json)

This script is READ-ONLY.  It never modifies the database.
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_app():
    """Create a Flask app context for DB access."""
    from app_config import create_app
    app = create_app()
    return app


def _parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD into a UTC datetime."""
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _base_query(session, db, model, args):
    """Build base query with optional date filters."""
    q = session.query(model).order_by(model.action_timestamp.asc())
    if args.since:
        q = q.filter(model.action_timestamp >= _parse_date(args.since))
    if args.until:
        q = q.filter(model.action_timestamp <= _parse_date(args.until))
    return q


def _row_to_dict(row) -> dict:
    """Convert a ChainOfCustody row to a serialisable dict."""
    return {
        "id": row.id,
        "evidence_id": row.evidence_id,
        "action": row.action,
        "actor_id": row.actor_id,
        "actor_name": row.actor_name,
        "action_timestamp": row.action_timestamp.isoformat() if row.action_timestamp else None,
        "action_details": row.action_details,
        "ip_address": row.ip_address,
        "hash_before": row.hash_before,
        "hash_after": row.hash_after,
    }


def _output(data, args):
    """Write data to stdout or file in the requested format."""
    fmt = getattr(args, "format", "json") or "json"
    dest = getattr(args, "output", None)

    if fmt == "csv":
        if not data:
            text = ""
        else:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            text = buf.getvalue()
    else:
        text = json.dumps(data, indent=2, default=str)

    if dest:
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Report written to {dest}", file=sys.stderr)
    else:
        print(text)


# -------------------------------------------------------------------
# Sub-commands
# -------------------------------------------------------------------

def cmd_activity(args):
    """Full chronological activity log."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from models.evidence import ChainOfCustody
        rows = _base_query(db.session, db, ChainOfCustody, args).all()
        data = [_row_to_dict(r) for r in rows]
        _output(data, args)
        print(f"\n--- {len(data)} audit records ---", file=sys.stderr)


def cmd_evidence(args):
    """Access history for a single evidence item."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from models.evidence import ChainOfCustody
        q = _base_query(db.session, db, ChainOfCustody, args)
        q = q.filter(ChainOfCustody.evidence_id == args.id)
        rows = q.all()
        data = [_row_to_dict(r) for r in rows]
        _output(data, args)
        print(f"\n--- {len(data)} records for evidence_id={args.id} ---", file=sys.stderr)


def cmd_actors(args):
    """Summary of actions per actor."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from models.evidence import ChainOfCustody
        from sqlalchemy import func
        q = db.session.query(
            ChainOfCustody.actor_id,
            ChainOfCustody.actor_name,
            ChainOfCustody.action,
            func.count().label("count"),
        ).group_by(
            ChainOfCustody.actor_id,
            ChainOfCustody.actor_name,
            ChainOfCustody.action,
        ).order_by(
            ChainOfCustody.actor_name,
            ChainOfCustody.action,
        )
        if args.since:
            q = q.filter(ChainOfCustody.action_timestamp >= _parse_date(args.since))
        if args.until:
            q = q.filter(ChainOfCustody.action_timestamp <= _parse_date(args.until))

        rows = q.all()
        data = [
            {
                "actor_id": r.actor_id,
                "actor_name": r.actor_name,
                "action": r.action,
                "count": r.count,
            }
            for r in rows
        ]
        _output(data, args)
        print(f"\n--- {len(data)} actor/action groups ---", file=sys.stderr)


def cmd_exports(args):
    """All export-related audit events."""
    app = _get_app()
    with app.app_context():
        from auth.models import db
        from models.evidence import ChainOfCustody
        q = _base_query(db.session, db, ChainOfCustody, args)
        q = q.filter(ChainOfCustody.action.like("%export%"))
        rows = q.all()
        data = [_row_to_dict(r) for r in rows]
        _output(data, args)
        print(f"\n--- {len(data)} export records ---", file=sys.stderr)


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evident — Audit Transparency Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", "-o", help="Write to file instead of stdout")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("activity", help="Full chronological audit log")

    ev_parser = sub.add_parser("evidence", help="History for a single evidence item")
    ev_parser.add_argument("--id", type=int, required=True, help="Evidence item ID")

    sub.add_parser("actors", help="Action counts per actor")
    sub.add_parser("exports", help="Export-related events only")

    args = parser.parse_args()

    commands = {
        "activity": cmd_activity,
        "evidence": cmd_evidence,
        "actors": cmd_actors,
        "exports": cmd_exports,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
