from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Legal Trinity Service
Unified search across LOCAL, STATE, and FEDERAL law

The "Holy Trinity" of government law:
- LOCAL: Municipal codes, ordinances (Code360, Municode)
- STATE: State statutes, regulations, court rules
- FEDERAL: U.S. Code, CFR, Federal Rules (GovInfo API)

Enables Evident to:
1. Search all levels simultaneously
2. Match evidence to applicable law at all levels
3. Identify jurisdiction hierarchy conflicts
4. Generate comprehensive compliance reports
5. Align filings with proper jurisdictional authority
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import requests

from code360_client import Code360Client, Municipality
from legal_library import LegalLibraryService
from municipal_code_service import MunicipalCodeService
from statutory_compliance_checker import StatutoryComplianceChecker
from verified_legal_sources import VerifiedLegalSources

logger = logging.getLogger(__name__)


class JurisdictionLevel(Enum):
    """Government jurisdiction levels"""

    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"


class LawType(Enum):
    """Types of law"""

    CONSTITUTION = "constitution"
    STATUTE = "statute"
    REGULATION = "regulation"
    ORDINANCE = "ordinance"
    COURT_RULE = "court_rule"
    CASE_LAW = "case_law"
    EXECUTIVE_ORDER = "executive_order"


@dataclass
class Jurisdiction:
    """Represents a jurisdiction"""

    level: JurisdictionLevel
    name: str
    code: str  # State code (e.g., "NJ") or "US" for federal
    parent: Optional["Jurisdiction"] = None

    @property
    def full_path(self) -> str:
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


@dataclass
class LegalAuthority:
    """A legal authority (statute, ordinance, regulation, etc.)"""

Optional[id: int] = None
    level: JurisdictionLevel = JurisdictionLevel.FEDERAL
    law_type: LawType = LawType.STATUTE
    jurisdiction: str = ""  # "US", "NJ", "Atlantic City, NJ"

    # Citation info
    citation: str = ""  # e.g., "18 U.S.C. § 242", "N.J.S.A. 2C:39-5"
    title: str = ""
    text: str = ""

    # Source
    source_url: str = ""
    source_name: str = ""
Optional[effective_date: datetime] = None

    # Hierarchy
Optional[superseded_by: str] = None  # Higher authority that preempts

    # Relevance (set during search)
    relevance_score: float = 0.0
    matched_terms: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Normalize citation
        if self.citation:
            self.citation = self.citation.strip()


@dataclass
class TrinitySearchResult:
    """Combined results from LOCAL, STATE, and FEDERAL search"""

    query: str
Optional[jurisdiction_filter: str] = None

    federal_results: list[LegalAuthority] = field(default_factory=list)
    state_results: list[LegalAuthority] = field(default_factory=list)
    local_results: list[LegalAuthority] = field(default_factory=list)

    # Analysis
    hierarchy_notes: list[str] = field(default_factory=list)  # Preemption issues, conflicts
    applicable_authorities: list[LegalAuthority] = field(
        default_factory=list
    )  # Ranked by relevance

    searched_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_results(self) -> int:
        return len(self.federal_results) + len(self.state_results) + len(self.local_results)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "jurisdiction_filter": self.jurisdiction_filter,
            "total_results": self.total_results,
            "federal": {
                "count": len(self.federal_results),
                "results": [self._authority_to_dict(a) for a in self.federal_results[:10]],
            },
            "state": {
                "count": len(self.state_results),
                "results": [self._authority_to_dict(a) for a in self.state_results[:10]],
            },
            "local": {
                "count": len(self.local_results),
                "results": [self._authority_to_dict(a) for a in self.local_results[:10]],
            },
            "hierarchy_notes": self.hierarchy_notes,
            "top_authorities": [
                self._authority_to_dict(a) for a in self.applicable_authorities[:15]
            ],
            "searched_at": self.searched_at.isoformat(),
        }

    def _authority_to_dict(self, auth: LegalAuthority) -> dict:
        return {
            "level": auth.level.value,
            "type": auth.law_type.value,
            "jurisdiction": auth.jurisdiction,
            "citation": auth.citation,
            "title": auth.title,
            "text_preview": auth.text[:500] if auth.text else "",
            "source_url": auth.source_url,
            "relevance_score": auth.relevance_score,
            "matched_terms": auth.matched_terms,
        }


