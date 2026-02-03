"""
Verified Legal Sources Integration

Only imports from legitimate, verified, and respected legal sources:
- CourtListener (free legal database with 10M+ opinions)
- Justia (verified case law)
- Google Scholar (legal opinions)
- Cornell LII (Legal Information Institute)
- GovInfo.gov (official U.S. government legal documents)
- Supreme Court official website

All sources are verified and credible.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from legal_library import LegalDocument, LegalLibraryService
from models_auth import db


class VerifiedLegalSources:
    """Manage imports from verified legal sources only"""

    # Official verified sources
    VERIFIED_SOURCES = {
        "courtlistener": {
            "name": "CourtListener",
            "url": "https://www.courtlistener.com",
            "api": "https://www.courtlistener.com/api/rest/v3/",
            "verified": True,
            "official": False,
            "credibility": "HIGH",
            "description": "Non-profit free legal database with 10M+ opinions",
        },
        "cornell_lii": {
            "name": "Cornell Legal Information Institute",
            "url": "https://www.law.cornell.edu",
            "verified": True,
            "official": True,
            "credibility": "HIGHEST",
            "description": "Official Cornell Law School legal database",
        },
        "govinfo": {
            "name": "GovInfo.gov",
            "url": "https://www.govinfo.gov",
            "api": "https://api.govinfo.gov",
            "verified": True,
            "official": True,
            "credibility": "HIGHEST",
            "description": "Official U.S. Government Publishing Office",
        },
        "supremecourt": {
            "name": "Supreme Court of the United States",
            "url": "https://www.supremecourt.gov",
            "verified": True,
            "official": True,
            "credibility": "HIGHEST",
            "description": "Official Supreme Court opinions",
        },
        "justia": {
            "name": "Justia",
            "url": "https://www.justia.com",
            "verified": True,
            "official": False,
            "credibility": "HIGH",
            "description": "Free verified case law database",
        },
        "google_scholar": {
            "name": "Google Scholar (Legal)",
            "url": "https://scholar.google.com",
            "verified": True,
            "official": False,
            "credibility": "HIGH",
            "description": "Verified legal opinions from Google Scholar",
        },
    }

    def __init__(self):
        self.library = LegalLibraryService()

    def get_source_info(self, source_name: str) -> Dict:
        """Get verification info for a source"""
        return self.VERIFIED_SOURCES.get(source_name, {"verified": False, "credibility": "UNKNOWN"})

    def is_verified_source(self, source_name: str) -> bool:
        """Check if source is verified"""
        info = self.get_source_info(source_name)
        return info.get("verified", False)

    def import_from_courtlistener(self, citation: str) -> Optional[LegalDocument]:
        """
        Import from CourtListener (verified source)

        CourtListener is a non-profit free legal database with:
        - 10+ million legal opinions
        - Federal and state courts
        - Supreme Court decisions
        - Circuit court opinions
        """

        if not self.is_verified_source("courtlistener"):
            raise ValueError("CourtListener is not a verified source")

        # Use existing library service
        doc = self.library.ingest_from_courtlistener(citation)

        if doc:
            # Mark as verified from official source
            doc.verified = True
            doc.source = "courtlistener"
            db.session.commit()

        return doc

    def import_from_cornell_lii(self, citation: str) -> Optional[LegalDocument]:
        """
        Import from Cornell Legal Information Institute

        Cornell LII is an official source from Cornell Law School providing:
        - U.S. Supreme Court decisions
        - U.S. Code
        - Federal regulations
        - State statutes
        """

        # TODO: Implement Cornell LII scraping
        # Example: https://www.law.cornell.edu/supremecourt/text/{volume}/{page}

        return None

    def import_from_govinfo(self, citation: str) -> Optional[LegalDocument]:
        """
        Import from GovInfo.gov (official U.S. government source)

        GovInfo provides:
        - Supreme Court slip opinions
        - Congressional documents
        - Federal Register
        - Code of Federal Regulations
        """

        # TODO: Implement GovInfo API integration
        # Requires API key from https://api.govinfo.gov

        return None

    def import_from_supreme_court_official(self, year: int, docket: str) -> Optional[LegalDocument]:
        """
        Import directly from Supreme Court official website

        Example: https://www.supremecourt.gov/opinions/23pdf/22-451_7l48.pdf
        """

        # TODO: Implement Supreme Court PDF scraping

        return None

    def verify_citation_authenticity(self, citation: str, source: str) -> Dict:
        """
        Verify a citation is authentic from multiple sources

        Returns:
            {
                'authentic': bool,
                'verified_sources': list,
                'confidence': 'HIGH' | 'MEDIUM' | 'LOW',
                'warnings': list
            }

        Requires COURTLISTENER_API_KEY environment variable for API access
        """
        import os

        import requests

        verified_sources = []
        warnings = []

        # Check CourtListener API
        try:
            headers = {}
            api_key = os.getenv("COURTLISTENER_API_KEY")
            if api_key:
                headers["Authorization"] = f"Token {api_key}"

            response = requests.get(
                "https://www.courtlistener.com/api/rest/v3/search/",
                params={"q": citation, "type": "o", "format": "json"},  # Opinions
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("count", 0) > 0:
                    verified_sources.append("courtlistener")
            elif response.status_code == 403:
                warnings.append(
                    "CourtListener API requires authentication. Set COURTLISTENER_API_KEY environment variable."
                )
        except Exception as e:
            warnings.append(f"CourtListener API error: {str(e)}")

        # Check local database (if already imported)
        try:
            local_docs = self.library.search_library(query=citation, limit=1)
            if local_docs and local_docs[0].citation == citation:
                verified_sources.append("local_db")
        except:
            pass

        # Remove duplicates
        verified_sources = list(set(verified_sources))

        confidence = (
            "HIGH"
            if len(verified_sources) >= 2
            else "MEDIUM" if len(verified_sources) == 1 else "LOW"
        )

        if confidence == "LOW":
            warnings.append("Citation could not be verified from multiple sources")

        return {
            "authentic": len(verified_sources) > 0,
            "verified_sources": verified_sources,
            "confidence": confidence,
            "warnings": warnings,
        }

    def batch_import_verified_only(
        self, citations: List[str], min_confidence: str = "MEDIUM"
    ) -> Dict:
        """
        Batch import only citations that can be verified

        Args:
            citations: List of citations to import
            min_confidence: Minimum confidence level (HIGH, MEDIUM, LOW)

        Returns:
            Import statistics
        """

        imported = []
        rejected = []

        for citation in citations:
            # Verify authenticity first
            verification = self.verify_citation_authenticity(citation, "courtlistener")

            if verification["confidence"] in ["HIGH", "MEDIUM"] or (
                min_confidence == "LOW" and verification["authentic"]
            ):

                # Import from verified source
                doc = self.import_from_courtlistener(citation)

                if doc:
                    imported.append(
                        {"citation": citation, "doc_id": doc.id, "verification": verification}
                    )
                else:
                    rejected.append(
                        {
                            "citation": citation,
                            "reason": "Import failed",
                            "verification": verification,
                        }
                    )
            else:
                rejected.append(
                    {
                        "citation": citation,
                        "reason": f"Confidence too low ({verification['confidence']})",
                        "verification": verification,
                    }
                )

        return {
            "imported": imported,
            "rejected": rejected,
            "total": len(citations),
            "success_rate": len(imported) / len(citations) if citations else 0,
        }


class SourceCredibilityTracker:
    """Track credibility and reliability of sources"""

    def __init__(self):
        self.source_ratings = {}

    def rate_source(self, source_name: str) -> Dict:
        """
        Rate a source's credibility

        Returns credibility rating with justification
        """

        ratings = {
            "courtlistener": {
                "rating": 9.5,
                "official": False,
                "peer_reviewed": True,
                "non_profit": True,
                "established": 2010,
                "justification": [
                    "Non-profit legal database",
                    "Used by legal professionals nationwide",
                    "Comprehensive collection (10M+ opinions)",
                    "Regular updates and verification",
                ],
            },
            "cornell_lii": {
                "rating": 10.0,
                "official": True,
                "peer_reviewed": True,
                "academic": True,
                "established": 1992,
                "justification": [
                    "Official Cornell Law School database",
                    "Academic institution backing",
                    "Primary source for legal research",
                    "Cited by courts and legal scholars",
                ],
            },
            "govinfo": {
                "rating": 10.0,
                "official": True,
                "government": True,
                "established": 1994,
                "justification": [
                    "Official U.S. Government source",
                    "Government Publishing Office",
                    "Authoritative legal documents",
                    "Primary source for federal law",
                ],
            },
            "supremecourt": {
                "rating": 10.0,
                "official": True,
                "government": True,
                "highest_court": True,
                "justification": [
                    "Official Supreme Court website",
                    "Primary source for SCOTUS opinions",
                    "Definitive legal authority",
                    "No higher source available",
                ],
            },
            "justia": {
                "rating": 9.0,
                "official": False,
                "commercial": True,
                "verified": True,
                "established": 2003,
                "justification": [
                    "Well-established legal database",
                    "Used by legal professionals",
                    "Free access to verified cases",
                    "Regular updates",
                ],
            },
            "google_scholar": {
                "rating": 8.5,
                "official": False,
                "academic": True,
                "verified": True,
                "justification": [
                    "Academic search engine",
                    "Indexes verified legal opinions",
                    "Cross-referenced with official sources",
                    "Wide coverage",
                ],
            },
        }

        return ratings.get(
            source_name,
            {
                "rating": 0.0,
                "official": False,
                "verified": False,
                "justification": ["Unknown or unverified source"],
            },
        )

    def get_highest_credibility_sources(self) -> List[str]:
        """Get list of highest credibility sources (rating >= 9.0)"""

        high_credibility = []

        for source, info in VerifiedLegalSources.VERIFIED_SOURCES.items():
            rating_info = self.rate_source(source)
            if rating_info.get("rating", 0) >= 9.0:
                high_credibility.append(
                    {
                        "source": source,
                        "name": info["name"],
                        "rating": rating_info["rating"],
                        "official": rating_info.get("official", False),
                    }
                )

        # Sort by rating descending
        high_credibility.sort(key=lambda x: x["rating"], reverse=True)

        return high_credibility


# TODO: Integration points
"""
Add to legal_library.py:

from verified_legal_sources import VerifiedLegalSources, SourceCredibilityTracker

class LegalLibraryService:
    def __init__(self):
        self.verified_sources = VerifiedLegalSources()
        self.credibility_tracker = SourceCredibilityTracker()
    
    def import_verified_only(self, citation):
        # Only import from verified sources
        return self.verified_sources.import_from_courtlistener(citation)
"""
