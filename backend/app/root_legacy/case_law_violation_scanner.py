"""
Case Law Analysis & Violation Scanner
Advanced legal competence tools for identifying violations, precedents, and case law

Features:
- Constitutional rights violation detection
- Case law citation and precedent matching
- Legal standard violation flagging
- Statutory compliance checking
- Evidence admissibility analysis
- Miranda rights analysis
- Fourth Amendment search/seizure analysis
- Brady/Giglio violation detection
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ViolationType(Enum):
    """Categories of legal violations"""

    CONSTITUTIONAL = "constitutional"
    STATUTORY = "statutory"
    PROCEDURAL = "procedural"
    EVIDENTIARY = "evidentiary"
    MIRANDA = "miranda"
    BRADY_GIGLIO = "brady_giglio"
    FOURTH_AMENDMENT = "fourth_amendment"
    FIFTH_AMENDMENT = "fifth_amendment"
    SIXTH_AMENDMENT = "sixth_amendment"
    FOURTEENTH_AMENDMENT = "fourteenth_amendment"


class ViolationSeverity(Enum):
    """Severity levels for violations"""

    CRITICAL = "critical"  # Case-ending violation
    HIGH = "high"  # Major evidentiary impact
    MEDIUM = "medium"  # Significant but not fatal
    LOW = "low"  # Minor procedural issue
    INFORMATIONAL = "informational"  # Worth noting


@dataclass
class Violation:
    """Represents a detected legal violation"""

    violation_type: ViolationType
    severity: ViolationSeverity
    title: str
    description: str
    evidence_reference: str
    legal_basis: str
    case_law_support: List[str]
    recommended_action: str
    timestamp_reference: Optional[str] = None
    confidence: float = 0.0


@dataclass
class CaseLawPrecedent:
    """Legal precedent from case law"""

    case_name: str
    citation: str
    year: int
    jurisdiction: str
    holding: str
    relevance_score: float
    key_facts: List[str]
    distinguishing_factors: Optional[List[str]] = None


class ConstitutionalRightsAnalyzer:
    """Analyzes evidence for constitutional violations"""

    def __init__(self):
        self.violations = []

    def analyze_miranda_compliance(self, transcript: str, context: Dict) -> List[Violation]:
        """
        Check for Miranda rights violations

        Required elements:
        1. Right to remain silent
        2. Anything said can be used against you
        3. Right to attorney
        4. Attorney appointed if cannot afford
        5. Waiver must be voluntary and knowing
        """
        violations = []
        miranda_warnings = {
            "right_to_silence": r"(right to remain silent|don't have to say anything)",
            "use_against": r"(anything you say can|may be used against you)",
            "right_to_attorney": r"(right to an attorney|right to a lawyer)",
            "appointed_attorney": r"(attorney will be appointed|appointed.*attorney|provided.*attorney)",
        }

        missing_warnings = []
        for warning_name, pattern in miranda_warnings.items():
            if not re.search(pattern, transcript, re.IGNORECASE):
                missing_warnings.append(warning_name.replace("_", " "))

        if missing_warnings:
            violations.append(
                Violation(
                    violation_type=ViolationType.MIRANDA,
                    severity=ViolationSeverity.CRITICAL,
                    title="Incomplete Miranda Warnings",
                    description=f"Miranda warnings incomplete. Missing: {', '.join(missing_warnings)}",
                    evidence_reference=context.get("evidence_id", "Unknown"),
                    legal_basis="Fifth Amendment, Miranda v. Arizona, 384 U.S. 436 (1966)",
                    case_law_support=[
                        "Miranda v. Arizona, 384 U.S. 436 (1966)",
                        "Dickerson v. United States, 530 U.S. 428 (2000)",
                        "Berghuis v. Thompkins, 560 U.S. 370 (2010)",
                    ],
                    recommended_action="File motion to suppress statements. Statements obtained without proper Miranda warnings may be inadmissible.",
                    confidence=0.95,
                )
            )

        # Check for invocation of rights
        if re.search(r"(I want|I'd like|get me|call).*attorney|lawyer", transcript, re.IGNORECASE):
            # Check if questioning continued
            attorney_request_pos = re.search(
                r"(I want|I'd like|get me|call).*attorney|lawyer", transcript, re.IGNORECASE
            ).start()
            text_after = transcript[attorney_request_pos:]

            if re.search(r"(officer|detective|agent).*:.*\?", text_after[:500], re.IGNORECASE):
                violations.append(
                    Violation(
                        violation_type=ViolationType.MIRANDA,
                        severity=ViolationSeverity.CRITICAL,
                        title="Continued Interrogation After Attorney Request",
                        description="Questioning continued after suspect invoked right to attorney",
                        evidence_reference=context.get("evidence_id", "Unknown"),
                        legal_basis="Fifth Amendment, Sixth Amendment, Edwards v. Arizona",
                        case_law_support=[
                            "Edwards v. Arizona, 451 U.S. 477 (1981)",
                            "Minnick v. Mississippi, 498 U.S. 146 (1990)",
                            "Davis v. United States, 512 U.S. 452 (1994)",
                        ],
                        recommended_action="File motion to suppress all statements after invocation. Edwards rule prohibits further interrogation.",
                        confidence=0.90,
                    )
                )

        return violations

    def analyze_fourth_amendment(self, transcript: str, context: Dict) -> List[Violation]:
        """
        Check for Fourth Amendment search/seizure violations

        Analysis includes:
        - Warrant requirements
        - Consent validity
        - Probable cause
        - Exigent circumstances
        - Scope of search
        """
        violations = []

        # Check for warrantless search
        has_warrant = re.search(
            r"(search warrant|warrant|judge.*signed)", transcript, re.IGNORECASE
        )
        has_consent = re.search(
            r"(can I search|do you mind if|permission to search|consent)", transcript, re.IGNORECASE
        )

        if not has_warrant and not has_consent:
            # Check for exigent circumstances
            exigent = re.search(
                r"(emergency|exigent|hot pursuit|imminent|destruction of evidence)",
                transcript,
                re.IGNORECASE,
            )

            if not exigent:
                violations.append(
                    Violation(
                        violation_type=ViolationType.FOURTH_AMENDMENT,
                        severity=ViolationSeverity.HIGH,
                        title="Warrantless Search Without Exception",
                        description="Search conducted without warrant, consent, or apparent exigent circumstances",
                        evidence_reference=context.get("evidence_id", "Unknown"),
                        legal_basis="Fourth Amendment, Katz v. United States, 389 U.S. 347 (1967)",
                        case_law_support=[
                            "Katz v. United States, 389 U.S. 347 (1967)",
                            "United States v. Jones, 565 U.S. 400 (2012)",
                            "Riley v. California, 573 U.S. 373 (2014)",
                        ],
                        recommended_action="File motion to suppress evidence. Warrantless searches presumptively unreasonable.",
                        confidence=0.85,
                    )
                )

        # Check consent validity
        if has_consent:
            # Check for coercion indicators
            coercion_indicators = [
                r"have to|must|required to",
                r"refuse.*consequences",
                r"make it (worse|harder)",
                r"cooperate or else",
            ]

            for indicator in coercion_indicators:
                if re.search(indicator, transcript, re.IGNORECASE):
                    violations.append(
                        Violation(
                            violation_type=ViolationType.FOURTH_AMENDMENT,
                            severity=ViolationSeverity.HIGH,
                            title="Potentially Coerced Consent",
                            description="Consent may have been coerced or not voluntary",
                            evidence_reference=context.get("evidence_id", "Unknown"),
                            legal_basis="Fourth Amendment, Schneckloth v. Bustamonte, 412 U.S. 218 (1973)",
                            case_law_support=[
                                "Schneckloth v. Bustamonte, 412 U.S. 218 (1973)",
                                "Florida v. Royer, 460 U.S. 491 (1983)",
                                "United States v. Drayton, 536 U.S. 194 (2002)",
                            ],
                            recommended_action="Challenge voluntariness of consent. Consent must be freely and voluntarily given.",
                            confidence=0.75,
                        )
                    )
                    break

        return violations

    def analyze_brady_giglio(self, documents: List[str], context: Dict) -> List[Violation]:
        """
        Check for Brady/Giglio material (exculpatory evidence)

        Detects:
        - Withheld exculpatory evidence
        - Undisclosed impeachment material
        - Witness credibility issues
        - Deals with witnesses
        """
        violations = []

        # Keywords indicating potential Brady material
        brady_indicators = [
            r"inconsistent.*statement",
            r"recant|changed.*story",
            r"unreliable witness",
            r"credibility.*issue",
            r"deal.*testimony",
            r"immunity.*granted",
            r"charges.*dropped",
            r"alternative.*suspect",
            r"exculpatory",
            r"alibi.*evidence",
        ]

        for doc in documents:
            for indicator in brady_indicators:
                if re.search(indicator, doc, re.IGNORECASE):
                    violations.append(
                        Violation(
                            violation_type=ViolationType.BRADY_GIGLIO,
                            severity=ViolationSeverity.CRITICAL,
                            title="Potential Brady/Giglio Material",
                            description=f"Document contains potential exculpatory/impeachment evidence: {indicator}",
                            evidence_reference=context.get("document_id", "Unknown"),
                            legal_basis="Brady v. Maryland, 373 U.S. 83 (1963); Giglio v. United States, 405 U.S. 150 (1972)",
                            case_law_support=[
                                "Brady v. Maryland, 373 U.S. 83 (1963)",
                                "Giglio v. United States, 405 U.S. 150 (1972)",
                                "Kyles v. Whitley, 514 U.S. 419 (1995)",
                                "Smith v. Cain, 565 U.S. 73 (2012)",
                            ],
                            recommended_action="Immediately request disclosure of all Brady/Giglio material. File motion to compel if not provided.",
                            confidence=0.80,
                        )
                    )

        return violations


class CaseLawDatabase:
    """Database of relevant case law and precedents"""

    def __init__(self):
        self.cases = self._load_precedents()

    def _load_precedents(self) -> Dict[str, List[CaseLawPrecedent]]:
        """Load case law database"""
        return {
            "miranda": [
                CaseLawPrecedent(
                    case_name="Miranda v. Arizona",
                    citation="384 U.S. 436 (1966)",
                    year=1966,
                    jurisdiction="federal",
                    holding="Suspects must be warned of rights before custodial interrogation",
                    relevance_score=1.0,
                    key_facts=[
                        "Custodial interrogation",
                        "No warning of rights",
                        "Coercive police environment",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Edwards v. Arizona",
                    citation="451 U.S. 477 (1981)",
                    year=1981,
                    jurisdiction="federal",
                    holding="Once suspect invokes right to counsel, questioning must cease",
                    relevance_score=0.95,
                    key_facts=[
                        "Invocation of right to counsel",
                        "Continued interrogation prohibited",
                        "Edwards rule",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Berghuis v. Thompkins",
                    citation="560 U.S. 370 (2010)",
                    year=2010,
                    jurisdiction="federal",
                    holding="Suspect must unambiguously invoke Miranda rights",
                    relevance_score=0.90,
                    key_facts=[
                        "Ambiguous invocation insufficient",
                        "Silence not invocation",
                        "Must be unambiguous",
                    ],
                ),
            ],
            "fourth_amendment": [
                CaseLawPrecedent(
                    case_name="Katz v. United States",
                    citation="389 U.S. 347 (1967)",
                    year=1967,
                    jurisdiction="federal",
                    holding="Fourth Amendment protects reasonable expectation of privacy",
                    relevance_score=1.0,
                    key_facts=[
                        "Reasonable expectation of privacy",
                        "Warrantless wiretapping",
                        "Privacy not limited to property",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Riley v. California",
                    citation="573 U.S. 373 (2014)",
                    year=2014,
                    jurisdiction="federal",
                    holding="Warrant required to search cell phones incident to arrest",
                    relevance_score=0.95,
                    key_facts=[
                        "Digital privacy",
                        "Cell phone search requires warrant",
                        "Search incident to arrest exception limited",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Terry v. Ohio",
                    citation="392 U.S. 1 (1968)",
                    year=1968,
                    jurisdiction="federal",
                    holding="Officer may conduct pat-down search with reasonable suspicion",
                    relevance_score=0.90,
                    key_facts=["Reasonable suspicion standard", "Stop and frisk", "Officer safety"],
                ),
            ],
            "brady": [
                CaseLawPrecedent(
                    case_name="Brady v. Maryland",
                    citation="373 U.S. 83 (1963)",
                    year=1963,
                    jurisdiction="federal",
                    holding="Prosecution must disclose material exculpatory evidence",
                    relevance_score=1.0,
                    key_facts=[
                        "Exculpatory evidence",
                        "Due process violation",
                        "Materiality standard",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Giglio v. United States",
                    citation="405 U.S. 150 (1972)",
                    year=1972,
                    jurisdiction="federal",
                    holding="Impeachment evidence must be disclosed",
                    relevance_score=0.95,
                    key_facts=[
                        "Witness credibility",
                        "Impeachment material",
                        "Deals with witnesses",
                    ],
                ),
                CaseLawPrecedent(
                    case_name="Kyles v. Whitley",
                    citation="514 U.S. 419 (1995)",
                    year=1995,
                    jurisdiction="federal",
                    holding="Prosecution has duty to learn of favorable evidence known to police",
                    relevance_score=0.90,
                    key_facts=[
                        "Prosecution's duty to investigate",
                        "Police knowledge imputed",
                        "Materiality analysis",
                    ],
                ),
            ],
        }

    def find_relevant_cases(
        self, violation_type: ViolationType, facts: List[str]
    ) -> List[CaseLawPrecedent]:
        """Find case law relevant to specific violation"""
        category_map = {
            ViolationType.MIRANDA: "miranda",
            ViolationType.FOURTH_AMENDMENT: "fourth_amendment",
            ViolationType.BRADY_GIGLIO: "brady",
        }

        category = category_map.get(violation_type, "")
        return self.cases.get(category, [])


class ViolationScanner:
    """Main violation scanner orchestrator"""

    def __init__(self):
        self.constitutional_analyzer = ConstitutionalRightsAnalyzer()
        self.case_law_db = CaseLawDatabase()

    def scan_transcript(self, transcript: str, context: Dict) -> Dict[str, Any]:
        """
        Comprehensive scan of transcript for violations

        Args:
            transcript: Text transcript of evidence
            context: Additional context (evidence_id, case_number, etc.)

        Returns:
            Dict with violations, case law, and recommendations
        """
        all_violations = []

        # Miranda analysis
        all_violations.extend(
            self.constitutional_analyzer.analyze_miranda_compliance(transcript, context)
        )

        # Fourth Amendment analysis
        all_violations.extend(
            self.constitutional_analyzer.analyze_fourth_amendment(transcript, context)
        )

        # Get supporting case law for each violation
        for violation in all_violations:
            violation.case_law_support = [
                case.citation
                for case in self.case_law_db.find_relevant_cases(violation.violation_type, [])
            ]

        # Categorize by severity
        critical = [v for v in all_violations if v.severity == ViolationSeverity.CRITICAL]
        high = [v for v in all_violations if v.severity == ViolationSeverity.HIGH]
        medium = [v for v in all_violations if v.severity == ViolationSeverity.MEDIUM]
        low = [v for v in all_violations if v.severity == ViolationSeverity.LOW]

        return {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "evidence_id": context.get("evidence_id", "Unknown"),
            "total_violations": len(all_violations),
            "violations_by_severity": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
            },
            "critical_violations": [self._violation_to_dict(v) for v in critical],
            "high_violations": [self._violation_to_dict(v) for v in high],
            "medium_violations": [self._violation_to_dict(v) for v in medium],
            "low_violations": [self._violation_to_dict(v) for v in low],
            "recommended_motions": self._generate_motion_recommendations(all_violations),
            "case_law_citations": self._collect_case_law(all_violations),
            "summary": self._generate_summary(all_violations),
        }

    def scan_documents(self, documents: List[str], context: Dict) -> Dict[str, Any]:
        """Scan legal documents for Brady/Giglio material"""
        violations = self.constitutional_analyzer.analyze_brady_giglio(documents, context)

        return {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "documents_scanned": len(documents),
            "total_violations": len(violations),
            "violations": [self._violation_to_dict(v) for v in violations],
            "case_law_citations": self._collect_case_law(violations),
        }

    def _violation_to_dict(self, violation: Violation) -> Dict:
        """Convert violation to dictionary"""
        return {
            "type": violation.violation_type.value,
            "severity": violation.severity.value,
            "title": violation.title,
            "description": violation.description,
            "evidence_reference": violation.evidence_reference,
            "legal_basis": violation.legal_basis,
            "case_law_support": violation.case_law_support,
            "recommended_action": violation.recommended_action,
            "confidence": violation.confidence,
        }

    def _generate_motion_recommendations(self, violations: List[Violation]) -> List[Dict]:
        """Generate motion filing recommendations"""
        motions = []

        # Motion to suppress based on Miranda
        miranda_violations = [v for v in violations if v.violation_type == ViolationType.MIRANDA]
        if miranda_violations:
            motions.append(
                {
                    "motion_type": "Motion to Suppress Statements",
                    "basis": "Miranda violations",
                    "violations": len(miranda_violations),
                    "priority": "critical",
                    "template": "motion_suppress_statements",
                }
            )

        # Motion to suppress based on Fourth Amendment
        fourth_violations = [
            v for v in violations if v.violation_type == ViolationType.FOURTH_AMENDMENT
        ]
        if fourth_violations:
            motions.append(
                {
                    "motion_type": "Motion to Suppress Evidence",
                    "basis": "Fourth Amendment violations",
                    "violations": len(fourth_violations),
                    "priority": "critical",
                    "template": "motion_suppress_evidence",
                }
            )

        # Brady motion
        brady_violations = [v for v in violations if v.violation_type == ViolationType.BRADY_GIGLIO]
        if brady_violations:
            motions.append(
                {
                    "motion_type": "Motion to Compel Discovery",
                    "basis": "Brady/Giglio material",
                    "violations": len(brady_violations),
                    "priority": "high",
                    "template": "motion_compel_brady",
                }
            )

        return motions

    def _collect_case_law(self, violations: List[Violation]) -> List[str]:
        """Collect all cited case law"""
        citations = set()
        for violation in violations:
            citations.update(violation.case_law_support)
        return sorted(list(citations))

    def _generate_summary(self, violations: List[Violation]) -> str:
        """Generate executive summary of violations"""
        if not violations:
            return "No violations detected in evidence."

        critical_count = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL])
        high_count = len([v for v in violations if v.severity == ViolationSeverity.HIGH])

        summary = f"Scan detected {len(violations)} potential violations. "

        if critical_count > 0:
            summary += f"{critical_count} CRITICAL violations found that may result in suppression of evidence or dismissal. "

        if high_count > 0:
            summary += f"{high_count} HIGH severity violations requiring immediate attention. "

        summary += "Review detailed violations and consider filing recommended motions."

        return summary


# Example usage and testing
if __name__ == "__main__":
    # Sample transcript with violations
    sample_transcript = """
    Officer: Step out of the vehicle.
    Suspect: What's this about?
    Officer: We're going to search your car.
    Suspect: Do you have a warrant?
    Officer: We don't need one. You can either let us search or we'll make it harder on you.
    Suspect: I guess, go ahead.
    Officer: Good choice. Now, where were you tonight?
    Suspect: I don't want to say anything. I want a lawyer.
    Officer: Come on, just tell me where you were. It'll help you out.
    Suspect: I want my lawyer.
    Officer: Fine, but you're making this worse. Where were you at 10 PM?
    """

    scanner = ViolationScanner()
    results = scanner.scan_transcript(
        sample_transcript, {"evidence_id": "BWC-2024-001", "case_number": "CR-2024-123"}
    )

    print("=" * 80)
    print("VIOLATION SCAN RESULTS")
    print("=" * 80)
    print(f"\nEvidence ID: {results['evidence_id']}")
    print(f"Total Violations: {results['total_violations']}")
    print(f"\nSummary: {results['summary']}")

    print("\n" + "=" * 80)
    print("CRITICAL VIOLATIONS")
    print("=" * 80)
    for v in results["critical_violations"]:
        print(f"\n{v['title']}")
        print(f"  Severity: {v['severity'].upper()}")
        print(f"  Type: {v['type']}")
        print(f"  Description: {v['description']}")
        print(f"  Legal Basis: {v['legal_basis']}")
        print(f"  Action: {v['recommended_action']}")

    print("\n" + "=" * 80)
    print("RECOMMENDED MOTIONS")
    print("=" * 80)
    for motion in results["recommended_motions"]:
        print(f"\n{motion['motion_type']}")
        print(f"  Basis: {motion['basis']}")
        print(f"  Priority: {motion['priority'].upper()}")

    print("\n" + "=" * 80)
    print("CASE LAW SUPPORT")
    print("=" * 80)
    for citation in results["case_law_citations"]:
        print(f"  • {citation}")


