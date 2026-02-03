"""
Chat Tools Integration
Wraps all analysis tools with chat-friendly output formatting

Usage in chat:
    from chat_tools import ChatTools

    tools = ChatTools(user_id=current_user.id)

    # Analyze evidence - returns formatted chat output
    result = tools.analyze_evidence(file_path, evidence_type="video")
    print(result)  # Formatted markdown ready for chat display

    # Get usage report
    usage = tools.get_usage_report(days=30)
    print(usage)  # Formatted usage summary
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from chat_output_formatter import (ChatOutput, Finding, OutputFormatter,
                                   OutputType, Severity, extract_action_items,
                                   format_for_chat, get_critical_findings,
                                   quick_summary)

logger = logging.getLogger(__name__)


class ChatTools:
    """
    Unified interface for all analysis tools with chat-friendly outputs

    All methods return formatted markdown strings ready for display
    in a chat interface. Raw data is available via the _raw suffix methods.
    """

    def __init__(self, user_id: int, verbose: bool = False):
        """
        Initialize chat tools

        Args:
            user_id: Current user ID for quota tracking
            verbose: Whether to include full details in outputs
        """
        self.user_id = user_id
        self.verbose = verbose
        self.formatter = OutputFormatter()

    # =========================================================================
    # EVIDENCE ANALYSIS
    # =========================================================================

    def analyze_evidence(
        self,
        file_path: Union[str, Path],
        evidence_type: str = "document",
        case_number: str = None,
        **kwargs,
    ) -> str:
        """
        Analyze evidence file through full processing pipeline

        Args:
            file_path: Path to evidence file
            evidence_type: video, audio, document, image, transcript
            case_number: Optional case number for tracking

        Returns:
            Formatted markdown analysis results
        """
        start_time = time.time()

        try:
            from unified_evidence_service import (EvidenceType,
                                                  UnifiedEvidenceProcessor)

            processor = UnifiedEvidenceProcessor()

            # Map string to enum
            type_map = {
                "video": EvidenceType.VIDEO,
                "audio": EvidenceType.AUDIO,
                "document": EvidenceType.DOCUMENT,
                "image": EvidenceType.IMAGE,
                "transcript": EvidenceType.TRANSCRIPT,
            }
            ev_type = type_map.get(evidence_type.lower(), EvidenceType.DOCUMENT)

            context = {
                "evidence_id": f"EVID-{self.user_id}-{int(time.time())}",
                "case_number": case_number or "N/A",
                "user_id": self.user_id,
                **kwargs,
            }

            result = processor.process_evidence(Path(file_path), ev_type.value, context)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            return format_for_chat(result, "evidence", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Evidence Analysis", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Evidence analysis failed: {e}")
            return self._format_error("Evidence Analysis", str(e))

    def analyze_evidence_raw(
        self, file_path: Union[str, Path], evidence_type: str = "document", **kwargs
    ) -> Dict:
        """Get raw evidence analysis results (for programmatic use)"""
        from unified_evidence_service import (EvidenceType,
                                              UnifiedEvidenceProcessor)

        processor = UnifiedEvidenceProcessor()
        type_map = {
            "video": EvidenceType.VIDEO,
            "audio": EvidenceType.AUDIO,
            "document": EvidenceType.DOCUMENT,
            "image": EvidenceType.IMAGE,
            "transcript": EvidenceType.TRANSCRIPT,
        }
        ev_type = type_map.get(evidence_type.lower(), EvidenceType.DOCUMENT)

        return processor.process_evidence(
            Path(file_path),
            ev_type.value,
            {"evidence_id": f"EVID-{self.user_id}-{int(time.time())}", **kwargs},
        )

    # =========================================================================
    # TRANSCRIPTION
    # =========================================================================

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = None,
        include_timestamps: bool = True,
    ) -> str:
        """
        Transcribe audio/video file

        Args:
            audio_path: Path to audio or video file
            language: Optional language code (None = auto-detect)
            include_timestamps: Include timestamps in output

        Returns:
            Formatted transcription results
        """
        start_time = time.time()

        try:
            from whisper_transcription import WhisperTranscriptionService

            service = WhisperTranscriptionService(model_size="base")
            result = service.transcribe_audio(
                str(audio_path),
                language=language,
                enable_timestamps=include_timestamps,
            )
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            return format_for_chat(result, "transcription", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Transcription", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return self._format_error("Transcription", str(e))

    def transcribe_raw(self, audio_path: Union[str, Path], **kwargs) -> Dict:
        """Get raw transcription results"""
        from whisper_transcription import WhisperTranscriptionService

        service = WhisperTranscriptionService(model_size="base")
        return service.transcribe_audio(str(audio_path), **kwargs)

    # =========================================================================
    # VIOLATION SCANNING
    # =========================================================================

    def scan_for_violations(
        self,
        text: str,
        context: Dict = None,
    ) -> str:
        """
        Scan text for constitutional violations

        Args:
            text: Text to analyze (transcript, statement, etc.)
            context: Additional context (case_type, jurisdiction, etc.)

        Returns:
            Formatted violation scan results
        """
        start_time = time.time()

        try:
            from case_law_violation_scanner import ViolationScanner

            scanner = ViolationScanner()
            result = scanner.scan_transcript(text, context or {})
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            return format_for_chat(result, "violation", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Violation Scan", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Violation scan failed: {e}")
            return self._format_error("Violation Scan", str(e))

    def scan_for_violations_raw(self, text: str, context: Dict = None) -> Dict:
        """Get raw violation scan results"""
        from case_law_violation_scanner import ViolationScanner

        scanner = ViolationScanner()
        return scanner.scan_transcript(text, context or {})

    # =========================================================================
    # COMPLIANCE CHECKING
    # =========================================================================

    def check_compliance(
        self,
        evidence_data: Dict,
    ) -> str:
        """
        Check evidence for statutory compliance

        Args:
            evidence_data: Evidence metadata including type, custody log, etc.

        Returns:
            Formatted compliance check results
        """
        start_time = time.time()

        try:
            from statutory_compliance_checker import StatutoryComplianceChecker

            checker = StatutoryComplianceChecker()
            result = checker.comprehensive_check(evidence_data)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            return format_for_chat(result, "compliance", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Compliance Check", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return self._format_error("Compliance Check", str(e))

    # =========================================================================
    # CITATION ANALYSIS
    # =========================================================================

    def analyze_citation(
        self,
        case_citation: str = None,
        opinion_id: int = None,
    ) -> str:
        """
        Analyze citation network for a case (Shepardize equivalent)

        Args:
            case_citation: Citation string (e.g., "384 U.S. 436")
            opinion_id: CourtListener opinion ID

        Returns:
            Formatted citation analysis results
        """
        start_time = time.time()

        try:
            from citation_network_analyzer import CitationNetworkAnalyzer

            analyzer = CitationNetworkAnalyzer()

            if opinion_id:
                treatment = analyzer.analyze_treatment(opinion_id)
                citing = analyzer.get_citing_cases(opinion_id)
                result = {
                    "opinion_id": opinion_id,
                    "treatment": treatment,
                    "citing_cases": citing,
                    "case_name": treatment.get("case_name", f"Opinion #{opinion_id}"),
                }
            else:
                result = {"error": "Opinion ID required", "case_citation": case_citation}

            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            return format_for_chat(result, "citation", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Citation Analysis", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Citation analysis failed: {e}")
            return self._format_error("Citation Analysis", str(e))

    # =========================================================================
    # API USAGE
    # =========================================================================

    def get_usage_report(self, days: int = 30) -> str:
        """
        Get API usage report

        Args:
            days: Number of days to report on

        Returns:
            Formatted usage report
        """
        try:
            from api_usage_metering import APIUsageMeteringService

            service = APIUsageMeteringService()
            result = service.get_usage_summary(self.user_id, days)

            return format_for_chat(result, "usage", verbose=self.verbose)

        except ImportError as e:
            return self._format_error("Usage Report", f"Service not available: {e}")
        except Exception as e:
            logger.error(f"Usage report failed: {e}")
            return self._format_error("Usage Report", str(e))

    def get_quota_status(self) -> str:
        """Get current quota status"""
        try:
            from api_usage_metering import APIUsageMeteringService

            service = APIUsageMeteringService()
            allowed, error = service.check_rate_limit(self.user_id)
            summary = service.get_usage_summary(self.user_id, 30)

            quota = summary.get("quota", {})

            output = ChatOutput(
                output_type=OutputType.USAGE_REPORT,
                title="Quota Status",
                summary="✅ Ready" if allowed else f"⚠️ {error}",
                stats={
                    "Tokens Used": f"{quota.get('tokens_used', 0):,}",
                    "Limit": f"{quota.get('monthly_token_limit', 0):,}",
                    "Remaining": f"{quota.get('monthly_token_limit', 0) - quota.get('tokens_used', 0):,}",
                },
                success=allowed,
                error=error or "",
            )

            return output.to_chat_message(verbose=False)

        except Exception as e:
            return self._format_error("Quota Status", str(e))

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4",
        provider: str = "openai",
    ) -> str:
        """
        Estimate cost for an API call

        Args:
            prompt_tokens: Expected input tokens
            completion_tokens: Expected output tokens
            model: Model to use
            provider: API provider

        Returns:
            Formatted cost estimate
        """
        try:
            from api_usage_metering import APIPricingCalculator

            cost = APIPricingCalculator.calculate_cost(
                provider, model, prompt_tokens, completion_tokens
            )

            output = ChatOutput(
                output_type=OutputType.USAGE_REPORT,
                title="Cost Estimate",
                summary=f"Estimated cost: **${cost:.6f}**",
                stats={
                    "Model": model,
                    "Prompt Tokens": prompt_tokens,
                    "Completion Tokens": completion_tokens,
                    "Total Tokens": prompt_tokens + completion_tokens,
                    "Cost": f"${cost:.6f}",
                },
                success=True,
            )

            return output.to_chat_message(verbose=False)

        except Exception as e:
            return self._format_error("Cost Estimate", str(e))

    # =========================================================================
    # LEGAL RESEARCH
    # =========================================================================

    def search_legal_library(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """
        Search legal document library

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            Formatted search results
        """
        try:
            from retrieval_service import RetrievalService

            service = RetrievalService()
            results = service.retrieve(query, top_k=top_k)

            findings = []
            citations = []

            for doc in results.get("documents", [])[:top_k]:
                findings.append(
                    Finding(
                        title=doc.get("title", "Document"),
                        description=doc.get("snippet", doc.get("content", "")[:200]),
                        severity=Severity.INFO,
                        category=doc.get("type", "Legal Document"),
                        citation=doc.get("citation", ""),
                    )
                )
                if doc.get("citation"):
                    citations.append(doc["citation"])

            output = ChatOutput(
                output_type=OutputType.LEGAL_RESEARCH,
                title=f"Search Results: '{query}'",
                summary=f"Found {len(findings)} relevant documents",
                key_points=[f.title for f in findings[:3]],
                findings=findings,
                stats={
                    "Query": query,
                    "Results": len(findings),
                },
                citations=citations,
                raw_data=results,
                success=True,
            )

            return output.to_chat_message(verbose=self.verbose)

        except Exception as e:
            logger.error(f"Legal search failed: {e}")
            return self._format_error("Legal Search", str(e))

    def find_similar_cases(
        self,
        case_facts: str,
        jurisdiction: str = None,
        limit: int = 5,
    ) -> str:
        """
        Find similar cases based on facts

        Args:
            case_facts: Description of case facts
            jurisdiction: Optional jurisdiction filter
            limit: Max results

        Returns:
            Formatted similar case results
        """
        try:
            from similar_case_finder import SimilarCaseFinder

            finder = SimilarCaseFinder()
            results = finder.find_similar(case_facts, jurisdiction=jurisdiction, limit=limit)

            findings = []
            citations = []

            for case in results.get("cases", []):
                findings.append(
                    Finding(
                        title=case.get("case_name", "Case"),
                        description=f"Similarity: {case.get('similarity', 0):.0%}",
                        severity=Severity.INFO,
                        category=case.get("court", ""),
                        citation=case.get("citation", ""),
                    )
                )
                if case.get("citation"):
                    citations.append(case["citation"])

            output = ChatOutput(
                output_type=OutputType.CASE_ANALYSIS,
                title="Similar Cases Found",
                summary=f"Found {len(findings)} similar cases",
                findings=findings,
                citations=citations,
                raw_data=results,
                success=True,
            )

            return output.to_chat_message(verbose=self.verbose)

        except Exception as e:
            logger.error(f"Similar case search failed: {e}")
            return self._format_error("Similar Cases", str(e))

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _format_error(self, tool_name: str, error: str) -> str:
        """Format an error message for chat display"""
        output = ChatOutput(
            output_type=OutputType.GENERAL,
            title=f"{tool_name} Error",
            summary=f"Unable to complete {tool_name.lower()}",
            success=False,
            error=error,
        )
        return output.to_chat_message()

    def help(self) -> str:
        """Get help on available tools"""
        return """## 🛠️ Available Chat Tools

