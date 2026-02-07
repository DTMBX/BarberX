from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Enhanced Chat Assistant with Memory, Storage & Reference Retrieval

Integrates with unified AI pipeline for:
- Persistent conversation memory
- Citation-based retrieval
- Document references with provenance
- Accessibility features (text-to-speech, screen reader support)
"""

import json
import logging
from datetime import datetime
from typing import Any

from src.ai.pipeline import AnalysisResult, Passage, get_orchestrator

logger = logging.getLogger(__name__)


class EnhancedChatAssistant:
    """
    Enhanced chat assistant with comprehensive memory and retrieval

    Features:
    - Persistent conversation memory (database-backed)
    - Document-grounded responses with citations
    - Accessibility support (ARIA labels, TTS-ready)
    - Reference tracking and provenance
    - Multi-modal context (text, audio transcripts, evidence)
    """

Optional[def __init__(self, user_id: int, project_id: int] = None):
        """
        Initialize enhanced chat assistant

        Args:
            user_id: User ID for personalization
            project_id: Optional project/workspace ID
        """
        self.user_id = user_id
        self.project_id = project_id

        # Get unified pipeline orchestrator
        self.orchestrator = get_orchestrator()

        # Conversation state
Optional[self.conversation_id: int] = None
        self.message_history: list[dict] = []
        self.referenced_documents: list[int] = []  # Track doc_ids

        logger.info(f"EnhancedChatAssistant initialized for user_id={user_id}")

    def start_conversation(
Optional[self, title: str]Optional[= None, context_documents: list[int]] = None
    ) -> dict[str, Any]:
        """
        Start a new conversation with optional document context

        Args:
            title: Conversation title
            context_documents: List of doc_ids to load into context

        Returns:
            Conversation metadata
        """
        # Create conversation record
        conversation = self._create_conversation_record(
            title=title or f"Conversation {datetime.utcnow().isoformat()}"
        )

        self.conversation_id = conversation["id"]
        self.message_history = []

        # Load context documents if provided
        if context_documents:
            self._load_context_documents(context_documents)

        # Add system message with instructions
        system_message = self._generate_system_message()
        self.message_history.append(system_message)

        logger.info(f"Started conversation_id={self.conversation_id}")

        return {
            "conversation_id": self.conversation_id,
            "title": conversation["title"],
            "context_documents": len(self.referenced_documents),
            "created_at": conversation["created_at"],
        }

    def ask(
        self,
        query: str,
        retrieve_references: bool = True,
        max_passages: int = 5,
        accessibility_mode: bool = False,
    ) -> dict[str, Any]:
        """
        Ask a question with automatic reference retrieval

        Args:
            query: User question
            retrieve_references: Whether to retrieve relevant documents
            max_passages: Max passages to retrieve
            accessibility_mode: Enable screen reader optimizations

        Returns:
            Response with answer, citations, and accessibility metadata
        """
        logger.info(f"Processing query: '{query[:100]}...'")

        # Add user message to history
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.message_history.append(user_message)

        # Retrieve relevant passages if enabled
        passages: list[Passage] = []
        if retrieve_references:
            retrieve_result = self.orchestrator.retrieve(
                query=query,
                top_k=max_passages,
                method="hybrid",  # Use keyword + semantic
            )
            passages = retrieve_result.passages

            logger.info(f"Retrieved {len(passages)} relevant passages")

        # Generate response using unified pipeline
        analysis_result = self.orchestrator.analyze(
            query=query, context=passages, mode="legal_research"
        )

        # Format response for accessibility
        response = self._format_response(
            analysis_result=analysis_result,
            passages=passages,
            accessibility_mode=accessibility_mode,
        )

        # Add assistant message to history
        assistant_message = {
            "role": "assistant",
            "content": response["answer"],
            "citations": response["citations"],
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.message_history.append(assistant_message)

        # Persist to database
        self._save_message_exchange(user_message, assistant_message)

        # Update referenced documents
        for citation in analysis_result.citations:
            if citation.document_id not in self.referenced_documents:
                self.referenced_documents.append(citation.document_id)

        return response

    def record_exchange(
        self, user_message: dict[str, Any], assistant_message: dict[str, Any]
    ) -> None:
        """
        Record a message exchange to memory and persistence hooks.

        Args:
            user_message: User message payload
            assistant_message: Assistant message payload (may include citations)
        """
        self.message_history.append(user_message)
        self.message_history.append(assistant_message)
        self._save_message_exchange(user_message, assistant_message)

        for citation in assistant_message.get("citations", []):
            document_id = citation.get("document_id")
            if document_id and document_id not in self.referenced_documents:
                self.referenced_documents.append(document_id)

    def get_conversation_summary(self, include_citations: bool = True) -> dict[str, Any]:
        """
        Get comprehensive conversation summary with memory

        Args:
            include_citations: Include all citations from conversation

        Returns:
            Summary with message count, topics, referenced documents
        """
        # Analyze conversation topics
        all_messages = " ".join([msg["content"] for msg in self.message_history])

        # Extract key topics (simplified - could use NER)
        topics = self._extract_topics(all_messages)

        # Get citation summary
        all_citations = []
        if include_citations:
            for msg in self.message_history:
                if msg["role"] == "assistant" and "citations" in msg:
                    all_citations.extend(msg["citations"])

        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.message_history),
            "user_messages": sum(1 for m in self.message_history if m["role"] == "user"),
            "assistant_messages": sum(1 for m in self.message_history if m["role"] == "assistant"),
            "topics": topics,
            "referenced_documents": len(self.referenced_documents),
            "total_citations": len(all_citations),
            "unique_citations": len(set(c["document_id"] for c in all_citations)),
            "duration_minutes": self._calculate_duration(),
        }

    def search_conversation_history(
Optional[self, query: str, message_type: str] = None
    ) -> list[dict[str, Any]]:
        """
        Search within conversation history

        Args:
            query: Search query
            message_type: Filter by 'user' or 'assistant'

        Returns:
            Matching messages with context
        """
        matches = []

        for i, msg in enumerate(self.message_history):
            if message_type and msg["role"] != message_type:
                continue

            if query.lower() in msg["content"].lower():
                # Include context (previous and next message)
                context_before = self.message_history[i - 1] if i > 0 else None
                context_after = (
                    self.message_history[i + 1] if i < len(self.message_history) - 1 else None
                )

                matches.append(
                    {
                        "message": msg,
                        "message_index": i,
                        "context_before": context_before,
                        "context_after": context_after,
                    }
                )

        logger.info(f"Found {len(matches)} matches for '{query}'")
        return matches

    def export_conversation(self, format: str = "markdown", include_citations: bool = True) -> str:
        """
        Export conversation in various formats

        Args:
            format: Export format (markdown, json, html)
            include_citations: Include citation details

        Returns:
            Formatted conversation export
        """
        if format == "markdown":
            return self._export_as_markdown(include_citations)
        elif format == "json":
            return json.dumps(
                {
                    "conversation_id": self.conversation_id,
                    "messages": self.message_history,
                    "summary": self.get_conversation_summary(),
                },
                indent=2,
            )
        elif format == "html":
            return self._export_as_html(include_citations)
        else:
            raise ValueError(f"Unsupported format: {format}")

    # ================================================================
    # ACCESSIBILITY FEATURES
    # ================================================================

    def get_accessible_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Enhance response with accessibility metadata

        Args:
            response: Standard response dict

        Returns:
            Response with ARIA labels, TTS hints, etc.
        """
        return {
            **response,
            "accessibility": {
                "aria_label": f"Answer with {len(response['citations'])} citations",
                "screen_reader_text": self._generate_screen_reader_text(response),
                "tts_text": self._generate_tts_text(response),
                "reading_time_seconds": self._estimate_reading_time(response["answer"]),
                "complexity_score": self._calculate_complexity(response["answer"]),
            },
        }

    def generate_audio_summary(self, response: dict[str, Any]) -> str:
        """
        Generate audio-optimized summary (for TTS)

        Args:
            response: Response to summarize

        Returns:
            TTS-friendly text
        """
        # Remove citation markers like [Doc-1-Page-5]
        text = response["answer"]

        # Replace citation markers with spoken references
        import re

        text = re.sub(r"\[Doc-(\d+)-Page-(\d+)\]", r"as referenced in document \1, page \2,", text)

        # Add citation count at end
        citation_count = len(response.get("citations", []))
        if citation_count > 0:
            text += f"\n\nThis answer references {citation_count} source documents."

        return text

    # ================================================================
    # INTERNAL HELPERS
    # ================================================================

    def _generate_system_message(self) -> dict[str, str]:
        """Generate system message with instructions"""
        return {
            "role": "system",
            "content": """You are Evident Legal Assistant, a precise and helpful AI trained in constitutional law, 
criminal procedure, and civil rights. You provide answers based ONLY on retrieved documents and cite all sources.

Guidelines:
- Cite sources using [Doc-X-Page-Y] format
- Never invent facts or cases
- If information is not in provided passages, say so
- Explain legal concepts clearly for non-lawyers
- Flag procedural violations and constitutional issues
- Provide actionable guidance when appropriate

Always ground your answers in evidence and cite your sources.""",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _load_context_documents(self, doc_ids: list[int]):
        """Load documents into conversation context"""
        self.referenced_documents.extend(doc_ids)
        logger.info(f"Loaded {len(doc_ids)} context documents")

    def _format_response(
        self, analysis_result: AnalysisResult, passages: list[Passage], accessibility_mode: bool
    ) -> dict[str, Any]:
        """Format analysis result as chat response"""
        # Extract citations with full metadata
        citations = []
        for citation in analysis_result.citations:
            citations.append(
                {
                    "document_id": citation.document_id,
                    "page_number": citation.page_number,
                    "snippet": citation.snippet,
                    "text_start": citation.text_start,
                    "text_end": citation.text_end,
                    "authority_name": citation.authority_name,
                    "authority_citation": citation.authority_citation,
                }
            )

        response = {
            "answer": analysis_result.response,
            "citations": citations,
            "passages_used": len(passages),
            "confidence": analysis_result.confidence_score,
            "model": analysis_result.model,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Add accessibility enhancements if requested
        if accessibility_mode:
            response = self.get_accessible_response(response)

        return response

    def _extract_topics(self, text: str) -> list[str]:
        """Extract key topics from text (simplified)"""
        # TODO: Use NER or topic modeling
        # For now, return placeholder
        return ["constitutional_law", "criminal_procedure"]

    def _calculate_duration(self) -> float:
        """Calculate conversation duration in minutes"""
        if len(self.message_history) < 2:
            return 0.0

        start = datetime.fromisoformat(self.message_history[0]["timestamp"])
        end = datetime.fromisoformat(self.message_history[-1]["timestamp"])
        return (end - start).total_seconds() / 60.0

    def _generate_screen_reader_text(self, response: dict) -> str:
        """Generate screen reader optimized text"""
        citations = len(response.get("citations", []))
        return f"Answer with {citations} source citations. {response['answer']}"

    def _generate_tts_text(self, response: dict) -> str:
        """Generate text-to-speech optimized text"""
        return self.generate_audio_summary(response)

    def _estimate_reading_time(self, text: str) -> int:
        """Estimate reading time in seconds (avg 200 wpm)"""
        words = len(text.split())
        return int((words / 200) * 60)

    def _calculate_complexity(self, text: str) -> str:
        """Calculate text complexity (simplified)"""
        words = len(text.split())
        if words < 100:
            return "simple"
        elif words < 300:
            return "moderate"
        else:
            return "complex"

    def _export_as_markdown(self, include_citations: bool) -> str:
        """Export conversation as markdown"""
        md = f"# Conversation {self.conversation_id}\n\n"

        for msg in self.message_history:
            if msg["role"] == "system":
                continue

            role_label = "**You:**" if msg["role"] == "user" else "**Evident:**"
            md += f"{role_label} {msg['content']}\n\n"

            if include_citations and msg["role"] == "assistant" and "citations" in msg:
                md += "**Citations:**\n"
                for cit in msg["citations"]:
                    md += f"- Document {cit['document_id']}, Page {cit['page_number']}\n"
                md += "\n"

        return md

    def _export_as_html(self, include_citations: bool) -> str:
        """Export conversation as accessible HTML"""
        html = f'<article role="article" aria-label="Conversation {self.conversation_id}">\n'
        html += f"  <h1>Conversation {self.conversation_id}</h1>\n"

        for i, msg in enumerate(self.message_history):
            if msg["role"] == "system":
                continue

            role = msg["role"]
            html += f'  <section class="message message-{role}" id="msg-{i}" role="region">\n'
            html += f"    <h2>{role.capitalize()}</h2>\n"
            html += f'    <div class="message-content">{msg["content"]}</div>\n'

            if include_citations and role == "assistant" and "citations" in msg:
                html += '    <aside class="citations" aria-label="Source citations">\n'
                html += "      <h3>Citations</h3>\n"
                html += "      <ul>\n"
                for cit in msg["citations"]:
                    html += f'        <li><a href="/doc/{cit["document_id"]}#page-{cit["page_number"]}">'
                    html += f"Doc {cit['document_id']}, Page {cit['page_number']}</a></li>\n"
                html += "      </ul>\n"
                html += "    </aside>\n"

            html += "  </section>\n"

        html += "</article>\n"
        return html

    def _create_conversation_record(self, title: str) -> dict:
        """Create conversation record in database"""
        # TODO: Integrate with actual database
        return {
            "id": hash(title) % 1000000,
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _save_message_exchange(self, user_msg: dict, assistant_msg: dict):
        """Persist message exchange to database"""
        # TODO: Integrate with actual database
        logger.debug(f"Saved message exchange to conversation {self.conversation_id}")