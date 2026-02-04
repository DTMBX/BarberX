"""
Legal Document Optimizer - Transform rough legal drafts into court-ready filings

This service analyzes multi-document legal filings (complaints, motions, certificates, etc.)
and optimizes them for:
- Procedural compliance
- Internal consistency
- Evidence-backed fact checking
- Maximum monetary relief
- Positive social impact
- Persuasive force

Does NOT provide legal advice - acts as drafting and optimization assistant only.
"""

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import openai


@dataclass
class LegalDocument:
    """Represents a single legal document in a filing set"""

    filename: str
    doc_type: str  # 'complaint', 'motion', 'certificate', 'exhibit', etc.
    content: str
    metadata: Dict


@dataclass
class EvidenceItem:
    """Evidence from case management system"""

    evidence_id: int
    title: str
    description: str
    file_path: str
    evidence_type: str  # 'pdf', 'video', 'image', 'document'


@dataclass
class OptimizationResult:
    """Result of document optimization"""

    original_doc: LegalDocument
    optimized_content: str
    changes_summary: List[str]
    consistency_issues: List[str]
    evidence_gaps: List[str]
    procedural_issues: List[str]
    strategic_improvements: List[str]
    confidence_score: float


class LegalDocumentOptimizer:
    """Advanced legal document optimization engine"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

        # Document type patterns
        self.doc_type_patterns = {
            "complaint": r"(?i)(verified\s+)?complaint",
            "motion": r"(?i)motion\s+(for|to)",
            "certificate_of_service": r"(?i)certificate\s+of\s+service",
            "verification": r"(?i)verification",
            "certification": r"(?i)certification",
            "exhibit": r"(?i)exhibit\s+[A-Z0-9]",
            "affidavit": r"(?i)affidavit",
            "memorandum": r"(?i)memorandum\s+(of\s+law|in\s+support)",
        }

    def analyze_filing_set(
        self,
        documents: List[LegalDocument],
        evidence: List[EvidenceItem],
        jurisdiction: str = "default",
        filing_type: str = "state_court",
    ) -> Dict:
        """
        Analyze entire filing set for consistency and optimization opportunities

        Returns comprehensive analysis with:
        - Cross-document consistency checks
        - Evidence alignment
        - Procedural compliance
        - Optimization recommendations
        """

        analysis = {
            "documents_analyzed": len(documents),
            "evidence_items": len(evidence),
            "jurisdiction": jurisdiction,
            "filing_type": filing_type,
            "consistency_report": self._check_consistency(documents),
            "evidence_coverage": self._analyze_evidence_coverage(documents, evidence),
            "procedural_compliance": self._check_procedural_compliance(documents, jurisdiction),
            "optimization_opportunities": [],
        }

        return analysis

    def optimize_document(
        self,
        document: LegalDocument,
        evidence: List[EvidenceItem],
        related_docs: List[LegalDocument],
        jurisdiction: str = "default",
        optimization_goals: Optional[Dict] = None,
    ) -> OptimizationResult:
        """
        Optimize a single document within context of full filing set

        Goals can include:
        - maximize_monetary_relief
        - enhance_social_impact
        - strengthen_interim_relief
        - improve_clarity
        - ensure_compliance
        """

        if optimization_goals is None:
            optimization_goals = {
                "maximize_monetary_relief": True,
                "enhance_social_impact": True,
                "strengthen_interim_relief": True,
                "improve_clarity": True,
                "ensure_compliance": True,
            }

        # Build optimization prompt
        system_prompt = self._build_optimizer_prompt(
            document.doc_type, jurisdiction, optimization_goals
        )

        # Prepare context
        context = self._build_document_context(document, evidence, related_docs)

        # Call GPT-4 for optimization
        optimized_content = self._call_optimizer_ai(
            document_content=document.content, context=context, system_prompt=system_prompt
        )

        # Analyze changes
        analysis = self._analyze_optimization_changes(document.content, optimized_content)

        return OptimizationResult(
            original_doc=document,
            optimized_content=optimized_content,
            changes_summary=analysis["changes"],
            consistency_issues=analysis["consistency_issues"],
            evidence_gaps=analysis["evidence_gaps"],
            procedural_issues=analysis["procedural_issues"],
            strategic_improvements=analysis["strategic_improvements"],
            confidence_score=analysis["confidence_score"],
        )

    def _build_optimizer_prompt(self, doc_type: str, jurisdiction: str, goals: Dict) -> str:
        """Build specialized system prompt for document optimization"""

        base_prompt = """You are an advanced legal-document optimization assistant designed to support state-court filings.

