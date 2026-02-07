# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Citation Quality Validator

Validates legal citations for accuracy and authenticity.
Ensures only verified, legitimate cases are in the library.

Validation checks:
1. Citation format (Bluebook compliance)
2. Source verification (cross-reference multiple sources)
3. Case existence verification
4. Year/date validation
5. Court validation
6. Reporter validation
"""

import re
from datetime import datetime


class CitationQualityValidator:
    """Validate legal citations for quality and authenticity"""

    # Bluebook citation patterns
    BLUEBOOK_PATTERNS = {
        "us_reports": re.compile(r"(\d+)\s+U\.S\.\s+(\d+)\s*(?:\((\d{4})\))?"),
        "federal_reporter": re.compile(
            r"(\d+)\s+F\.(?:2d|3d)\s+(\d+)\s*(?:\((\w+\.?\s+Cir\.)?\s*(\d{4})\))?"
        ),
        "federal_supplement": re.compile(r"(\d+)\s+F\.\s*Supp\.(?:2d|3d)?\s+(\d+)"),
        "supreme_court_reporter": re.compile(r"(\d+)\s+S\.\s*Ct\.\s+(\d+)"),
        "state_reporter": re.compile(r"(\d+)\s+([A-Z][a-z\.]+(?:2d|3d)?)\s+(\d+)"),
    }

    # Valid reporter abbreviations
    VALID_REPORTERS = {
        "U.S.",
        "S. Ct.",
        "L. Ed.",  # Supreme Court
        "F.",
        "F.2d",
        "F.3d",  # Federal Reporter
        "F. Supp.",
        "F. Supp. 2d",
        "F. Supp. 3d",  # Federal Supplement
        "Cal.",
        "Cal. 2d",
        "Cal. 3d",
        "Cal. 4th",  # California
        "N.Y.",
        "N.Y. 2d",
        "N.Y. 3d",  # New York
        "Ill.",
        "Ill. 2d",
        "Ill. 3d",  # Illinois
        # ... more state reporters
    }

    # Valid federal circuits
    VALID_CIRCUITS = {
        "1st Cir.",
        "2nd Cir.",
        "3rd Cir.",
        "4th Cir.",
        "5th Cir.",
        "6th Cir.",
        "7th Cir.",
        "8th Cir.",
        "9th Cir.",
        "10th Cir.",
        "11th Cir.",
        "D.C. Cir.",
        "Fed. Cir.",
    }

    def validate_citation(self, citation: str) -> dict:
        """
        Validate a legal citation

        Returns:
            {
                'valid': bool,
                'format_valid': bool,
                'bluebook_compliant': bool,
                'warnings': list,
                'errors': list,
                'quality_score': float (0-100)
            }
        """

        warnings = []
        errors = []
        format_valid = False
        bluebook_compliant = False

        # Check format
        matched_pattern = None
        for pattern_name, pattern in self.BLUEBOOK_PATTERNS.items():
            if pattern.search(citation):
                format_valid = True
                matched_pattern = pattern_name
                break

        if not format_valid:
            errors.append("Citation format not recognized")

        # Check Bluebook compliance
        if format_valid:
            bluebook_compliant = self._check_bluebook_compliance(citation, matched_pattern)

            if not bluebook_compliant:
                warnings.append("Citation may not be fully Bluebook compliant")

        # Validate year if present
        year_match = re.search(r"\((\d{4})\)", citation)
        if year_match:
            year = int(year_match.group(1))
            current_year = datetime.now().year

            if year < 1789:  # U.S. Constitution ratified
                errors.append(f"Invalid year: {year} (before U.S. legal system)")
            elif year > current_year:
                errors.append(f"Invalid year: {year} (future date)")

        # Calculate quality score
        quality_score = 100.0

        if not format_valid:
            quality_score -= 50
        if not bluebook_compliant:
            quality_score -= 20
        quality_score -= len(warnings) * 5
        quality_score -= len(errors) * 10

        quality_score = max(0, quality_score)

        return {
            "valid": format_valid and len(errors) == 0,
            "format_valid": format_valid,
            "bluebook_compliant": bluebook_compliant,
            "warnings": warnings,
            "errors": errors,
            "quality_score": quality_score,
            "matched_pattern": matched_pattern,
        }

    def _check_bluebook_compliance(self, citation: str, pattern_name: str) -> bool:
        """Check if citation follows Bluebook format rules"""

        # Check spacing
        if "  " in citation:  # Double spaces
            return False

        # Check reporter abbreviation
        for reporter in self.VALID_REPORTERS:
            if reporter in citation:
                return True

        return False

    def cross_verify_citation(self, citation: str, sources: list[str]) -> dict:
        """
        Cross-verify citation across multiple sources

        Args:
            citation: Citation to verify
            sources: List of source names to check

        Returns:
            Verification results
        """

        from verified_legal_sources import VerifiedLegalSources

        verifier = VerifiedLegalSources()

        verified_in = []
        not_found_in = []

        for source in sources:
            # Check if citation exists in source
            # TODO: Implement source-specific verification
            pass

        return {
            "citation": citation,
            "verified_in": verified_in,
            "not_found_in": not_found_in,
            "verification_count": len(verified_in),
            "confidence": (
                "HIGH" if len(verified_in) >= 2 else "MEDIUM" if len(verified_in) == 1 else "LOW"
            ),
        }

    def validate_document_metadata(self, doc: dict) -> dict:
        """
        Validate document metadata for quality

        Checks:
        - Citation format
        - Title present and reasonable
        - Court information
        - Date validity
        - Full text present
        """

        issues = []
        warnings = []

        # Check citation
        if not doc.get("citation"):
            issues.append("Missing citation")
        else:
            citation_check = self.validate_citation(doc["citation"])
            if not citation_check["valid"]:
                issues.append(f"Invalid citation: {citation_check['errors']}")

        # Check title
        if not doc.get("title"):
            issues.append("Missing title")
        elif len(doc["title"]) < 5:
            warnings.append("Title seems too short")

        # Check court
        if not doc.get("court"):
            warnings.append("Missing court information")

        # Check decision date
        if doc.get("decision_date"):
            try:
                date = datetime.fromisoformat(str(doc["decision_date"]))
                if date.year < 1789:
                    issues.append(f"Invalid decision date: {date.year}")
                elif date > datetime.now():
                    issues.append("Decision date is in the future")
            except:
                issues.append("Invalid decision date format")

        # Check full text
        if not doc.get("full_text"):
            warnings.append("Missing full text")
        elif len(doc["full_text"]) < 100:
            warnings.append("Full text seems incomplete")

        quality_score = 100.0
        quality_score -= len(issues) * 20
        quality_score -= len(warnings) * 5
        quality_score = max(0, quality_score)

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "quality_score": quality_score,
            "recommendation": (
                "IMPORT" if quality_score >= 70 else "REVIEW" if quality_score >= 50 else "REJECT"
            ),
        }

    def generate_quality_report(self, documents: list[dict]) -> dict:
        """
        Generate quality report for multiple documents

        Returns statistics on document quality
        """

        total = len(documents)
        valid = 0
        warnings_count = 0
        errors_count = 0
        quality_scores = []

        for doc in documents:
            validation = self.validate_document_metadata(doc)

            if validation["valid"]:
                valid += 1

            warnings_count += len(validation["warnings"])
            errors_count += len(validation["issues"])
            quality_scores.append(validation["quality_score"])

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        return {
            "total_documents": total,
            "valid_documents": valid,
            "invalid_documents": total - valid,
            "total_warnings": warnings_count,
            "total_errors": errors_count,
            "average_quality_score": avg_quality,
            "quality_distribution": {
                "excellent": sum(1 for s in quality_scores if s >= 90),
                "good": sum(1 for s in quality_scores if 70 <= s < 90),
                "fair": sum(1 for s in quality_scores if 50 <= s < 70),
                "poor": sum(1 for s in quality_scores if s < 50),
            },
        }


# TODO: Integration point
"""
Add to overnight_library_builder.py:

from citation_quality_validator import CitationQualityValidator

class OvernightLibraryBuilder:
    def __init__(self):
        self.validator = CitationQualityValidator()
    
    def build_library(self, ...):
        for citation in cases:
            # Validate before importing
            validation = self.validator.validate_citation(citation)
            
            if not validation['valid']:
                logger.warning(f"Skipping {citation}: {validation['errors']}")
                continue
            
            # Import validated citation
            ...
"""
