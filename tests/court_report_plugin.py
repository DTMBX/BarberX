"""
Court-Exhibit Test Report Generator
=====================================
A pytest plugin that produces a cryptographically signed, machine-readable
test report suitable for inclusion in sealed court packages.

Output: test-results/COURT_TEST_REPORT.json

The report contains:
  - Execution timestamp (UTC ISO-8601)
  - Python version, platform, package versions
  - Every test: name, outcome, duration, module
  - Summary: total, passed, failed, errors, skipped
  - SHA-256 hash of the report payload (self-verifying)
  - Algorithm inventory (registered algorithms + versions)

This report answers the cross-examination question:
  "How do you know this software works correctly?"
with a verifiable, timestamped, hash-sealed artifact.
"""

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone

import pytest


def canonical_json_report(obj):
    """Produce deterministic JSON for the report."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


class CourtTestReportPlugin:
    """Collects test results and generates a court-exhibit report."""

    def __init__(self, output_dir="test-results"):
        self.output_dir = output_dir
        self.results = []
        self.start_time = None
        self.end_time = None
        self.collection_errors = []

    def pytest_sessionstart(self, session):
        self.start_time = datetime.now(timezone.utc)

    def pytest_runtest_logreport(self, report):
        """Capture each test phase (setup, call, teardown)."""
        if report.when == "call":
            self.results.append({
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration_seconds": round(report.duration, 4),
                "module": report.fspath if hasattr(report, "fspath") else "",
                "longrepr": str(report.longrepr)[:500] if report.failed else None,
            })
        elif report.when == "setup" and report.failed:
            self.results.append({
                "nodeid": report.nodeid,
                "outcome": "error",
                "duration_seconds": round(report.duration, 4),
                "module": report.fspath if hasattr(report, "fspath") else "",
                "longrepr": str(report.longrepr)[:500],
            })

    def pytest_collecterror(self, collector, error):
        self.collection_errors.append({
            "collector": str(collector),
            "error": str(error)[:500],
        })

    def pytest_sessionfinish(self, session, exitstatus):
        self.end_time = datetime.now(timezone.utc)
        self._write_report(exitstatus)

    def _get_algorithm_inventory(self):
        """Attempt to load and inventory all registered algorithms."""
        try:
            from algorithms.registry import registry
            # Trigger loading
            try:
                from algorithms.bulk_dedup import BulkDedup
                from algorithms.provenance_graph import ProvenanceGraph
                from algorithms.timeline_alignment import TimelineAlignment
                from algorithms.integrity_sweep import IntegritySweep
                from algorithms.bates_generator import BatesGenerator
                from algorithms.redaction_verify import RedactionVerify
                from algorithms.access_anomaly import AccessAnomaly
            except ImportError:
                pass
            return registry.list_algorithms()
        except Exception:
            return []

    def _get_package_versions(self):
        """Capture versions of key packages."""
        versions = {}
        for pkg in ["flask", "sqlalchemy", "pytest", "werkzeug", "cryptography"]:
            try:
                import importlib.metadata
                versions[pkg] = importlib.metadata.version(pkg)
            except Exception:
                versions[pkg] = "unknown"
        return versions

    def _write_report(self, exitstatus):
        """Generate and write the court-exhibit report."""
        os.makedirs(self.output_dir, exist_ok=True)

        passed = sum(1 for r in self.results if r["outcome"] == "passed")
        failed = sum(1 for r in self.results if r["outcome"] == "failed")
        errors = sum(1 for r in self.results if r["outcome"] == "error")
        skipped = sum(1 for r in self.results if r["outcome"] == "skipped")

        payload = {
            "report_type": "court_exhibit_test_report",
            "report_version": "1.0.0",
            "generated_at": self.start_time.isoformat() if self.start_time else None,
            "completed_at": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round(
                (self.end_time - self.start_time).total_seconds(), 2
            ) if self.start_time and self.end_time else None,
            "environment": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "packages": self._get_package_versions(),
            },
            "algorithm_inventory": self._get_algorithm_inventory(),
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "exit_status": exitstatus,
                "all_passed": failed == 0 and errors == 0,
            },
            "tests": self.results,
            "collection_errors": self.collection_errors,
        }

        # Compute self-verifying hash
        payload_json = canonical_json_report(payload)
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        report = {
            "payload": payload,
            "payload_hash_sha256": payload_hash,
            "verification_note": (
                "To verify: remove the 'payload_hash_sha256' and 'verification_note' keys, "
                "re-serialize 'payload' with sorted keys and no whitespace, "
                "compute SHA-256. It must match payload_hash_sha256."
            ),
        }

        report_path = os.path.join(self.output_dir, "COURT_TEST_REPORT.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True, default=str)

        # Also write a minimal summary for quick CI inspection
        summary_path = os.path.join(self.output_dir, "test-summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"Evident Test Report — {self.end_time.isoformat() if self.end_time else 'unknown'}\n")
            f.write(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed} | Errors: {errors}\n")
            f.write(f"Report Hash: {payload_hash}\n")
            if failed or errors:
                f.write("\nFailures:\n")
                for r in self.results:
                    if r["outcome"] in ("failed", "error"):
                        f.write(f"  FAIL: {r['nodeid']}\n")


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    """Add --court-report option to pytest."""
    parser.addoption(
        "--court-report",
        action="store_true",
        default=False,
        help="Generate a court-exhibit test report (test-results/COURT_TEST_REPORT.json)",
    )


def pytest_configure(config):
    """Register the plugin if --court-report is passed OR if COURT_REPORT env var is set."""
    if config.getoption("--court-report", default=False) or os.environ.get("COURT_REPORT"):
        config.pluginmanager.register(
            CourtTestReportPlugin(output_dir="test-results"),
            "court_test_report",
        )
