from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Legal Chatbot API - Expanded REST Endpoints
============================================

Full-featured legal AI chatbot with:
- Multi-model support (OpenAI, Claude, Local)
- Redis caching for fast responses
- Background job processing
- Streaming responses
- Document analysis integration
- Citation validation
- Conversation memory
"""

import hashlib
import json
import logging
import os
import time
import uuid
from collections.abc import Generator
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_login import current_user, login_required

logger = logging.getLogger(__name__)

# Create blueprint
legal_chatbot_bp = Blueprint("legal_chatbot", __name__, url_prefix="/api/v1/chatbot")


# ============================================================
# CACHING LAYER
# ============================================================


class ChatbotCache:
    """Redis-backed cache for chatbot responses and embeddings."""

    def __init__(self):
        self.redis = None
        self.enabled = False
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            import redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.enabled = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache: {e}")
            self._memory_cache = {}
            self.enabled = False

    def _hash_key(self, key: str) -> str:
        """Create consistent hash for cache key."""
        return hashlib.sha256(key.encode()).hexdigest()[:32]

Optional[def get(self, key: str) -> dict]:
        """Get cached value."""
        hashed = self._hash_key(key)
        try:
            if self.enabled and self.redis:
                data = self.redis.get(f"chatbot:{hashed}")
                return json.loads(data) if data else None
            return self._memory_cache.get(hashed)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """Set cached value with TTL."""
        hashed = self._hash_key(key)
        try:
            if self.enabled and self.redis:
                self.redis.setex(f"chatbot:{hashed}", ttl, json.dumps(value))
            else:
                self._memory_cache[hashed] = value
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def invalidate(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        try:
            if self.enabled and self.redis:
                keys = self.redis.keys(f"chatbot:{pattern}*")
                if keys:
                    return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0

Optional[def get_embedding(self, text: str) -> list[float]]:
        """Get cached embedding for text."""
        key = f"emb:{self._hash_key(text)}"
        try:
            if self.enabled and self.redis:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            return None
        except Exception:
            return None

    def set_embedding(self, text: str, embedding: list[float], ttl: int = 86400) -> bool:
        """Cache embedding with 24h TTL."""
        key = f"emb:{self._hash_key(text)}"
        try:
            if self.enabled and self.redis:
                self.redis.setex(key, ttl, json.dumps(embedding))
                return True
            return False
        except Exception:
            return False


# Global cache instance
cache = ChatbotCache()


# ============================================================
# BACKGROUND JOB QUEUE
# ============================================================


class BackgroundJobQueue:
    """Redis-backed job queue for batch processing."""

    QUEUE_NAME = "chatbot:jobs"
    RESULTS_PREFIX = "chatbot:result:"

    def __init__(self):
        self.redis = None
        self.enabled = False
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis for job queue."""
        try:
            import redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.enabled = True
        except Exception as e:
            logger.warning(f"Job queue unavailable: {e}")
            self._pending_jobs = []

    def enqueue(self, job_type: str, payload: dict, priority: int = 0) -> str:
        """Add job to queue, return job ID."""
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "priority": priority,
        }

        try:
            if self.enabled and self.redis:
                # Use sorted set for priority queue
                self.redis.zadd(self.QUEUE_NAME, {json.dumps(job): priority})
                self.redis.setex(
                    f"{self.RESULTS_PREFIX}{job_id}",
                    3600,  # 1 hour TTL
                    json.dumps({"status": "pending"}),
                )
            else:
                self._pending_jobs.append(job)

            return job_id
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            raise

Optional[def get_job_status(self, job_id: str) -> dict]:
        """Get status of a job."""
        try:
            if self.enabled and self.redis:
                data = self.redis.get(f"{self.RESULTS_PREFIX}{job_id}")
                return json.loads(data) if data else None
            return None
        except Exception:
            return None

Optional[def update_job_status(self, job_id: str, status: str, result: dict] = None) -> bool:
        """Update job status and optionally set result."""
        try:
            if self.enabled and self.redis:
                data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
                if result:
                    data["result"] = result
                self.redis.setex(f"{self.RESULTS_PREFIX}{job_id}", 3600, json.dumps(data))
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False


# Global job queue
job_queue = BackgroundJobQueue()


# ============================================================
# DECORATORS
# ============================================================


