# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Legal Trinity API Endpoints
Unified search across LOCAL, STATE, and FEDERAL law

Endpoints:
- POST /api/v1/trinity/search - Search all government levels
- POST /api/v1/trinity/municipality - Add a municipality
- GET  /api/v1/trinity/municipalities - List integrated municipalities
- POST /api/v1/trinity/sync/<id> - Sync municipality codes
- POST /api/v1/trinity/analyze - Analyze evidence against all applicable law
- GET  /api/v1/trinity/jurisdictions - Get available jurisdictions info
"""

import logging

from flask import Blueprint, jsonify, request

from auth_routes import login_required, tier_required
from models_auth import TierLevel

logger = logging.getLogger(__name__)

# Blueprint
trinity_api = Blueprint("trinity_api", __name__, url_prefix="/api/v1/trinity")


def get_trinity_service():
    """Lazy import to avoid circular dependencies"""
    from legal_trinity_service import LegalTrinityService

    return LegalTrinityService()


def get_code360_client():
    """Lazy import"""
    from code360_client import Code360Client

    return Code360Client()


# ═══════════════════════════════════════════════════════════════════════════
# SEARCH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


@trinity_api.route("/search", methods=["POST"])
@login_required
def trinity_search():
    """
    Search across all levels of government law

    POST /api/v1/trinity/search
    Body: {
        "query": "excessive force",
        "state": "NJ",
        "municipality": "Newark",
        "county": "Essex",
        "levels": ["federal", "state", "local"],  // optional filter
        "limit": 15  // per level
    }

    Returns: {
        "query": "excessive force",
        "jurisdiction_filter": "Newark, Essex County, NJ",
        "total_results": 45,
        "federal": { "count": 15, "results": [...] },
        "state": { "count": 15, "results": [...] },
        "local": { "count": 15, "results": [...] },
        "hierarchy_notes": [...],
        "top_authorities": [...]
    }
    """
    data = request.get_json() or {}

    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    state = data.get("state")
    municipality = data.get("municipality")
    county = data.get("county")
    levels = data.get("levels")  # Will be converted to enum
    limit = min(data.get("limit", 15), 50)  # Cap at 50

    # Convert level strings to enums
    level_enums = None
    if levels:
        from legal_trinity_service import JurisdictionLevel

        level_map = {
            "federal": JurisdictionLevel.FEDERAL,
            "state": JurisdictionLevel.STATE,
            "local": JurisdictionLevel.LOCAL,
        }
        level_enums = [level_map[l.lower()] for l in levels if l.lower() in level_map]

    try:
        service = get_trinity_service()
        result = service.search(
            query=query,
            state=state,
            municipality=municipality,
            county=county,
            levels=level_enums,
            limit_per_level=limit,
        )

        return jsonify(result.to_dict()), 200

    except Exception as e:
        logger.error(f"Trinity search error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/search/federal", methods=["POST"])
@login_required
def search_federal():
    """
    Search federal law only (USC, CFR, Federal Rules)

    POST /api/v1/trinity/search/federal
    Body: {"query": "search and seizure", "limit": 20}
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    limit = min(data.get("limit", 20), 50)

    try:
        from legal_trinity_service import JurisdictionLevel

        service = get_trinity_service()
        result = service.search(
            query=query, levels=[JurisdictionLevel.FEDERAL], limit_per_level=limit
        )

        return (
            jsonify(
                {
                    "query": query,
                    "count": len(result.federal_results),
                    "results": result.to_dict()["federal"]["results"],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Federal search error: {e}")
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/search/state/<state_code>", methods=["POST"])
@login_required
def search_state(state_code: str):
    """
    Search state law only

    POST /api/v1/trinity/search/state/NJ
    Body: {"query": "use of force", "limit": 20}
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    limit = min(data.get("limit", 20), 50)

    try:
        from legal_trinity_service import JurisdictionLevel

        service = get_trinity_service()
        result = service.search(
            query=query,
            state=state_code.upper(),
            levels=[JurisdictionLevel.STATE],
            limit_per_level=limit,
        )

        return (
            jsonify(
                {
                    "query": query,
                    "state": state_code.upper(),
                    "count": len(result.state_results),
                    "results": result.to_dict()["state"]["results"],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"State search error: {e}")
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/search/local", methods=["POST"])
@login_required
def search_local():
    """
    Search local/municipal codes only

    POST /api/v1/trinity/search/local
    Body: {
        "query": "noise ordinance",
        "state": "NJ",
        "municipality": "Atlantic City",
        "county": "Atlantic",
        "limit": 20
    }
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    state = data.get("state")
    municipality = data.get("municipality")
    county = data.get("county")
    limit = min(data.get("limit", 20), 50)

    try:
        from legal_trinity_service import JurisdictionLevel

        service = get_trinity_service()
        result = service.search(
            query=query,
            state=state,
            municipality=municipality,
            county=county,
            levels=[JurisdictionLevel.LOCAL],
            limit_per_level=limit,
        )

        return (
            jsonify(
                {
                    "query": query,
                    "jurisdiction": f"{municipality or ''}, {county or ''} County, {state or ''}".strip(
                        ", "
                    ),
                    "count": len(result.local_results),
                    "results": result.to_dict()["local"]["results"],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Local search error: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# MUNICIPALITY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


@trinity_api.route("/municipality", methods=["POST"])
@login_required
@tier_required(TierLevel.PROFESSIONAL)
def add_municipality():
    """
    Add a new municipality for Code360 integration

    POST /api/v1/trinity/municipality
    Body: {
        "state": "NJ",
        "name": "Atlantic City",
        "county": "Atlantic"
    }

    Returns municipality info if found/added
    """
    data = request.get_json() or {}

    state = data.get("state", "").strip().upper()
    name = data.get("name", "").strip()
    county = data.get("county", "").strip()

    if not state or not name:
        return jsonify({"error": "State and name are required"}), 400

    try:
        client = get_code360_client()
        municipality = client.discover_municipality(state, name, county)

        if municipality:
            municipality.id = client._save_municipality(municipality)

            return (
                jsonify(
                    {
                        "success": True,
                        "municipality": {
                            "id": municipality.id,
                            "state": municipality.state,
                            "county": municipality.county,
                            "name": municipality.name,
                            "provider": municipality.provider.value,
                            "base_url": municipality.base_url,
                            "enabled": municipality.enabled,
                        },
                        "message": f"Successfully added {municipality.full_name}",
                    }
                ),
                201,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Could not find online code for {name}, {state}",
                        "suggestion": "Try searching on ecode360.com or municode.com manually",
                    }
                ),
                404,
            )

    except Exception as e:
        logger.error(f"Add municipality error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/municipalities", methods=["GET"])
@login_required
def list_municipalities():
    """
    List all integrated municipalities

    GET /api/v1/trinity/municipalities
    GET /api/v1/trinity/municipalities?state=NJ
    """
    state = request.args.get("state")

    try:
        client = get_code360_client()
        municipalities = client.list_municipalities(state=state)

        return (
            jsonify(
                {
                    "count": len(municipalities),
                    "municipalities": [
                        {
                            "id": m.id,
                            "state": m.state,
                            "county": m.county,
                            "name": m.name,
                            "full_name": m.full_name,
                            "provider": m.provider.value,
                            "base_url": m.base_url,
                            "enabled": m.enabled,
                            "last_sync": m.last_sync.isoformat() if m.last_sync else None,
                        }
                        for m in municipalities
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"List municipalities error: {e}")
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/sync/<int:municipality_id>", methods=["POST"])
@login_required
@tier_required(TierLevel.PROFESSIONAL)
def sync_municipality(municipality_id: int):
    """
    Sync/update municipal codes from source

    POST /api/v1/trinity/sync/123
    Body: {"chapters": ["15", "170"]}  // optional chapter filter
    """
    data = request.get_json() or {}
    chapters = data.get("chapters")

    try:
        client = get_code360_client()
        municipality = client.get_municipality(municipality_id)

        if not municipality:
            return jsonify({"error": "Municipality not found"}), 404

        stats = client.sync_municipality(municipality, chapters=chapters)

        return (
            jsonify({"success": True, "municipality": municipality.full_name, "sync_stats": stats}),
            200,
        )

    except Exception as e:
        logger.error(f"Sync error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# EVIDENCE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════


@trinity_api.route("/analyze", methods=["POST"])
@login_required
@tier_required(TierLevel.PROFESSIONAL)
def analyze_evidence():
    """
    Analyze evidence against applicable law at all levels

    POST /api/v1/trinity/analyze
    Body: {
        "evidence": {
            "id": "EVD-001",
            "type": "bwc",
            "content": "...",
            "violations": [
                {"type": "excessive force", "description": "..."}
            ]
        },
        "state": "NJ",
        "municipality": "Newark",
        "county": "Essex"
    }

    Returns:
    - Applicable laws at each level
    - Violation-to-law matching
    - Filing recommendations
    - Jurisdiction hierarchy notes
    """
    data = request.get_json() or {}

    evidence = data.get("evidence", {})
    state = data.get("state")
    municipality = data.get("municipality")
    county = data.get("county")

    if not evidence:
        return jsonify({"error": "Evidence data is required"}), 400

    if not state:
        return jsonify({"error": "State is required for jurisdiction analysis"}), 400

    try:
        service = get_trinity_service()
        analysis = service.analyze_evidence_against_law(
            evidence=evidence, state=state, municipality=municipality, county=county
        )

        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# JURISDICTION INFO
# ═══════════════════════════════════════════════════════════════════════════


@trinity_api.route("/jurisdictions", methods=["GET"])
@login_required
def get_jurisdictions():
    """
    Get information about available jurisdictions

    GET /api/v1/trinity/jurisdictions

    Returns supported states, federal sources, and integrated municipalities
    """
    try:
        client = get_code360_client()
        municipalities = client.list_municipalities()

        # Group municipalities by state
        by_state = {}
        for m in municipalities:
            if m.state not in by_state:
                by_state[m.state] = []
            by_state[m.state].append({"id": m.id, "name": m.name, "county": m.county})

        return (
            jsonify(
                {
                    "federal": {
                        "sources": [
                            {
                                "code": "USC",
                                "name": "United States Code",
                                "url": "https://uscode.house.gov",
                            },
                            {
                                "code": "CFR",
                                "name": "Code of Federal Regulations",
                                "url": "https://www.ecfr.gov",
                            },
                            {
                                "code": "FRCP",
                                "name": "Federal Rules of Criminal Procedure",
                                "url": "https://www.law.cornell.edu/rules/frcrmp",
                            },
                            {
                                "code": "FRE",
                                "name": "Federal Rules of Evidence",
                                "url": "https://www.law.cornell.edu/rules/fre",
                            },
                        ],
                        "case_law_sources": [
                            {"name": "CourtListener", "url": "https://www.courtlistener.com"},
                            {"name": "Cornell LII", "url": "https://www.law.cornell.edu"},
                            {"name": "GovInfo", "url": "https://www.govinfo.gov"},
                        ],
                    },
                    "states": {"supported": list(by_state.keys()), "count": len(by_state)},
                    "local": {
                        "total_municipalities": len(municipalities),
                        "by_state": by_state,
                        "providers": ["ecode360", "municode", "american_legal", "sterling"],
                    },
                    "hierarchy_note": "Federal law supersedes state law (Supremacy Clause). State law generally preempts local ordinances unless home rule applies.",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Jurisdictions error: {e}")
        return jsonify({"error": str(e)}), 500


@trinity_api.route("/discover", methods=["POST"])
@login_required
def discover_municipality():
    """
    Discover if a municipality has online codes (without adding)

    POST /api/v1/trinity/discover
    Body: {"state": "NJ", "name": "Atlantic City"}

    Returns discovery result without persisting
    """
    data = request.get_json() or {}

    state = data.get("state", "").strip().upper()
    name = data.get("name", "").strip()

    if not state or not name:
        return jsonify({"error": "State and name are required"}), 400

    try:
        client = get_code360_client()
        municipality = client.discover_municipality(state, name)

        if municipality:
            return (
                jsonify(
                    {
                        "found": True,
                        "municipality": {
                            "state": municipality.state,
                            "name": municipality.name,
                            "provider": municipality.provider.value,
                            "base_url": municipality.base_url,
                        },
                        "message": f"Found code source for {municipality.name}, {municipality.state}",
                        "action": "Use POST /api/v1/trinity/municipality to add this municipality",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "found": False,
                        "message": f"No online code found for {name}, {state}",
                        "suggestions": [
                            f"Search manually: https://ecode360.com/search?q={name}+{state}",
                            f"Try Municode: https://library.municode.com/{state.lower()}",
                        ],
                    }
                ),
                404,
            )

    except Exception as e:
        logger.error(f"Discovery error: {e}")
        return jsonify({"error": str(e)}), 500
