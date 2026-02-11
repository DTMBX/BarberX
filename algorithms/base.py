"""
Algorithm Base Classes
=======================
Defines the contract that every court-defensible algorithm must satisfy.

Every algorithm:
  1. Declares a unique (algorithm_id, version) pair.
  2. Accepts typed, serializable parameters (AlgorithmParams).
  3. Returns an AlgorithmResult with full provenance metadata.
  4. Is deterministic: same inputs + params → identical result hash.
  5. Emits audit events via the AuditStream interface.
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Canonical JSON serialization (deterministic)
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> str:
    """
    Produce a deterministic JSON string.

    Keys are sorted, no extra whitespace, ASCII-safe.
    This ensures that hashing the output is reproducible across runs.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def hash_json(obj: Any) -> str:
    """SHA-256 of the canonical JSON representation."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AlgorithmParams:
    """
    Immutable, serializable parameters for an algorithm run.

    Subclass this for algorithm-specific parameters. The base carries
    tenant/case context that every algorithm requires.
    """
    case_id: int
    tenant_id: int  # organization_id for isolation
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def canonical(self) -> str:
        return canonical_json(self.to_dict())


@dataclass
class AlgorithmResult:
    """
    Standard result envelope for every algorithm run.

    Contains full provenance metadata required for court defensibility.
    """
    # Identity
    algorithm_id: str
    algorithm_version: str
    run_id: str  # UUIDv4 assigned at run start

    # Provenance
    input_hashes: List[str]  # SHA-256 of each input object
    output_hashes: List[str] = field(default_factory=list)  # SHA-256 of each output
    params_hash: str = ""  # SHA-256 of canonical params
    result_hash: str = ""  # SHA-256 of the canonical result payload

    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)

    # Timing
    started_at: str = ""  # ISO-8601 UTC
    completed_at: str = ""  # ISO-8601 UTC
    duration_seconds: float = 0.0

    # Status
    success: bool = True
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    # Integrity
    integrity_check: str = ""  # SHA-256 of entire result (self-verifying)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compute_integrity(self) -> str:
        """
        Compute a self-verifying hash of the result.

        Excludes the integrity_check field itself to avoid circularity.
        """
        d = self.to_dict()
        d.pop("integrity_check", None)
        return hash_json(d)

    def finalize(self) -> "AlgorithmResult":
        """Set the integrity_check field and return self."""
        self.integrity_check = self.compute_integrity()
        return self


# ---------------------------------------------------------------------------
# Algorithm base class
# ---------------------------------------------------------------------------

class AlgorithmBase(ABC):
    """
    Abstract base for all court-defensible algorithms.

    Subclasses must implement:
      - algorithm_id (property) — unique identifier e.g. "bulk_dedup"
      - algorithm_version (property) — semver string e.g. "1.0.0"
      - _execute(params, context) — the deterministic core logic
    """

    @property
    @abstractmethod
    def algorithm_id(self) -> str:
        """Unique algorithm identifier (lowercase, underscored)."""
        ...

    @property
    @abstractmethod
    def algorithm_version(self) -> str:
        """Semantic version of this algorithm implementation."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for documentation and UI."""
        return self.__class__.__doc__ or ""

    @abstractmethod
    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Core algorithm logic. Must be deterministic.

        Args:
            params: Algorithm parameters (case, tenant, extras).
            context: Runtime context (db_session, evidence_store, etc.).

        Returns:
            Payload dict that will be wrapped in AlgorithmResult.
        """
        ...

    def run(
        self,
        params: AlgorithmParams,
        context: Dict[str, Any],
        input_hashes: Optional[List[str]] = None,
    ) -> AlgorithmResult:
        """
        Execute the algorithm with full provenance tracking.

        This method:
        1. Records start time.
        2. Computes params hash for reproducibility.
        3. Calls _execute() for the deterministic core.
        4. Wraps the result with metadata.
        5. Computes the result integrity hash.
        6. Emits an audit event if an AuditStream is in context.

        Args:
            params: Typed algorithm parameters.
            context: Must include 'db_session' and 'evidence_store'.
                     May include 'audit_stream'.
            input_hashes: SHA-256 hashes of input evidence objects.

        Returns:
            Finalized AlgorithmResult with integrity check.
        """
        import uuid

        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        result = AlgorithmResult(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            run_id=run_id,
            input_hashes=input_hashes or [],
            params_hash=hash_json(params.to_dict()),
            started_at=started_at.isoformat(),
        )

        try:
            payload = self._execute(params, context)
            result.payload = payload
            result.output_hashes = payload.get("output_hashes", [])
            result.success = True
        except Exception as exc:
            logger.error(
                "Algorithm %s v%s run %s failed: %s",
                self.algorithm_id,
                self.algorithm_version,
                run_id,
                exc,
                exc_info=True,
            )
            result.success = False
            result.error = str(exc)

        completed_at = datetime.now(timezone.utc)
        result.completed_at = completed_at.isoformat()
        result.duration_seconds = round(
            (completed_at - started_at).total_seconds(), 4
        )
        result.result_hash = hash_json(result.payload)
        result.finalize()

        # Emit audit event
        self._emit_audit(result, params, context)

        return result

    def _emit_audit(
        self,
        result: AlgorithmResult,
        params: AlgorithmParams,
        context: Dict[str, Any],
    ) -> None:
        """Append an audit record for this algorithm run."""
        audit_stream = context.get("audit_stream")
        if audit_stream is None:
            return

        action = (
            "algorithm.completed" if result.success else "algorithm.failed"
        )
        details = {
            "algorithm_id": self.algorithm_id,
            "algorithm_version": self.algorithm_version,
            "run_id": result.run_id,
            "params_hash": result.params_hash,
            "result_hash": result.result_hash,
            "integrity_check": result.integrity_check,
            "duration_seconds": result.duration_seconds,
            "input_count": len(result.input_hashes),
            "output_count": len(result.output_hashes),
        }
        if result.error:
            details["error"] = result.error

        try:
            audit_stream.record(
                evidence_id=str(params.case_id),
                action=action,
                actor_id=params.actor_id,
                actor_name=params.actor_name,
                details=details,
            )
        except Exception as exc:
            logger.warning("Failed to emit audit for algorithm run %s: %s", result.run_id, exc)
