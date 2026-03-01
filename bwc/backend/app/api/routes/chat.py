"""Chat API — grounded Q&A with RAG context + CourtListener."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas import (
    ChatAskRequest,
    ChatAskResponse,
    ChatCitation,
    ChatMessageOut,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.models.evidence_artifact import EvidenceArtifact
from app.services.audit import append_audit_event
from app.services.courtlistener import search_with_cache
from app.services.llm import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/context")
def get_context(
    scope: str = Query("global"),
    case_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
):
    """Return a structured context pack for the given scope."""
    context: dict = {"scope": scope, "rag_context": {}, "case_context": {}}

    # Always include RAG context
    rag_root = Path(settings.suite_root) / "rag_context"
    for fname in ["file_index.json", "repo_tree.txt", "integrity_statement.json"]:
        fpath = rag_root / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                if fname.endswith(".json"):
                    context["rag_context"][fname] = json.loads(content)
                else:
                    context["rag_context"][fname] = content[:5000]
            except Exception as exc:
                logger.warning("Failed to read %s: %s", fpath, exc)

    # Load excerpts
    excerpts_dir = rag_root / "excerpts"
    if excerpts_dir.is_dir():
        excerpts = {}
        for f in sorted(excerpts_dir.iterdir()):
            if f.is_file():
                try:
                    excerpts[f.name] = f.read_text(encoding="utf-8")[:2000]
                except Exception:
                    pass
        context["rag_context"]["excerpts"] = excerpts

    # Case-specific context
    if case_id:
        artifacts = (
            db.query(EvidenceArtifact)
            .filter(EvidenceArtifact.case_id == case_id)
            .all()
        )
        context["case_context"]["artifacts"] = [
            {
                "type": a.artifact_type,
                "evidence_id": str(a.evidence_id),
                "preview": a.content_preview[:1000] if a.content_preview else None,
            }
            for a in artifacts
        ]

    return context


@router.post("/ask", response_model=ChatAskResponse)
def chat_ask(body: ChatAskRequest, db: Session = Depends(get_db)):
    """Process a chat question with grounded context."""
    citations: list[ChatCitation] = []
    context_parts: list[str] = []

    # 1. Build RAG context
    rag_root = Path(settings.suite_root) / "rag_context"
    for fname in ["file_index.json", "integrity_statement.json"]:
        fpath = rag_root / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")[:2000]
                context_parts.append(f"[Internal: {fname}]\n{content}")
                citations.append(ChatCitation(
                    source_type="rag_context",
                    source_id=fname,
                    title=fname,
                    snippet=content[:200],
                    verification_status="verified",
                ))
            except Exception:
                pass

    # 2. Case-scoped artifacts
    if body.case_id:
        artifacts = (
            db.query(EvidenceArtifact)
            .filter(EvidenceArtifact.case_id == body.case_id)
            .all()
        )
        for a in artifacts:
            if a.content_preview:
                preview = a.content_preview[:1500]
                context_parts.append(
                    f"[Evidence artifact: {a.artifact_type} for {a.evidence_id}]\n{preview}"
                )
                citations.append(ChatCitation(
                    source_type="internal",
                    source_id=str(a.id),
                    title=f"{a.artifact_type} for evidence {str(a.evidence_id)[:8]}",
                    snippet=preview[:200],
                    verification_status="verified",
                ))

    # 3. CourtListener search
    cl_result = search_with_cache(db, body.question)
    cl_results = cl_result.get("results", [])
    for item in cl_results[:5]:
        case_name = item.get("caseName", item.get("case_name", "Unknown"))
        snippet = item.get("snippet", "")[:500]
        court_name = item.get("court", "")
        date_filed = item.get("dateFiled", item.get("date_filed", ""))
        cl_id = item.get("id", "")
        cl_url = f"https://www.courtlistener.com/opinion/{cl_id}/"

        context_parts.append(
            f"[CourtListener: {case_name} ({court_name}, {date_filed})]\n{snippet}"
        )
        citations.append(ChatCitation(
            source_type="courtlistener",
            source_id=str(cl_id),
            url=cl_url,
            title=case_name,
            snippet=snippet[:200],
            court=court_name,
            date=date_filed,
            verification_status="needs_verification",
        ))

    # 4. Generate answer
    combined_context = "\n\n".join(context_parts) if context_parts else "No context found."
    llm = get_llm_provider()
    result = llm.generate_answer(body.question, combined_context)

    # Merge LLM-extracted citations
    for c in result.get("citations", []):
        citations.append(ChatCitation(**c))

    verification_status = "needs_verification"
    if all(c.verification_status == "verified" for c in citations) and citations:
        verification_status = "verified"

    # 5. Store messages
    user_msg = ChatMessage(
        scope=body.scope,
        project_id=body.project_id,
        case_id=body.case_id,
        role="user",
        content=body.question,
    )
    db.add(user_msg)

    assistant_msg = ChatMessage(
        scope=body.scope,
        project_id=body.project_id,
        case_id=body.case_id,
        role="assistant",
        content=result["text"],
        citations=[c.model_dump() for c in citations],
        verification_status=verification_status,
    )
    db.add(assistant_msg)

    append_audit_event(
        db,
        case_id=body.case_id,
        event_type="chat.ask",
        payload={
            "question_length": len(body.question),
            "scope": body.scope,
            "citations_count": len(citations),
            "courtlistener_results": len(cl_results),
        },
    )

    db.commit()
    db.refresh(assistant_msg)

    return ChatAskResponse(
        message_id=assistant_msg.id,
        answer=result["text"],
        citations=citations,
        verification_status=verification_status,
    )


@router.get("/history", response_model=list[ChatMessageOut])
def chat_history(
    scope: str = Query("global"),
    case_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve chat history for a given scope."""
    q = db.query(ChatMessage).filter(ChatMessage.scope == scope)
    if case_id:
        q = q.filter(ChatMessage.case_id == case_id)
    if project_id:
        q = q.filter(ChatMessage.project_id == project_id)
    return q.order_by(ChatMessage.created_at.desc()).limit(limit).all()
