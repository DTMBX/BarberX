# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
API endpoints for Legal Reference Library

Provides endpoints for:
- Searching case law and statutes
- Uploading legal documents
- Web scraping from legal databases
- Citation parsing and linking
- Annotations and notes
- Integration with AI tools
"""

import os
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user, login_required
from legal_library import (
    Citation,
    CitationParser,
    DocumentAnnotation,
    LegalDocument,
    LegalLibraryService,
    LegalTopic,
)
from models_auth import db

bp = Blueprint("legal_library", __name__, url_prefix="/api/legal-library")

# Initialize service
library_service = LegalLibraryService()


@bp.route("/search", methods=["GET"])
@login_required
def search_library():
    """
    Search legal library

    Query params:
    - q: search query
    - doc_type: filter by document type
    - court: filter by court
    - jurisdiction: filter by jurisdiction
    - date_from: filter by date (YYYY-MM-DD)
    - date_to: filter by date (YYYY-MM-DD)
    - limit: max results (default 50)

    Returns:
    {
        "success": true,
        "results": [
            {
                "id": 1,
                "title": "Miranda v. Arizona",
                "citation": "384 U.S. 436 (1966)",
                "court": "U.S. Supreme Court",
                "summary": "...",
                "topics": ["5th Amendment", "Miranda Rights"],
                "url": "https://..."
            },
            ...
        ],
        "count": 25
    }
    """

    try:
        query = request.args.get("q", "")
        doc_type = request.args.get("doc_type")
        court = request.args.get("court")
        jurisdiction = request.args.get("jurisdiction")
        limit = int(request.args.get("limit", 50))

        # Parse dates
        date_from = None
        date_to = None
        if request.args.get("date_from"):
            date_from = datetime.fromisoformat(request.args.get("date_from"))
        if request.args.get("date_to"):
            date_to = datetime.fromisoformat(request.args.get("date_to"))

        # Search
        results = library_service.search_library(
            query=query,
            doc_type=doc_type,
            court=court,
            jurisdiction=jurisdiction,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )

        # Format results
        formatted_results = []
        for doc in results:
            formatted_results.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "citation": doc.citation,
                    "court": doc.court,
                    "jurisdiction": doc.jurisdiction,
                    "decision_date": doc.decision_date.isoformat() if doc.decision_date else None,
                    "summary": doc.summary,
                    "topics": json.loads(doc.topics) if doc.topics else [],
                    "legal_issues": json.loads(doc.legal_issues) if doc.legal_issues else [],
                    "url": doc.url,
                }
            )

        return jsonify(
            {"success": True, "results": formatted_results, "count": len(formatted_results)}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/document/<int:doc_id>", methods=["GET"])
@login_required
def get_document(doc_id):
    """
    Get full document by ID

    Returns:
    {
        "success": true,
        "document": {
            "id": 1,
            "title": "...",
            "citation": "...",
            "full_text": "...",
            "summary": "...",
            "topics": [...],
            "legal_issues": [...],
            "citations_made": [...],  # Cases cited by this case
            "citations_received": [...],  # Cases citing this case
            "annotations": [...]  # User annotations
        }
    }
    """

    try:
        doc = LegalDocument.query.get(doc_id)

        if not doc:
            return jsonify({"success": False, "error": "Document not found"}), 404

        # Check access permissions
        if not doc.public and doc.user_id != current_user.id:
            return jsonify({"success": False, "error": "Access denied"}), 403

        # Get citations made by this document
        citations_made = []
        for citation in doc.citations_made:
            cited = citation.cited_document
            citations_made.append(
                {
                    "id": cited.id,
                    "citation": cited.citation,
                    "title": cited.title,
                    "context": citation.context,
                }
            )

        # Get citations to this document
        citations_received = []
        for citation in doc.citations_received:
            citing = citation.citing_document
            citations_received.append(
                {
                    "id": citing.id,
                    "citation": citing.citation,
                    "title": citing.title,
                    "context": citation.context,
                }
            )

        # Get user's annotations
        annotations = []
        for annot in doc.annotations:
            if annot.user_id == current_user.id:
                annotations.append(
                    {
                        "id": annot.id,
                        "text_selection": annot.text_selection,
                        "annotation": annot.annotation,
                        "tags": annot.tags.split(", ") if annot.tags else [],
                        "created_at": annot.created_at.isoformat(),
                    }
                )

        return jsonify(
            {
                "success": True,
                "document": {
                    "id": doc.id,
                    "title": doc.title,
                    "citation": doc.citation,
                    "doc_type": doc.doc_type,
                    "court": doc.court,
                    "jurisdiction": doc.jurisdiction,
                    "decision_date": doc.decision_date.isoformat() if doc.decision_date else None,
                    "full_text": doc.full_text,
                    "summary": doc.summary,
                    "topics": json.loads(doc.topics) if doc.topics else [],
                    "legal_issues": json.loads(doc.legal_issues) if doc.legal_issues else [],
                    "judges": doc.judges,
                    "case_number": doc.case_number,
                    "url": doc.url,
                    "citations_made": citations_made,
                    "citations_received": citations_received,
                    "annotations": annotations,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/upload", methods=["POST"])
@login_required
def upload_document():
    """
    Upload legal document (PDF, TXT, DOCX)

    Form data:
    - file: document file
    - title: document title
    - doc_type: 'case', 'statute', 'article', etc.
    - citation: optional citation
    - court: optional court name
    - jurisdiction: optional jurisdiction
    - decision_date: optional date (YYYY-MM-DD)
    - summary: optional summary
    - public: true/false (default false)
    - case_id: optional case association

    Returns:
    {
        "success": true,
        "document_id": 123,
        "message": "Document uploaded successfully"
    }
    """

    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        title = request.form.get("title")
        doc_type = request.form.get("doc_type", "user_upload")

        if not title:
            return jsonify({"success": False, "error": "Title is required"}), 400

        # Save file
        upload_dir = "uploads/legal_library"
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Prepare metadata
        metadata = {
            "citation": request.form.get("citation"),
            "court": request.form.get("court"),
            "jurisdiction": request.form.get("jurisdiction"),
            "summary": request.form.get("summary"),
            "public": request.form.get("public", "false").lower() == "true",
        }

        if request.form.get("decision_date"):
            metadata["decision_date"] = datetime.fromisoformat(request.form.get("decision_date"))

        case_id = request.form.get("case_id")

        # Ingest document
        doc = library_service.ingest_from_file(
            file_path=file_path,
            title=title,
            doc_type=doc_type,
            user_id=current_user.id,
            case_id=int(case_id) if case_id else None,
            metadata=metadata,
        )

        if not doc:
            return jsonify({"success": False, "error": "Failed to process document"}), 500

        return jsonify(
            {"success": True, "document_id": doc.id, "message": "Document uploaded successfully"}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/import-from-web", methods=["POST"])
@login_required
def import_from_web():
    """
    Import case from web sources (CourtListener, Justia, etc.)

    JSON body:
    {
        "citation": "384 U.S. 436",
        "source": "courtlistener"  # or "justia"
    }

    Returns:
    {
        "success": true,
        "document_id": 123,
        "message": "Case imported successfully"
    }
    """

    try:
        data = request.get_json()
        citation = data.get("citation")
        source = data.get("source", "courtlistener")

        if not citation:
            return jsonify({"success": False, "error": "Citation is required"}), 400

        # Check if already exists
        existing = LegalDocument.query.filter_by(citation=citation).first()
        if existing:
            return jsonify(
                {
                    "success": True,
                    "document_id": existing.id,
                    "message": "Document already in library",
                }
            )

        # Import from source
        if source == "courtlistener":
            doc = library_service.ingest_from_courtlistener(citation)
        else:
            return jsonify({"success": False, "error": f'Source "{source}" not supported'}), 400

        if not doc:
            return (
                jsonify({"success": False, "error": "Failed to import document from source"}),
                500,
            )

        return jsonify(
            {"success": True, "document_id": doc.id, "message": "Case imported successfully"}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/web-search", methods=["GET"])
@login_required
def web_search():
    """
    Search web for cases (Justia, Google Scholar)

    Query params:
    - q: search query
    - source: 'justia' or 'scholar' (default 'justia')

    Returns:
    {
        "success": true,
        "results": [
            {
                "title": "Miranda v. Arizona",
                "url": "https://...",
                "snippet": "..."
            },
            ...
        ]
    }
    """

    try:
        query = request.args.get("q", "")
        source = request.args.get("source", "justia")

        results = library_service.search_web_for_case(query, source)

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/annotate", methods=["POST"])
@login_required
def add_annotation():
    """
    Add annotation to document

    JSON body:
    {
        "document_id": 123,
        "text_selection": "The right to remain silent...",
        "annotation": "Key holding for Miranda rights",
        "tags": ["miranda", "5th-amendment"]
    }

    Returns:
    {
        "success": true,
        "annotation_id": 456
    }
    """

    try:
        data = request.get_json()

        annot = library_service.annotate_document(
            doc_id=data["document_id"],
            user_id=current_user.id,
            text_selection=data["text_selection"],
            annotation=data["annotation"],
            tags=data.get("tags", []),
        )

        return jsonify({"success": True, "annotation_id": annot.id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/related/<int:doc_id>", methods=["GET"])
@login_required
def get_related_cases(doc_id):
    """
    Get related cases based on topics, citations, etc.

    Returns:
    {
        "success": true,
        "related_cases": [
            {
                "id": 2,
                "title": "Terry v. Ohio",
                "citation": "392 U.S. 1 (1968)",
                "relevance_reason": "Similar topics: 4th Amendment, Search and Seizure"
            },
            ...
        ]
    }
    """

    try:
        related = library_service.get_related_cases(doc_id, limit=10)

        results = []
        for doc in related:
            results.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "citation": doc.citation,
                    "court": doc.court,
                    "topics": json.loads(doc.topics) if doc.topics else [],
                    "summary": doc.summary,
                }
            )

        return jsonify({"success": True, "related_cases": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/parse-citation", methods=["POST"])
def parse_citation():
    """
    Parse and validate citation

    JSON body:
    {
        "citation": "Brown v. Board of Education, 347 U.S. 483 (1954)"
    }

    Returns:
    {
        "success": true,
        "parsed": {
            "case_name": "Brown v. Board of Education",
            "volume": "347",
            "reporter": "U.S.",
            "page": "483",
            "year": "1954",
            "full_citation": "347 U.S. 483 (1954)"
        },
        "valid": true
    }
    """

    try:
        data = request.get_json()
        citation = data.get("citation", "")

        parsed = CitationParser.parse(citation)
        valid = CitationParser.is_valid(citation)

        return jsonify({"success": True, "parsed": parsed, "valid": valid})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/topics", methods=["GET"])
def get_topics():
    """
    Get list of legal topics

    Returns:
    {
        "success": true,
        "topics": [
            {"id": 1, "name": "4th Amendment", "description": "..."},
            {"id": 2, "name": "Civil Rights", "description": "..."},
            ...
        ]
    }
    """

    try:
        topics = LegalTopic.query.all()

        results = []
        for topic in topics:
            results.append(
                {
                    "id": topic.id,
                    "name": topic.name,
                    "description": topic.description,
                    "parent_id": topic.parent_id,
                }
            )

        return jsonify({"success": True, "topics": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Import json module
import json