### Evidence Analysis
• `analyze_evidence(file_path, evidence_type)` - Full evidence analysis pipeline
• `transcribe(audio_path)` - Transcribe audio/video

### Legal Analysis  
• `scan_for_violations(text)` - Scan for constitutional violations
• `check_compliance(evidence_data)` - Check statutory compliance
• `analyze_citation(case_citation)` - Shepardize™-equivalent citation analysis

### Research
• `search_legal_library(query)` - Search legal documents
• `find_similar_cases(facts)` - Find similar cases

### Usage & Billing
• `get_usage_report(days=30)` - API usage summary
• `get_quota_status()` - Current quota status
• `estimate_cost(prompt_tokens, completion_tokens)` - Cost estimate

---
*Set `verbose=True` when initializing for detailed outputs*
"""


# =============================================================================
# QUICK ACCESS FUNCTIONS
# =============================================================================


def get_tools(user_id: int, verbose: bool = False) -> ChatTools:
    """Quick helper to get ChatTools instance"""
    return ChatTools(user_id=user_id, verbose=verbose)


def analyze(file_path: str, user_id: int = 1, evidence_type: str = "document") -> str:
    """Quick analyze function"""
    return ChatTools(user_id).analyze_evidence(file_path, evidence_type)


def transcribe(audio_path: str, user_id: int = 1) -> str:
    """Quick transcribe function"""
    return ChatTools(user_id).transcribe(audio_path)


def scan_violations(text: str, user_id: int = 1) -> str:
    """Quick violation scan function"""
    return ChatTools(user_id).scan_for_violations(text)


def usage_report(user_id: int = 1, days: int = 30) -> str:
    """Quick usage report function"""
    return ChatTools(user_id).get_usage_report(days)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================


if __name__ == "__main__":
    # Demo the chat tools
    tools = ChatTools(user_id=1, verbose=True)

    print("=" * 60)
    print("CHAT TOOLS DEMO")
    print("=" * 60)

    # Show help
    print(tools.help())

    # Demo violation scan
    print("\n" + "=" * 60)
    print("VIOLATION SCAN DEMO")
    print("=" * 60)

    sample_text = """
    Officer: Do you know why I stopped you?
    Civilian: No, sir.
    Officer: You were going 45 in a 35 zone.
    Civilian: I'd like to speak to a lawyer before answering any questions.
    Officer: We'll get to that later. First, tell me where you're coming from.
    Civilian: I said I want a lawyer.
    Officer: Just answer the question. Where were you tonight?
    """

    print(tools.scan_for_violations(sample_text))

    # Demo cost estimate
    print("\n" + "=" * 60)
    print("COST ESTIMATE DEMO")
    print("=" * 60)
    print(tools.estimate_cost(1000, 500, model="gpt-4"))
    print(tools.estimate_cost(1000, 500, model="gpt-4o-mini"))
