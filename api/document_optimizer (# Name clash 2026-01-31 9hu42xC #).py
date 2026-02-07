# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
API endpoints for Legal Document Optimizer

Provides endpoints for:
- Multi-document upload and analysis
- Document optimization with AI
- Consistency checking across filing set
- Evidence cross-referencing
- Court-ready output generation
"""

import os
import tempfile
import zipfile
from datetime import datetime
from functools import wraps
from typing import Dict, List

from flask import Blueprint, jsonify, request, send_file
from legal_document_optimizer import (
    EvidenceItem,
    LegalDocument,
    LegalDocumentOptimizer,
    OptimizationResult,
)

# Import auth if using authentication
# from models_auth import User, db
# from flask_login import login_required, current_user

bp = Blueprint("document_optimizer", __name__, url_prefix="/api/document-optimizer")

# Initialize optimizer (will use user's API key if provided)
optimizer = LegalDocumentOptimizer()


@bp.route("/analyze-filing-set", methods=["POST"])
# @login_required  # Uncomment if using auth
def analyze_filing_set():
    """
    Analyze complete filing set for consistency and optimization opportunities

    Expected input:
    {
        "documents": [
            {"filename": "complaint.pdf", "doc_type": "complaint", "content": "..."},
            {"filename": "motion.pdf", "doc_type": "motion", "content": "..."},
            ...
        ],
        "evidence": [
            {"evidence_id": 1, "title": "BWC Footage", "description": "...", ...},
            ...
        ],
        "jurisdiction": "california",  # optional
        "filing_type": "state_court"   # optional
    }

    Returns:
    {
        "analysis": {
            "documents_analyzed": 5,
            "consistency_report": {...},
            "evidence_coverage": {...},
            "procedural_compliance": {...},
            "optimization_opportunities": [...]
        }
    }
    """

    try:
        data = request.get_json()

        # Parse documents
        documents = []
        for doc_data in data.get("documents", []):
            doc = LegalDocument(
                filename=doc_data["filename"],
                doc_type=doc_data.get("doc_type", "unknown"),
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
            )
            documents.append(doc)

        # Parse evidence
        evidence = []
        for ev_data in data.get("evidence", []):
            ev = EvidenceItem(
                evidence_id=ev_data["evidence_id"],
                title=ev_data["title"],
                description=ev_data.get("description", ""),
                file_path=ev_data.get("file_path", ""),
                evidence_type=ev_data.get("evidence_type", "document"),
            )
            evidence.append(ev)

        jurisdiction = data.get("jurisdiction", "default")
        filing_type = data.get("filing_type", "state_court")

        # Analyze filing set
        analysis = optimizer.analyze_filing_set(
            documents=documents,
            evidence=evidence,
            jurisdiction=jurisdiction,
            filing_type=filing_type,
        )

        return jsonify({"success": True, "analysis": analysis})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/optimize-document", methods=["POST"])
# @login_required
def optimize_document():
    """
    Optimize a single document within context of filing set

    Expected input:
    {
        "document": {
            "filename": "complaint.pdf",
            "doc_type": "complaint",
            "content": "...",
            "metadata": {}
        },
        "evidence": [...],
        "related_documents": [...],
        "jurisdiction": "california",
        "optimization_goals": {
            "maximize_monetary_relief": true,
            "enhance_social_impact": true,
            "strengthen_interim_relief": true,
            "improve_clarity": true,
            "ensure_compliance": true
        },
        "api_key": "sk-..."  # Optional: user's OpenAI API key
    }

    Returns:
    {
        "success": true,
        "result": {
            "optimized_content": "...",
            "changes_summary": [...],
            "consistency_issues": [...],
            "evidence_gaps": [...],
            "procedural_issues": [...],
            "strategic_improvements": [...],
            "confidence_score": 0.92
        }
    }
    """

    try:
        data = request.get_json()

        # Get user's API key if provided
        user_api_key = data.get("api_key")
        if user_api_key:
            doc_optimizer = LegalDocumentOptimizer(api_key=user_api_key)
        else:
            doc_optimizer = optimizer  # Use default

        # Parse main document
        doc_data = data["document"]
        document = LegalDocument(
            filename=doc_data["filename"],
            doc_type=doc_data.get("doc_type", "unknown"),
            content=doc_data["content"],
            metadata=doc_data.get("metadata", {}),
        )

        # Parse evidence
        evidence = []
        for ev_data in data.get("evidence", []):
            ev = EvidenceItem(
                evidence_id=ev_data["evidence_id"],
                title=ev_data["title"],
                description=ev_data.get("description", ""),
                file_path=ev_data.get("file_path", ""),
                evidence_type=ev_data.get("evidence_type", "document"),
            )
            evidence.append(ev)

        # Parse related documents
        related_docs = []
        for doc_data in data.get("related_documents", []):
            doc = LegalDocument(
                filename=doc_data["filename"],
                doc_type=doc_data.get("doc_type", "unknown"),
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
            )
            related_docs.append(doc)

        jurisdiction = data.get("jurisdiction", "default")
        optimization_goals = data.get("optimization_goals", None)

        # Optimize document
        result = doc_optimizer.optimize_document(
            document=document,
            evidence=evidence,
            related_docs=related_docs,
            jurisdiction=jurisdiction,
            optimization_goals=optimization_goals,
        )

        return jsonify(
            {
                "success": True,
                "result": {
                    "optimized_content": result.optimized_content,
                    "changes_summary": result.changes_summary,
                    "consistency_issues": result.consistency_issues,
                    "evidence_gaps": result.evidence_gaps,
                    "procedural_issues": result.procedural_issues,
                    "strategic_improvements": result.strategic_improvements,
                    "confidence_score": result.confidence_score,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/optimize-filing-set", methods=["POST"])
# @login_required
def optimize_filing_set():
    """
    Optimize entire filing set (all documents)

    Returns ZIP file with:
    - Optimized version of each document
    - Comprehensive consistency report
    - Strategic improvement summary
    - Evidence cross-reference report

    Input same as analyze-filing-set, plus optimization_goals

    Returns: ZIP file download
    """

    try:
        data = request.get_json()

        # Get user's API key if provided
        user_api_key = data.get("api_key")
        if user_api_key:
            doc_optimizer = LegalDocumentOptimizer(api_key=user_api_key)
        else:
            doc_optimizer = optimizer

        # Parse all data (similar to above endpoints)
        documents = []
        for doc_data in data.get("documents", []):
            doc = LegalDocument(
                filename=doc_data["filename"],
                doc_type=doc_data.get("doc_type", "unknown"),
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
            )
            documents.append(doc)

        evidence = []
        for ev_data in data.get("evidence", []):
            ev = EvidenceItem(
                evidence_id=ev_data["evidence_id"],
                title=ev_data["title"],
                description=ev_data.get("description", ""),
                file_path=ev_data.get("file_path", ""),
                evidence_type=ev_data.get("evidence_type", "document"),
            )
            evidence.append(ev)

        jurisdiction = data.get("jurisdiction", "default")
        optimization_goals = data.get("optimization_goals", None)

        # Optimize each document
        results = []
        for doc in documents:
            # Other docs are "related" to current doc
            related = [d for d in documents if d.filename != doc.filename]

            result = doc_optimizer.optimize_document(
                document=doc,
                evidence=evidence,
                related_docs=related,
                jurisdiction=jurisdiction,
                optimization_goals=optimization_goals,
            )
            results.append(result)

        # Create ZIP file with results
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "optimized_filing_set.zip")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            # Add optimized documents
            for result in results:
                filename = f"OPTIMIZED_{result.original_doc.filename}.txt"
                zipf.writestr(filename, result.optimized_content)

            # Add comprehensive report
            report = generate_filing_set_report(results, jurisdiction)
            zipf.writestr("OPTIMIZATION_REPORT.txt", report)

        return send_file(
            zip_path,
            as_attachment=True,
            download_name="optimized_filing_set.zip",
            mimetype="application/zip",
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/check-compliance", methods=["POST"])
def check_compliance():
    """
    Quick compliance check without full optimization

    Input:
    {
        "documents": [...],
        "jurisdiction": "california"
    }

    Returns:
    {
        "compliant": false,
        "issues": [
            "Missing certificate of service",
            "Complaint appears unverified",
            ...
        ],
        "warnings": [...],
        "recommendations": [...]
    }
    """

    try:
        data = request.get_json()

        documents = []
        for doc_data in data.get("documents", []):
            doc = LegalDocument(
                filename=doc_data["filename"],
                doc_type=doc_data.get("doc_type", "unknown"),
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
            )
            documents.append(doc)

        jurisdiction = data.get("jurisdiction", "default")

        # Check procedural compliance
        compliance = optimizer._check_procedural_compliance(documents, jurisdiction)

        # Check consistency
        consistency = optimizer._check_consistency(documents)

        return jsonify(
            {
                "success": True,
                "compliant": compliance["compliant"] and consistency["consistent"],
                "procedural_issues": compliance["issues"],
                "consistency_issues": consistency["issues"],
                "jurisdiction": jurisdiction,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def generate_filing_set_report(results: list[OptimizationResult], jurisdiction: str) -> str:
    """Generate comprehensive optimization report"""

    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("Evident LEGAL DOCUMENT OPTIMIZATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Jurisdiction: {jurisdiction}")
    report_lines.append(f"Documents Optimized: {len(results)}")
    report_lines.append("\n")

    # Executive Summary
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 80)

    total_changes = sum(len(r.changes_summary) for r in results)
    total_issues = sum(
        len(r.consistency_issues) + len(r.evidence_gaps) + len(r.procedural_issues) for r in results
    )
    avg_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0

    report_lines.append(f"Total Changes Made: {total_changes}")
    report_lines.append(f"Total Issues Identified: {total_issues}")
    report_lines.append(f"Average Confidence Score: {avg_confidence:.2%}")
    report_lines.append("\n")

    # Document-by-document breakdown
    for i, result in enumerate(results, 1):
        report_lines.append(f"\nDOCUMENT {i}: {result.original_doc.filename}")
        report_lines.append("=" * 80)

        report_lines.append(f"\nDocument Type: {result.original_doc.doc_type}")
        report_lines.append(f"Confidence Score: {result.confidence_score:.2%}")

        if result.changes_summary:
            report_lines.append("\nCHANGES MADE:")
            for change in result.changes_summary:
                report_lines.append(f"  • {change}")

        if result.consistency_issues:
            report_lines.append("\nCONSISTENCY ISSUES RESOLVED:")
            for issue in result.consistency_issues:
                report_lines.append(f"  ⚠ {issue}")

        if result.evidence_gaps:
            report_lines.append("\nEVIDENCE GAPS IDENTIFIED:")
            for gap in result.evidence_gaps:
                report_lines.append(f"  ⚠ {gap}")

        if result.procedural_issues:
            report_lines.append("\nPROCEDURAL ISSUES ADDRESSED:")
            for issue in result.procedural_issues:
                report_lines.append(f"  ⚠ {issue}")

        if result.strategic_improvements:
            report_lines.append("\nSTRATEGIC IMPROVEMENTS:")
            for improvement in result.strategic_improvements:
                report_lines.append(f"  ✓ {improvement}")

        report_lines.append("\n")

    # Overall recommendations
    report_lines.append("\nOVERALL RECOMMENDATIONS")
    report_lines.append("=" * 80)
    report_lines.append("1. Review all optimized documents for accuracy and completeness")
    report_lines.append("2. Verify all factual allegations against attached evidence")
    report_lines.append("3. Ensure all certificates of service are properly executed")
    report_lines.append("4. Consider additional evidence to support any identified gaps")
    report_lines.append("5. Have all documents reviewed by supervising attorney before filing")
    report_lines.append("\n")

    report_lines.append("DISCLAIMER")
    report_lines.append("-" * 80)
    report_lines.append(
        "This optimization report is provided as a drafting and organizational assistant."
    )
    report_lines.append(
        "It does NOT constitute legal advice. All documents must be reviewed by a licensed"
    )
    report_lines.append("attorney before filing. Evident makes no guarantees about outcomes.")
    report_lines.append("\n")

    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)
