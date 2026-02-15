"""
Algorithm C — Cross-Device Timeline Alignment
================================================
Normalizes timestamps across evidence files from multiple devices,
detects clock drift, and builds a unified timeline.

Design constraints:
  - No guesswork: if a timestamp is missing, it is marked "unknown".
  - Clock drift is detected by comparing overlapping events and
    recorded as an explicit offset.
  - Confidence labels: "exact" (from metadata), "derived" (calculated),
    "unknown" (missing or unreliable).
  - Fully deterministic given the same evidence metadata.
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)

# Confidence labels
CONFIDENCE_EXACT = "exact"
CONFIDENCE_DERIVED = "derived"
CONFIDENCE_UNKNOWN = "unknown"


def _parse_timestamp(value: Any) -> Optional[datetime]:
    """Attempt to parse a timestamp from various formats. Returns None on failure."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
        ):
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    return None


def _detect_clock_drift(
    device_groups: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Detect potential clock drift between devices.

    Strategy: for each pair of devices with overlapping time ranges,
    compute the median offset of events that are within a 5-minute
    window of each other.

    Returns a list of drift records.
    """
    drifts = []
    device_ids = sorted(device_groups.keys())

    for i in range(len(device_ids)):
        for j in range(i + 1, len(device_ids)):
            dev_a = device_ids[i]
            dev_b = device_ids[j]

            events_a = sorted(device_groups[dev_a], key=lambda e: e["timestamp"])
            events_b = sorted(device_groups[dev_b], key=lambda e: e["timestamp"])

            offsets = []
            for ea in events_a:
                for eb in events_b:
                    delta = abs((ea["timestamp"] - eb["timestamp"]).total_seconds())
                    if delta <= 300:  # within 5-minute window
                        offset = (ea["timestamp"] - eb["timestamp"]).total_seconds()
                        offsets.append(offset)

            if offsets:
                offsets.sort()
                median_offset = offsets[len(offsets) // 2]
                drifts.append({
                    "device_a": dev_a,
                    "device_b": dev_b,
                    "sample_count": len(offsets),
                    "median_offset_seconds": round(median_offset, 3),
                    "min_offset_seconds": round(min(offsets), 3),
                    "max_offset_seconds": round(max(offsets), 3),
                    "assessment": (
                        "negligible" if abs(median_offset) < 2
                        else "minor" if abs(median_offset) < 30
                        else "significant"
                    ),
                })

    return drifts


@registry.register
class TimelineAlignmentAlgorithm(AlgorithmBase):
    """Normalize cross-device timestamps and detect clock drift."""

    @property
    def algorithm_id(self) -> str:
        return "timeline_alignment"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build an aligned timeline for all evidence in a case.

        Returns payload with:
          - timeline_entries: Sorted list of timeline entries with confidence.
          - clock_drift_analysis: Drift records between device pairs.
          - device_summary: Per-device statistics.
          - assumptions: Explicit record of all assumptions made.
          - timeline_hash: SHA-256 of the canonical timeline.
        """
        db_session = context["db_session"]

        from models.evidence import EvidenceItem, CaseEvidence
        from models.legal_case import LegalCase

        # Tenant isolation
        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get case evidence
        links = (
            db_session.query(CaseEvidence)
            .filter_by(case_id=params.case_id)
            .filter(CaseEvidence.unlinked_at.is_(None))
            .all()
        )
        evidence_ids = [link.evidence_id for link in links]

        items = (
            db_session.query(EvidenceItem)
            .filter(EvidenceItem.id.in_(evidence_ids))
            .all()
        ) if evidence_ids else []

        # Build timeline entries
        timeline_entries = []
        device_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        assumptions = []
        input_hashes = []

        for item in items:
            if item.hash_sha256:
                input_hashes.append(item.hash_sha256)

            # Determine timestamp and confidence
            ts = _parse_timestamp(item.collected_date)
            if ts:
                confidence = CONFIDENCE_EXACT
            else:
                # Try created_at as fallback
                ts = _parse_timestamp(item.created_at)
                if ts:
                    confidence = CONFIDENCE_DERIVED
                    assumptions.append({
                        "evidence_id": item.id,
                        "assumption": "Used record created_at as timestamp proxy; original collection date unavailable.",
                        "original_filename": item.original_filename,
                    })
                else:
                    confidence = CONFIDENCE_UNKNOWN

            device_label = item.device_label or "unknown_device"

            entry = {
                "evidence_id": item.id,
                "hash_sha256": item.hash_sha256,
                "original_filename": item.original_filename,
                "device_label": device_label,
                "device_type": item.device_type,
                "timestamp_iso": ts.isoformat() if ts else None,
                "timestamp_confidence": confidence,
                "file_type": item.file_type,
                "duration_seconds": item.duration_seconds,
            }
            timeline_entries.append(entry)

            if ts:
                device_groups[device_label].append({
                    **entry,
                    "timestamp": ts,
                })

        # Sort entries: exact first, then derived, then unknown; within same confidence by timestamp
        confidence_order = {CONFIDENCE_EXACT: 0, CONFIDENCE_DERIVED: 1, CONFIDENCE_UNKNOWN: 2}
        timeline_entries.sort(
            key=lambda e: (
                confidence_order.get(e["timestamp_confidence"], 3),
                e["timestamp_iso"] or "9999",
            )
        )

        # Clock drift analysis
        clock_drifts = _detect_clock_drift(device_groups)

        # Device summary
        device_summary = {}
        for device, events in sorted(device_groups.items()):
            timestamps = [e["timestamp"] for e in events]
            device_summary[device] = {
                "event_count": len(events),
                "earliest": min(timestamps).isoformat() if timestamps else None,
                "latest": max(timestamps).isoformat() if timestamps else None,
            }

        timeline = {
            "case_id": params.case_id,
            "total_entries": len(timeline_entries),
            "confidence_breakdown": {
                CONFIDENCE_EXACT: sum(1 for e in timeline_entries if e["timestamp_confidence"] == CONFIDENCE_EXACT),
                CONFIDENCE_DERIVED: sum(1 for e in timeline_entries if e["timestamp_confidence"] == CONFIDENCE_DERIVED),
                CONFIDENCE_UNKNOWN: sum(1 for e in timeline_entries if e["timestamp_confidence"] == CONFIDENCE_UNKNOWN),
            },
            "timeline_entries": timeline_entries,
            "clock_drift_analysis": clock_drifts,
            "device_summary": device_summary,
            "assumptions": assumptions,
        }
        timeline_hash = hash_json(timeline)
        timeline["timeline_hash"] = timeline_hash

        return {
            **timeline,
            "output_hashes": [timeline_hash],
            "input_hashes": input_hashes,
        }
