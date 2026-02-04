"""
Unified Evidence Processing Service
Connects all evidence analysis tools into one cohesive workflow

Features:
- End-to-end evidence processing pipeline
- Automatic violation detection
- Compliance checking
- Transcription and OCR
- Legal analysis integration
- Report generation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .backend_integration import (Event, ValidationError, cache, cached,
                                 error_response, event_bus,
                                 handle_service_errors, monitored,
                                 service_registry, success_response)


class EvidenceType:
    """Evidence type constants"""

    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    TRANSCRIPT = "transcript"


class ProcessingStage:
    """Processing pipeline stages"""

    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    OCR_PROCESSING = "ocr_processing"
    ANALYZING_VIOLATIONS = "analyzing_violations"
    CHECKING_COMPLIANCE = "checking_compliance"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class UnifiedEvidenceProcessor:
    """
    Unified service that orchestrates all evidence processing tools

    Pipeline:
    1. Upload & Validation
    2. Transcription (if video/audio)
    3. OCR (if document/image)
    4. Violation Scanning
    5. Compliance Checking
    6. Report Generation
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Try to load services
        self._load_services()

    def _load_services(self):
        """Load and register all processing services"""
        # Transcription service
        try:
            from whisper_transcription import WhisperTranscriptionService

            transcription = WhisperTranscriptionService(model_size="base")
            service_registry.register("transcription", transcription, version="1.0.0")
            self.logger.info("[OK] Transcription service loaded")
        except ImportError:
            self.logger.warning("[WARN] Transcription service not available")

        # OCR service
        try:
            from ocr_service import OCRService

            ocr = OCRService(engine="tesseract")
            service_registry.register("ocr", ocr, version="1.0.0")
            self.logger.info("[OK] OCR service loaded")
        except ImportError:
            self.logger.warning("[WARN] OCR service not available")

        # Violation scanner
        try:
            from case_law_violation_scanner import ViolationScanner

            scanner = ViolationScanner()
            service_registry.register("violation_scanner", scanner, version="1.0.0")
            self.logger.info("[OK] Violation scanner loaded")
        except ImportError:
            self.logger.warning("[WARN] Violation scanner not available")

        # Compliance checker
        try:
            from statutory_compliance_checker import StatutoryComplianceChecker

            compliance = StatutoryComplianceChecker()
            service_registry.register("compliance_checker", compliance, version="1.0.0")
            self.logger.info("[OK] Compliance checker loaded")
        except ImportError:
            self.logger.warning("[WARN] Compliance checker not available")

    @monitored("evidence.process_full")
    @handle_service_errors("evidence_processor")
    def process_evidence(
        self, evidence_file: Path, evidence_type: str, context: Dict
    ) -> Dict[str, Any]:
        """
        Process evidence through complete pipeline

        Args:
            evidence_file: Path to evidence file
            evidence_type: Type of evidence (video, audio, document, image)
            context: Additional context (case_number, evidence_id, etc.)

        Returns:
            Complete analysis results
        """
        evidence_id = context.get("evidence_id", f"EVID-{datetime.utcnow().timestamp()}")

        results = {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "started_at": datetime.utcnow().isoformat(),
            "stages": {},
            "transcript": None,
            "ocr_text": None,
            "violations": None,
            "compliance": None,
            "recommendations": [],
            "case_law_citations": [],
            "motions_to_file": [],
        }

        try:
            # Stage 1: Transcription (if audio/video)
            if evidence_type in [EvidenceType.VIDEO, EvidenceType.AUDIO]:
                self.logger.info(f"Starting transcription for {evidence_id}")
                transcript_result = self._transcribe_evidence(evidence_file, context)
                results["transcript"] = transcript_result
                results["stages"]["transcription"] = "completed"

                # Publish event
                event_bus.publish(
                    Event(
                        event_type="evidence.transcribed",
                        data={"evidence_id": evidence_id},
                        source="evidence_processor",
                    )
                )

            # Stage 2: OCR (if document/image)
            elif evidence_type in [EvidenceType.DOCUMENT, EvidenceType.IMAGE]:
                self.logger.info(f"Starting OCR for {evidence_id}")
                ocr_result = self._extract_text(evidence_file, context)
                results["ocr_text"] = ocr_result
                results["stages"]["ocr"] = "completed"

            # Stage 3: Violation Analysis
            text_content = results.get("transcript") or results.get("ocr_text")
            if text_content:
                self.logger.info(f"Analyzing violations for {evidence_id}")
                violation_results = self._analyze_violations(text_content, context)
                results["violations"] = violation_results
                results["stages"]["violation_analysis"] = "completed"

                # Extract recommendations
                if violation_results and "recommended_motions" in violation_results:
                    results["motions_to_file"].extend(violation_results["recommended_motions"])

                # Extract case law
                if violation_results and "case_law_citations" in violation_results:
                    results["case_law_citations"].extend(violation_results["case_law_citations"])

            # Stage 4: Compliance Check
            self.logger.info(f"Checking compliance for {evidence_id}")
            compliance_results = self._check_compliance(evidence_file, evidence_type, context)
            results["compliance"] = compliance_results
            results["stages"]["compliance_check"] = "completed"

            # Extract compliance recommendations
            if compliance_results and "recommendations" in compliance_results:
                results["recommendations"].extend(compliance_results["recommendations"])

            # Stage 5: Generate Summary
            results["summary"] = self._generate_summary(results)
            results["stages"]["summary_generation"] = "completed"

            results["completed_at"] = datetime.utcnow().isoformat()
            results["status"] = "success"

            # Publish completion event
            event_bus.publish(
                Event(
                    event_type="evidence.processed",
                    data={"evidence_id": evidence_id, "status": "success"},
                    source="evidence_processor",
                )
            )

            return results

        except Exception as e:
            self.logger.error(f"Error processing evidence {evidence_id}: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["completed_at"] = datetime.utcnow().isoformat()

            # Publish failure event
            event_bus.publish(
                Event(
                    event_type="evidence.processing_failed",
                    data={"evidence_id": evidence_id, "error": str(e)},
                    source="evidence_processor",
                )
            )

            return results

    @cached(ttl=3600, key_prefix="transcription")
    def _transcribe_evidence(self, file_path: Path, context: Dict) -> Optional[str]:
        """Transcribe audio/video evidence"""
        transcription_service = service_registry.get("transcription")

        if not transcription_service:
            self.logger.warning("Transcription service not available")
            return None

        try:
            result = transcription_service.transcribe_audio(
                str(file_path), language=context.get("language"), enable_timestamps=True
            )

            return result.get("text", "")

        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            return None

    @cached(ttl=3600, key_prefix="ocr")
    def _extract_text(self, file_path: Path, context: Dict) -> Optional[str]:
        """Extract text from document/image"""
        ocr_service = service_registry.get("ocr")

        if not ocr_service:
            self.logger.warning("OCR service not available")
            return None

        try:
            result = ocr_service.extract_text(str(file_path))
            return result.get("text", "")

        except Exception as e:
            self.logger.error(f"OCR failed: {str(e)}")
            return None

    def _analyze_violations(self, text: str, context: Dict) -> Optional[Dict]:
        """Analyze text for legal violations"""
        scanner = service_registry.get("violation_scanner")

        if not scanner:
            self.logger.warning("Violation scanner not available")
            return None

        try:
            return scanner.scan_transcript(text, context)

        except Exception as e:
            self.logger.error(f"Violation analysis failed: {str(e)}")
            return None

    def _check_compliance(
        self, file_path: Path, evidence_type: str, context: Dict
    ) -> Optional[Dict]:
        """Check evidence compliance"""
        checker = service_registry.get("compliance_checker")

        if not checker:
            self.logger.warning("Compliance checker not available")
            return None

        try:
            evidence = {
                "id": context.get("evidence_id"),
                "type": evidence_type,
                "is_original": context.get("is_original", True),
                "authenticated": context.get("authenticated", False),
                "custody_log": context.get("custody_log", []),
            }

            return checker.comprehensive_check(evidence)

        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return None

    def _generate_summary(self, results: Dict) -> str:
        """Generate executive summary of analysis"""
        violations = results.get("violations", {})
        compliance = results.get("compliance", {})

        summary_parts = []

        # Violation summary
        if violations:
            total_violations = violations.get("total_violations", 0)
            critical = violations.get("violations_by_severity", {}).get("critical", 0)

            if total_violations > 0:
                summary_parts.append(
                    f"Found {total_violations} potential violation(s), "
                    f"including {critical} CRITICAL issue(s)."
                )

        # Compliance summary
        if compliance:
            status = compliance.get("overall_status", "UNKNOWN")
            if status == "NON_COMPLIANT":
                summary_parts.append(
                    "Evidence has compliance issues that may affect admissibility."
                )

        # Recommendations
        motions_count = len(results.get("motions_to_file", []))
        if motions_count > 0:
            summary_parts.append(f"Recommend filing {motions_count} motion(s).")

        return (
            " ".join(summary_parts)
            if summary_parts
            else "Analysis complete. No critical issues detected."
        )


class EvidenceReportGenerator:
    """Generate comprehensive reports from evidence analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @monitored("report.generate")
    def generate_report(self, analysis_results: Dict, format: str = "markdown") -> str:
        """
        Generate comprehensive report

        Args:
            analysis_results: Results from UnifiedEvidenceProcessor
            format: Output format (markdown, html, pdf)

        Returns:
            Formatted report string
        """
        if format == "markdown":
            return self._generate_markdown_report(analysis_results)
        elif format == "html":
            return self._generate_html_report(analysis_results)
        else:
            return self._generate_text_report(analysis_results)

    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate Markdown report"""
        report = f"""# Evidence Analysis Report

**Evidence ID:** {results.get('evidence_id')}  
**Evidence Type:** {results.get('evidence_type')}  
**Analysis Date:** {results.get('started_at')}  
**Status:** {results.get('status')}

---

## Executive Summary

{results.get('summary', 'No summary available')}

---

## Analysis Results

"""

        # Violation section
        violations = results.get("violations")
        if violations:
            report += f"""### Constitutional Violations

**Total Violations:** {violations.get('total_violations', 0)}

"""

            critical_violations = violations.get("critical_violations", [])
            if critical_violations:
                report += "#### Critical Violations\n\n"
                for v in critical_violations:
                    report += f"""**{v.get('title')}**
- **Type:** {v.get('type')}
- **Description:** {v.get('description')}
- **Legal Basis:** {v.get('legal_basis')}
- **Action:** {v.get('recommended_action')}

"""

        # Compliance section
        compliance = results.get("compliance")
        if compliance:
            report += f"""### Statutory Compliance

**Overall Status:** {compliance.get('overall_status')}  
**Total Issues:** {compliance.get('total_issues', 0)}

"""

        # Recommendations
        motions = results.get("motions_to_file", [])
        if motions:
            report += "### Recommended Motions\n\n"
            for motion in motions:
                if isinstance(motion, dict):
                    report += f"- **{motion.get('motion_type')}:** {motion.get('basis')} ({motion.get('priority')} priority)\n"
                else:
                    report += f"- {motion}\n"
            report += "\n"

        # Case law
        citations = results.get("case_law_citations", [])
        if citations:
            report += "### Case Law Support\n\n"
            for citation in citations:
                report += f"- {citation}\n"

        report += "\n---\n\n*Report generated by Evident Legal Technologies*"

        return report

    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML report"""
        # Convert markdown to HTML (simplified)
        markdown = self._generate_markdown_report(results)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Evidence Analysis Report - {results.get('evidence_id')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #d4af37; }}
        h2 {{ color: #2d2d2d; border-bottom: 1px solid #e0e0e0; }}
        .critical {{ background: #fee2e2; padding: 10px; border-left: 4px solid #ef4444; margin: 10px 0; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <pre>{markdown}</pre>
</body>
</html>"""

        return html

    def _generate_text_report(self, results: Dict) -> str:
        """Generate plain text report"""
        return self._generate_markdown_report(results)


# Example usage
if __name__ == "__main__":
    import tempfile

    # Initialize processor
    processor = UnifiedEvidenceProcessor()
    report_gen = EvidenceReportGenerator()

    # Create test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Officer: You have the right to remain silent.\nSuspect: I want a lawyer.")
        test_file = Path(f.name)

    # Process evidence
    print("Processing evidence...")
    results = processor.process_evidence(
        test_file,
        EvidenceType.TRANSCRIPT,
        {"evidence_id": "TEST-001", "case_number": "CR-2024-001", "is_original": True},
    )

    print("\n" + "=" * 80)
    print("PROCESSING RESULTS")
    print("=" * 80)
    print(f"Status: {results['status']}")
    print(f"Summary: {results['summary']}")
    print(f"\nStages completed: {', '.join(results['stages'].keys())}")

    # Generate report
    print("\n" + "=" * 80)
    print("MARKDOWN REPORT")
    print("=" * 80)
    report = report_gen.generate_report(results, format="markdown")
    print(report)

    # Clean up
    test_file.unlink()