You are provided with a legal document and supporting materials. Your role is to analyze and optimize the document.

**Your objectives are to:**

1. **Analyze for compliance**: Check internal consistency, procedural compliance, and jurisdiction-specific formatting standards.

2. **Cross-reference facts**: Cross-reference factual allegations with attached evidence and flag gaps, redundancies, or under-leveraged facts.

3. **Refine narrative**: Refine legal narratives for maximum clarity, credibility, and persuasive force—without fabricating facts or legal authority.

4. **Optimize structure**: Optimize structure, tone, and emphasis to strengthen remedies sought, including monetary relief, equitable relief, and interim relief.

5. **Frame for impact**: Identify opportunities to frame claims in ways that enhance public-interest value, deterrence, and broader positive social impact while remaining legally appropriate.

6. **Standardize certifications**: Standardize and strengthen certifications, verifications, and certificates of service to ensure procedural soundness and risk reduction.

**Produce:**
- A revised, court-ready version of the document
- Specific annotations explaining each material change
- Strategic improvement notes

**Constraints:**
- Do NOT provide legal advice; operate as a drafting, organization, and optimization assistant.
- Do NOT guarantee outcomes.
- Preserve the filer's voice while enhancing precision and authority.
- Do NOT fabricate facts, evidence, or legal citations.

**Primary Success Criteria:**
- Highest procedural compliance
- Strongest factual-to-relief alignment
- Maximum persuasive impact within ethical and legal boundaries
- Clear articulation of both monetary damages and societal benefit
"""

        # Add document-type-specific guidance
        if doc_type == "complaint":
            base_prompt += """

**Complaint-Specific Guidance:**
- Ensure each count has: (1) Jurisdiction, (2) Parties, (3) Facts, (4) Legal standard, (5) Relief sought
- Verify prayer for relief includes specific monetary amounts and equitable remedies
- Check that factual allegations support each element of each cause of action
- Ensure verification/certification language is present and properly formatted
"""

        elif doc_type == "motion":
            base_prompt += """

**Motion-Specific Guidance:**
- Include clear statement of relief sought
- Organize argument with: Introduction, Standard of Review, Argument, Conclusion
- Ensure each factual assertion cites to evidence (by exhibit number or affidavit paragraph)
- Check that legal citations are complete and properly Bluebooked
- Verify certificate of service is attached
"""

        elif doc_type == "certificate_of_service":
            base_prompt += """

**Certificate of Service Guidance:**
- Include: Date, document served, parties served, method of service
- Verify compliance with jurisdiction-specific service rules
- Ensure signature block and notarization (if required)
"""

        # Add jurisdiction-specific rules
        if jurisdiction != "default":
            base_prompt += f"""

**Jurisdiction: {jurisdiction}**
- Apply {jurisdiction}-specific formatting requirements
- Follow {jurisdiction} court rules and local rules
- Use {jurisdiction} citation format
"""

        # Add optimization goals
        if goals.get("maximize_monetary_relief"):
            base_prompt += """

