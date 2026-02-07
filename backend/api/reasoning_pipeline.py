# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident AI Reasoning Pipeline REST API

Exposes the 8-engine mathematical reasoning system via REST endpoints.
Each endpoint provides access to a specific formal reasoning capability.

CONFIDENTIAL - TRADE SECRET PROTECTED
Copyright (c) 2026 Evident. All rights reserved.
"""

import traceback
from functools import wraps

from flask import Blueprint, jsonify, request

# Import reasoning engines
try:
    from Evident_reasoning_core import (
        BurdenAwareBayesianInference,
        EvidencePipeline,
        LegalStateLattice,
        NarrativeDriftDetector,
        OptimalTransportMatcher,
        OriginalityAnalyzer,
        SpectralPrecedentGraph,
        TemporalLogicVerifier,
    )

    REASONING_AVAILABLE = True
except ImportError as e:
    REASONING_AVAILABLE = False
    print(f"[WARN] Reasoning pipeline not available: {e}")

reasoning_bp = Blueprint("reasoning", __name__, url_prefix="/api/v1/reasoning")


def require_auth(f):
    """Placeholder for authentication - integrate with existing auth system"""

    @wraps(f)
    def decorated(*args, **kwargs):
        # TODO: Integrate with existing authentication from app.py
        return f(*args, **kwargs)

    return decorated


def check_tier_access(min_tier="free"):
    """Placeholder for tier gating - integrate with existing tier system"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # TODO: Integrate with tier_gating.py
            return f(*args, **kwargs)

        return decorated

    return decorator


@reasoning_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "engines_available": REASONING_AVAILABLE, "version": "1.0.0"})


