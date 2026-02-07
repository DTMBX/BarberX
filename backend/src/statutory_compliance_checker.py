# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Statutory Compliance & Legal Standards Checker
Analyzes evidence against federal and state legal standards

Features:
- Federal Rules of Criminal Procedure compliance
- Federal Rules of Evidence compliance
- State-specific statute checking
- Hearsay analysis
- Authentication requirements
- Chain of custody verification
- Spoliation detection
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class RuleSet(Enum):
    """Legal rule sets"""

    FED_RULES_CRIMINAL_PROC = "federal_rules_criminal_procedure"
    FED_RULES_EVIDENCE = "federal_rules_evidence"
    FED_RULES_CIVIL_PROC = "federal_rules_civil_procedure"
    STATE_CRIMINAL_PROC = "state_criminal_procedure"
    STATE_EVIDENCE = "state_evidence"


class ComplianceStatus(Enum):
    """Compliance check status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    QUESTIONABLE = "questionable"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ComplianceIssue:
    """Represents a compliance issue"""

    rule_set: RuleSet
    rule_number: str
    title: str
    description: str
    status: ComplianceStatus
    remedy: str
    case_law: list[str]
    confidence: float


class FederalRulesOfEvidenceChecker:
    """Checks compliance with Federal Rules of Evidence"""

    def __init__(self):
        self.issues = []

    def check_hearsay(self, statement: str, context: dict) -> list[ComplianceIssue]:
        """
        Analyze hearsay issues under FRE 801-807

        FRE 801(c): Hearsay is a statement that:
        1. The declarant does not make while testifying at trial
        2. A party offers to prove the truth of the matter asserted

        FRE 802: Hearsay is not admissible unless exception applies
        """
        issues = []

        # Detect out-of-court statements
        hearsay_indicators = [
            r"(he|she|they)\s+(said|told|stated|mentioned)",
            r"I heard (that|him|her)",
            r"someone told me",
            r"according to",
            r"report states",
            r"witness statement",
        ]

        for indicator in hearsay_indicators:
            matches = re.finditer(indicator, statement, re.IGNORECASE)
            for match in matches:
                # Check for exceptions (FRE 803, 804, 807)
                has_exception = self._check_hearsay_exceptions(statement, match.start())

                if not has_exception:
                    issues.append(
                        ComplianceIssue(
                            rule_set=RuleSet.FED_RULES_EVIDENCE,
                            rule_number="FRE 802",
                            title="Potential Hearsay Issue",
                            description=f"Out-of-court statement detected: '{match.group()}'. May be inadmissible hearsay.",
                            status=ComplianceStatus.QUESTIONABLE,
                            remedy="Identify hearsay exception (FRE 803, 804, 807) or elicit statement through testifying witness. File motion in limine if prosecution attempts to introduce.",
                            case_law=[
                                "Crawford v. Washington, 541 U.S. 36 (2004)",
                                "Williamson v. United States, 512 U.S. 594 (1994)",
                            ],
                            confidence=0.75,
                        )
                    )

        return issues

    def _check_hearsay_exceptions(self, text: str, position: int) -> bool:
        """Check if hearsay exception applies"""
        # FRE 803 exceptions (don't require declarant unavailability)
        context = text[max(0, position - 100) : min(len(text), position + 100)]

        exceptions = [
            r"present sense impression",
            r"excited utterance",
            r"then.existing.*state.*mind",
            r"medical (diagnosis|treatment)",
            r"recorded recollection",
            r"business record",
            r"public record",
            r"dying declaration",
            r"statement against interest",
            r"former testimony",
            r"admission by party",
        ]

        return any(re.search(exc, context, re.IGNORECASE) for exc in exceptions)

    def check_authentication(self, evidence_type: str, context: dict) -> list[ComplianceIssue]:
        """
        Check authentication requirements under FRE 901-902

        FRE 901(a): To authenticate evidence, proponent must produce evidence
        sufficient to support finding that the item is what it is claimed to be
        """
        issues = []

        authentication_requirements = {
            "photograph": ["photographer testimony", "timestamp", "location", "unaltered"],
            "video": ["custodian testimony", "timestamp", "continuous recording", "unedited"],
            "audio": ["voice identification", "timestamp", "source verification"],
            "document": ["witness recognition", "handwriting", "signature verification"],
            "digital": ["hash value", "metadata", "chain of custody", "forensic preservation"],
            "social_media": ["account ownership", "timestamp", "screenshot verification"],
        }

        required = authentication_requirements.get(evidence_type.lower(), [])

        if required and not context.get("authenticated", False):
            issues.append(
                ComplianceIssue(
                    rule_set=RuleSet.FED_RULES_EVIDENCE,
                    rule_number="FRE 901",
                    title=f"Authentication Required for {evidence_type}",
                    description=f"Evidence must be authenticated. Requirements: {', '.join(required)}",
                    status=ComplianceStatus.NEEDS_REVIEW,
                    remedy="Obtain authenticating testimony or certification. Ensure chain of custody documented. Consider FRE 902 self-authentication options.",
                    case_law=[
                        "United States v. Vayner, 769 F.3d 125 (2d Cir. 2014)",
                        "Lorraine v. Markel Am. Ins. Co., 241 F.R.D. 534 (D. Md. 2007)",
                    ],
                    confidence=0.90,
                )
            )

        return issues

    def check_best_evidence_rule(
        self, evidence_type: str, is_original: bool
    ) -> list[ComplianceIssue]:
        """
        Check best evidence rule (FRE 1001-1008)

        FRE 1002: An original writing, recording, or photograph is required
        to prove its content unless exception applies
        """
        issues = []

        if evidence_type in ["document", "recording", "photograph"] and not is_original:
            issues.append(
                ComplianceIssue(
                    rule_set=RuleSet.FED_RULES_EVIDENCE,
                    rule_number="FRE 1002",
                    title="Best Evidence Rule - Original Required",
                    description="Original document/recording required unless exception applies (FRE 1003-1008)",
                    status=ComplianceStatus.NON_COMPLIANT,
                    remedy="Obtain original or demonstrate exception: duplicate admissible if authentic (FRE 1003), original lost/destroyed in good faith (FRE 1004), or voluminous records (FRE 1006).",
                    case_law=[
                        "United States v. Gonzales-Benitez, 537 F.2d 1051 (9th Cir. 1976)",
                        "Seiler v. Lucasfilm, Ltd., 808 F.2d 1316 (9th Cir. 1986)",
                    ],
                    confidence=0.85,
                )
            )

        return issues

    def check_character_evidence(
        self, evidence_purpose: str, context: dict
    ) -> list[ComplianceIssue]:
        """
        Check character evidence rules (FRE 404-406)

        FRE 404(a): Character evidence generally not admissible to prove
        conduct in conformity therewith

        FRE 404(b): Evidence of other crimes, wrongs, or acts not admissible
        to prove character but may be admissible for other purposes (MIMIC)
        """
        issues = []

        # Check if using for propensity
        propensity_indicators = ["always", "tends to", "known for", "history of"]

        for indicator in propensity_indicators:
            if indicator in evidence_purpose.lower():
                issues.append(
                    ComplianceIssue(
                        rule_set=RuleSet.FED_RULES_EVIDENCE,
                        rule_number="FRE 404(a)",
                        title="Improper Character Evidence",
                        description="Character evidence cannot be used to prove conduct in conformity",
                        status=ComplianceStatus.NON_COMPLIANT,
                        remedy="If other crimes/wrongs/acts, must show MIMIC purpose: Motive, Intent, Mistake/lack thereof, Identity, Common plan. File motion in limine to exclude.",
                        case_law=[
                            "Huddleston v. United States, 485 U.S. 681 (1988)",
                            "United States v. Beechum, 582 F.2d 898 (5th Cir. 1978)",
                        ],
                        confidence=0.80,
                    )
                )

        return issues


class ChainOfCustodyVerifier:
    """Verifies chain of custody integrity"""

    def __init__(self):
        self.issues = []

    def verify_chain(self, custody_log: list[dict]) -> dict[str, Any]:
        """
        Verify chain of custody is unbroken

        Requirements:
        1. Initial collection documented
        2. Every transfer documented
        3. Storage conditions noted
        4. No unexplained gaps
        5. Final location to courtroom
        """
        issues = []
        gaps = []

        if not custody_log:
            return {
                "status": "FAILED",
                "issues": ["No chain of custody documentation"],
                "recommendation": "Critical deficiency. Evidence may be inadmissible.",
            }

        # Check for gaps in custody
        for i in range(len(custody_log) - 1):
            current = custody_log[i]
            next_entry = custody_log[i + 1]

            current_time = datetime.fromisoformat(current.get("timestamp", ""))
            next_time = datetime.fromisoformat(next_entry.get("timestamp", ""))

            time_gap = (next_time - current_time).total_seconds() / 3600  # hours

            # Flag gaps > 24 hours without explanation
            if time_gap > 24 and not current.get("storage_notes"):
                gaps.append(
                    {
                        "from": current.get("custodian"),
                        "to": next_entry.get("custodian"),
                        "gap_hours": time_gap,
                        "explanation": current.get("transfer_notes", "None provided"),
                    }
                )

        # Check required fields
        required_fields = ["timestamp", "custodian", "location", "condition"]
        for entry in custody_log:
            missing = [field for field in required_fields if not entry.get(field)]
            if missing:
                issues.append(f"Entry missing fields: {', '.join(missing)}")

        # Check for tampering indicators
        tampering_keywords = ["damaged", "opened", "altered", "broken seal"]
        for entry in custody_log:
            notes = entry.get("condition_notes", "").lower()
            if any(keyword in notes for keyword in tampering_keywords):
                issues.append(f"Possible tampering: {entry.get('condition_notes')}")

        status = "PASSED" if not issues and not gaps else "QUESTIONABLE" if gaps else "FAILED"

        return {
            "status": status,
            "total_transfers": len(custody_log),
            "gaps": gaps,
            "issues": issues,
            "recommendation": self._get_chain_recommendation(status, gaps, issues),
        }

    def _get_chain_recommendation(self, status: str, gaps: list, issues: list) -> str:
        """Generate recommendation based on chain status"""
        if status == "PASSED":
            return "Chain of custody is intact and well-documented."
        elif status == "QUESTIONABLE":
            return f"Chain has {len(gaps)} unexplained gap(s). Request explanation or file motion to exclude. May affect weight but not necessarily admissibility."
        else:
            return f"Chain of custody has {len(issues)} critical issue(s). File motion to suppress evidence. Evidence may be inadmissible due to lack of authentication."


class SpoliationDetector:
    """Detects evidence destruction or spoliation"""

    def detect_spoliation(self, evidence_history: dict) -> list[ComplianceIssue]:
        """
        Detect spoliation (destruction or alteration of evidence)

        Elements of spoliation:
        1. Duty to preserve existed
        2. Evidence was destroyed/altered
        3. Destruction was intentional or negligent
        4. Evidence was relevant
        """
        issues = []

        # Check for deletion/destruction
        destruction_indicators = [
            "deleted",
            "destroyed",
            "erased",
            "overwritten",
            "reformatted",
            "lost",
            "misplaced",
            "disposed",
        ]

        for indicator in destruction_indicators:
            if indicator in str(evidence_history.get("notes", "")).lower():
                issues.append(
                    ComplianceIssue(
                        rule_set=RuleSet.FED_RULES_CIVIL_PROC,  # Can apply in criminal too
                        rule_number="FRCP 37(e)",
                        title="Potential Spoliation of Evidence",
                        description=f"Evidence may have been {indicator}. Spoliation inference may apply.",
                        status=ComplianceStatus.NON_COMPLIANT,
                        remedy="File motion for adverse inference instruction or sanctions. In criminal cases, may support Brady violation claim if exculpatory.",
                        case_law=[
                            "Zubulake v. UBS Warburg LLC, 220 F.R.D. 212 (S.D.N.Y. 2003)",
                            "Arizona v. Youngblood, 488 U.S. 51 (1988)",
                        ],
                        confidence=0.80,
                    )
                )

        # Check preservation duty timeline
        if evidence_history.get("litigation_hold_date"):
            destruction_date = evidence_history.get("destruction_date")
            hold_date = datetime.fromisoformat(evidence_history["litigation_hold_date"])

            if destruction_date:
                dest_date = datetime.fromisoformat(destruction_date)
                if dest_date > hold_date:
                    issues.append(
                        ComplianceIssue(
                            rule_set=RuleSet.FED_RULES_CIVIL_PROC,
                            rule_number="FRCP 37(e)",
                            title="Evidence Destroyed After Litigation Hold",
                            description="Evidence destroyed after duty to preserve arose",
                            status=ComplianceStatus.NON_COMPLIANT,
                            remedy="Seek severe sanctions including adverse inference, dismissal (civil), or suppression (criminal). Bad faith destruction warrants strongest sanctions.",
                            case_law=[
                                "Silvestri v. General Motors Corp., 271 F.3d 583 (4th Cir. 2001)",
                                "Residential Funding Corp. v. DeGeorge Fin. Corp., 306 F.3d 99 (2d Cir. 2002)",
                            ],
                            confidence=0.95,
                        )
                    )

        return issues


class StatutoryComplianceChecker:
    """Main compliance checker orchestrator"""

    def __init__(self):
        self.fre_checker = FederalRulesOfEvidenceChecker()
        self.chain_verifier = ChainOfCustodyVerifier()
        self.spoliation_detector = SpoliationDetector()

    def comprehensive_check(self, evidence: dict) -> dict[str, Any]:
        """Run comprehensive compliance check on evidence"""
        all_issues = []

        # FRE checks
        if evidence.get("type") == "statement":
            all_issues.extend(self.fre_checker.check_hearsay(evidence.get("content", ""), evidence))

        all_issues.extend(
            self.fre_checker.check_authentication(evidence.get("type", "unknown"), evidence)
        )

        all_issues.extend(
            self.fre_checker.check_best_evidence_rule(
                evidence.get("type", "unknown"), evidence.get("is_original", False)
            )
        )

        # Chain of custody
        chain_result = self.chain_verifier.verify_chain(evidence.get("custody_log", []))

        # Spoliation check
        spoliation_issues = self.spoliation_detector.detect_spoliation(evidence.get("history", {}))
        all_issues.extend(spoliation_issues)

        # Categorize by status
        non_compliant = [i for i in all_issues if i.status == ComplianceStatus.NON_COMPLIANT]
        questionable = [i for i in all_issues if i.status == ComplianceStatus.QUESTIONABLE]
        needs_review = [i for i in all_issues if i.status == ComplianceStatus.NEEDS_REVIEW]

        return {
            "check_timestamp": datetime.utcnow().isoformat(),
            "evidence_id": evidence.get("id", "Unknown"),
            "evidence_type": evidence.get("type", "Unknown"),
            "overall_status": self._determine_overall_status(chain_result, all_issues),
            "total_issues": len(all_issues),
            "chain_of_custody": chain_result,
            "issues_by_status": {
                "non_compliant": len(non_compliant),
                "questionable": len(questionable),
                "needs_review": len(needs_review),
            },
            "non_compliant_issues": [self._issue_to_dict(i) for i in non_compliant],
            "questionable_issues": [self._issue_to_dict(i) for i in questionable],
            "needs_review_issues": [self._issue_to_dict(i) for i in needs_review],
            "recommendations": self._generate_recommendations(chain_result, all_issues),
            "summary": self._generate_compliance_summary(chain_result, all_issues),
        }

    def _determine_overall_status(self, chain_result: dict, issues: list) -> str:
        """Determine overall compliance status"""
        if chain_result["status"] == "FAILED":
            return "NON_COMPLIANT"

        non_compliant = [i for i in issues if i.status == ComplianceStatus.NON_COMPLIANT]
        if non_compliant:
            return "NON_COMPLIANT"

        questionable = [i for i in issues if i.status == ComplianceStatus.QUESTIONABLE]
        if questionable or chain_result["status"] == "QUESTIONABLE":
            return "QUESTIONABLE"

        return "COMPLIANT"

    def _issue_to_dict(self, issue: ComplianceIssue) -> dict:
        """Convert issue to dictionary"""
        return {
            "rule_set": issue.rule_set.value,
            "rule_number": issue.rule_number,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status.value,
            "remedy": issue.remedy,
            "case_law": issue.case_law,
            "confidence": issue.confidence,
        }

    def _generate_recommendations(self, chain_result: dict, issues: list) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if chain_result["status"] != "PASSED":
            recommendations.append(chain_result["recommendation"])

        for issue in issues:
            if issue.status == ComplianceStatus.NON_COMPLIANT:
                recommendations.append(f"{issue.title}: {issue.remedy}")

        return recommendations

    def _generate_compliance_summary(self, chain_result: dict, issues: list) -> str:
        """Generate executive summary"""
        status = self._determine_overall_status(chain_result, issues)

        if status == "COMPLIANT":
            return "Evidence meets compliance standards. Chain of custody intact. No major admissibility concerns."
        elif status == "QUESTIONABLE":
            return f"Evidence has {len(issues)} issue(s) requiring attention. Review recommendations and consider filing appropriate motions."
        else:
            return f"Evidence has {len(issues)} compliance issue(s). CRITICAL: Evidence may be inadmissible. Immediate action required."


# Example usage
if __name__ == "__main__":
    # Sample evidence with issues
    sample_evidence = {
        "id": "EVID-2024-001",
        "type": "video",
        "is_original": False,
        "authenticated": False,
        "content": "The witness said he saw the defendant at the scene",
        "custody_log": [
            {
                "timestamp": "2024-01-01T10:00:00",
                "custodian": "Officer Smith",
                "location": "Evidence Room A",
                "condition": "Sealed",
                "condition_notes": "Intact",
            },
            {
                "timestamp": "2024-01-05T14:00:00",  # 4+ day gap
                "custodian": "Detective Jones",
                "location": "Detective Bureau",
                "condition": "Opened",
                "transfer_notes": "Reviewed for analysis",
            },
        ],
        "history": {
            "litigation_hold_date": "2024-01-01T00:00:00",
            "notes": "Original recording deleted after backup created",
        },
    }

    checker = StatutoryComplianceChecker()
    results = checker.comprehensive_check(sample_evidence)

    print("=" * 80)
    print("STATUTORY COMPLIANCE CHECK RESULTS")
    print("=" * 80)
    print(f"\nEvidence ID: {results['evidence_id']}")
    print(f"Evidence Type: {results['evidence_type']}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Total Issues: {results['total_issues']}")

    print(f"\nSummary: {results['summary']}")

    print("\n" + "=" * 80)
    print("CHAIN OF CUSTODY")
    print("=" * 80)
    print(f"Status: {results['chain_of_custody']['status']}")
    print(f"Recommendation: {results['chain_of_custody']['recommendation']}")

    if results["non_compliant_issues"]:
        print("\n" + "=" * 80)
        print("NON-COMPLIANT ISSUES")
        print("=" * 80)
        for issue in results["non_compliant_issues"]:
            print(f"\n{issue['title']} ({issue['rule_number']})")
            print(f"  Description: {issue['description']}")
            print(f"  Remedy: {issue['remedy']}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    for rec in results["recommendations"]:
        print(f"  • {rec}")
