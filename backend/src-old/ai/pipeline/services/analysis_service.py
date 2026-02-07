# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Analysis Service - LLM analysis with grounded citations

Responsibilities:
1. Format passages into LLM prompt with citation markers
2. Call LLM (GPT-4, Claude, etc.)
3. Parse response and extract citations
4. Validate citations against source passages
5. Persist analysis + citations to database
6. Smart tools fallback (web search, math, knowledge base)

CRITICAL: This ensures LLM outputs are grounded in retrieved passages.
"""

import logging
import re

from ..contracts import AnalysisResult, CitationRecord, Passage

logger = logging.getLogger(__name__)

# Try to import smart tools
try:
    from src.ai.tools import SmartTools

    SMART_TOOLS_AVAILABLE = True
except ImportError:
    SMART_TOOLS_AVAILABLE = False
    logger.warning("Smart tools not available")


class AnalysisService:
    """Handles LLM analysis with citation grounding and smart tools"""

    def __init__(self, retrieval_service=None, authority_cache=None):
        self.retrieval_service = retrieval_service
        self.authority_cache = authority_cache

        # Initialize smart tools if available
        self.smart_tools = SmartTools() if SMART_TOOLS_AVAILABLE else None

        logger.info(f"AnalysisService initialized (smart_tools={SMART_TOOLS_AVAILABLE})")

    def analyze(
        self, query: str, context: list[Passage], mode: str = "legal_research"
    ) -> AnalysisResult:
        """
        Perform analysis with grounded citations

        Steps:
        1. Format context passages into prompt
        2. Add citation markers [Doc-1-Page-5]
        3. Generate response based on passages
        4. Extract and validate citations

        Args:
            query: Analysis question
            context: Pre-retrieved passages
            mode: Analysis mode (legal_research, violation_scan, etc.)

        Returns:
            AnalysisResult with citations
        """
        logger.info(f"Analyzing query: '{query}' with {len(context)} passages")

        # Format passages for analysis
        formatted_passages = self._format_passages(context)

        # Generate response (local, no LLM API required)
        response_text = self._generate_local_response(query, context, mode)

        # Extract citations from response
        citations = self._extract_citations(response_text, context)

        # Build result
        result = AnalysisResult(
            analysis_id=0,  # Will be set when persisted
            query=query,
            response=response_text,
            passages_used=context,
            citations=citations,
            authorities_cited=[],
            model="local",
            tokens_used=0,
            confidence_score=0.8 if context else 0.3,
        )

        logger.info(f"Analysis complete: {len(citations)} citations")

        return result

    def _format_passages(self, passages: list[Passage]) -> str:
        """Format passages with citation markers"""
        if not passages:
            return "No relevant passages found."

        lines = []
        for passage in passages:
            marker = f"[Doc-{passage.document_id}-Page-{passage.page_number}]"
            snippet = passage.snippet.strip().replace("\n", " ")[:500]
            lines.append(f"{marker} {snippet}")

        return "\n\n".join(lines)

    def _generate_local_response(self, query: str, context: list[Passage], mode: str) -> str:
        """
        Generate a helpful response based on available passages
        This works without requiring an external LLM API
        """
        if not context:
            return self._generate_no_context_response(query, mode)

        # Build response from passages
        response_parts = []

        # Introduction
        response_parts.append(
            f'Based on the documents in your library, here\'s what I found regarding your question about "{query}":\n'
        )

        # Summarize each relevant passage
        for i, passage in enumerate(context[:5], 1):
            citation = f"[Doc-{passage.document_id}-Page-{passage.page_number}]"
            snippet = passage.snippet.strip()[:400]

            if i == 1:
                response_parts.append(f"**Key Finding:** {snippet} {citation}\n")
            else:
                response_parts.append(f"**Additional Context ({i}):** {snippet} {citation}\n")

        # Add helpful note
        response_parts.append("\n---\n")
        response_parts.append("*This response is grounded in documents from your legal library. ")
        response_parts.append(
            "For more detailed analysis, consider uploading additional relevant documents or using the Pro features with your own OpenAI API key.*"
        )

        return "\n".join(response_parts)

    def _generate_no_context_response(self, query: str, mode: str) -> str:
        """Generate response when no passages are available - uses smart tools"""

        # Try smart tools first
        if self.smart_tools:
            try:
                results = self.smart_tools.process_query(query)
                if results and any(r.success for r in results):
                    # Format smart tools response
                    response = self.smart_tools.format_response(results, query)

                    # Add helpful footer
                    response += "\n\n---\n"
                    response += "*This answer was generated using Evident's smart tools (web search, knowledge base, and calculations). "
                    response += "For document-grounded analysis, upload relevant legal documents to your library.*"

                    return response
            except Exception as e:
                logger.error(f"Smart tools error: {e}")

        # Fallback response if no smart tools or they failed
        return f"""I don't have any documents in your library that directly address "{query}".

**Suggestions:**
1. **Upload relevant documents** - Add legal documents, case files, or PDFs to your library
2. **Refine your search** - Try using different keywords or legal terminology
3. **Use Pro features** - Enable OpenAI integration in Account Settings for broader analysis

**About "{query}":**
This appears to be a legal research question. For accurate legal information, please:
- Consult official legal resources
- Upload relevant statutes, case law, or legal documents
- Consider speaking with a licensed attorney

Would you like me to help you search for something else?"""

    def _extract_citations(self, response: str, context: list[Passage]) -> list[CitationRecord]:
        """
        Extract citation markers from response and validate

        Args:
            response: Analysis response text
            context: Source passages

        Returns:
            List of validated CitationRecord objects
        """
        citations = []

        # Build a lookup of valid citations
        valid_citations = {}
        for passage in context:
            key = f"Doc-{passage.document_id}-Page-{passage.page_number}"
            valid_citations[key] = passage

        # Find all citation markers in response
        pattern = r"\[Doc-(\d+)-Page-(\d+)\]"
        matches = re.findall(pattern, response)

        seen = set()
        for doc_id, page_num in matches:
            key = f"Doc-{doc_id}-Page-{page_num}"
            if key in valid_citations and key not in seen:
                seen.add(key)
                passage = valid_citations[key]

                citation = CitationRecord(
                    analysis_id=0,  # Will be set when persisted
                    document_id=int(doc_id),
                    page_number=int(page_num),
                    text_start=passage.text_start,
                    text_end=passage.text_end,
                    snippet=passage.snippet[:200],
                    authority_name=None,
                    authority_citation=None,
                )
                citations.append(citation)

        return citations