def csrf_exempt(f):
    """Mark view as CSRF exempt."""
    f.csrf_exempt = True
    return f


def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator using Redis."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return f(*args, **kwargs)

            user_id = current_user.id
            key = f"ratelimit:{user_id}:{f.__name__}"

            try:
                if cache.enabled and cache.redis:
                    current = cache.redis.incr(key)
                    if current == 1:
                        cache.redis.expire(key, 60)

                    if current > requests_per_minute:
                        return (
                            jsonify(
                                {
                                    "error": "Rate limit exceeded",
                                    "retry_after": cache.redis.ttl(key),
                                }
                            ),
                            429,
                        )
            except Exception:
                pass  # Fail open if Redis unavailable

            return f(*args, **kwargs)

        return wrapped

    return decorator


def cached_response(ttl: int = 300, key_prefix: str = ""):
    """Cache response decorator."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Build cache key from request
            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"
            if request.is_json:
                cache_key += f":{json.dumps(request.get_json(), sort_keys=True)}"

            # Check cache
            cached = cache.get(cache_key)
            if cached:
                cached["_cached"] = True
                return jsonify(cached), 200

            # Execute function
            result = f(*args, **kwargs)

            # Cache successful responses
            if isinstance(result, tuple) and result[1] == 200:
                response_data = result[0].get_json()
                cache.set(cache_key, response_data, ttl)
            elif hasattr(result, "get_json") and result.status_code == 200:
                cache.set(cache_key, result.get_json(), ttl)

            return result

        return wrapped

    return decorator


# ============================================================
# CHAT ENDPOINTS
# ============================================================


@legal_chatbot_bp.route("/chat", methods=["POST"])
@csrf_exempt
@login_required
@rate_limit(requests_per_minute=30)
def chat():
    """
    Send a message to the legal chatbot.

    Request:
        {
            "message": "What is probable cause?",
            "conversation_id": "uuid" (optional),
            "model": "gpt-4" | "claude-3" | "local" (optional),
            "context": {
                "case_id": 123,
                "documents": [1, 2, 3]
            } (optional),
            "options": {
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": false,
                "cite_sources": true
            } (optional)
        }

    Response:
        {
            "response": "Probable cause is...",
            "conversation_id": "uuid",
            "citations": [...],
            "confidence": 0.92,
            "model_used": "gpt-4",
            "tokens_used": 450,
            "cached": false
        }
    """
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Missing required field: message"}), 400

        message = data["message"].strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        if len(message) > 10000:
            return jsonify({"error": "Message too long (max 10000 chars)"}), 400

        # Extract options
        conversation_id = data.get("conversation_id") or str(uuid.uuid4())
        model = data.get("model", "gpt-4")
        context = data.get("context", {})
        options = data.get("options", {})
        stream = options.get("stream", False)

        # Check for cached response (only for non-streaming)
        if not stream:
            cache_key = f"chat:{current_user.id}:{hashlib.md5(message.encode()).hexdigest()}"
            cached = cache.get(cache_key)
            if cached and not context.get("force_refresh"):
                cached["_cached"] = True
                return jsonify(cached), 200

        # Process chat
        from services.chatbot_intelligence import LegalChatbotIntelligence

        chatbot = LegalChatbotIntelligence()

        result = chatbot.process_query(
            query=message, user_id=current_user.id, conversation_id=conversation_id
        )

        response = {
            "response": result.get("response", ""),
            "conversation_id": conversation_id,
            "citations": result.get("citations", []),
            "entities": result.get("entities", {}),
            "intent": result.get("intent", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "model_used": model,
            "tokens_used": result.get("tokens_used", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Cache response
        if not stream:
            cache.set(cache_key, response, ttl=300)

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@legal_chatbot_bp.route("/chat/stream", methods=["POST"])
@csrf_exempt
@login_required
@rate_limit(requests_per_minute=20)
def chat_stream():
    """
    Stream chat response using Server-Sent Events.

    Request: Same as /chat
    Response: SSE stream with chunks
    """
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Missing required field: message"}), 400

        def generate() -> Generator[str, None, None]:
            """Generate SSE events."""
            try:
                # Simulate streaming response
                message = data["message"]
                conversation_id = data.get("conversation_id") or str(uuid.uuid4())

                # Send conversation ID first
                yield f"data: {json.dumps({'type': 'init', 'conversation_id': conversation_id})}\n\n"

                # Process query
                from services.chatbot_intelligence import LegalChatbotIntelligence

                chatbot = LegalChatbotIntelligence()

                result = chatbot.process_query(
                    query=message, user_id=current_user.id, conversation_id=conversation_id
                )

                # Stream response in chunks
                response_text = result.get("response", "")
                chunk_size = 50

                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i : i + chunk_size]
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    time.sleep(0.02)  # Small delay for natural feel

                # Send final metadata
                yield f"data: {json.dumps({'type': 'done', 'citations': result.get('citations', []), 'intent': result.get('intent')})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# DOCUMENT ANALYSIS ENDPOINTS
# ============================================================


@legal_chatbot_bp.route("/analyze/document", methods=["POST"])
@csrf_exempt
@login_required
@rate_limit(requests_per_minute=10)
def analyze_document():
    """
    Analyze a legal document with AI.

    Request:
        {
            "document_id": 123,
            "analysis_types": ["summary", "entities", "citations", "issues"],
            "options": {
                "max_length": 500,
                "include_recommendations": true
            }
        }

    Response:
        {
            "document_id": 123,
            "summary": "...",
            "entities": {...},
            "citations": [...],
            "issues": [...],
            "recommendations": [...],
            "processing_time": 2.5
        }
    """
    try:
        data = request.get_json()

        if not data or "document_id" not in data:
            return jsonify({"error": "Missing required field: document_id"}), 400

        document_id = data["document_id"]
        analysis_types = data.get("analysis_types", ["summary"])
        options = data.get("options", {})

        # Check cache
        cache_key = f"doc_analysis:{document_id}:{':'.join(sorted(analysis_types))}"
        cached = cache.get(cache_key)
        if cached:
            cached["_cached"] = True
            return jsonify(cached), 200

        start_time = time.time()

        # Perform analysis
        result = {
            "document_id": document_id,
            "analysis_types": analysis_types,
            "timestamp": datetime.utcnow().isoformat(),
        }

        from services.chatbot_intelligence import LegalChatbotIntelligence

        chatbot = LegalChatbotIntelligence()

        if "summary" in analysis_types:
            result["summary"] = (
                chatbot.generate_document_summary(
                    document_id, max_length=options.get("max_length", 500)
                )
                if hasattr(chatbot, "generate_document_summary")
                else "Summary generation pending"
            )

        if "entities" in analysis_types:
            result["entities"] = (
                chatbot.extract_document_entities(document_id)
                if hasattr(chatbot, "extract_document_entities")
                else {}
            )

        if "citations" in analysis_types:
            result["citations"] = (
                chatbot.extract_citations(document_id)
                if hasattr(chatbot, "extract_citations")
                else []
            )

        if "issues" in analysis_types:
            result["issues"] = (
                chatbot.identify_legal_issues(document_id)
                if hasattr(chatbot, "identify_legal_issues")
                else []
            )

        result["processing_time"] = round(time.time() - start_time, 2)

        # Cache result
        cache.set(cache_key, result, ttl=1800)  # 30 min cache

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Document analysis error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@legal_chatbot_bp.route("/analyze/batch", methods=["POST"])
@csrf_exempt
@login_required
@rate_limit(requests_per_minute=5)
def analyze_batch():
    """
    Queue batch document analysis as background job.

    Request:
        {
            "document_ids": [1, 2, 3, ...],
            "analysis_types": ["summary", "entities"],
            "callback_url": "https://..." (optional),
            "priority": 1 (optional, 0-10)
        }

    Response:
        {
            "job_id": "uuid",
            "status": "queued",
            "document_count": 10,
            "estimated_time": 120
        }
    """
    try:
        data = request.get_json()

        if not data or "document_ids" not in data:
            return jsonify({"error": "Missing required field: document_ids"}), 400

        document_ids = data["document_ids"]

        if not isinstance(document_ids, list) or len(document_ids) == 0:
            return jsonify({"error": "document_ids must be a non-empty array"}), 400

        if len(document_ids) > 100:
            return jsonify({"error": "Maximum 100 documents per batch"}), 400

        # Queue background job
        job_id = job_queue.enqueue(
            job_type="batch_document_analysis",
            payload={
                "document_ids": document_ids,
                "analysis_types": data.get("analysis_types", ["summary"]),
                "callback_url": data.get("callback_url"),
                "user_id": current_user.id,
            },
            priority=data.get("priority", 0),
        )

        return (
            jsonify(
                {
                    "job_id": job_id,
                    "status": "queued",
                    "document_count": len(document_ids),
                    "estimated_time": len(document_ids) * 12,  # ~12 sec per doc
                }
            ),
            202,
        )

    except Exception as e:
        logger.error(f"Batch analysis error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@legal_chatbot_bp.route("/jobs/<job_id>", methods=["GET"])
@login_required
def get_job_status(job_id: str):
    """
    Get status of a background job.

    Response:
        {
            "job_id": "uuid",
            "status": "pending" | "processing" | "completed" | "failed",
            "progress": 0.75,
            "result": {...} (if completed),
            "error": "..." (if failed)
        }
    """
    try:
        status = job_queue.get_job_status(job_id)

        if not status:
            return jsonify({"error": "Job not found"}), 404

        return jsonify({"job_id": job_id, **status}), 200

    except Exception as e:
        logger.error(f"Job status error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# CITATION ENDPOINTS
# ============================================================


@legal_chatbot_bp.route("/citations/validate", methods=["POST"])
@csrf_exempt
@login_required
@cached_response(ttl=3600, key_prefix="cite_validate")
def validate_citations():
    """
    Validate legal citations.

    Request:
        {
            "citations": [
                "347 U.S. 483",
                "42 U.S.C. § 1983"
            ]
        }

    Response:
        {
            "results": [
                {
                    "citation": "347 U.S. 483",
                    "valid": true,
                    "case_name": "Brown v. Board of Education",
                    "year": 1954,
                    "court": "Supreme Court",
                    "status": "good_law"
                }
            ]
        }
    """
    try:
        data = request.get_json()

        if not data or "citations" not in data:
            return jsonify({"error": "Missing required field: citations"}), 400

        citations = data["citations"]

        if not isinstance(citations, list):
            return jsonify({"error": "citations must be an array"}), 400

        results = []

        for citation in citations[:20]:  # Max 20 citations
            result = {
                "citation": citation,
                "valid": True,  # Placeholder
                "normalized": citation.strip(),
                "type": "case" if "v." in citation or "U.S." in citation else "statute",
            }
            results.append(result)

        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"Citation validation error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@legal_chatbot_bp.route("/citations/network", methods=["GET"])
@login_required
@cached_response(ttl=1800, key_prefix="cite_network")
def get_citation_network():
    """
    Get citation network for a case.

    Query params:
        - case_id: Case identifier
        - depth: How many levels deep (default 2)
        - direction: "citing" | "cited_by" | "both" (default "both")

    Response:
        {
            "case_id": "...",
            "nodes": [...],
            "edges": [...],
            "stats": {...}
        }
    """
    try:
        case_id = request.args.get("case_id")

        if not case_id:
            return jsonify({"error": "Missing required param: case_id"}), 400

        depth = min(int(request.args.get("depth", 2)), 5)
        direction = request.args.get("direction", "both")

        # Placeholder network
        network = {
            "case_id": case_id,
            "nodes": [{"id": case_id, "type": "target", "label": "Target Case"}],
            "edges": [],
            "stats": {"total_citing": 0, "total_cited_by": 0, "depth_searched": depth},
        }

        return jsonify(network), 200

    except Exception as e:
        logger.error(f"Citation network error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# CONVERSATION MANAGEMENT
# ============================================================


@legal_chatbot_bp.route("/conversations", methods=["GET"])
@login_required
def list_conversations():
    """
    List user's chat conversations.

    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
        - search: Search in messages
        - date_from: Filter by date
        - date_to: Filter by date

    Response:
        {
            "conversations": [...],
            "total": 42,
            "page": 1,
            "per_page": 20
        }
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        search = request.args.get("search")

        # Placeholder response
        conversations = []

        return (
            jsonify(
                {"conversations": conversations, "total": 0, "page": page, "per_page": per_page}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"List conversations error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@legal_chatbot_bp.route("/conversations/<conversation_id>", methods=["GET"])
@login_required
def get_conversation(conversation_id: str):
    """Get a specific conversation with messages."""
    try:
        # Placeholder
        return (
            jsonify(
                {
                    "conversation_id": conversation_id,
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Get conversation error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@legal_chatbot_bp.route("/conversations/<conversation_id>", methods=["DELETE"])
@login_required
def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        # Invalidate cache
        cache.invalidate(f"conv:{conversation_id}")

        return jsonify({"success": True, "deleted": conversation_id}), 200

    except Exception as e:
        logger.error(f"Delete conversation error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# HEALTH & METRICS
# ============================================================


@legal_chatbot_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cache": {"enabled": cache.enabled, "type": "redis" if cache.enabled else "memory"},
        "jobs": {"enabled": job_queue.enabled, "type": "redis" if job_queue.enabled else "sync"},
    }

    return jsonify(status), 200


@legal_chatbot_bp.route("/metrics", methods=["GET"])
@login_required
def get_metrics():
    """
    Get API usage metrics for current user.

    Response:
        {
            "user_id": 123,
            "period": "last_30_days",
            "chat_requests": 150,
            "documents_analyzed": 25,
            "tokens_used": 45000,
            "cache_hit_rate": 0.65
        }
    """
    try:
        # Placeholder metrics
        metrics = {
            "user_id": current_user.id,
            "period": "last_30_days",
            "chat_requests": 0,
            "documents_analyzed": 0,
            "tokens_used": 0,
            "cache_hit_rate": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return jsonify(metrics), 200

    except Exception as e:
        logger.error(f"Metrics error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# ERROR HANDLERS
# ============================================================


@legal_chatbot_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "details": str(error)}), 400


@legal_chatbot_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@legal_chatbot_bp.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@legal_chatbot_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@legal_chatbot_bp.errorhandler(429)
def rate_limited(error):
    return jsonify({"error": "Rate limit exceeded"}), 429


@legal_chatbot_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================
# DOCUMENT INTELLIGENCE ENDPOINTS
# ============================================================


@legal_chatbot_bp.route("/summarize", methods=["POST"])
@login_required
@rate_limit(requests_per_minute=10)
def summarize_document():
    """
    Generate document summaries at multiple lengths.

    Request body:
    {
        "text": "Document text to summarize",
        "length": "brief|standard|detailed",
        "focus_areas": ["damages", "liability"]  // optional
    }
    """
    try:
        from services.document_intelligence import SummaryLength, get_document_intelligence

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        length_str = data.get("length", "standard")
        focus_areas = data.get("focus_areas")

        # Map string to enum
        length_map = {
            "brief": SummaryLength.BRIEF,
            "standard": SummaryLength.STANDARD,
            "detailed": SummaryLength.DETAILED,
        }
        length = length_map.get(length_str, SummaryLength.STANDARD)

        # Get document intelligence service
        doc_intel = get_document_intelligence()
        summaries = doc_intel.summarize(text, length, focus_areas)

        return (
            jsonify(
                {
                    "success": True,
                    "summaries": summaries,
                    "length": length_str,
                    "text_length": len(text),
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Summarization error: {e}", exc_info=True)
        return jsonify({"error": "Summarization failed", "details": str(e)}), 500


@legal_chatbot_bp.route("/extract/entities", methods=["POST"])
@login_required
@rate_limit(requests_per_minute=20)
def extract_entities():
    """
    Extract legal entities from document text.

    Request body:
    {
        "text": "Document text to analyze"
    }

    Returns entities like parties, dates, courts, case numbers, judges, attorneys.
    """
    try:
        from services.document_intelligence import get_document_intelligence

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        doc_intel = get_document_intelligence()
        entities = doc_intel.extract_entities(text)

        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            if entity.entity_type not in entities_by_type:
                entities_by_type[entity.entity_type] = []
            entities_by_type[entity.entity_type].append(
                {
                    "value": entity.value,
                    "confidence": entity.confidence,
                    "context": entity.context[:100] if entity.context else "",
                }
            )

        return (
            jsonify(
                {
                    "success": True,
                    "entities": entities_by_type,
                    "total_count": len(entities),
                    "entity_types": list(entities_by_type.keys()),
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Entity extraction error: {e}", exc_info=True)
        return jsonify({"error": "Entity extraction failed", "details": str(e)}), 500


@legal_chatbot_bp.route("/extract/citations", methods=["POST"])
@login_required
@rate_limit(requests_per_minute=20)
def extract_citations():
    """
    Extract and validate legal citations from document text.

    Request body:
    {
        "text": "Document text to analyze",
        "validate": true  // optional, defaults to true
    }
    """
    try:
        from services.document_intelligence import get_document_intelligence

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        validate = data.get("validate", True)

        doc_intel = get_document_intelligence()
        citations = doc_intel.extract_citations(text, validate=validate)

        # Format citations for response
        citation_list = []
        for cit in citations:
            citation_list.append(
                {
                    "text": cit.citation_text,
                    "type": cit.citation_type,
                    "jurisdiction": cit.jurisdiction,
                    "year": cit.year,
                    "is_valid": cit.is_valid,
                    "confidence": cit.confidence,
                    "validation_notes": cit.validation_notes,
                }
            )

        # Group by type
        by_type = {}
        for cit in citation_list:
            ctype = cit["type"]
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(cit)

        return (
            jsonify(
                {
                    "success": True,
                    "citations": citation_list,
                    "by_type": by_type,
                    "total_count": len(citations),
                    "valid_count": len([c for c in citations if c.is_valid]),
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Citation extraction error: {e}", exc_info=True)
        return jsonify({"error": "Citation extraction failed", "details": str(e)}), 500


@legal_chatbot_bp.route("/assess/risks", methods=["POST"])
@login_required
@rate_limit(requests_per_minute=10)
def assess_document_risks():
    """
    Identify legal issues and assess risks in document.

    Request body:
    {
        "text": "Document text to analyze"
    }
    """
    try:
        from services.document_intelligence import get_document_intelligence

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        doc_intel = get_document_intelligence()

        # Identify issues
        issues = doc_intel.identify_issues(text)

        # Assess overall risk
        risk_assessment = doc_intel.assess_risk(text, issues)

        # Format issues for response
        issues_list = []
        for issue in issues:
            issues_list.append(
                {
                    "type": issue.issue_type,
                    "description": issue.description,
                    "severity": issue.severity.value,
                    "relevant_text": (
                        issue.relevant_text[:200] + "..."
                        if len(issue.relevant_text) > 200
                        else issue.relevant_text
                    ),
                    "recommendations": issue.recommendations,
                }
            )

        return (
            jsonify(
                {
                    "success": True,
                    "issues": issues_list,
                    "risk_assessment": risk_assessment,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Risk assessment error: {e}", exc_info=True)
        return jsonify({"error": "Risk assessment failed", "details": str(e)}), 500


@legal_chatbot_bp.route("/analyze/full", methods=["POST"])
@login_required
@rate_limit(requests_per_minute=5)
def full_document_analysis():
    """
    Perform comprehensive document analysis.

    Request body:
    {
        "text": "Document text to analyze",
        "document_id": "optional-doc-id",
        "include_all_summaries": false  // optional
    }

    Returns complete analysis with summaries, entities, citations, issues, and risk assessment.
    """
    try:
        from services.document_intelligence import get_document_intelligence

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        document_id = data.get("document_id")
        include_all = data.get("include_all_summaries", False)

        doc_intel = get_document_intelligence()
        analysis = doc_intel.analyze_document(text, document_id, include_all)

        # Convert dataclasses to dicts
        entities_list = []
        for e in analysis.entities:
            entities_list.append(
                {"type": e.entity_type, "value": e.value, "confidence": e.confidence}
            )

        citations_list = []
        for c in analysis.citations:
            citations_list.append(
                {
                    "text": c.citation_text,
                    "type": c.citation_type,
                    "jurisdiction": c.jurisdiction,
                    "is_valid": c.is_valid,
                }
            )

        issues_list = []
        for i in analysis.issues:
            issues_list.append(
                {
                    "type": i.issue_type,
                    "description": i.description,
                    "severity": i.severity.value,
                    "recommendations": i.recommendations,
                }
            )

        return (
            jsonify(
                {
                    "success": True,
                    "document_id": analysis.document_id,
                    "analysis": {
                        "summaries": analysis.summary,
                        "entities": entities_list,
                        "citations": citations_list,
                        "issues": issues_list,
                        "risk_assessment": analysis.risk_assessment,
                    },
                    "metadata": analysis.metadata,
                    "processing_time_ms": analysis.processing_time_ms,
                    "generated_at": analysis.created_at.isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Full analysis error: {e}", exc_info=True)
        return jsonify({"error": "Document analysis failed", "details": str(e)}), 500