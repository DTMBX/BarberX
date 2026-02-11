"""
Algorithm G — Access Anomaly Detector (Anti-Tamper + Misuse)
==============================================================
Detects suspicious access patterns by analyzing the audit log:
  - Excessive share-link access from a single IP.
  - Repeated downloads of the same evidence in a short window.
  - Failed authentication bursts.
  - Unusual off-hours access patterns.

Design constraints:
  - Purely operational security; avoids accusations or presumptions of guilt.
  - Reports observations with statistical context, not conclusions.
  - Deterministic given the same audit log entries.
  - Emits alerts into the audit log (append-only).
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)


# Anomaly severity levels
SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_ALERT = "alert"


def _detect_download_bursts(
    entries: List[Dict[str, Any]],
    window_minutes: int = 10,
    threshold: int = 5,
) -> List[Dict[str, Any]]:
    """
    Detect repeated downloads of the same evidence within a time window.

    Returns list of anomaly records.
    """
    # Group by (evidence_id, actor)
    groups: Dict[str, List[datetime]] = defaultdict(list)
    for entry in entries:
        if "download" in entry.get("action", "").lower():
            key = f"{entry.get('evidence_id', '?')}:{entry.get('actor', '?')}"
            ts = entry.get("timestamp")
            if ts:
                groups[key].append(ts)

    anomalies = []
    for key, timestamps in groups.items():
        timestamps.sort()
        for i in range(len(timestamps)):
            window_end = timestamps[i] + timedelta(minutes=window_minutes)
            count = sum(1 for t in timestamps[i:] if t <= window_end)
            if count >= threshold:
                evidence_id, actor = key.split(":", 1)
                anomalies.append({
                    "type": "download_burst",
                    "severity": SEVERITY_WARNING,
                    "evidence_id": evidence_id,
                    "actor": actor,
                    "count_in_window": count,
                    "window_start": timestamps[i].isoformat(),
                    "window_minutes": window_minutes,
                    "description": (
                        f"Evidence {evidence_id} downloaded {count} times "
                        f"within {window_minutes} minutes by {actor}."
                    ),
                })
                break  # One anomaly per group

    return anomalies


def _detect_share_link_abuse(
    entries: List[Dict[str, Any]],
    window_minutes: int = 60,
    threshold: int = 20,
) -> List[Dict[str, Any]]:
    """Detect excessive share-link access from a single IP."""
    # Group by (ip_address)
    ip_accesses: Dict[str, List[datetime]] = defaultdict(list)
    for entry in entries:
        if "share" in entry.get("action", "").lower() or "accessed" in entry.get("action", "").lower():
            ip = entry.get("ip_address", "unknown")
            ts = entry.get("timestamp")
            if ts:
                ip_accesses[ip].append(ts)

    anomalies = []
    for ip, timestamps in ip_accesses.items():
        timestamps.sort()
        for i in range(len(timestamps)):
            window_end = timestamps[i] + timedelta(minutes=window_minutes)
            count = sum(1 for t in timestamps[i:] if t <= window_end)
            if count >= threshold:
                anomalies.append({
                    "type": "share_link_abuse",
                    "severity": SEVERITY_ALERT,
                    "ip_address": ip,
                    "count_in_window": count,
                    "window_start": timestamps[i].isoformat(),
                    "window_minutes": window_minutes,
                    "description": (
                        f"IP {ip} accessed share links {count} times "
                        f"within {window_minutes} minutes."
                    ),
                })
                break

    return anomalies


def _detect_auth_failures(
    entries: List[Dict[str, Any]],
    window_minutes: int = 15,
    threshold: int = 10,
) -> List[Dict[str, Any]]:
    """Detect failed authentication bursts from a single IP."""
    ip_failures: Dict[str, List[datetime]] = defaultdict(list)
    for entry in entries:
        action = entry.get("action", "").lower()
        if "fail" in action and ("auth" in action or "login" in action):
            ip = entry.get("ip_address", "unknown")
            ts = entry.get("timestamp")
            if ts:
                ip_failures[ip].append(ts)

    anomalies = []
    for ip, timestamps in ip_failures.items():
        timestamps.sort()
        for i in range(len(timestamps)):
            window_end = timestamps[i] + timedelta(minutes=window_minutes)
            count = sum(1 for t in timestamps[i:] if t <= window_end)
            if count >= threshold:
                anomalies.append({
                    "type": "auth_failure_burst",
                    "severity": SEVERITY_ALERT,
                    "ip_address": ip,
                    "count_in_window": count,
                    "window_start": timestamps[i].isoformat(),
                    "window_minutes": window_minutes,
                    "description": (
                        f"IP {ip} had {count} failed auth attempts "
                        f"within {window_minutes} minutes."
                    ),
                })
                break

    return anomalies


def _detect_off_hours_access(
    entries: List[Dict[str, Any]],
    off_hours_start: int = 22,  # 10 PM
    off_hours_end: int = 6,  # 6 AM
) -> List[Dict[str, Any]]:
    """Detect access outside normal business hours."""
    off_hours_actors: Dict[str, int] = Counter()
    for entry in entries:
        ts = entry.get("timestamp")
        if ts:
            hour = ts.hour
            if hour >= off_hours_start or hour < off_hours_end:
                actor = entry.get("actor", "unknown")
                off_hours_actors[actor] += 1

    anomalies = []
    for actor, count in off_hours_actors.most_common():
        if count >= 5:  # Minimum threshold
            anomalies.append({
                "type": "off_hours_access",
                "severity": SEVERITY_INFO,
                "actor": actor,
                "off_hours_count": count,
                "hours_range": f"{off_hours_start}:00-{off_hours_end}:00 UTC",
                "description": (
                    f"User {actor} accessed evidence {count} times "
                    f"outside business hours ({off_hours_start}:00-{off_hours_end}:00 UTC)."
                ),
            })

    return anomalies


@registry.register
class AccessAnomalyAlgorithm(AlgorithmBase):
    """Detect suspicious access patterns from the audit log."""

    @property
    def algorithm_id(self) -> str:
        return "access_anomaly"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scan audit logs for access anomalies within a case.

        Params.extra keys:
          - lookback_days (int): How far back to scan (default: 30).
          - download_burst_threshold (int): Downloads per window (default: 5).
          - share_abuse_threshold (int): Share accesses per window (default: 20).
          - auth_failure_threshold (int): Failed auths per window (default: 10).

        Returns payload with:
          - anomalies: List of detected anomaly records.
          - summary: Counts by type and severity.
          - report_hash: SHA-256 of the report.
        """
        db_session = context["db_session"]

        lookback_days = params.extra.get("lookback_days", 30)
        download_threshold = params.extra.get("download_burst_threshold", 5)
        share_threshold = params.extra.get("share_abuse_threshold", 20)
        auth_threshold = params.extra.get("auth_failure_threshold", 10)

        from models.evidence import ChainOfCustody, CaseEvidence
        from models.legal_case import LegalCase

        # Tenant isolation
        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get evidence IDs for this case
        links = (
            db_session.query(CaseEvidence)
            .filter_by(case_id=params.case_id)
            .filter(CaseEvidence.unlinked_at.is_(None))
            .all()
        )
        evidence_ids = [link.evidence_id for link in links]

        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        # Query audit entries
        audit_entries_raw = (
            db_session.query(ChainOfCustody)
            .filter(ChainOfCustody.evidence_id.in_(evidence_ids))
            .filter(ChainOfCustody.action_timestamp >= cutoff)
            .order_by(ChainOfCustody.action_timestamp)
            .all()
        ) if evidence_ids else []

        # Normalize to dicts for analysis
        entries = []
        for entry in audit_entries_raw:
            entries.append({
                "evidence_id": str(entry.evidence_id),
                "action": entry.action or "",
                "actor": entry.actor_name or "unknown",
                "actor_id": entry.actor_id,
                "timestamp": entry.action_timestamp,
                "ip_address": entry.ip_address or "unknown",
            })

        # Run detectors
        all_anomalies = []
        all_anomalies.extend(_detect_download_bursts(entries, threshold=download_threshold))
        all_anomalies.extend(_detect_share_link_abuse(entries, threshold=share_threshold))
        all_anomalies.extend(_detect_auth_failures(entries, threshold=auth_threshold))
        all_anomalies.extend(_detect_off_hours_access(entries))

        # Sort by severity
        severity_order = {SEVERITY_ALERT: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}
        all_anomalies.sort(key=lambda a: severity_order.get(a.get("severity", ""), 3))

        # Summary
        type_counts = Counter(a["type"] for a in all_anomalies)
        severity_counts = Counter(a["severity"] for a in all_anomalies)

        report = {
            "case_id": params.case_id,
            "lookback_days": lookback_days,
            "audit_entries_scanned": len(entries),
            "total_anomalies": len(all_anomalies),
            "anomalies": all_anomalies,
            "summary_by_type": dict(type_counts),
            "summary_by_severity": dict(severity_counts),
            "parameters": {
                "lookback_days": lookback_days,
                "download_burst_threshold": download_threshold,
                "share_abuse_threshold": share_threshold,
                "auth_failure_threshold": auth_threshold,
            },
        }
        report_hash = hash_json(report)
        report["report_hash"] = report_hash

        return {
            **report,
            "output_hashes": [report_hash],
        }
