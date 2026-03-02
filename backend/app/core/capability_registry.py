"""
AI Assistant Capability Registry
==================================
Defines a restricted, auditable action layer for the AI Assistant.

This is NOT a general-purpose AI system. It is a capability-restricted
action dispatcher. Every action:
  - Has a declared capability_id.
  - Requires a specific role.
  - Validates input against a schema.
  - Is logged to the audit stream.
  - Returns a deterministic, traceable result.

No direct database access from the assistant layer.
No undeclared capabilities.
No silent execution.

Copyright 2024-2026 Evident Technologies, LLC. All rights reserved.
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schema validation primitives
# ---------------------------------------------------------------------------

class ParamType(Enum):
    """Supported parameter types for capability schemas."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FILE = "file"
    LIST = "list"
    DICT = "dict"


@dataclass(frozen=True)
class ParamSchema:
    """Schema for a single capability parameter."""
    name: str
    param_type: ParamType
    required: bool = True
    description: str = ""
    max_length: Optional[int] = None
    allowed_values: Optional[tuple] = None


@dataclass(frozen=True)
class CapabilityDefinition:
    """
    Immutable definition of a single assistant capability.

    Once registered, a capability cannot be modified. This ensures
    the registry is auditable and deterministic.
    """
    capability_id: str
    description: str
    required_role: str  # e.g., "PRO_USER", "MODERATOR", "ADMIN"
    params: tuple  # tuple of ParamSchema
    audit_required: bool = True
    handler_name: str = ""  # Dotted path to handler function


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class CapabilityValidationError(Exception):
    """Raised when capability input fails schema validation."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {'; '.join(errors)}")


# ---------------------------------------------------------------------------
# Input validator
# ---------------------------------------------------------------------------

def validate_args(params: tuple, args: Dict[str, Any]) -> List[str]:
    """
    Validate arguments against a capability's parameter schema.

    Returns a list of error strings (empty if valid).
    """
    errors = []

    for param in params:
        value = args.get(param.name)

        if param.required and value is None:
            errors.append(f"Missing required parameter: {param.name}")
            continue

        if value is None:
            continue

        # Type checking
        expected_types = {
            ParamType.STRING: str,
            ParamType.INTEGER: int,
            ParamType.BOOLEAN: bool,
            ParamType.FILE: str,  # File path or ID as string
            ParamType.LIST: list,
            ParamType.DICT: dict,
        }

        expected = expected_types.get(param.param_type)
        if expected and not isinstance(value, expected):
            errors.append(
                f"Parameter '{param.name}' must be {param.param_type.value}, "
                f"got {type(value).__name__}"
            )
            continue

        if param.max_length and isinstance(value, str) and len(value) > param.max_length:
            errors.append(
                f"Parameter '{param.name}' exceeds max length "
                f"({len(value)} > {param.max_length})"
            )

        if param.allowed_values and value not in param.allowed_values:
            errors.append(
                f"Parameter '{param.name}' must be one of "
                f"{list(param.allowed_values)}, got '{value}'"
            )

    # Reject unknown parameters
    known_names = {p.name for p in params}
    unknown = set(args.keys()) - known_names
    if unknown:
        errors.append(f"Unknown parameters: {', '.join(sorted(unknown))}")

    return errors


# ---------------------------------------------------------------------------
# Audit record
# ---------------------------------------------------------------------------

@dataclass
class ActionAuditRecord:
    """Immutable record of an assistant action execution."""
    audit_id: str
    request_id: str
    capability_id: str
    case_id: Optional[str]
    actor_id: Optional[int]
    actor_name: Optional[str]
    timestamp: str
    args_hash: str
    status: str  # "success", "denied", "validation_error", "handler_error"
    result_summary: Optional[str] = None
    error_detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return {
            "audit_id": self.audit_id,
            "request_id": self.request_id,
            "capability_id": self.capability_id,
            "case_id": self.case_id,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "timestamp": self.timestamp,
            "args_hash": self.args_hash,
            "status": self.status,
            "result_summary": self.result_summary,
            "error_detail": self.error_detail,
        }


# ---------------------------------------------------------------------------
# Capability Registry
# ---------------------------------------------------------------------------

class CapabilityRegistry:
    """
    Singleton registry for all assistant capabilities.

    Usage:
        registry = CapabilityRegistry()
        registry.register(case_create_note_capability)
        result = registry.execute("case.create_note", args={...}, context={...})
    """

    def __init__(self):
        self._capabilities: Dict[str, CapabilityDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._audit_log: List[ActionAuditRecord] = []
        self._frozen = False

    def register(
        self,
        capability: CapabilityDefinition,
        handler: Callable,
    ) -> None:
        """
        Register a capability with its handler.

        Raises ValueError if capability_id is already registered or
        if the registry is frozen.
        """
        if self._frozen:
            raise RuntimeError("Registry is frozen — no new capabilities allowed")

        if capability.capability_id in self._capabilities:
            raise ValueError(
                f"Capability '{capability.capability_id}' is already registered"
            )

        self._capabilities[capability.capability_id] = capability
        self._handlers[capability.capability_id] = handler

        logger.info(
            "Registered capability: %s (role: %s, audit: %s)",
            capability.capability_id,
            capability.required_role,
            capability.audit_required,
        )

    def freeze(self) -> None:
        """
        Freeze the registry. No new capabilities can be added after this.
        Call after all capabilities are registered at startup.
        """
        self._frozen = True
        logger.info(
            "Capability registry frozen with %d capabilities.",
            len(self._capabilities),
        )

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """Return a list of all registered capabilities (metadata only)."""
        result = []
        for cap in self._capabilities.values():
            result.append({
                "capability_id": cap.capability_id,
                "description": cap.description,
                "required_role": cap.required_role,
                "audit_required": cap.audit_required,
                "params": [
                    {
                        "name": p.name,
                        "type": p.param_type.value,
                        "required": p.required,
                        "description": p.description,
                    }
                    for p in cap.params
                ],
            })
        return result

    def execute(
        self,
        capability_id: str,
        args: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a capability action.

        Args:
            capability_id: Registered capability identifier.
            args: User-provided arguments.
            context: Execution context containing:
                - request_id: Unique request identifier.
                - case_id: Associated case (optional).
                - actor_id: Authenticated user's ID.
                - actor_name: Authenticated user's display name.
                - actor_role: User's role string.

        Returns:
            Dict with keys: status, result, audit_reference
        """
        request_id = context.get("request_id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        args_hash = hashlib.sha256(
            json.dumps(args, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

        # 1. Capability exists?
        capability = self._capabilities.get(capability_id)
        if capability is None:
            audit = self._record_audit(
                request_id=request_id,
                capability_id=capability_id,
                context=context,
                args_hash=args_hash,
                timestamp=now,
                status="denied",
                error_detail=f"Unknown capability: {capability_id}",
            )
            return {
                "status": "error",
                "error": f"Unknown capability: {capability_id}",
                "audit_reference": audit.audit_id,
            }

        # 2. Role enforcement
        actor_role = context.get("actor_role", "")
        if not self._check_role(actor_role, capability.required_role):
            audit = self._record_audit(
                request_id=request_id,
                capability_id=capability_id,
                context=context,
                args_hash=args_hash,
                timestamp=now,
                status="denied",
                error_detail=(
                    f"Role '{actor_role}' insufficient; "
                    f"requires '{capability.required_role}'"
                ),
            )
            return {
                "status": "denied",
                "error": "Insufficient permissions",
                "required_role": capability.required_role,
                "audit_reference": audit.audit_id,
            }

        # 3. Input validation
        validation_errors = validate_args(capability.params, args)
        if validation_errors:
            audit = self._record_audit(
                request_id=request_id,
                capability_id=capability_id,
                context=context,
                args_hash=args_hash,
                timestamp=now,
                status="validation_error",
                error_detail="; ".join(validation_errors),
            )
            return {
                "status": "validation_error",
                "errors": validation_errors,
                "audit_reference": audit.audit_id,
            }

        # 4. Execute handler
        handler = self._handlers[capability_id]
        try:
            result = handler(args=args, context=context)
            audit = self._record_audit(
                request_id=request_id,
                capability_id=capability_id,
                context=context,
                args_hash=args_hash,
                timestamp=now,
                status="success",
                result_summary=_truncate(str(result), 500),
            )
            return {
                "status": "success",
                "result": result,
                "audit_reference": audit.audit_id,
            }
        except Exception as exc:
            logger.error(
                "Handler error for %s: %s",
                capability_id,
                exc,
                exc_info=True,
            )
            audit = self._record_audit(
                request_id=request_id,
                capability_id=capability_id,
                context=context,
                args_hash=args_hash,
                timestamp=now,
                status="handler_error",
                error_detail=str(exc),
            )
            return {
                "status": "error",
                "error": "Action failed. See audit log for details.",
                "audit_reference": audit.audit_id,
            }

    # ------------------------------------------------------------------
    # Audit log access
    # ------------------------------------------------------------------

    def get_audit_log(
        self,
        capability_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return recent audit records, optionally filtered by capability."""
        records = self._audit_log
        if capability_id:
            records = [r for r in records if r.capability_id == capability_id]
        return [r.to_dict() for r in records[-limit:]]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    _ROLE_RANK = {
        "USER": 0,
        "PRO_USER": 1,
        "MODERATOR": 2,
        "ADMIN": 3,
    }

    def _check_role(self, actor_role: str, required_role: str) -> bool:
        """Check if actor_role meets or exceeds required_role."""
        actor_rank = self._ROLE_RANK.get(actor_role.upper(), -1)
        required_rank = self._ROLE_RANK.get(required_role.upper(), 999)
        return actor_rank >= required_rank

    def _record_audit(
        self,
        request_id: str,
        capability_id: str,
        context: Dict[str, Any],
        args_hash: str,
        timestamp: str,
        status: str,
        result_summary: Optional[str] = None,
        error_detail: Optional[str] = None,
    ) -> ActionAuditRecord:
        """Create and store an audit record. Returns the record."""
        record = ActionAuditRecord(
            audit_id=str(uuid.uuid4()),
            request_id=request_id,
            capability_id=capability_id,
            case_id=context.get("case_id"),
            actor_id=context.get("actor_id"),
            actor_name=context.get("actor_name"),
            timestamp=timestamp,
            args_hash=args_hash,
            status=status,
            result_summary=result_summary,
            error_detail=error_detail,
        )
        self._audit_log.append(record)

        logger.info(
            "Audit [%s] cap=%s actor=%s status=%s",
            record.audit_id[:8],
            capability_id,
            context.get("actor_name", "unknown"),
            status,
        )

        return record


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

registry = CapabilityRegistry()


# ---------------------------------------------------------------------------
# Built-in capability definitions
# ---------------------------------------------------------------------------

BUILTIN_CAPABILITIES = {
    "case.create_note": CapabilityDefinition(
        capability_id="case.create_note",
        description="Add a note to a case file",
        required_role="PRO_USER",
        audit_required=True,
        params=(
            ParamSchema(name="case_id", param_type=ParamType.STRING, required=True,
                        description="Target case identifier"),
            ParamSchema(name="content", param_type=ParamType.STRING, required=True,
                        description="Note content", max_length=10000),
        ),
    ),
    "evidence.upload": CapabilityDefinition(
        capability_id="evidence.upload",
        description="Upload new evidence to a case",
        required_role="PRO_USER",
        audit_required=True,
        params=(
            ParamSchema(name="case_id", param_type=ParamType.STRING, required=True,
                        description="Target case identifier"),
            ParamSchema(name="file_path", param_type=ParamType.FILE, required=True,
                        description="Path or ID of file to ingest"),
            ParamSchema(name="description", param_type=ParamType.STRING, required=False,
                        description="Evidence description", max_length=2000),
        ),
    ),
    "job.start_transcode": CapabilityDefinition(
        capability_id="job.start_transcode",
        description="Start a media transcode job for evidence",
        required_role="PRO_USER",
        audit_required=True,
        params=(
            ParamSchema(name="evidence_id", param_type=ParamType.STRING, required=True,
                        description="Evidence item to transcode"),
            ParamSchema(name="output_format", param_type=ParamType.STRING, required=True,
                        description="Target format",
                        allowed_values=("mp4", "webm", "mp3", "wav", "pdf")),
        ),
    ),
    "export.create": CapabilityDefinition(
        capability_id="export.create",
        description="Create an export package for a case",
        required_role="PRO_USER",
        audit_required=True,
        params=(
            ParamSchema(name="case_id", param_type=ParamType.STRING, required=True,
                        description="Case to export"),
            ParamSchema(name="format", param_type=ParamType.STRING, required=True,
                        description="Export format",
                        allowed_values=("zip", "tar", "court_package")),
            ParamSchema(name="include_derivatives", param_type=ParamType.BOOLEAN,
                        required=False, description="Include derivative files"),
        ),
    ),
    "export.verify": CapabilityDefinition(
        capability_id="export.verify",
        description="Verify integrity of an export package",
        required_role="USER",
        audit_required=True,
        params=(
            ParamSchema(name="export_id", param_type=ParamType.STRING, required=True,
                        description="Export package to verify"),
        ),
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _truncate(s: str, max_len: int) -> str:
    """Truncate string to max_len, appending '...' if truncated."""
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."
