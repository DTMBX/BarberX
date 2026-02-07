# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Document Optimizer Integration with Legal Reference Library

Auto-suggests relevant citations when optimizing legal documents
"""

from .legal_library import LegalLibraryService


class DocumentOptimizerLibraryIntegration:
    """Integrates legal library into document optimization"""

    def __init__(self):
        self.library = LegalLibraryService()

    def suggest_citations_for_document(
        self, document_text: str, doc_type: str = None
    ) -> list[dict]:
        """
        Suggest relevant citations based on document content

        Args:
            document_text: Full text of legal document
            doc_type: Type of document (complaint, motion, brief, etc.)

        Returns:
            List of suggested citations with relevance scores
        """

        # Extract key legal issues from document
        legal_issues = self._extract_legal_issues(document_text)

        suggestions = []

        for issue in legal_issues:
            # Search library for cases on this issue
            cases = self.library.search_library(query=issue, doc_type="case", limit=3)

            for case in cases:
                suggestions.append(
                    {
                        "citation": case.citation,
                        "title": case.title,
                        "court": case.court,
                        "summary": case.summary[:200] if case.summary else "",
                        "relevance_reason": f"Relevant to: {issue}",
                        "suggested_usage": self._suggest_usage(case, doc_type),
                        "doc_id": case.id,
                    }
                )

        # Remove duplicates and rank by relevance
        suggestions = self._deduplicate_and_rank(suggestions)

        return suggestions[:10]  # Top 10 suggestions

    def enhance_optimization_prompt(self, base_prompt: str, document_text: str) -> str:
        """
        Add citation suggestions to optimization prompt

        Args:
            base_prompt: Base GPT-4 optimization prompt
            document_text: Document being optimized

        Returns:
            Enhanced prompt with suggested citations
        """

        suggestions = self.suggest_citations_for_document(document_text)

        if not suggestions:
            return base_prompt

        citation_context = "\n\nSUGGESTED CITATIONS FROM USER'S LEGAL LIBRARY:\n\n"
        citation_context += "Consider incorporating these relevant cases:\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            citation_context += f"{i}. {suggestion['citation']} - {suggestion['title']}\n"
            citation_context += f"   Court: {suggestion['court']}\n"
            citation_context += f"   Relevance: {suggestion['relevance_reason']}\n"
            citation_context += f"   Usage: {suggestion['suggested_usage']}\n\n"

        citation_context += (
            "Only cite cases if they genuinely strengthen the document. Do not force citations.\n"
        )

        return base_prompt + citation_context

    def verify_citations_exist(self, document_text: str) -> dict:
        """
        Verify that all citations in document exist in library

        Returns:
            Dict with verified citations and missing citations
        """

        from legal_library import CitationParser

        parser = CitationParser()

        # Extract all citations from document
        citations = parser.extract_all(document_text)

        verified = []
        missing = []

        for citation in citations:
            # Check if in library
            result = self.library.search_library(query=citation, limit=1)

            if result and result[0].citation == citation:
                verified.append({"citation": citation, "in_library": True, "doc_id": result[0].id})
            else:
                missing.append(
                    {
                        "citation": citation,
                        "in_library": False,
                        "suggestion": "Consider importing this case to your library",
                    }
                )

        return {
            "verified": verified,
            "missing": missing,
            "coverage": len(verified) / len(citations) if citations else 0,
        }

    def _extract_legal_issues(self, text: str) -> list[str]:
        """Extract legal issues from document text"""

        # Keywords indicating legal issues
        issue_indicators = [
            "excessive force",
            "unlawful search",
            "unlawful seizure",
            "miranda violation",
            "due process violation",
            "equal protection",
            "qualified immunity",
            "municipal liability",
            "monell claim",
            "brady violation",
            "prosecutorial misconduct",
            "ineffective assistance",
            "warrantless search",
            "probable cause",
            "reasonable suspicion",
            "fourth amendment",
            "fifth amendment",
            "sixth amendment",
            "fourteenth amendment",
            "discrimination",
            "retaliation",
            "wrongful termination",
        ]

        text_lower = text.lower()
        issues = []

        for indicator in issue_indicators:
            if indicator in text_lower:
                issues.append(indicator)

        return issues

    def _suggest_usage(self, case, doc_type: str) -> str:
        """Suggest how to use this case in document"""

        if doc_type == "complaint":
            return "Cite in factual allegations to establish legal standard"
        elif doc_type == "motion":
            return "Cite in argument section to support legal theory"
        elif doc_type == "brief":
            return "Cite as precedent in legal analysis"
        else:
            return "Cite to support legal argument"

    def _deduplicate_and_rank(self, suggestions: list[dict]) -> list[dict]:
        """Remove duplicate citations and rank by relevance"""

        seen = set()
        unique = []

        for suggestion in suggestions:
            if suggestion["citation"] not in seen:
                seen.add(suggestion["citation"])
                unique.append(suggestion)

        # TODO: Add relevance scoring algorithm
        # For now, just return in order found
        return unique


# TODO: Integration point for legal_document_optimizer.py
"""
Add to LegalDocumentOptimizer class:

from .document_optimizer_library_integration import DocumentOptimizerLibraryIntegration

class LegalDocumentOptimizer:
    def __init__(self):
        self.library_integration = DocumentOptimizerLibraryIntegration()
    
    def optimize_document(self, document_text, ...):
        # Get citation suggestions
        suggestions = self.library_integration.suggest_citations_for_document(document_text)
        
        # Enhance optimization prompt
        enhanced_prompt = self.library_integration.enhance_optimization_prompt(
            base_prompt,
            document_text
        )
        
        # Run optimization with enhanced prompt
        result = self._call_gpt4(enhanced_prompt)
        
        # Verify all citations exist
        citation_check = self.library_integration.verify_citations_exist(result)
        
        return OptimizationResult(
            optimized_text=result,
            citation_suggestions=suggestions,
            citation_coverage=citation_check
        )
"""