class LegalTrinityService:
    """
    Unified service for searching LOCAL, STATE, and FEDERAL law

    Example usage:
        trinity = LegalTrinityService()

        # Search all levels
        results = trinity.search("excessive force", state="NJ", municipality="Newark")

        # Analyze evidence against applicable law
        analysis = trinity.analyze_evidence(evidence, jurisdiction="Newark, NJ")

        # Get filing recommendations
        filings = trinity.recommend_filings(violations, jurisdiction="Newark, NJ")
    """

    # State statute citation patterns
    STATE_STATUTE_PATTERNS = {
        "NJ": {"prefix": "N.J.S.A.", "pattern": r"N\.?J\.?S\.?A\.?\s*[\d:]+"},
        "NY": {"prefix": "N.Y.", "pattern": r"N\.?Y\.?\s+\w+\s+Law\s+§?\s*\d+"},
        "CA": {"prefix": "Cal.", "pattern": r"Cal\.?\s+\w+\s+Code\s+§?\s*\d+"},
        "PA": {"prefix": "Pa.C.S.", "pattern": r"\d+\s+Pa\.?C\.?S\.?\s+§?\s*\d+"},
        "FL": {"prefix": "Fla. Stat.", "pattern": r"Fla\.?\s+Stat\.?\s+§?\s*[\d\.]+"},
        "TX": {"prefix": "Tex.", "pattern": r"Tex\.?\s+\w+\s+Code\s+§?\s*[\d\.]+"},
        # Add more states as needed
    }

    # Federal code sources
    FEDERAL_SOURCES = {
        "usc": {
            "name": "United States Code",
            "url": "https://uscode.house.gov",
            "api": "https://api.congress.gov/v3",
            "pattern": r"\d+\s+U\.?S\.?C\.?\s+§?\s*\d+",
        },
        "cfr": {
            "name": "Code of Federal Regulations",
            "url": "https://www.ecfr.gov",
            "api": "https://www.ecfr.gov/api/versioner/v1",
            "pattern": r"\d+\s+C\.?F\.?R\.?\s+§?\s*[\d\.]+",
        },
        "frcp": {
            "name": "Federal Rules of Criminal Procedure",
            "url": "https://www.law.cornell.edu/rules/frcrmp",
            "pattern": r"Fed\.?\s*R\.?\s*Crim\.?\s*P\.?\s*\d+",
        },
        "fre": {
            "name": "Federal Rules of Evidence",
            "url": "https://www.law.cornell.edu/rules/fre",
            "pattern": r"Fed\.?\s*R\.?\s*Evid\.?\s*\d+",
        },
    }

    def __init__(self):
        self.code360 = Code360Client()
        self.municipal = MunicipalCodeService()
        self.legal_library = LegalLibraryService()
        self.verified_sources = VerifiedLegalSources()
        self.compliance_checker = StatutoryComplianceChecker()

        # GovInfo API key (optional, increases rate limits)
        self.govinfo_api_key = os.getenv("GOVINFO_API_KEY", "")
        self.congress_api_key = os.getenv("CONGRESS_API_KEY", "")

    # ═══════════════════════════════════════════════════════════════════════════
    # UNIFIED SEARCH
    # ═══════════════════════════════════════════════════════════════════════════

    def search(
        self,
        query: str,
Optional[state: str] = None,
Optional[municipality: str] = None,
Optional[county: str] = None,
Optional[levels: list[JurisdictionLevel]] = None,
Optional[law_types: list[LawType]] = None,
        limit_per_level: int = 15,
    ) -> TrinitySearchResult:
        """
        Search across all three levels of government law

        Args:
            query: Search terms
            state: State code (e.g., "NJ", "CA") - required for state/local
            municipality: Municipality name for local search
            county: County name for more specific local search
            levels: Which levels to search (default: all)
            law_types: Filter by law type
            limit_per_level: Max results per level

        Returns:
            TrinitySearchResult with results from all levels
        """
        levels = levels or [
            JurisdictionLevel.FEDERAL,
            JurisdictionLevel.STATE,
            JurisdictionLevel.LOCAL,
        ]

        result = TrinitySearchResult(
            query=query,
            jurisdiction_filter=self._build_jurisdiction_string(state, municipality, county),
        )

        # Search Federal
        if JurisdictionLevel.FEDERAL in levels:
            result.federal_results = self._search_federal(query, law_types, limit_per_level)

        # Search State
        if JurisdictionLevel.STATE in levels and state:
            result.state_results = self._search_state(query, state, law_types, limit_per_level)

        # Search Local
        if JurisdictionLevel.LOCAL in levels and (municipality or county):
            result.local_results = self._search_local(
                query, state, municipality, county, limit_per_level
            )

        # Analyze hierarchy and rank results
        result.hierarchy_notes = self._analyze_hierarchy(result)
        result.applicable_authorities = self._rank_authorities(result)

        return result

    def _search_federal(
Optional[self, query: str, law_types: list[LawType]], limit: int
    ) -> list[LegalAuthority]:
        """Search federal law sources"""
        results = []

        # Search U.S. Code via GovInfo
        try:
            usc_results = self._search_govinfo_usc(query, limit)
            results.extend(usc_results)
        except Exception as e:
            logger.error(f"USC search error: {e}")

        # Search CFR
        try:
            cfr_results = self._search_ecfr(query, limit)
            results.extend(cfr_results)
        except Exception as e:
            logger.error(f"CFR search error: {e}")

        # Search legal library for federal case law
        try:
            cases = self.legal_library.search_library(query, jurisdiction="Federal", limit=limit)
            for case in cases:
                results.append(
                    LegalAuthority(
                        level=JurisdictionLevel.FEDERAL,
                        law_type=LawType.CASE_LAW,
                        jurisdiction="US",
                        citation=case.citation or "",
                        title=case.title,
                        text=case.summary or case.full_text[:1000],
                        source_url=case.url or "",
                        source_name="CourtListener/Legal Library",
                    )
                )
        except Exception as e:
            logger.error(f"Federal case law search error: {e}")

        # Filter by law type if specified
        if law_types:
            results = [r for r in results if r.law_type in law_types]

        return results[:limit]

    def _search_govinfo_usc(self, query: str, limit: int) -> list[LegalAuthority]:
        """Search U.S. Code via GovInfo API"""
        results = []

        try:
            url = "https://api.govinfo.gov/search"
            params = {
                "query": query,
                "collection": "USCODE",
                "pageSize": min(limit, 100),
                "offsetMark": "*",
            }

            if self.govinfo_api_key:
                params["api_key"] = self.govinfo_api_key

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                for result in data.get("results", []):
                    results.append(
                        LegalAuthority(
                            level=JurisdictionLevel.FEDERAL,
                            law_type=LawType.STATUTE,
                            jurisdiction="US",
                            citation=result.get("title", ""),
                            title=result.get("title", ""),
                            text=result.get("summary", ""),
                            source_url=result.get("download", {}).get("txtLink", ""),
                            source_name="GovInfo U.S. Code",
                        )
                    )
        except Exception as e:
            logger.error(f"GovInfo search error: {e}")

        return results

    def _search_ecfr(self, query: str, limit: int) -> list[LegalAuthority]:
        """Search Code of Federal Regulations via eCFR API"""
        results = []

        try:
            url = "https://www.ecfr.gov/api/search/v1/results"
            params = {"query": query, "per_page": min(limit, 100)}

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                for result in data.get("results", []):
                    results.append(
                        LegalAuthority(
                            level=JurisdictionLevel.FEDERAL,
                            law_type=LawType.REGULATION,
                            jurisdiction="US",
                            citation=result.get("hierarchy_headings", ""),
                            title=result.get("headings", {}).get("title", ""),
                            text=result.get("full_text_excerpt", ""),
                            source_url=f"https://www.ecfr.gov{result.get('url', '')}",
                            source_name="eCFR",
                        )
                    )
        except Exception as e:
            logger.error(f"eCFR search error: {e}")

        return results

    def _search_state(
Optional[self, query: str, state: str, law_types: list[LawType]], limit: int
    ) -> list[LegalAuthority]:
        """Search state law sources"""
        results = []
        state = state.upper()

        # Search legal library for state cases and statutes
        try:
            docs = self.legal_library.search_library(query, jurisdiction=state, limit=limit)
            for doc in docs:
                law_type = LawType.STATUTE if doc.doc_type == "statute" else LawType.CASE_LAW
                results.append(
                    LegalAuthority(
                        level=JurisdictionLevel.STATE,
                        law_type=law_type,
                        jurisdiction=state,
                        citation=doc.citation or "",
                        title=doc.title,
                        text=doc.summary or doc.full_text[:1000],
                        source_url=doc.url or "",
                        source_name="Legal Library",
                    )
                )
        except Exception as e:
            logger.error(f"State search error: {e}")

        # TODO: Add state-specific statute databases
        # Cornell LII, state legislature sites, etc.

        if law_types:
            results = [r for r in results if r.law_type in law_types]

        return results[:limit]

    def _search_local(
        self,
        query: str,
Optional[state: str],
Optional[municipality: str],
Optional[county: str],
        limit: int,
    ) -> list[LegalAuthority]:
        """Search local/municipal law sources"""
        results = []

        # Search via Code360 client
        try:
            code360_results = self.code360.search(query, state=state, limit=limit)

            for r in code360_results:
                results.append(
                    LegalAuthority(
                        level=JurisdictionLevel.LOCAL,
                        law_type=LawType.ORDINANCE,
                        jurisdiction=f"{r.get('municipality', '')}, {r.get('county', '')} County, {r.get('state', '')}",
                        citation=r.get("section_number", ""),
                        title=r.get("title", ""),
                        text=r.get("snippet", ""),
                        source_url=r.get("source_url", ""),
                        source_name="Code360",
                    )
                )
        except Exception as e:
            logger.debug(f"Code360 search: {e}")

        # Search via municipal code service
        try:
            muni_results = self.municipal.search(
                query, county=county, municipality=municipality, limit=limit
            )

            for r in muni_results:
                results.append(
                    LegalAuthority(
                        level=JurisdictionLevel.LOCAL,
                        law_type=LawType.ORDINANCE,
                        jurisdiction=f"{r.get('municipality', '')}, {r.get('county', '')} County",
                        citation=r.get("section_citation", ""),
                        title=r.get("title", ""),
                        text=r.get("snippet", ""),
                        source_url=r.get("source_url", ""),
                        source_name="Municipal Code Service",
                    )
                )
        except Exception as e:
            logger.debug(f"Municipal search: {e}")

        return results[:limit]

    def _build_jurisdiction_string(
Optional[self, state: str]Optional[, municipality: str]Optional[, county: str]
    ) -> str:
        """Build jurisdiction description string"""
        parts = []
        if municipality:
            parts.append(municipality)
        if county:
            parts.append(f"{county} County")
        if state:
            parts.append(state.upper())
        return ", ".join(parts) if parts else "All Jurisdictions"

    def _analyze_hierarchy(self, result: TrinitySearchResult) -> list[str]:
        """Analyze jurisdictional hierarchy and note conflicts/preemptions"""
        notes = []

        # Check for federal preemption issues
        federal_topics = set()
        for auth in result.federal_results:
            if "preempt" in auth.text.lower() or "supremacy" in auth.text.lower():
                federal_topics.add(auth.title.lower())
                notes.append(
                    f"⚠️ Federal preemption may apply: {auth.citation} - "
                    "State/local laws on this topic may be invalidated"
                )

        # Check for state preemption of local
        for state_auth in result.state_results:
            if "preempt" in state_auth.text.lower():
                notes.append(
                    f"⚠️ State preemption: {state_auth.citation} may preempt local ordinances"
                )

        # Note hierarchy
        if result.federal_results and (result.state_results or result.local_results):
            notes.append(
                "📋 Hierarchy: Federal law is supreme (Supremacy Clause). "
                "Check for express/implied preemption."
            )

        if result.state_results and result.local_results:
            notes.append(
                "📋 State laws generally preempt conflicting local ordinances "
                "unless home rule authority applies."
            )

        return notes

    def _rank_authorities(self, result: TrinitySearchResult) -> list[LegalAuthority]:
        """Rank all authorities by relevance and hierarchy"""
        all_authorities = result.federal_results + result.state_results + result.local_results

        def score(auth: LegalAuthority) -> float:
            # Base relevance score
            base = auth.relevance_score or 0.5

            # Hierarchy boost (federal > state > local for legal weight)
            hierarchy_boost = {
                JurisdictionLevel.FEDERAL: 0.3,
                JurisdictionLevel.STATE: 0.2,
                JurisdictionLevel.LOCAL: 0.1,
            }

            # Law type boost (statutes > regulations > ordinances for authority)
            type_boost = {
                LawType.CONSTITUTION: 0.4,
                LawType.STATUTE: 0.3,
                LawType.REGULATION: 0.2,
                LawType.COURT_RULE: 0.2,
                LawType.CASE_LAW: 0.15,
                LawType.ORDINANCE: 0.1,
                LawType.EXECUTIVE_ORDER: 0.1,
            }

            return base + hierarchy_boost.get(auth.level, 0) + type_boost.get(auth.law_type, 0)

        # Sort by combined score
        all_authorities.sort(key=score, reverse=True)

        # Update relevance scores
        for auth in all_authorities:
            auth.relevance_score = score(auth)

        return all_authorities

    # ═══════════════════════════════════════════════════════════════════════════
    # EVIDENCE ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════

    def analyze_evidence_against_law(
        self,
        evidence: dict,
        state: str,
Optional[municipality: str] = None,
Optional[county: str] = None,
    ) -> dict[str, Any]:
        """
        Analyze evidence against applicable law at all levels

        Args:
            evidence: Evidence dict with 'type', 'content', 'violations', etc.
            state: State code
            municipality: Optional municipality for local law
            county: Optional county

        Returns:
            Comprehensive analysis with applicable laws and recommendations
        """
        # Get keywords from evidence
        keywords = self._extract_keywords(evidence)

        # Search all levels
        search_results = self.search(
            query=" ".join(keywords), state=state, municipality=municipality, county=county
        )

        # Run compliance check
        compliance = self.compliance_checker.comprehensive_check(evidence)

        # Match violations to authorities
        violation_matches = []
        for violation in evidence.get("violations", []):
            matches = self._match_violation_to_law(violation, search_results)
            violation_matches.append(
                {
                    "violation": violation,
                    "applicable_laws": matches,
                    "jurisdiction_notes": self._get_jurisdiction_notes(matches),
                }
            )

        return {
            "evidence_id": evidence.get("id", "unknown"),
            "jurisdiction": self._build_jurisdiction_string(state, municipality, county),
            "search_results": search_results.to_dict(),
            "compliance_check": compliance,
            "violation_law_matches": violation_matches,
            "filing_recommendations": self._generate_filing_recommendations(
                violation_matches, state, municipality
            ),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    def _extract_keywords(self, evidence: dict) -> list[str]:
        """Extract search keywords from evidence"""
        keywords = []

        # From content
        content = evidence.get("content", "")
        if content:
            # Extract legal-relevant terms
            legal_terms = [
                "force",
                "arrest",
                "search",
                "seizure",
                "warrant",
                "rights",
                "miranda",
                "excessive",
                "assault",
                "battery",
                "violation",
                "procedure",
                "evidence",
                "custody",
                "detention",
            ]
            for term in legal_terms:
                if term.lower() in content.lower():
                    keywords.append(term)

        # From violations
        for violation in evidence.get("violations", []):
            if isinstance(violation, dict):
                keywords.append(violation.get("type", ""))
                keywords.extend(violation.get("keywords", []))
            elif isinstance(violation, str):
                keywords.append(violation)

        # From evidence type
        evidence_type = evidence.get("type", "")
        type_keywords = {
            "bwc": ["body camera", "police video", "use of force"],
            "document": ["records", "report"],
            "statement": ["testimony", "witness"],
        }
        keywords.extend(type_keywords.get(evidence_type, []))

        # Deduplicate and clean
        keywords = list(set(k.strip() for k in keywords if k and k.strip()))
        return keywords[:10]  # Limit to top 10

    def _match_violation_to_law(
        self, violation: dict, results: TrinitySearchResult
    ) -> list[LegalAuthority]:
        """Match a violation to applicable legal authorities"""
        matches = []

        violation_type = violation.get("type", "").lower()
        violation_text = violation.get("description", "").lower()

        for auth in results.applicable_authorities:
            # Score match
            score = 0
            matched_terms = []

            # Check title match
            if violation_type in auth.title.lower():
                score += 0.5
                matched_terms.append(violation_type)

            # Check text match
            auth_text = auth.text.lower()
            for word in violation_text.split():
                if len(word) > 3 and word in auth_text:
                    score += 0.1
                    matched_terms.append(word)

            if score > 0.3:
                auth.relevance_score = score
                auth.matched_terms = matched_terms[:5]
                matches.append(auth)

        # Sort by relevance
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches[:5]  # Top 5 matches

    def _get_jurisdiction_notes(self, authorities: list[LegalAuthority]) -> list[str]:
        """Get notes about jurisdiction for matched authorities"""
        notes = []

        levels = set(a.level for a in authorities)

        if JurisdictionLevel.FEDERAL in levels and len(levels) > 1:
            notes.append("Federal law may preempt state/local provisions")

        if JurisdictionLevel.LOCAL in levels:
            notes.append("Local ordinance violations typically filed in municipal court")

        if JurisdictionLevel.STATE in levels:
            notes.append("State violations filed in state court (Superior/District)")

        return notes

    def _generate_filing_recommendations(
Optional[self, violation_matches: list[dict], state: str, municipality: str]
    ) -> list[dict]:
        """Generate filing recommendations based on violations and applicable law"""
        recommendations = []

        for match in violation_matches:
            authorities = match.get("applicable_laws", [])

            if not authorities:
                continue

            # Determine primary authority level
            levels = [a.level for a in authorities]

            if JurisdictionLevel.FEDERAL in levels:
                recommendations.append(
                    {
                        "violation": match["violation"],
                        "recommended_filing": "Federal Court (USDC)",
                        "basis": [
                            a.citation for a in authorities if a.level == JurisdictionLevel.FEDERAL
                        ][:3],
                        "notes": "Federal civil rights claims (42 U.S.C. § 1983) or federal criminal referral",
                        "priority": (
                            "HIGH"
                            if "constitutional" in str(match["violation"]).lower()
                            else "MEDIUM"
                        ),
                    }
                )

            if JurisdictionLevel.STATE in levels:
                recommendations.append(
                    {
                        "violation": match["violation"],
                        "recommended_filing": f"{state} Superior Court / State Court",
                        "basis": [
                            a.citation for a in authorities if a.level == JurisdictionLevel.STATE
                        ][:3],
                        "notes": "State law claims, tort actions, or criminal complaint",
                        "priority": "MEDIUM",
                    }
                )

            if JurisdictionLevel.LOCAL in levels and municipality:
                recommendations.append(
                    {
                        "violation": match["violation"],
                        "recommended_filing": f"{municipality} Municipal Court",
                        "basis": [
                            a.citation for a in authorities if a.level == JurisdictionLevel.LOCAL
                        ][:3],
                        "notes": "Local ordinance violations, administrative complaints",
                        "priority": "LOW",
                    }
                )

        return recommendations

    # ═══════════════════════════════════════════════════════════════════════════
    # MUNICIPALITY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

Optional[def add_municipality(self, state: str, name: str, county: str = "") -> Municipality]:
        """
        Add a new municipality for local code integration

        Example:
            trinity.add_municipality("NJ", "Newark", "Essex")
            trinity.add_municipality("CA", "Los Angeles", "Los Angeles")
        """
        return self.code360.discover_municipality(state, name, county)

Optional[def list_municipalities(self, state: str] = None) -> list[Municipality]:
        """List all integrated municipalities"""
        return self.code360.list_municipalities(state=state)

    def sync_municipality(self, municipality_id: int) -> dict:
        """Sync/update municipal code from source"""
        municipality = self.code360.get_municipality(municipality_id)
        if municipality:
            return self.code360.sync_municipality(municipality)
        return {"error": "Municipality not found"}


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


Optional[def trinity_search(query: str, state: str]Optional[= None, municipality: str] = None) -> dict:
    """
    Quick search across all levels of law

    Example:
        results = trinity_search("excessive force", state="NJ", municipality="Newark")
    """
    service = LegalTrinityService()
    result = service.search(query, state=state, municipality=municipality)
    return result.to_dict()


Optional[def analyze_evidence(evidence: dict, state: str, municipality: str] = None) -> dict:
    """
    Analyze evidence against applicable law at all levels

    Example:
        analysis = analyze_evidence(
            {"type": "bwc", "violations": [{"type": "excessive force"}]},
            state="NJ",
            municipality="Newark"
        )
    """
    service = LegalTrinityService()
    return service.analyze_evidence_against_law(evidence, state, municipality)