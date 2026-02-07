# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Municipal Code API endpoints for Evident
Provides REST API access to Code360 municipal ordinance retrieval

Copyright (C) 2026 Evident.info - All Rights Reserved
CONFIDENTIAL AND PROPRIETARY
"""

from Evident_reasoning_core import MunicipalCodeIntegration
from flask import Blueprint, jsonify, request
from tier_gating import check_tier_access, require_auth

# Create blueprint
municipal_bp = Blueprint("municipal", __name__, url_prefix="/api/v1/municipal")

# Initialize integration
municipal_integration = MunicipalCodeIntegration()


@municipal_bp.route("/search", methods=["POST"])
@require_auth
@check_tier_access(min_tier="pro")
def search_ordinances():
    """
    Search for municipal ordinances

    POST /api/v1/municipal/search

    Body:
    {
        "municipality": "Newark",
        "state": "NJ",
        "chapter": "2",  // optional
        "section": "45", // optional
        "keywords": ["police", "use of force"]  // optional
    }

    Returns:
    {
        "success": true,
        "count": 1,
        "ordinances": [
            {
                "id": "uuid",
                "title": "Police Department Organization",
                "chapter": "2",
                "section": "45",
                "text": "Full ordinance text...",
                "source_url": "https://ecode360.com/...",
                "retrieved_at": "2026-01-30T00:00:00"
            }
        ],
        "audit_trail": ["..."]
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    municipality = data.get("municipality")
    if not municipality:
        return jsonify({"error": "municipality is required"}), 400

    # Retrieve ordinances
    result = municipal_integration.get_ordinance_on_demand(
        municipality=municipality,
        state=data.get("state", "NJ"),
        chapter=data.get("chapter"),
        section=data.get("section"),
        keywords=data.get("keywords"),
    )

    # Format response
    ordinances = []
    for ordinance in result.findings:
        ordinances.append(
            {
                "id": str(ordinance.ordinance_id),
                "title": ordinance.title,
                "chapter": ordinance.chapter,
                "section": ordinance.section,
                "text": ordinance.full_text,
                "jurisdiction": {
                    "name": ordinance.jurisdiction.municipality_name,
                    "state": ordinance.jurisdiction.state,
                    "type": ordinance.jurisdiction.municipality_type,
                    "population": ordinance.jurisdiction.population,
                },
                "effective_date": (
                    ordinance.effective_date.isoformat() if ordinance.effective_date else None
                ),
                "source_url": ordinance.source_url,
                "retrieved_at": ordinance.retrieved_at.isoformat(),
            }
        )

    return jsonify(
        {
            "success": result.success,
            "count": len(ordinances),
            "ordinances": ordinances,
            "warnings": result.warnings,
            "errors": result.errors,
            "audit_trail": result.audit_trail,
        }
    )


@municipal_bp.route("/cite", methods=["POST"])
@require_auth
def validate_citation():
    """
    Validate and parse a municipal code citation

    POST /api/v1/municipal/cite

    Body:
    {
        "citation": "Newark Code § 2-45.3"
    }

    Returns:
    {
        "success": true,
        "parsed": {
            "municipality": "Newark",
            "chapter": "2",
            "section": "45.3"
        },
        "ordinance": {...}  // if found
    }
    """
    data = request.get_json()

    if not data or not data.get("citation"):
        return jsonify({"error": "citation is required"}), 400

    citation = data["citation"]

    # Validate citation
    result = municipal_integration.database.validate_ordinance_citation(citation)

    return jsonify(
        {
            "success": result.success,
            "findings": result.findings,
            "warnings": result.warnings,
            "errors": result.errors,
            "audit_trail": result.audit_trail,
        }
    )


@municipal_bp.route("/jurisdictions", methods=["GET"])
@require_auth
def list_jurisdictions():
    """
    List available municipalities

    GET /api/v1/municipal/jurisdictions?state=NJ

    Returns:
    {
        "count": 15,
        "jurisdictions": [
            {
                "id": "uuid",
                "state": "NJ",
                "municipality": "Newark",
                "type": "city",
                "population": 311549,
                "code360_available": true,
                "code360_url": "https://ecode360.com/NE1540"
            }
        ]
    }
    """
    state = request.args.get("state")

    jurisdictions = municipal_integration.list_available_municipalities(state=state)

    return jsonify({"count": len(jurisdictions), "jurisdictions": jurisdictions})


@municipal_bp.route("/topic", methods=["POST"])
@require_auth
@check_tier_access(min_tier="pro")
def search_by_topic():
    """
    Search ordinances by topic across jurisdictions

    POST /api/v1/municipal/topic

    Body:
    {
        "topic": "zoning",
        "state": "NJ",  // optional
        "municipality": "Newark"  // optional
    }

    Returns:
    {
        "success": true,
        "count": 5,
        "ordinances": [...]
    }
    """
    data = request.get_json()

    if not data or not data.get("topic"):
        return jsonify({"error": "topic is required"}), 400

    result = municipal_integration.search_by_topic(
        topic=data["topic"], state=data.get("state"), municipality=data.get("municipality")
    )

    # Format ordinances
    ordinances = []
    for ordinance in result.findings:
        ordinances.append(
            {
                "id": str(ordinance.ordinance_id),
                "title": ordinance.title,
                "chapter": ordinance.chapter,
                "section": ordinance.section,
                "text": ordinance.full_text,
                "jurisdiction": ordinance.jurisdiction.municipality_name,
                "source_url": ordinance.source_url,
            }
        )

    return jsonify(
        {
            "success": result.success,
            "count": len(ordinances),
            "ordinances": ordinances,
            "audit_trail": result.audit_trail,
        }
    )
