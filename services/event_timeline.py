"""
Event Timeline Builder
======================
Produces a canonical, deterministic event timeline from EventEvidence
records and their associated EvidenceItem metadata.

This service is METADATA-ONLY:
  - No video frames are altered.
  - No transcoding or enhancement.
  - No inference of fault, intent, or legal significance.
  - Alignment is sync_offset_ms + arithmetic only.

The output is a deterministic JSON structure whose SHA-256 hash is
recorded in the audit log, protecting against post-hoc manipulation
claims.

Usage:
    from services.event_timeline import EventTimelineBuilder
    builder = EventTimelineBuilder()
    result = builder.build(event_id, user_id=current_user.id)
    # result.timeline  → dict (the canonical JSON payload)
    # result.hash      → str  (SHA-256 of canonical JSON)
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from auth.models import db
from models.case_event import Event, EventEvidence
from models.evidence import EvidenceItem

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class TimelineBuildResult:
    """Immutable result of a timeline build operation."""
    success: bool
    timeline: Optional[Dict[str, Any]] = None
    hash: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TrackInfo:
    """Metadata for a single evidence track in the timeline."""
    evidence_id: int
    evidence_store_id: Optional[str]
    camera_label: str
    original_filename: str
    file_type: Optional[str]
    mime_type: Optional[str]
    hash_sha256: Optional[str]
    offset_ms: int
    duration_ms: Optional[int]
    is_sync_anchor: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_store_id": self.evidence_store_id,
            "camera_label": self.camera_label,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "hash_sha256": self.hash_sha256,
            "offset_ms": self.offset_ms,
            "duration_ms": self.duration_ms,
            "is_sync_anchor": self.is_sync_anchor,
        }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class EventTimelineBuilder:
    """
    Builds a canonical event timeline from event-evidence links.

    The timeline is a pure function of the data: same inputs always
    produce the same output and the same hash.
    """

    def build(self, event_id: str, user_id: Optional[int] = None) -> TimelineBuildResult:
        """
        Build a timeline for the given event.

        Args:
            event_id: UUID of the event.
            user_id: Actor performing the build (for audit).

        Returns:
            TimelineBuildResult with timeline dict and SHA-256 hash.
        """
        event = db.session.get(Event, event_id)
        if not event:
            return TimelineBuildResult(success=False, error="Event not found")

        # Load all evidence links for this event
        links = EventEvidence.query.filter_by(event_id=event_id).all()
        if not links:
            return TimelineBuildResult(
                success=False, error="No evidence linked to this event",
            )

        tracks: List[TrackInfo] = []
        evidence_ids: List[int] = []
        offsets_used: Dict[int, int] = {}

        for link in links:
            evidence = db.session.get(EvidenceItem, link.evidence_id)
            if not evidence:
                continue

            duration_ms = self._get_duration_ms(evidence)
            offset = link.sync_offset_ms or 0

            tracks.append(TrackInfo(
                evidence_id=evidence.id,
                evidence_store_id=evidence.evidence_store_id,
                camera_label=link.camera_label or evidence.device_label or evidence.original_filename,
                original_filename=evidence.original_filename,
                file_type=evidence.file_type,
                mime_type=evidence.mime_type,
                hash_sha256=evidence.hash_sha256,
                offset_ms=offset,
                duration_ms=duration_ms,
                is_sync_anchor=bool(link.is_sync_anchor),
            ))
            evidence_ids.append(evidence.id)
            offsets_used[evidence.id] = offset

        if not tracks:
            return TimelineBuildResult(
                success=False, error="No valid evidence tracks found",
            )

        # Sort by offset (anchor first, then ascending offset)
        tracks.sort(key=lambda t: (not t.is_sync_anchor, t.offset_ms))

        # Compute timeline bounds
        timeline_start_offset = min(t.offset_ms for t in tracks)
        timeline_end_offset = max(
            t.offset_ms + (t.duration_ms or 0) for t in tracks
        )
        total_duration_ms = timeline_end_offset - timeline_start_offset

        # Build canonical payload
        generated_at = datetime.now(timezone.utc).isoformat()
        timeline = {
            "event_id": event.id,
            "event_name": event.event_name,
            "case_id": event.case_id,
            "event_start": event.event_start.isoformat() if event.event_start else None,
            "event_end": event.event_end.isoformat() if event.event_end else None,
            "timeline_start_offset_ms": timeline_start_offset,
            "timeline_end_offset_ms": timeline_end_offset,
            "total_duration_ms": total_duration_ms,
            "track_count": len(tracks),
            "tracks": [t.to_dict() for t in tracks],
            "generated_at": generated_at,
            "metadata_only_notice": (
                "Timeline alignment is metadata-only. "
                "Original recordings are unaltered."
            ),
        }

        # Deterministic hash (excludes generated_at for reproducibility)
        timeline_hash = self._compute_hash(timeline)
        timeline["timeline_hash"] = timeline_hash

        # Audit
        self._audit(
            event_id=event.id,
            evidence_ids=evidence_ids,
            offsets_used=offsets_used,
            timeline_hash=timeline_hash,
            user_id=user_id,
        )

        return TimelineBuildResult(
            success=True,
            timeline=timeline,
            hash=timeline_hash,
        )

    # ------------------------------------------------------------------
    # Duration extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _get_duration_ms(evidence: EvidenceItem) -> Optional[int]:
        """
        Extract duration in milliseconds from evidence metadata.

        Sources checked in order:
          1. EvidenceItem.duration_seconds (populated at ingest)
          2. Evidence store manifest metadata
          3. None (unknown)
        """
        # Source 1: DB column
        if evidence.duration_seconds and evidence.duration_seconds > 0:
            return int(evidence.duration_seconds * 1000)

        # Source 2: Evidence store manifest
        if evidence.evidence_store_id:
            try:
                from services.evidence_store import EvidenceStore
                store = EvidenceStore()
                manifest = store.load_manifest(evidence.evidence_store_id)
                if manifest:
                    for deriv in manifest.derivatives:
                        if deriv.derivative_type == "metadata":
                            meta_path = store.get_derivative_path(
                                evidence.hash_sha256,
                                "metadata",
                                deriv.filename,
                            )
                            if meta_path:
                                import json as _json
                                from pathlib import Path
                                meta_data = _json.loads(
                                    Path(meta_path).read_text(encoding="utf-8"),
                                )
                                dur = meta_data.get("duration_seconds", 0)
                                if dur and dur > 0:
                                    return int(float(dur) * 1000)
            except Exception as exc:
                logger.debug("Could not read manifest for %s: %s", evidence.id, exc)

        return None

    # ------------------------------------------------------------------
    # Deterministic hash
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_hash(timeline: Dict[str, Any]) -> str:
        """
        Compute SHA-256 of the canonical timeline payload.

        The hash covers tracks and offsets but excludes the mutable
        generated_at timestamp so that the same logical timeline always
        yields the same hash.
        """
        hashable = {
            "event_id": timeline["event_id"],
            "tracks": timeline["tracks"],
        }
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    @staticmethod
    def _audit(event_id, evidence_ids, offsets_used, timeline_hash, user_id):
        """
        Record audit entry: event_timeline_generated.

        Logged fields:
          - event_id
          - evidence_ids
          - offsets used
          - hash of generated timeline JSON
        """
        try:
            from services.evidence_store import EvidenceStore
            from services.audit_stream import AuditStream

            store = EvidenceStore()
            audit = AuditStream(db.session, store)
            audit.record(
                evidence_id=str(event_id),
                action="event_timeline_generated",
                actor_id=user_id,
                actor_name=None,
                details={
                    "event_id": event_id,
                    "evidence_ids": evidence_ids,
                    "offsets_used": {str(k): v for k, v in offsets_used.items()},
                    "timeline_hash": timeline_hash,
                },
            )
        except Exception as exc:
            logger.warning("Audit write failed for timeline build: %s", exc)