@reasoning_bp.route("/procedural-consistency", methods=["POST"])
@require_auth
@check_tier_access("standard")
def check_procedural_consistency():
    """
    Validate procedural consistency using Legal State Lattices

    Detects contradictions in facts, claims, posture, and burden.

    Request body:
    {
        "facts": ["fact1", "fact2", ...],
        "claims": ["claim1", "claim2", ...],
        "posture": "motion_to_dismiss" | "summary_judgment" | "trial" | ...,
        "burden": "preponderance" | "clear_and_convincing" | "beyond_reasonable_doubt",
        "jurisdiction": "NJ" | "Federal"
    }

    Response:
    {
        "consistent": true/false,
        "violations": [...],
        "lattice_state": {...},
        "recommendations": [...]
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create lattice instance
        lattice = LegalStateLattice(jurisdiction=data.get("jurisdiction", "NJ"))

        # Create legal state
        state = lattice.create_state(
            facts=data.get("facts", []),
            claims=data.get("claims", []),
            posture=data.get("posture", "initial"),
            burden=data.get("burden", "preponderance"),
        )

        # Check consistency
        is_consistent = lattice.is_consistent(state)
        violations = lattice.find_violations(state)

        return jsonify(
            {
                "consistent": is_consistent,
                "violations": violations,
                "lattice_state": state.to_dict(),
                "recommendations": lattice.generate_recommendations(state),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/burden-analysis", methods=["POST"])
@require_auth
@check_tier_access("standard")
def analyze_burden():
    """
    Perform burden-aware Bayesian inference

    Request body:
    {
        "hypothesis": "Defendant violated constitutional rights",
        "evidence": [
            {"description": "...", "strength": 0.8, "reliability": 0.9},
            ...
        ],
        "burden": "preponderance" | "clear_and_convincing" | "beyond_reasonable_doubt",
        "prior_probability": 0.5
    }

    Response:
    {
        "posterior_probability": 0.75,
        "confidence_interval": [0.65, 0.85],
        "burden_met": true/false,
        "sensitivity_analysis": {...},
        "explanation": "..."
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create Bayesian inference engine
        bayesian = BurdenAwareBayesianInference(burden=data.get("burden", "preponderance"))

        # Set prior
        bayesian.set_prior(data.get("prior_probability", 0.5))

        # Update with evidence
        for evidence in data.get("evidence", []):
            bayesian.update(
                evidence_description=evidence.get("description"),
                likelihood=evidence.get("strength", 0.5),
                reliability=evidence.get("reliability", 1.0),
            )

        # Get posterior and analysis
        result = bayesian.analyze(hypothesis=data.get("hypothesis"))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/precedent-analysis", methods=["POST"])
@require_auth
@check_tier_access("premium")
def analyze_precedent():
    """
    Analyze precedent using spectral graph methods

    Request body:
    {
        "case_citations": ["cite1", "cite2", ...],
        "jurisdiction": "NJ" | "Federal" | "3rd_Circuit",
        "issue": "qualified_immunity" | "due_process" | ...,
        "max_results": 10
    }

    Response:
    {
        "controlling_cases": [...],
        "citation_network": {...},
        "centrality_scores": {...},
        "binding_authority": [...],
        "distinguishing_factors": [...]
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create precedent graph
        precedent_graph = SpectralPrecedentGraph(jurisdiction=data.get("jurisdiction", "NJ"))

        # Build graph from citations
        precedent_graph.build_from_citations(data.get("case_citations", []))

        # Compute centrality
        centrality = precedent_graph.compute_spectral_centrality()

        # Find controlling cases
        controlling = precedent_graph.find_controlling_authority(
            issue=data.get("issue"), max_results=data.get("max_results", 10)
        )

        return jsonify(
            {
                "controlling_cases": controlling,
                "citation_network": precedent_graph.to_dict(),
                "centrality_scores": centrality,
                "binding_authority": precedent_graph.get_binding_authority(),
                "distinguishing_factors": precedent_graph.find_distinguishing_factors(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/fact-pattern-similarity", methods=["POST"])
@require_auth
@check_tier_access("standard")
def compute_fact_similarity():
    """
    Compare fact patterns using optimal transport

    Request body:
    {
        "source_facts": ["fact1", "fact2", ...],
        "target_facts": ["fact1", "fact2", ...],
        "method": "wasserstein" | "earth_movers"
    }

    Response:
    {
        "similarity_score": 0.85,
        "transport_plan": {...},
        "matching_facts": [...],
        "distinguishing_facts": [...],
        "explanation": "..."
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create optimal transport matcher
        matcher = OptimalTransportMatcher(method=data.get("method", "wasserstein"))

        # Compute similarity
        result = matcher.compare(
            source_facts=data.get("source_facts", []), target_facts=data.get("target_facts", [])
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/narrative-drift", methods=["POST"])
@require_auth
@check_tier_access("premium")
def detect_narrative_drift():
    """
    Detect narrative drift using information geometry

    Request body:
    {
        "timeline": [
            {"timestamp": "2024-01-01", "narrative": "..."},
            {"timestamp": "2024-02-01", "narrative": "..."},
            ...
        ]
    }

    Response:
    {
        "drift_detected": true/false,
        "drift_magnitude": 0.3,
        "critical_changes": [...],
        "timeline_analysis": {...},
        "credibility_impact": "low" | "medium" | "high"
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create drift detector
        detector = NarrativeDriftDetector()

        # Analyze timeline
        result = detector.analyze_timeline(data.get("timeline", []))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/due-process-verification", methods=["POST"])
@require_auth
@check_tier_access("standard")
def verify_due_process():
    """
    Verify due process compliance using temporal logic

    Request body:
    {
        "events": [
            {"type": "service", "timestamp": "2024-01-01"},
            {"type": "hearing_scheduled", "timestamp": "2024-02-01"},
            ...
        ],
        "requirements": ["notice", "opportunity_to_be_heard", "impartial_tribunal"]
    }

    Response:
    {
        "compliant": true/false,
        "violations": [...],
        "timeline_verification": {...},
        "recommendations": [...]
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create temporal logic verifier
        verifier = TemporalLogicVerifier()

        # Verify events
        result = verifier.verify_timeline(
            events=data.get("events", []), requirements=data.get("requirements", [])
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/originality-check", methods=["POST"])
@require_auth
@check_tier_access("premium")
def check_originality():
    """
    Check document originality using algorithmic information theory

    Request body:
    {
        "text": "Document text to analyze...",
        "comparison_corpus": ["doc1", "doc2", ...] (optional)
    }

    Response:
    {
        "originality_score": 0.85,
        "complexity_estimate": 1234,
        "boilerplate_percentage": 0.15,
        "unique_contributions": [...],
        "similarity_warnings": [...]
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create originality analyzer
        analyzer = OriginalityAnalyzer()

        # Analyze text
        result = analyzer.analyze(
            text=data.get("text", ""), comparison_corpus=data.get("comparison_corpus", [])
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@reasoning_bp.route("/evidence-pipeline", methods=["POST"])
@require_auth
@check_tier_access("standard")
def process_evidence():
    """
    Process evidence through category-theoretic pipeline

    Request body:
    {
        "evidence_id": "bwc_001",
        "transformations": ["ocr", "transcription", "redaction", "annotation"],
        "metadata": {...}
    }

    Response:
    {
        "pipeline_id": "...",
        "transformations_applied": [...],
        "audit_trail": [...],
        "chain_of_custody": {...},
        "result": {...}
    }
    """
    if not REASONING_AVAILABLE:
        return jsonify({"error": "Reasoning pipeline not available"}), 503

    try:
        data = request.get_json()

        # Create evidence pipeline
        pipeline = EvidencePipeline()

        # Process evidence
        result = pipeline.process(
            evidence_id=data.get("evidence_id"),
            transformations=data.get("transformations", []),
            metadata=data.get("metadata", {}),
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# Error handlers
@reasoning_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@reasoning_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
