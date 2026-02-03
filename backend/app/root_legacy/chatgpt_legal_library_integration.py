"""
ChatGPT Integration with Legal Reference Library

Enables ChatGPT assistant to:
- Search user's legal library when answering questions
- Cite cases from the library in responses with provenance
- Suggest relevant cases based on conversation context
- Link to full case text in the library
"""

import json
from typing import Dict, List, Optional, Tuple

from retrieval_service import Passage, RetrievalService

try:
    from legal_library import CitationParser, LegalLibraryService

    LEGACY_LIBRARY_AVAILABLE = True
except ImportError:
    LEGACY_LIBRARY_AVAILABLE = False
    CitationParser = None


class ChatGPTLegalLibraryIntegration:
    """Integrates legal library search into ChatGPT conversations"""

    def __init__(self):
        self.retrieval = RetrievalService()
        self.citation_parser = CitationParser() if LEGACY_LIBRARY_AVAILABLE else None

    def search_library_for_context(
        self, user_message: str, user_id: int = None
    ) -> Tuple[List[Passage], Dict[str, Any]]:
        """
        Search legal library based on user's question using unified retrieval

        Args:
            user_message: User's chat message
            user_id: Optional user ID for private documents

        Returns:
            (passages, citations_metadata) - passages with full provenance
        """

        # Extract legal keywords
        legal_keywords = self._extract_legal_keywords(user_message)

        if not legal_keywords:
            return [], {}

        # Use unified retrieval service
        query = " ".join(legal_keywords)
        passages = self.retrieval.retrieve(
            query=query,
            filters={"source_system": "legal_library"},  # Can expand to include muni_code
            top_k=5,
        )

        # Build citations metadata
        citations_metadata = {
            "query": query,
            "passages": [p.to_dict() for p in passages],
            "count": len(passages),
        }

        return passages, citations_metadata

    def enhance_system_prompt(self, base_prompt: str, passages: List[Passage]) -> str:
        """
        Add retrieved passages to ChatGPT system prompt with strict citation requirements

        Args:
            base_prompt: Original system prompt
            passages: Retrieved passages from search_library_for_context()

        Returns:
            Enhanced prompt with SOURCES block
        """

        if not passages:
            return base_prompt

        # Build SOURCES block with numbered citations
        sources_block = "\n\n=== SOURCES (Retrieved Legal Documents) ===\n"
        sources_block += "You MUST ground your analysis in these sources. "
        sources_block += "Cite sources using [Source N] format.\n\n"

        for idx, passage in enumerate(passages, 1):
            sources_block += f"[Source {idx}]\n"
            sources_block += f"Document: {passage.filename}\n"
            sources_block += f"Page: {passage.page_number}\n"
            sources_block += f"Excerpt: {passage.snippet}\n"
            sources_block += f"(doc_id: {passage.document_id}, offsets: {passage.text_start}-{passage.text_end})\n"
            sources_block += "\n"

        sources_block += "=== END SOURCES ===\n\n"
        sources_block += "CRITICAL: Every factual claim must cite a source from above. "
        sources_block += "Do not invent citations. If information isn't in the sources, say so.\n"

        return base_prompt + sources_block

    def format_citation_links(self, response_text: str) -> str:
        """
        Convert citations in response to clickable links

        Args:
            response_text: ChatGPT's response text

        Returns:
            Response with citations converted to markdown links
        """

        # Find all citations in response
        citations = self.citation_parser.extract_all(response_text)

        # Replace each citation with a link
        for citation in citations:
            # Look up in library
            doc = self.library.search_library(query=citation, limit=1)
            if doc:
                doc_id = doc[0].id
                link = f"[{citation}](/api/legal-library/document/{doc_id})"
                response_text = response_text.replace(citation, link)

        return response_text

    def _extract_legal_keywords(self, text: str) -> List[str]:
        """Extract legal keywords from user message"""

        # Common legal terms
        legal_terms = [
            "amendment",
            "constitutional",
            "supreme court",
            "circuit",
            "search",
            "seizure",
            "warrant",
            "probable cause",
            "miranda",
            "rights",
            "due process",
            "equal protection",
            "excessive force",
            "qualified immunity",
            "section 1983",
            "brady",
            "giglio",
            "discovery",
            "evidence",
            "counsel",
            "trial",
            "appeal",
            "habeas",
            "discrimination",
            "employment",
            "wrongful termination",
        ]

        text_lower = text.lower()
        keywords = []

        for term in legal_terms:
            if term in text_lower:
                keywords.append(term)

        # Also extract any citations mentioned
        citations = self.citation_parser.extract_all(text)
        keywords.extend(citations)

        return keywords


# TODO: Integration points for api/chatgpt.py
"""
Add to chat endpoint in api/chatgpt.py:

from chatgpt_legal_library_integration import ChatGPTLegalLibraryIntegration

library_integration = ChatGPTLegalLibraryIntegration()

@chatgpt_bp.route('/api/v1/chat/message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    
    # Search library for relevant cases
    relevant_cases = library_integration.search_library_for_context(
        user_message,
        user_id=current_user.id
    )
    
    # Enhance system prompt
    system_prompt = library_integration.enhance_system_prompt(
        base_system_prompt,
        relevant_cases
    )
    
    # Call ChatGPT with enhanced prompt
    response = chatgpt_service.chat(user_message, system_prompt)
    
    # Format citations as links
    response = library_integration.format_citation_links(response)
    
    return jsonify({'response': response})
"""
