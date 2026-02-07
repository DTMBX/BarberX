# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Enhanced Chat API - REST endpoints with memory & references

Provides:
- POST /api/chat/ask - Ask question with automatic reference retrieval
- GET /api/chat/conversations - List conversations with search/filter
- GET /api/chat/conversation/:id - Get conversation with full history
- POST /api/chat/conversation/:id/continue - Continue existing conversation
- GET /api/chat/references/suggest - Get reference suggestions
- GET /api/chat/conversation/:id/export - Export conversation
- GET /api/chat/analytics - Get conversation analytics
"""

import logging
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from src.ai.chat import ConversationMemoryStore, EnhancedChatAssistant, ReferenceManager

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint("enhanced_chat", __name__, url_prefix="/api/chat")


def csrf_exempt_api(f):
    """Mark a view as exempt from CSRF protection"""
    f.csrf_exempt = True
    return f


def build_openai_context(passages, max_chars=5000):
    """Build a compact, citation-tagged context block for OpenAI prompts."""
    if not passages:
        return "No document passages were provided."

    context_lines = []
    total_chars = 0

    for passage in passages:
        tag = f"[Doc-{passage.document_id}-Page-{passage.page_number}]"
        snippet = passage.snippet.strip().replace("\n", " ")
        line = f"{tag} {snippet}"

        if total_chars + len(line) > max_chars:
            break

        context_lines.append(line)
        total_chars += len(line)

    return "\n".join(context_lines)


@chat_bp.route("/ask", methods=["POST"])
@csrf_exempt_api
@login_required
def ask_question():
    """
    Ask a question with automatic reference retrieval

    Request body:
        {
            "query": "What is probable cause?",
            "conversation_id": 123,  // optional, creates new if omitted
            "retrieve_references": true,  // default true
            "max_passages": 5,  // default 5
            "accessibility_mode": false,  // default false
            "use_openai": false,  // optional: use OpenAI Pro (requires key)
            "openai_model": "gpt-4",  // optional
            "openai_temperature": 0.7,  // optional
            "openai_max_tokens": 1200  // optional
        }

    Response:
        {
            "conversation_id": 123,
            "answer": "Probable cause is...",
            "citations": [...],
            "passages_used": 5,
            "suggested_references": [...],
            "accessibility": {...}  // if accessibility_mode=true
        }
    """
    try:
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Missing required field: query"}), 400

        query = data["query"]
        conversation_id = data.get("conversation_id")
        retrieve_references = data.get("retrieve_references", True)
        max_passages = data.get("max_passages", 5)
        accessibility_mode = data.get("accessibility_mode", False)
        use_openai = bool(data.get("use_openai", False))
        openai_model = data.get("openai_model") or "gpt-4"
        openai_temperature = float(data.get("openai_temperature", 0.7))
        openai_max_tokens = int(data.get("openai_max_tokens", 1200))

        openai_max_tokens = max(256, min(openai_max_tokens, 4000))
        openai_temperature = max(0.0, min(openai_temperature, 1.2))

        # Initialize or load assistant
        assistant = EnhancedChatAssistant(
            user_id=current_user.id, project_id=data.get("project_id")
        )

        # Start or continue conversation
        if not conversation_id:
            conv_result = assistant.start_conversation(
                title=data.get("title"), context_documents=data.get("context_documents")
            )
            conversation_id = conv_result["conversation_id"]
        else:
            # Load existing conversation
            assistant.conversation_id = conversation_id
            # TODO: Load message history from database

        # Ask question
        if use_openai:
            from api.chatgpt import get_user_api_key
            from chatgpt_service import ChatGPTService

            user_api_key = get_user_api_key(current_user.id)
            if not user_api_key:
                return (
                    jsonify(
                        {
                            "error": "OpenAI API key required to use OpenAI Pro.",
                            "upgrade_required": True,
                            "upgrade_url": "/pricing",
                            "settings_url": "/account",
                        }
                    ),
                    400,
                )

            passages = []
            if retrieve_references:
                retrieve_result = assistant.orchestrator.retrieve(
                    query=query,
                    top_k=max_passages,
                    method="hybrid",
                )
                passages = retrieve_result.passages

            system_prompt = ChatGPTService().build_legal_system_prompt()
            context_block = build_openai_context(passages)

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                    + "\n\nUse the provided context and cite sources as [Doc-#-Page-#].",
                },
                {
                    "role": "system",
                    "content": f"Context:\n{context_block}",
                },
                {"role": "user", "content": query},
            ]

            chatgpt = ChatGPTService(api_key=user_api_key)
            openai_result = chatgpt.create_chat_completion(
                messages=messages,
                model=openai_model,
                max_tokens=openai_max_tokens,
                temperature=openai_temperature,
            )

            if not openai_result.get("success"):
                return (
                    jsonify(
                        {
                            "error": openai_result.get("error", "OpenAI request failed"),
                            "openai_error": True,
                        }
                    ),
                    502,
                )

            citations = [
                {
                    "document_id": passage.document_id,
                    "page_number": passage.page_number,
                    "snippet": passage.snippet,
                    "text_start": passage.text_start,
                    "text_end": passage.text_end,
                }
                for passage in passages
            ]

            response = {
                "answer": openai_result.get("content"),
                "citations": citations,
                "passages_used": len(passages),
                "model": openai_result.get("model", openai_model),
                "engine": "openai",
                "timestamp": datetime.utcnow().isoformat(),
            }

            if accessibility_mode:
                response = assistant.get_accessible_response(response)

            user_message = {
                "role": "user",
                "content": query,
                "timestamp": datetime.utcnow().isoformat(),
            }
            assistant_message = {
                "role": "assistant",
                "content": response["answer"],
                "citations": response["citations"],
                "timestamp": datetime.utcnow().isoformat(),
            }
            assistant.record_exchange(user_message, assistant_message)
        else:
            response = assistant.ask(
                query=query,
                retrieve_references=retrieve_references,
                max_passages=max_passages,
                accessibility_mode=accessibility_mode,
            )

        # Add conversation_id to response
        response["conversation_id"] = conversation_id

        # Optionally suggest additional references
        if data.get("suggest_references", False):
            ref_manager = ReferenceManager()
            suggestions = ref_manager.suggest_references(query=query, max_suggestions=3)
            response["suggested_references"] = suggestions

        return jsonify(response), 200

    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        logger.error(f"Error in ask_question: {error_msg}\n{tb}")
        print(f"CHAT ERROR: {error_msg}\n{tb}")  # Also print to console
        return jsonify({"error": "Internal server error", "details": error_msg}), 500


@chat_bp.route("/conversations", methods=["GET"])
@login_required
def list_conversations():
    """
    List user's conversations with search/filter

    Query params:
        - q: Search query
        - date_from: Start date (ISO format)
        - date_to: End date
        - has_citations: Filter by citations (true/false)
        - topics: Comma-separated topic tags
        - limit: Max results (default 50)

    Response:
        {
            "conversations": [
                {
                    "id": 123,
                    "title": "Fourth Amendment analysis",
                    "message_count": 15,
                    "citation_count": 8,
                    "created_at": "2026-01-30T...",
                    "updated_at": "2026-01-30T..."
                }
            ],
            "total": 42
        }
    """
    try:
        memory_store = ConversationMemoryStore()

        # Parse query params
        query = request.args.get("q")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        has_citations = request.args.get("has_citations", "").lower() == "true"
        topics = request.args.get("topics", "").split(",") if request.args.get("topics") else None
        limit = int(request.args.get("limit", 50))

        # Convert dates
        date_from = datetime.fromisoformat(date_from) if date_from else None
        date_to = datetime.fromisoformat(date_to) if date_to else None

        # Search conversations
        conversations = memory_store.search_conversations(
            user_id=current_user.id,
            query=query,
            date_from=date_from,
            date_to=date_to,
            has_citations=has_citations,
            topics=topics,
            limit=limit,
        )

        return jsonify({"conversations": conversations, "total": len(conversations)}), 200

    except Exception as e:
        logger.error(f"Error in list_conversations: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route("/conversation/<int:conversation_id>", methods=["GET"])
@login_required
def get_conversation(conversation_id: int):
    """
    Get conversation with full message history

    Query params:
        - include_messages: Include full messages (default true)
        - include_citations: Include citation details (default true)

    Response:
        {
            "id": 123,
            "title": "Fourth Amendment analysis",
            "messages": [...],
            "citations": [...],
            "referenced_documents": [...],
            "summary": {...}
        }
    """
    try:
        memory_store = ConversationMemoryStore()

        include_messages = request.args.get("include_messages", "true").lower() == "true"

        # Retrieve conversation
        conversation = memory_store.retrieve_conversation(
            conversation_id=conversation_id, include_messages=include_messages
        )

        # Verify ownership
        if conversation.get("user_id") != current_user.id:
            return jsonify({"error": "Forbidden"}), 403

        # Get citation graph if requested
        if request.args.get("include_citation_graph", "false").lower() == "true":
            citation_graph = memory_store.get_citation_graph(conversation_id)
            conversation["citation_graph"] = citation_graph

        return jsonify(conversation), 200

    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route("/conversation/<int:conversation_id>/export", methods=["GET"])
@login_required
def export_conversation(conversation_id: int):
    """
    Export conversation in various formats

    Query params:
        - format: Export format (markdown, json, html) - default markdown
        - include_citations: Include citations (default true)

    Response:
        Content-Type varies by format
    """
    try:
        assistant = EnhancedChatAssistant(user_id=current_user.id)
        assistant.conversation_id = conversation_id

        # TODO: Load conversation from database

        export_format = request.args.get("format", "markdown")
        include_citations = request.args.get("include_citations", "true").lower() == "true"

        exported = assistant.export_conversation(
            format=export_format, include_citations=include_citations
        )

        # Set appropriate content type
        if export_format == "markdown":
            content_type = "text/markdown"
            extension = "md"
        elif export_format == "json":
            content_type = "application/json"
            extension = "json"
        elif export_format == "html":
            content_type = "text/html"
            extension = "html"

        return (
            exported,
            200,
            {
                "Content-Type": content_type,
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.{extension}",
            },
        )

    except Exception as e:
        logger.error(f"Error in export_conversation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route("/references/suggest", methods=["POST"])
@login_required
def suggest_references():
    """
    Get reference suggestions for a query

    Request body:
        {
            "query": "unlawful search and seizure",
            "max_suggestions": 5
        }

    Response:
        {
            "suggestions": [
                {
                    "document_id": 42,
                    "filename": "miranda_v_arizona.pdf",
                    "relevance_score": 0.95,
                    "preview_snippet": "...",
                    "why_relevant": "Contains relevant terms: search, seizure"
                }
            ]
        }
    """
    try:
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Missing required field: query"}), 400

        ref_manager = ReferenceManager()

        suggestions = ref_manager.suggest_references(
            query=data["query"], max_suggestions=data.get("max_suggestions", 5)
        )

        return jsonify({"suggestions": suggestions}), 200

    except Exception as e:
        logger.error(f"Error in suggest_references: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    """
    Get conversation analytics for current user

    Query params:
        - days: Number of days to analyze (default 30)

    Response:
        {
            "total_conversations": 42,
            "total_messages": 350,
            "total_citations": 120,
            "unique_documents_cited": 35,
            "avg_messages_per_conversation": 8.3,
            "most_active_topics": [...],
            "period_start": "2026-01-01T...",
            "period_end": "2026-01-30T..."
        }
    """
    try:
        memory_store = ConversationMemoryStore()

        days = int(request.args.get("days", 30))
        date_from = datetime.utcnow()
        date_from = date_from.replace(day=date_from.day - days)

        analytics = memory_store.get_conversation_analytics(
            user_id=current_user.id, date_from=date_from
        )

        return jsonify(analytics), 200

    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route("/reference/<int:document_id>/context", methods=["GET"])
@login_required
def get_reference_context(document_id: int):
    """
    Get context for a referenced document

    Query params:
        - page: Specific page number (optional)
        - context_pages: Pages before/after (default 2)

    Response:
        {
            "document_id": 42,
            "filename": "motion_to_suppress.pdf",
            "target_page": 5,
            "context_pages": [
                {"page_number": 3, "text": "..."},
                {"page_number": 4, "text": "..."},
                {"page_number": 5, "text": "..."},
                {"page_number": 6, "text": "..."},
                {"page_number": 7, "text": "..."}
            ]
        }
    """
    try:
        ref_manager = ReferenceManager()

        page = int(request.args.get("page")) if request.args.get("page") else None
        context_pages = int(request.args.get("context_pages", 2))

        context = ref_manager.get_reference_context(
            document_id=document_id, page_number=page, context_pages=context_pages
        )

        return jsonify(context), 200

    except Exception as e:
        logger.error(f"Error in get_reference_context: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# Error handlers
@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
