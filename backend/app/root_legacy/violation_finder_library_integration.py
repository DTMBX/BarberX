"""
Violation Finder Integration with Legal Reference Library

Links detected violations to precedent case law
"""

import json
from typing import Dict, List

from .legal_library import LegalLibraryService


class ViolationFinderLibraryIntegration:
    """Link violations to precedent cases"""

    def __init__(self):
        self.library = LegalLibraryService()

        # Map violation types to search queries
        self.violation_precedents = {
            "miranda_violation": "Miranda v. Arizona",
            "unlawful_search": "Katz v. United States warrantless search",
            "unlawful_seizure": "Terry v. Ohio",
            "excessive_force": "Graham v. Connor Tennessee v. Garner",
            "brady_violation": "Brady v. Maryland",
            "giglio_violation": "Giglio v. United States",
            "false_arrest": "Payton v. New York",
            "malicious_prosecution": "malicious prosecution",
            "qualified_immunity": "Harlow v. Fitzgerald qualified immunity",
            "municipal_liability": "Monell v. Department of Social Services",
        }

    def link_violation_to_precedent(self, violation_type: str) -> List[Dict]:
        """
        Find precedent cases for a violation type

        Args:
            violation_type: Type of violation (e.g., 'miranda_violation')

        Returns:
            List of relevant precedent cases
        """

        # Get search query for this violation type
        query = self.violation_precedents.get(violation_type, violation_type)

        # Search library
        cases = self.library.search_library(query=query, doc_type="case", limit=5)

        # Format results
        precedents = []
        for case in cases:
            precedents.append(
                {
                    "citation": case.citation,
                    "title": case.title,
                    "court": case.court,
                    "summary": case.summary[:300] if case.summary else "",
                    "relevance": f"Precedent for {violation_type.replace('_', ' ')}",
                    "doc_id": case.id,
                    "url": f"/api/legal-library/document/{case.id}",
                }
            )

        return precedents

    def enhance_violation_report(self, violations: List[Dict]) -> Dict:
        """
        Enhance violation report with case law citations

        Args:
            violations: List of detected violations

        Returns:
            Enhanced report with precedent citations
        """

        enhanced_violations = []

        for violation in violations:
            violation_type = violation.get("type", "")

            # Find precedent cases
            precedents = self.link_violation_to_precedent(violation_type)

            # Add to violation
            enhanced_violation = violation.copy()
            enhanced_violation["precedent_cases"] = precedents

            # Generate legal summary
            if precedents:
                enhanced_violation["legal_standard"] = self._generate_legal_standard(
                    violation_type, precedents[0]  # Use top precedent
                )

            enhanced_violations.append(enhanced_violation)

        return {
            "violations": enhanced_violations,
            "total_precedents_cited": sum(
                len(v.get("precedent_cases", [])) for v in enhanced_violations
            ),
        }

    def generate_citation_section(self, violation_type: str) -> str:
        """
        Generate formatted citation section for legal brief

        Args:
            violation_type: Type of violation

        Returns:
            Formatted citation section (markdown)
        """

        precedents = self.link_violation_to_precedent(violation_type)

        if not precedents:
            return ""

        section = f"## Applicable Case Law\n\n"

        for i, case in enumerate(precedents, 1):
            section += f"{i}. **{case['title']}**, {case['citation']}\n"
            if case["summary"]:
                section += f"   {case['summary']}\n"
            section += "\n"

        return section

    def _generate_legal_standard(self, violation_type: str, precedent: Dict) -> str:
        """Generate legal standard text based on precedent"""

        standards = {
            "miranda_violation": f"Under {precedent['citation']}, law enforcement must advise suspects of their rights before custodial interrogation.",
            "excessive_force": f"Under {precedent['citation']}, the standard for excessive force is 'objective reasonableness' under the Fourth Amendment.",
            "unlawful_search": f"Under {precedent['citation']}, warrantless searches are per se unreasonable unless an exception applies.",
            "brady_violation": f"Under {precedent['citation']}, the prosecution must disclose all exculpatory evidence to the defense.",
        }

        return standards.get(
            violation_type, f"Applicable legal standard established in {precedent['citation']}"
        )


# TODO: Integration point for case_law_violation_scanner.py
"""
Add to ViolationScanner class:

from .violation_finder_library_integration import ViolationFinderLibraryIntegration

class ViolationScanner:
    def __init__(self):
        self.library_integration = ViolationFinderLibraryIntegration()
    
    def scan_for_violations(self, transcript):
        violations = self._detect_violations(transcript)
        
        # Link to precedent cases
        enhanced_report = self.library_integration.enhance_violation_report(violations)
        
        return enhanced_report
"""


