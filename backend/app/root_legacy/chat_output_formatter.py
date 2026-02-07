# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Chat-Friendly Output Formatter
Standardizes all tool outputs for easy use in chat assistants

Provides:
- Consistent structured output format
- Markdown-ready summaries
- Key findings highlights
- Action items extraction
- Easy-to-reference citations
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OutputType(Enum):
    """Types of outputs from various tools"""

    TRANSCRIPTION = "transcription"
    BWC_ANALYSIS = "bwc_analysis"
    EVIDENCE_PROCESSING = "evidence_processing"
    CITATION_ANALYSIS = "citation_analysis"
    VIOLATION_SCAN = "violation_scan"
    COMPLIANCE_CHECK = "compliance_check"
    USAGE_REPORT = "usage_report"
    LEGAL_RESEARCH = "legal_research"
    CASE_ANALYSIS = "case_analysis"
    DOCUMENT_ANALYSIS = "document_analysis"
    GENERAL = "general"


class Severity(Enum):
    """Severity levels for findings"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """A single finding or insight"""

    title: str
    description: str
    severity: Severity = Severity.INFO
    category: str = ""
    evidence: str = ""
    citation: str = ""
    action_required: bool = False
    suggested_action: str = ""

    def to_markdown(self) -> str:
        """Format as markdown"""
        icons = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢",
            Severity.INFO: "ℹ️",
        }
        icon = icons.get(self.severity, "•")

        md = f"{icon} **{self.title}**"
        if self.category:
            md += f" ({self.category})"
        md += f"\n   {self.description}"

        if self.evidence:
            md += f"\n   > Evidence: {self.evidence}"
        if self.citation:
            md += f"\n   📖 *{self.citation}*"
        if self.action_required and self.suggested_action:
            md += f"\n   ➡️ **Action:** {self.suggested_action}"

        return md

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category,
            "evidence": self.evidence,
            "citation": self.citation,
            "action_required": self.action_required,
            "suggested_action": self.suggested_action,
        }


@dataclass
class ChatOutput:
    """
    Standardized output format for chat assistant integration

    All tool outputs should be converted to this format for
    consistent display and easy reference in conversations.
    """

    # Metadata
    output_type: OutputType
    title: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: int = 0

    # Summary (for quick overview)
    summary: str = ""
    key_points: list[str] = field(default_factory=list)

    # Detailed findings
    findings: list[Finding] = field(default_factory=list)

    # Statistics/metrics
    stats: dict[str, Any] = field(default_factory=dict)

    # Action items
    action_items: list[str] = field(default_factory=list)

    # Citations/references
    citations: list[str] = field(default_factory=list)

    # Raw data (for programmatic access)
    raw_data: dict[str, Any] = field(default_factory=dict)

    # Status
    success: bool = True
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_chat_message(self, verbose: bool = False) -> str:
        """
        Format for display in chat assistant

        Args:
            verbose: Include all details if True, summary only if False
        """
        lines = []

        # Header
        type_icons = {
            OutputType.TRANSCRIPTION: "🎙️",
            OutputType.BWC_ANALYSIS: "📹",
            OutputType.EVIDENCE_PROCESSING: "🔍",
            OutputType.CITATION_ANALYSIS: "📚",
            OutputType.VIOLATION_SCAN: "⚖️",
            OutputType.COMPLIANCE_CHECK: "✅",
            OutputType.USAGE_REPORT: "📊",
            OutputType.LEGAL_RESEARCH: "📖",
            OutputType.CASE_ANALYSIS: "📋",
            OutputType.DOCUMENT_ANALYSIS: "📄",
            OutputType.GENERAL: "📝",
        }
        icon = type_icons.get(self.output_type, "📝")
        lines.append(f"## {icon} {self.title}")
        lines.append("")

        # Status
        if not self.success:
            lines.append(f"❌ **Error:** {self.error}")
            lines.append("")
            return "\n".join(lines)

        # Summary
        if self.summary:
            lines.append(f"**Summary:** {self.summary}")
            lines.append("")

        # Key Points
        if self.key_points:
            lines.append("### Key Points")
            for point in self.key_points[:5]:  # Limit to top 5
                lines.append(f"• {point}")
            lines.append("")

        # Stats (compact)
        if self.stats:
            stats_str = " | ".join([f"**{k}:** {v}" for k, v in list(self.stats.items())[:4]])
            lines.append(f"📊 {stats_str}")
            lines.append("")

        # Critical findings (always show)
        critical_findings = [f for f in self.findings if f.severity == Severity.CRITICAL]
        if critical_findings:
            lines.append("### 🚨 Critical Findings")
            for finding in critical_findings:
                lines.append(finding.to_markdown())
            lines.append("")

        # Other findings (if verbose)
        if verbose:
            other_findings = [f for f in self.findings if f.severity != Severity.CRITICAL]
            if other_findings:
                lines.append("### Findings")
                for finding in other_findings:
                    lines.append(finding.to_markdown())
                lines.append("")
        else:
            # Just show count
            other_count = len([f for f in self.findings if f.severity != Severity.CRITICAL])
            if other_count > 0:
                lines.append(f"*+ {other_count} additional findings (ask for details)*")
                lines.append("")

        # Action items
        if self.action_items:
            lines.append("### ➡️ Recommended Actions")
            for i, action in enumerate(self.action_items[:5], 1):
                lines.append(f"{i}. {action}")
            lines.append("")

        # Citations (if verbose)
        if verbose and self.citations:
            lines.append("### 📖 Citations")
            for citation in self.citations[:10]:
                lines.append(f"• {citation}")
            lines.append("")

        # Warnings
        if self.warnings:
            for warning in self.warnings:
                lines.append(f"⚠️ {warning}")
            lines.append("")

        # Footer
        if self.processing_time_ms > 0:
            lines.append(f"*Processed in {self.processing_time_ms}ms*")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "output_type": self.output_type.value,
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "summary": self.summary,
            "key_points": self.key_points,
            "findings": [f.to_dict() for f in self.findings],
            "stats": self.stats,
            "action_items": self.action_items,
            "citations": self.citations,
            "success": self.success,
            "error": self.error,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict) -> "ChatOutput":
        """Create from dictionary"""
        findings = [
            Finding(
                title=f["title"],
                description=f["description"],
                severity=Severity(f.get("severity", "info")),
                category=f.get("category", ""),
                evidence=f.get("evidence", ""),
                citation=f.get("citation", ""),
                action_required=f.get("action_required", False),
                suggested_action=f.get("suggested_action", ""),
            )
            for f in data.get("findings", [])
        ]

        return cls(
            output_type=OutputType(data.get("output_type", "general")),
            title=data.get("title", "Analysis Results"),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if "timestamp" in data
                else datetime.utcnow()
            ),
            processing_time_ms=data.get("processing_time_ms", 0),
            summary=data.get("summary", ""),
            key_points=data.get("key_points", []),
            findings=findings,
            stats=data.get("stats", {}),
            action_items=data.get("action_items", []),
            citations=data.get("citations", []),
            success=data.get("success", True),
            error=data.get("error", ""),
            warnings=data.get("warnings", []),
        )


# =============================================================================
# CONVERTER FUNCTIONS - Transform tool outputs to ChatOutput
# =============================================================================


class OutputFormatter:
    """
    Central formatter for converting various tool outputs to chat-friendly format
    """

    @staticmethod
    def format_transcription(result: dict) -> ChatOutput:
        """Format transcription results for chat"""
        segments = result.get("segments", [])
        text = result.get("text", "")
        language = result.get("language", "unknown")
        duration = result.get("duration", 0)

        # Extract key quotes/statements
        key_points = []
        if text:
            sentences = text.split(". ")[:5]
            key_points = [s.strip() + "." for s in sentences if len(s) > 20]

        return ChatOutput(
            output_type=OutputType.TRANSCRIPTION,
            title="Audio Transcription Complete",
            summary=f"Transcribed {duration:.1f} seconds of audio ({language})",
            key_points=key_points,
            stats={
                "Duration": f"{duration:.1f}s",
                "Language": language,
                "Segments": len(segments),
                "Words": len(text.split()) if text else 0,
            },
            raw_data={"text": text, "segments": segments},
            success=True,
        )

    @staticmethod
    def format_bwc_analysis(result: dict) -> ChatOutput:
        """Format BWC forensic analysis for chat"""
        findings = []
        action_items = []
        citations = []

        # Extract discrepancies
        discrepancies = result.get("discrepancies", [])
        for disc in discrepancies:
            severity = Severity.HIGH if disc.get("severity") == "high" else Severity.MEDIUM
            findings.append(
                Finding(
                    title=disc.get("title", "Discrepancy Found"),
                    description=disc.get("description", ""),
                    severity=severity,
                    category="Timeline Discrepancy",
                    evidence=disc.get("evidence", ""),
                    action_required=True,
                    suggested_action=disc.get("recommendation", "Review and document"),
                )
            )

        # Extract violations
        violations = result.get("violations", [])
        for v in violations:
            findings.append(
                Finding(
                    title=v.get("type", "Potential Violation"),
                    description=v.get("description", ""),
                    severity=Severity.CRITICAL if v.get("critical") else Severity.HIGH,
                    category="Constitutional Violation",
                    citation=v.get("legal_basis", ""),
                    action_required=True,
                    suggested_action=v.get("motion_to_file", "File appropriate motion"),
                )
            )
            if v.get("case_law"):
                citations.extend(v.get("case_law", []))

        # Extract recommended actions
        if result.get("recommended_motions"):
            action_items = [f"File {m}" for m in result["recommended_motions"]]

        key_points = []
        if discrepancies:
            key_points.append(f"Found {len(discrepancies)} timeline discrepancies")
        if violations:
            key_points.append(f"Identified {len(violations)} potential violations")
        if result.get("officer_statements_inconsistent"):
            key_points.append("Officer statements contain inconsistencies")

        return ChatOutput(
            output_type=OutputType.BWC_ANALYSIS,
            title="BWC Forensic Analysis Results",
            summary=result.get("summary", f"Analyzed footage with {len(findings)} findings"),
            key_points=key_points,
            findings=findings,
            stats={
                "Discrepancies": len(discrepancies),
                "Violations": len(violations),
                "Duration": result.get("video_duration", "N/A"),
                "Speakers": result.get("speaker_count", "N/A"),
            },
            action_items=action_items,
            citations=list(set(citations)),
            raw_data=result,
            success=True,
        )

    @staticmethod
    def format_evidence_processing(result: dict) -> ChatOutput:
        """Format evidence processing results for chat"""
        findings = []
        action_items = []
        citations = []

        # Violation findings
        violations = result.get("violations", {})
        if violations:
            total = violations.get("total_violations", 0)
            for v in violations.get("critical_violations", []):
                findings.append(
                    Finding(
                        title=v.get("title", "Violation"),
                        description=v.get("description", ""),
                        severity=Severity.CRITICAL,
                        category=v.get("type", ""),
                        citation=v.get("legal_basis", ""),
                        action_required=True,
                        suggested_action=v.get("recommended_action", ""),
                    )
                )

        # Compliance findings
        compliance = result.get("compliance", {})
        if compliance:
            status = compliance.get("overall_status", "UNKNOWN")
            if status == "NON_COMPLIANT":
                for issue in compliance.get("issues", []):
                    findings.append(
                        Finding(
                            title=issue.get("title", "Compliance Issue"),
                            description=issue.get("description", ""),
                            severity=Severity.HIGH,
                            category="Compliance",
                        )
                    )

        # Motions to file
        motions = result.get("motions_to_file", [])
        for motion in motions:
            if isinstance(motion, dict):
                action_items.append(f"{motion.get('motion_type')}: {motion.get('basis')}")
            else:
                action_items.append(str(motion))

        # Citations
        citations = result.get("case_law_citations", [])

        key_points = [result.get("summary", "")] if result.get("summary") else []

        return ChatOutput(
            output_type=OutputType.EVIDENCE_PROCESSING,
            title=f"Evidence Analysis: {result.get('evidence_id', 'Unknown')}",
            summary=result.get("summary", "Evidence processing complete"),
            key_points=key_points,
            findings=findings,
            stats={
                "Evidence ID": result.get("evidence_id", "N/A"),
                "Type": result.get("evidence_type", "N/A"),
                "Status": result.get("status", "N/A"),
                "Violations": violations.get("total_violations", 0) if violations else 0,
            },
            action_items=action_items,
            citations=citations,
            raw_data=result,
            success=result.get("status") != "failed",
            error=result.get("error", ""),
        )

    @staticmethod
    def format_citation_analysis(result: dict) -> ChatOutput:
        """Format citation network analysis for chat"""
        findings = []

        # Treatment analysis
        treatment = result.get("treatment", {})
        if treatment.get("signal") == "red_flag":
            findings.append(
                Finding(
                    title="⚠️ Case Has Been Overruled/Reversed",
                    description=treatment.get("reason", "This case may no longer be good law"),
                    severity=Severity.CRITICAL,
                    category="Citation Treatment",
                    action_required=True,
                    suggested_action="Verify current status and find alternative authority",
                )
            )
        elif treatment.get("signal") == "yellow_flag":
            findings.append(
                Finding(
                    title="Case Has Been Questioned",
                    description=treatment.get(
                        "reason", "This case has received negative treatment"
                    ),
                    severity=Severity.HIGH,
                    category="Citation Treatment",
                )
            )

        # Citing cases
        citing_cases = result.get("citing_cases", [])
        cited_by_count = len(citing_cases)

        key_points = []
        if cited_by_count > 0:
            key_points.append(f"Cited by {cited_by_count} subsequent cases")
        if result.get("authority_score"):
            key_points.append(f"Authority score: {result['authority_score']}/100")

        return ChatOutput(
            output_type=OutputType.CITATION_ANALYSIS,
            title=f"Citation Analysis: {result.get('case_name', 'Unknown Case')}",
            summary=f"{'Good law ✓' if treatment.get('signal') == 'green_plus' else 'Review treatment carefully'}",
            key_points=key_points,
            findings=findings,
            stats={
                "Cited By": cited_by_count,
                "Treatment": treatment.get("signal", "unknown"),
                "Authority": result.get("authority_score", "N/A"),
            },
            citations=[c.get("citation") for c in citing_cases[:5] if c.get("citation")],
            raw_data=result,
            success=True,
        )

    @staticmethod
    def format_violation_scan(result: dict) -> ChatOutput:
        """Format violation scan results for chat"""
        findings = []
        action_items = []
        citations = []

        violations = result.get("violations", [])
        for v in violations:
            sev = Severity.CRITICAL if v.get("severity") == "critical" else Severity.HIGH
            findings.append(
                Finding(
                    title=v.get("violation_type", "Violation"),
                    description=v.get("description", ""),
                    severity=sev,
                    category=v.get("amendment", "Constitutional"),
                    evidence=v.get("quote", ""),
                    citation=v.get("case_law", ""),
                    action_required=True,
                    suggested_action=v.get("motion", ""),
                )
            )
            if v.get("case_law"):
                citations.append(v["case_law"])
            if v.get("motion"):
                action_items.append(f"File {v['motion']}")

        key_points = []
        by_type = {}
        for v in violations:
            vtype = v.get("violation_type", "Unknown")
            by_type[vtype] = by_type.get(vtype, 0) + 1
        for vtype, count in by_type.items():
            key_points.append(f"{count} potential {vtype} violation(s)")

        return ChatOutput(
            output_type=OutputType.VIOLATION_SCAN,
            title="Constitutional Violation Scan",
            summary=(
                f"Found {len(violations)} potential violation(s)"
                if violations
                else "No violations detected"
            ),
            key_points=key_points,
            findings=findings,
            stats={
                "Total Violations": len(violations),
                "Critical": len([v for v in violations if v.get("severity") == "critical"]),
                "Motions Recommended": len(action_items),
            },
            action_items=list(set(action_items)),
            citations=list(set(citations)),
            raw_data=result,
            success=True,
        )

    @staticmethod
    def format_usage_report(result: dict) -> ChatOutput:
        """Format API usage report for chat"""
        summary_data = result.get("summary", {})
        quota = result.get("quota", {})

        key_points = []
        if summary_data.get("total_tokens"):
            key_points.append(f"Used {summary_data['total_tokens']:,} tokens")
        if summary_data.get("total_cost_usd"):
            key_points.append(f"Total cost: ${summary_data['total_cost_usd']:.4f}")
        if quota.get("tokens_used"):
            pct = (quota["tokens_used"] / quota.get("monthly_token_limit", 1)) * 100
            key_points.append(f"Quota usage: {pct:.1f}%")

        # Warnings for high usage
        warnings = []
        if quota.get("tokens_used", 0) > quota.get("monthly_token_limit", 100000) * 0.8:
            warnings.append("You've used over 80% of your monthly quota")

        return ChatOutput(
            output_type=OutputType.USAGE_REPORT,
            title="API Usage Report",
            summary=f"Period: Last {result.get('period_days', 30)} days",
            key_points=key_points,
            stats={
                "Tokens": f"{summary_data.get('total_tokens', 0):,}",
                "Cost": f"${summary_data.get('total_cost_usd', 0):.4f}",
                "Requests": summary_data.get("total_requests", 0),
                "Quota Left": (
                    f"{quota.get('tokens_remaining', 'N/A'):,}"
                    if isinstance(quota.get("tokens_remaining"), int)
                    else "N/A"
                ),
            },
            warnings=warnings,
            raw_data=result,
            success=True,
        )

    @staticmethod
    def format_compliance_check(result: dict) -> ChatOutput:
        """Format compliance check results for chat"""
        findings = []
        action_items = []

        status = result.get("overall_status", "UNKNOWN")
        issues = result.get("issues", [])

        for issue in issues:
            findings.append(
                Finding(
                    title=issue.get("title", "Compliance Issue"),
                    description=issue.get("description", ""),
                    severity=Severity.HIGH if issue.get("critical") else Severity.MEDIUM,
                    category=issue.get("category", "Compliance"),
                    action_required=True,
                    suggested_action=issue.get("remedy", ""),
                )
            )
            if issue.get("remedy"):
                action_items.append(issue["remedy"])

        recommendations = result.get("recommendations", [])
        action_items.extend(recommendations)

        return ChatOutput(
            output_type=OutputType.COMPLIANCE_CHECK,
            title="Statutory Compliance Check",
            summary=f"Status: {status}",
            key_points=[f"Overall compliance: {status}"] + [f.title for f in findings[:3]],
            findings=findings,
            stats={
                "Status": status,
                "Issues": len(issues),
                "Recommendations": len(recommendations),
            },
            action_items=action_items[:5],
            raw_data=result,
            success=True,
        )

    @staticmethod
    def format_generic(result: dict, title: str = "Analysis Results") -> ChatOutput:
        """Format generic results for chat"""
        return ChatOutput(
            output_type=OutputType.GENERAL,
            title=title,
            summary=result.get("summary", result.get("message", "Analysis complete")),
            key_points=result.get("key_points", []),
            stats=result.get("stats", {}),
            raw_data=result,
            success=result.get("success", True),
            error=result.get("error", ""),
        )


# =============================================================================
# QUICK HELPER FUNCTIONS
# =============================================================================


def format_for_chat(result: dict, output_type: str = "general", **kwargs) -> str:
    """
    Quick helper to format any result for chat display

    Args:
        result: Raw result dictionary
        output_type: Type of output (transcription, bwc_analysis, etc.)
        **kwargs: Additional options (verbose=True for full details)

    Returns:
        Formatted markdown string for chat display
    """
    formatter = OutputFormatter()

    type_map = {
        "transcription": formatter.format_transcription,
        "bwc_analysis": formatter.format_bwc_analysis,
        "bwc": formatter.format_bwc_analysis,
        "evidence": formatter.format_evidence_processing,
        "evidence_processing": formatter.format_evidence_processing,
        "citation": formatter.format_citation_analysis,
        "citation_analysis": formatter.format_citation_analysis,
        "violation": formatter.format_violation_scan,
        "violation_scan": formatter.format_violation_scan,
        "compliance": formatter.format_compliance_check,
        "compliance_check": formatter.format_compliance_check,
        "usage": formatter.format_usage_report,
        "usage_report": formatter.format_usage_report,
    }

    format_func = type_map.get(output_type.lower(), formatter.format_generic)

    if format_func == formatter.format_generic:
        chat_output = format_func(result, kwargs.get("title", "Analysis Results"))
    else:
        chat_output = format_func(result)

    return chat_output.to_chat_message(verbose=kwargs.get("verbose", False))


def quick_summary(result: dict, output_type: str = "general") -> str:
    """Get a one-line summary of results"""
    formatter = OutputFormatter()

    type_map = {
        "transcription": formatter.format_transcription,
        "bwc_analysis": formatter.format_bwc_analysis,
        "evidence": formatter.format_evidence_processing,
        "citation": formatter.format_citation_analysis,
        "violation": formatter.format_violation_scan,
        "compliance": formatter.format_compliance_check,
        "usage": formatter.format_usage_report,
    }

    format_func = type_map.get(output_type.lower(), formatter.format_generic)

    if format_func == formatter.format_generic:
        chat_output = format_func(result)
    else:
        chat_output = format_func(result)

    return chat_output.summary


def extract_action_items(result: dict, output_type: str = "general") -> list[str]:
    """Extract action items from results"""
    formatter = OutputFormatter()

    type_map = {
        "bwc_analysis": formatter.format_bwc_analysis,
        "evidence": formatter.format_evidence_processing,
        "violation": formatter.format_violation_scan,
        "compliance": formatter.format_compliance_check,
    }

    format_func = type_map.get(output_type.lower(), formatter.format_generic)

    if format_func == formatter.format_generic:
        chat_output = format_func(result)
    else:
        chat_output = format_func(result)

    return chat_output.action_items


def get_critical_findings(result: dict, output_type: str = "general") -> list[dict]:
    """Extract only critical findings from results"""
    formatter = OutputFormatter()

    type_map = {
        "bwc_analysis": formatter.format_bwc_analysis,
        "evidence": formatter.format_evidence_processing,
        "violation": formatter.format_violation_scan,
    }

    format_func = type_map.get(output_type.lower(), formatter.format_generic)

    if format_func == formatter.format_generic:
        chat_output = format_func(result)
    else:
        chat_output = format_func(result)

    return [f.to_dict() for f in chat_output.findings if f.severity == Severity.CRITICAL]


# =============================================================================
# EXAMPLE USAGE
# =============================================================================


if __name__ == "__main__":
    # Example: Format a transcription result
    transcription_result = {
        "text": "Officer: Do you know why I stopped you? Civilian: No sir. Officer: You were speeding. I clocked you at 75 in a 55 zone.",
        "language": "en",
        "duration": 12.5,
        "segments": [
            {"start": 0, "end": 3.2, "text": "Officer: Do you know why I stopped you?"},
            {"start": 3.5, "end": 5.1, "text": "Civilian: No sir."},
        ],
    }

    print("=" * 60)
    print("TRANSCRIPTION OUTPUT")
    print("=" * 60)
    print(format_for_chat(transcription_result, "transcription"))

    # Example: Format violation scan results
    violation_result = {
        "violations": [
            {
                "violation_type": "Miranda Violation",
                "severity": "critical",
                "description": "Suspect invoked right to counsel but questioning continued",
                "quote": "I want a lawyer",
                "case_law": "Miranda v. Arizona, 384 U.S. 436 (1966)",
                "amendment": "5th Amendment",
                "motion": "Motion to Suppress Statements",
            }
        ]
    }

    print("\n" + "=" * 60)
    print("VIOLATION SCAN OUTPUT")
    print("=" * 60)
    print(format_for_chat(violation_result, "violation", verbose=True))

    # Example: Format usage report
    usage_result = {
        "period_days": 30,
        "summary": {
            "total_tokens": 125000,
            "total_cost_usd": 4.75,
            "total_requests": 89,
        },
        "quota": {
            "monthly_token_limit": 100000,
            "tokens_used": 125000,
            "tokens_remaining": -25000,
        },
    }

    print("\n" + "=" * 60)
    print("USAGE REPORT OUTPUT")
    print("=" * 60)
    print(format_for_chat(usage_result, "usage"))
