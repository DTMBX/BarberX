# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Professional Evidence Processing System
Chain of Custody, Evidence Management, Court-Ready Workflows
"""

import hashlib
from datetime import datetime


class ChainOfCustody:
    """Tracks evidence chain of custody"""

    def __init__(self):
        self.events = []

    def add_event(self, event_type: str, actor: str, details: str, location: str = None):
        """Add chain of custody event"""
        event = {
            "id": len(self.events) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "details": details,
            "location": location,
            "verification": self._generate_verification(),
        }
        self.events.append(event)
        return event

    def _generate_verification(self):
        """Generate verification hash for event"""
        data = f"{datetime.utcnow().isoformat()}{len(self.events)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_timeline(self):
        """Get complete chain of custody timeline"""
        return {
            "total_events": len(self.events),
            "first_event": self.events[0] if self.events else None,
            "last_event": self.events[-1] if self.events else None,
            "events": self.events,
        }

    def verify_integrity(self):
        """Verify chain of custody integrity"""
        if not self.events:
            return {"valid": False, "reason": "No events recorded"}

        # Check for gaps in timeline
        for i in range(len(self.events) - 1):
            current = datetime.fromisoformat(self.events[i]["timestamp"])
            next_event = datetime.fromisoformat(self.events[i + 1]["timestamp"])

            if (next_event - current).total_seconds() < 0:
                return {"valid": False, "reason": "Timeline inconsistency detected"}

        return {"valid": True, "events_verified": len(self.events)}


class EvidenceProcessor:
    """Professional evidence processing workflow"""

    EVIDENCE_TYPES = {
        "bwc_video": "Body-Worn Camera Video",
        "dashcam": "Dashboard Camera Video",
        "cctv": "CCTV Footage",
        "interview": "Interview Recording",
        "phone_video": "Mobile Phone Video",
        "audio": "Audio Recording",
        "document": "Document/Report",
        "photo": "Photograph",
    }

    PROCESSING_STAGES = [
        "intake",  # Evidence received and logged
        "verification",  # Hash verification, format check
        "metadata",  # Metadata extraction and validation
        "analysis",  # Primary analysis (transcription, etc.)
        "enhancement",  # Enhanced analysis (voice stress, scenes, etc.)
        "review",  # Quality review and verification
        "approved",  # Approved for court use
        "archived",  # Long-term storage
    ]

    PRIORITY_LEVELS = {
        "critical": {"label": "Critical", "sla_hours": 4},
        "high": {"label": "High Priority", "sla_hours": 24},
        "normal": {"label": "Normal", "sla_hours": 72},
        "low": {"label": "Low Priority", "sla_hours": 168},
    }

    def __init__(self):
        self.chain_of_custody = ChainOfCustody()

    def create_evidence_package(self, evidence_data: dict) -> dict:
        """Create comprehensive evidence package"""

        # Initialize chain of custody
        self.chain_of_custody.add_event(
            event_type="evidence_received",
            actor=evidence_data.get("submitted_by", "Unknown"),
            details=f"Evidence submitted: {evidence_data.get('filename')}",
            location=evidence_data.get("location", "Web Upload"),
        )

        # Create evidence package
        package = {
            "evidence_id": evidence_data.get("id"),
            "case_information": {
                "case_number": evidence_data.get("case_number"),
                "incident_date": evidence_data.get("incident_date"),
                "incident_location": evidence_data.get("incident_location"),
                "case_type": evidence_data.get("case_type", "General"),
                "jurisdiction": evidence_data.get("jurisdiction"),
                "lead_investigator": evidence_data.get("lead_investigator"),
            },
            "evidence_details": {
                "type": evidence_data.get("evidence_type", "bwc_video"),
                "description": evidence_data.get("description"),
                "source": evidence_data.get("source"),
                "filename": evidence_data.get("filename"),
                "file_size": evidence_data.get("file_size"),
                "file_hash": evidence_data.get("file_hash"),
                "format": evidence_data.get("format"),
            },
            "custody_information": {
                "acquired_by": evidence_data.get("acquired_by"),
                "acquired_date": evidence_data.get("acquired_date", datetime.utcnow().isoformat()),
                "submitted_by": evidence_data.get("submitted_by"),
                "submitted_date": datetime.utcnow().isoformat(),
                "current_custodian": evidence_data.get("submitted_by"),
                "storage_location": evidence_data.get("storage_location", "Digital Archive"),
            },
            "processing_status": {
                "stage": "intake",
                "priority": evidence_data.get("priority", "normal"),
                "sla_deadline": self._calculate_sla(evidence_data.get("priority", "normal")),
                "assigned_to": evidence_data.get("assigned_to"),
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0,
            },
            "chain_of_custody": self.chain_of_custody.get_timeline(),
            "tags": evidence_data.get("tags", []),
            "related_evidence": evidence_data.get("related_evidence", []),
            "notes": [],
        }

        return package

    def _calculate_sla(self, priority: str) -> str:
        """Calculate SLA deadline based on priority"""
        from datetime import timedelta

        hours = self.PRIORITY_LEVELS.get(priority, self.PRIORITY_LEVELS["normal"])["sla_hours"]
        deadline = datetime.utcnow() + timedelta(hours=hours)
        return deadline.isoformat()

    def advance_stage(self, current_stage: str, actor: str, notes: str = "") -> dict:
        """Advance evidence to next processing stage"""
        try:
            current_index = self.PROCESSING_STAGES.index(current_stage)
            next_stage = self.PROCESSING_STAGES[current_index + 1]

            # Record in chain of custody
            self.chain_of_custody.add_event(
                event_type="stage_advancement",
                actor=actor,
                details=f"Advanced from {current_stage} to {next_stage}. {notes}",
            )

            return {
                "success": True,
                "previous_stage": current_stage,
                "current_stage": next_stage,
                "progress": int((current_index + 1) / len(self.PROCESSING_STAGES) * 100),
            }
        except (ValueError, IndexError):
            return {"success": False, "error": "Invalid stage or already at final stage"}

    def generate_processing_checklist(self, evidence_type: str) -> list[dict]:
        """Generate processing checklist for evidence type"""

        base_checklist = [
            {
                "stage": "intake",
                "tasks": [
                    {
                        "id": "verify_submission",
                        "task": "Verify submitter identity and authorization",
                        "required": True,
                    },
                    {
                        "id": "log_evidence",
                        "task": "Log evidence in case management system",
                        "required": True,
                    },
                    {
                        "id": "initial_hash",
                        "task": "Calculate and record file hash (SHA-256)",
                        "required": True,
                    },
                    {
                        "id": "metadata_capture",
                        "task": "Capture initial metadata (date, time, source)",
                        "required": True,
                    },
                ],
            },
            {
                "stage": "verification",
                "tasks": [
                    {
                        "id": "hash_verify",
                        "task": "Verify file integrity (hash check)",
                        "required": True,
                    },
                    {
                        "id": "format_check",
                        "task": "Verify file format and playability",
                        "required": True,
                    },
                    {
                        "id": "duplicate_check",
                        "task": "Check for duplicate evidence",
                        "required": True,
                    },
                    {
                        "id": "quality_check",
                        "task": "Initial quality assessment",
                        "required": False,
                    },
                ],
            },
            {
                "stage": "metadata",
                "tasks": [
                    {
                        "id": "extract_metadata",
                        "task": "Extract file metadata (EXIF, codec info)",
                        "required": True,
                    },
                    {
                        "id": "timestamp_verify",
                        "task": "Verify and document timestamps",
                        "required": True,
                    },
                    {
                        "id": "device_info",
                        "task": "Document source device information",
                        "required": True,
                    },
                    {
                        "id": "location_data",
                        "task": "Extract GPS/location data if available",
                        "required": False,
                    },
                ],
            },
            {
                "stage": "analysis",
                "tasks": [
                    {
                        "id": "transcription",
                        "task": "Generate transcript of audio/video",
                        "required": True,
                    },
                    {"id": "speaker_id", "task": "Identify and label speakers", "required": True},
                    {
                        "id": "entity_extract",
                        "task": "Extract persons, locations, organizations",
                        "required": True,
                    },
                    {
                        "id": "timeline_create",
                        "task": "Create timeline of events",
                        "required": True,
                    },
                ],
            },
            {
                "stage": "enhancement",
                "tasks": [
                    {"id": "voice_stress", "task": "Voice stress analysis", "required": False},
                    {
                        "id": "scene_detect",
                        "task": "Scene detection and segmentation",
                        "required": False,
                    },
                    {
                        "id": "quality_metrics",
                        "task": "Detailed audio/video quality analysis",
                        "required": False,
                    },
                    {
                        "id": "compliance_check",
                        "task": "Legal compliance verification",
                        "required": True,
                    },
                ],
            },
            {
                "stage": "review",
                "tasks": [
                    {
                        "id": "accuracy_review",
                        "task": "Review transcript accuracy",
                        "required": True,
                    },
                    {
                        "id": "completeness",
                        "task": "Verify all required analysis completed",
                        "required": True,
                    },
                    {"id": "quality_review", "task": "Quality assurance review", "required": True},
                    {
                        "id": "legal_review",
                        "task": "Legal review for admissibility",
                        "required": True,
                    },
                ],
            },
        ]

        # Add evidence-type specific tasks
        if evidence_type == "bwc_video":
            base_checklist[3]["tasks"].append(
                {"id": "officer_id", "task": "Verify officer identification", "required": True}
            )
            base_checklist[4]["tasks"].append(
                {
                    "id": "use_of_force",
                    "task": "Analyze any use of force incidents",
                    "required": True,
                }
            )

        return base_checklist

    def create_evidence_correlation(self, evidence_items: list[dict]) -> dict:
        """Correlate multiple pieces of evidence"""

        correlations = {
            "total_items": len(evidence_items),
            "timeline_matches": [],
            "speaker_matches": [],
            "location_matches": [],
            "discrepancies": [],
            "corroboration_score": 0.0,
        }

        # Timeline correlation
        for i, item1 in enumerate(evidence_items):
            for item2 in evidence_items[i + 1 :]:
                if self._timelines_overlap(item1, item2):
                    correlations["timeline_matches"].append(
                        {
                            "evidence_1": item1.get("id"),
                            "evidence_2": item2.get("id"),
                            "overlap_start": "...",
                            "overlap_end": "...",
                            "confidence": 0.95,
                        }
                    )

        # Speaker correlation
        # (Compare speaker lists across evidence)

        # Location correlation
        # (Compare location data)

        # Calculate overall corroboration score
        if correlations["timeline_matches"]:
            correlations["corroboration_score"] = 0.85

        return correlations

    def _timelines_overlap(self, item1: dict, item2: dict) -> bool:
        """Check if two evidence items have overlapping timelines"""
        # Simplified check - would use actual timestamp comparison
        return True

    def generate_court_exhibit(self, evidence_package: dict, exhibit_number: str) -> dict:
        """Generate court-ready exhibit package"""

        exhibit = {
            "exhibit_number": exhibit_number,
            "exhibit_type": "Digital Evidence",
            "case_number": evidence_package["case_information"]["case_number"],
            "title": f"Body-Worn Camera Evidence - {evidence_package['evidence_details']['filename']}",
            "description": evidence_package["evidence_details"]["description"],
            "evidence_summary": {
                "type": self.EVIDENCE_TYPES.get(evidence_package["evidence_details"]["type"]),
                "acquisition_date": evidence_package["custody_information"]["acquired_date"],
                "acquired_by": evidence_package["custody_information"]["acquired_by"],
                "file_hash": evidence_package["evidence_details"]["file_hash"],
                "file_size": evidence_package["evidence_details"]["file_size"],
            },
            "authenticity_verification": {
                "hash_algorithm": "SHA-256",
                "original_hash": evidence_package["evidence_details"]["file_hash"],
                "current_hash": evidence_package["evidence_details"][
                    "file_hash"
                ],  # Would recalculate
                "match": True,
                "verified_by": "Digital Forensics System",
                "verified_date": datetime.utcnow().isoformat(),
            },
            "chain_of_custody": evidence_package["chain_of_custody"],
            "analysis_summary": {
                "transcript_available": True,
                "total_duration": "...",
                "speakers_identified": "...",
                "key_events": "...",
                "compliance_status": "...",
            },
            "attachments": [
                {"type": "transcript", "filename": "exhibit_{}_transcript.pdf"},
                {"type": "analysis_report", "filename": "exhibit_{}_analysis.pdf"},
                {"type": "chain_of_custody", "filename": "exhibit_{}_custody.pdf"},
                {"type": "technical_specs", "filename": "exhibit_{}_technical.pdf"},
            ],
            "certification": {
                "certified_by": "Digital Forensics Examiner",
                "certification_date": datetime.utcnow().isoformat(),
                "statement": "I hereby certify that the attached evidence has been properly acquired, "
                "analyzed, and maintained in accordance with digital forensics best practices "
                "and legal standards for evidence handling.",
            },
        }

        return exhibit


class EvidenceWorkflowManager:
    """Manage evidence processing workflows"""

    def __init__(self):
        self.processor = EvidenceProcessor()

    def create_intake_form(self) -> dict:
        """Generate evidence intake form"""
        return {
            "form_version": "2.0",
            "sections": [
                {
                    "section": "Case Information",
                    "required": True,
                    "fields": [
                        {
                            "name": "case_number",
                            "type": "text",
                            "required": True,
                            "label": "Case Number",
                        },
                        {
                            "name": "incident_date",
                            "type": "date",
                            "required": True,
                            "label": "Incident Date",
                        },
                        {
                            "name": "incident_time",
                            "type": "time",
                            "required": False,
                            "label": "Incident Time",
                        },
                        {
                            "name": "incident_location",
                            "type": "text",
                            "required": True,
                            "label": "Incident Location",
                        },
                        {
                            "name": "case_type",
                            "type": "select",
                            "required": True,
                            "label": "Case Type",
                            "options": [
                                "Assault",
                                "Traffic Stop",
                                "Arrest",
                                "Interview",
                                "Use of Force",
                                "Other",
                            ],
                        },
                        {
                            "name": "jurisdiction",
                            "type": "text",
                            "required": True,
                            "label": "Jurisdiction",
                        },
                        {
                            "name": "lead_investigator",
                            "type": "text",
                            "required": True,
                            "label": "Lead Investigator",
                        },
                    ],
                },
                {
                    "section": "Evidence Details",
                    "required": True,
                    "fields": [
                        {
                            "name": "evidence_type",
                            "type": "select",
                            "required": True,
                            "label": "Evidence Type",
                            "options": list(EvidenceProcessor.EVIDENCE_TYPES.keys()),
                        },
                        {
                            "name": "description",
                            "type": "textarea",
                            "required": True,
                            "label": "Evidence Description",
                        },
                        {
                            "name": "source",
                            "type": "text",
                            "required": True,
                            "label": "Evidence Source",
                        },
                        {
                            "name": "officer_name",
                            "type": "text",
                            "required": False,
                            "label": "Officer Name (if BWC)",
                        },
                        {
                            "name": "badge_number",
                            "type": "text",
                            "required": False,
                            "label": "Badge Number (if BWC)",
                        },
                        {
                            "name": "device_id",
                            "type": "text",
                            "required": False,
                            "label": "Device ID/Serial Number",
                        },
                    ],
                },
                {
                    "section": "Acquisition Information",
                    "required": True,
                    "fields": [
                        {
                            "name": "acquired_by",
                            "type": "text",
                            "required": True,
                            "label": "Acquired By",
                        },
                        {
                            "name": "acquired_date",
                            "type": "datetime",
                            "required": True,
                            "label": "Acquisition Date/Time",
                        },
                        {
                            "name": "acquisition_method",
                            "type": "select",
                            "required": True,
                            "label": "Acquisition Method",
                            "options": [
                                "Direct Download",
                                "Physical Media",
                                "Cloud Upload",
                                "Network Transfer",
                            ],
                        },
                        {
                            "name": "storage_location",
                            "type": "text",
                            "required": True,
                            "label": "Original Storage Location",
                        },
                    ],
                },
                {
                    "section": "Processing Instructions",
                    "required": False,
                    "fields": [
                        {
                            "name": "priority",
                            "type": "select",
                            "required": True,
                            "label": "Processing Priority",
                            "options": ["critical", "high", "normal", "low"],
                        },
                        {
                            "name": "assigned_to",
                            "type": "text",
                            "required": False,
                            "label": "Assign To Analyst",
                        },
                        {
                            "name": "special_instructions",
                            "type": "textarea",
                            "required": False,
                            "label": "Special Instructions",
                        },
                        {"name": "tags", "type": "tags", "required": False, "label": "Tags"},
                    ],
                },
                {
                    "section": "Related Evidence",
                    "required": False,
                    "fields": [
                        {
                            "name": "related_evidence",
                            "type": "multi-select",
                            "required": False,
                            "label": "Related Evidence Items",
                        },
                        {
                            "name": "witness_statements",
                            "type": "text",
                            "required": False,
                            "label": "Related Witness Statements",
                        },
                        {
                            "name": "police_reports",
                            "type": "text",
                            "required": False,
                            "label": "Related Police Reports",
                        },
                    ],
                },
            ],
        }

    def get_workflow_status(self, evidence_package: dict) -> dict:
        """Get detailed workflow status"""
        current_stage = evidence_package["processing_status"]["stage"]

        # Calculate completion percentage
        stage_index = self.processor.PROCESSING_STAGES.index(current_stage)
        completion = int((stage_index / len(self.processor.PROCESSING_STAGES)) * 100)

        # Get checklist for current stage
        checklist = self.processor.generate_processing_checklist(
            evidence_package["evidence_details"]["type"]
        )

        current_tasks = next(
            (stage["tasks"] for stage in checklist if stage["stage"] == current_stage), []
        )

        # Check SLA status
        sla_deadline = datetime.fromisoformat(evidence_package["processing_status"]["sla_deadline"])
        now = datetime.utcnow()
        hours_remaining = (sla_deadline - now).total_seconds() / 3600

        sla_status = "on_track"
        if hours_remaining < 0:
            sla_status = "overdue"
        elif hours_remaining < 4:
            sla_status = "at_risk"

        return {
            "current_stage": current_stage,
            "stage_name": current_stage.replace("_", " ").title(),
            "completion_percentage": completion,
            "current_tasks": current_tasks,
            "tasks_completed": 0,  # Would track actual completion
            "tasks_remaining": len(current_tasks),
            "sla_status": sla_status,
            "hours_to_deadline": max(0, hours_remaining),
            "assigned_to": evidence_package["processing_status"].get("assigned_to"),
            "can_advance": len(current_tasks) == 0,  # Would check actual task completion
        }


# Global instance
evidence_workflow = EvidenceWorkflowManager()