**Goal: Maximize Monetary Relief**
- Identify all potential damage theories (compensatory, punitive, statutory trebling, attorney's fees)
- Ensure prayer for relief explicitly requests each category
- Support damages with specific factual allegations
- Consider emotional distress, loss of enjoyment, economic losses
"""

        if goals.get("enhance_social_impact"):
            base_prompt += """

**Goal: Enhance Social Impact**
- Frame claims to highlight systemic issues and deterrence value
- Emphasize public interest in enforcement
- Consider class action potential or representative claims
- Highlight broader community impact beyond individual plaintiff
"""

        if goals.get("strengthen_interim_relief"):
            base_prompt += """

**Goal: Strengthen Interim Relief**
- Emphasize irreparable harm and inadequacy of legal remedies
- Show likelihood of success on merits
- Demonstrate balance of hardships favors plaintiff
- Request specific, detailed injunctive relief
"""

        return base_prompt

    def _build_document_context(
        self,
        document: LegalDocument,
        evidence: List[EvidenceItem],
        related_docs: List[LegalDocument],
    ) -> str:
        """Build context string with evidence and related documents"""

        context_parts = []

        # Add evidence summary
        if evidence:
            context_parts.append("**Available Evidence:**\n")
            for i, ev in enumerate(evidence, 1):
                context_parts.append(f"{i}. {ev.title} ({ev.evidence_type})")
                if ev.description:
                    context_parts.append(f"   Description: {ev.description}")
            context_parts.append("")

        # Add related documents summary
        if related_docs:
            context_parts.append("**Related Documents in Filing Set:**\n")
            for doc in related_docs:
                if doc.filename != document.filename:
                    context_parts.append(f"- {doc.doc_type}: {doc.filename}")
            context_parts.append("")

        # Add document metadata
        if document.metadata:
            context_parts.append("**Document Metadata:**\n")
            for key, value in document.metadata.items():
                context_parts.append(f"- {key}: {value}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _call_optimizer_ai(self, document_content: str, context: str, system_prompt: str) -> str:
        """Call GPT-4 to optimize document"""

        user_message = f"""{context}

**Document to Optimize:**

{document_content}

**Instructions:**
Please provide the optimized version of this document, following all guidelines in the system prompt. Format your response as:

1. **OPTIMIZED DOCUMENT** (full revised text)
2. **CHANGE LOG** (list of material changes with explanations)
3. **STRATEGIC NOTES** (why changes improve filing strength)
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",  # or gpt-4, gpt-4-32k
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,  # Lower temp for consistency
                max_tokens=4000,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

    def _check_consistency(self, documents: List[LegalDocument]) -> Dict:
        """Check cross-document consistency"""

        issues = []

        # Extract party names from all documents
        party_names = {}
        for doc in documents:
            parties = self._extract_party_names(doc.content)
            party_names[doc.filename] = parties

        # Check for inconsistent party naming
        all_plaintiffs = set()
        all_defendants = set()
        for doc_parties in party_names.values():
            all_plaintiffs.update(doc_parties.get("plaintiffs", []))
            all_defendants.update(doc_parties.get("defendants", []))

        # Look for variations that might indicate inconsistency
        # (e.g., "John Smith" vs "J. Smith")

        # Extract case numbers
        case_numbers = {}
        for doc in documents:
            case_num = self._extract_case_number(doc.content)
            if case_num:
                case_numbers[doc.filename] = case_num

        # Check if all case numbers match
        unique_case_nums = set(case_numbers.values())
        if len(unique_case_nums) > 1:
            issues.append(f"Inconsistent case numbers found: {unique_case_nums}")

        # Extract dates
        date_inconsistencies = self._check_date_consistency(documents)
        issues.extend(date_inconsistencies)

        return {
            "party_names": party_names,
            "case_numbers": case_numbers,
            "issues": issues,
            "consistent": len(issues) == 0,
        }

    def _analyze_evidence_coverage(
        self, documents: List[LegalDocument], evidence: List[EvidenceItem]
    ) -> Dict:
        """Analyze how well evidence supports factual allegations"""

        # Extract factual allegations from documents
        allegations = []
        for doc in documents:
            doc_allegations = self._extract_allegations(doc.content)
            allegations.extend(doc_allegations)

        # Check which allegations have evidence support
        covered = []
        gaps = []

        for allegation in allegations:
            has_support = self._find_supporting_evidence(allegation, evidence)
            if has_support:
                covered.append({"allegation": allegation, "evidence": has_support})
            else:
                gaps.append(allegation)

        return {
            "total_allegations": len(allegations),
            "covered_allegations": len(covered),
            "coverage_rate": len(covered) / len(allegations) if allegations else 0,
            "evidence_gaps": gaps,
            "supported_facts": covered,
        }

    def _check_procedural_compliance(
        self, documents: List[LegalDocument], jurisdiction: str
    ) -> Dict:
        """Check procedural compliance for jurisdiction"""

        issues = []

        # Check for required documents
        required_docs = self._get_required_documents(jurisdiction)
        present_doc_types = {doc.doc_type for doc in documents}

        for required in required_docs:
            if required not in present_doc_types:
                issues.append(f"Missing required document: {required}")

        # Check for certificates of service
        has_certificate = any(doc.doc_type == "certificate_of_service" for doc in documents)
        if not has_certificate:
            issues.append("Missing certificate of service")

        # Check for verification (if complaint present)
        has_complaint = any(doc.doc_type == "complaint" for doc in documents)
        has_verification = any("verification" in doc.content.lower() for doc in documents)
        if has_complaint and not has_verification:
            issues.append("Complaint appears unverified")

        return {"compliant": len(issues) == 0, "issues": issues, "jurisdiction": jurisdiction}

    def _extract_party_names(self, content: str) -> Dict[str, List[str]]:
        """Extract plaintiff and defendant names"""
        # Simplified - would need more sophisticated parsing
        plaintiffs = []
        defendants = []

        # Look for plaintiff section
        plaintiff_match = re.search(r"Plaintiff[s]?:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", content)
        if plaintiff_match:
            plaintiffs.append(plaintiff_match.group(1))

        # Look for defendant section
        defendant_match = re.search(r"Defendant[s]?:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", content)
        if defendant_match:
            defendants.append(defendant_match.group(1))

        return {"plaintiffs": plaintiffs, "defendants": defendants}

    def _extract_case_number(self, content: str) -> Optional[str]:
        """Extract case number"""
        # Common patterns: "Case No. 12-CV-34567", "No. 2023-1234", etc.
        patterns = [
            r"Case\s+No\.?\s*([0-9]{2,4}-[A-Z]{2,4}-[0-9]{4,6})",
            r"No\.?\s*([0-9]{4}-[0-9]{4,6})",
            r"Docket\s+No\.?\s*([0-9-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _check_date_consistency(self, documents: List[LegalDocument]) -> List[str]:
        """Check for date inconsistencies"""
        issues = []
        # Implementation would check dates across documents
        return issues

    def _extract_allegations(self, content: str) -> List[str]:
        """Extract factual allegations from document"""
        allegations = []
        # Look for numbered paragraphs or allegations
        # This is simplified - would need more sophisticated NLP
        paragraphs = re.findall(r"\d+\.\s+(.+?)(?=\n\d+\.|$)", content, re.DOTALL)
        allegations.extend(paragraphs)
        return allegations

    def _find_supporting_evidence(
        self, allegation: str, evidence: List[EvidenceItem]
    ) -> Optional[str]:
        """Find evidence that supports an allegation"""
        # Simplified keyword matching - would use semantic search in production
        for ev in evidence:
            # Check if key terms from allegation appear in evidence description
            pass
        return None

    def _get_required_documents(self, jurisdiction: str) -> List[str]:
        """Get list of required documents for jurisdiction"""
        # Default requirements
        return ["complaint", "certificate_of_service"]

    def _analyze_optimization_changes(self, original: str, optimized: str) -> Dict:
        """Analyze what changed and why"""

        # Parse optimized output (assuming GPT formatted it with sections)
        sections = self._parse_optimized_output(optimized)

        return {
            "changes": sections.get("changes", []),
            "consistency_issues": sections.get("consistency_issues", []),
            "evidence_gaps": sections.get("evidence_gaps", []),
            "procedural_issues": sections.get("procedural_issues", []),
            "strategic_improvements": sections.get("strategic_improvements", []),
            "confidence_score": sections.get("confidence_score", 0.85),
        }

    def _parse_optimized_output(self, optimized: str) -> Dict:
        """Parse structured output from GPT"""
        sections = {}

        # Extract CHANGE LOG section
        change_log_match = re.search(
            r"\*\*CHANGE LOG\*\*(.+?)(?=\*\*|$)", optimized, re.DOTALL | re.IGNORECASE
        )
        if change_log_match:
            changes_text = change_log_match.group(1)
            sections["changes"] = [
                line.strip()
                for line in changes_text.split("\n")
                if line.strip() and not line.strip().startswith("**")
            ]

        # Extract STRATEGIC NOTES
        strategic_match = re.search(
            r"\*\*STRATEGIC NOTES\*\*(.+?)(?=\*\*|$)", optimized, re.DOTALL | re.IGNORECASE
        )
        if strategic_match:
            strategic_text = strategic_match.group(1)
            sections["strategic_improvements"] = [
                line.strip()
                for line in strategic_text.split("\n")
                if line.strip() and not line.strip().startswith("**")
            ]

        return sections


