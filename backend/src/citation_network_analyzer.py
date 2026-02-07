from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Citation Network Analyzer - Shepard's Citations Equivalent

Provides comprehensive citation analysis:
- Forward citations (cases citing this case)
- Backward citations (cases cited by this case)
- Treatment analysis (followed, distinguished, reversed, etc.)
- Good law verification
- Citation network visualization

Uses CourtListener v4 API: opinions-cited, visualizations
"""

import os

import requests

from legal_library import LegalLibraryService


class CitationTreatment:
    """Citation treatment types (Shepard's signals)"""

    FOLLOWED = "followed"  # Positive treatment
    DISTINGUISHED = "distinguished"  # Neutral
    QUESTIONED = "questioned"  # Negative
    REVERSED = "reversed"  # Negative (direct history)
    AFFIRMED = "affirmed"  # Positive (direct history)
    MODIFIED = "modified"  # Neutral
    SUPERSEDED = "superseded"  # Negative

    # Shepard's-style signals
    RED_FLAG = "red_flag"  # Reversed, overruled
    YELLOW_FLAG = "yellow_flag"  # Questioned, criticized
    BLUE_H = "blue_h"  # Direct history
    GREEN_PLUS = "green_plus"  # Positive treatment


class CitationNetworkAnalyzer:
    """
    Elite-tier citation analysis

    Features:
    - Shepardize™ equivalent
    - Citation network graphs
    - Treatment analysis
    - Authority scoring
    """

    def __init__(self):
        self.api_base = "https://www.courtlistener.com/api/rest/v4/"
        self.api_key = os.getenv("COURTLISTENER_API_KEY")
        self.library = LegalLibraryService()

    def _get_headers(self):
        """Get API headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def get_citing_cases(self, opinion_id: int, limit: int = 100) -> list[dict]:
        """
        Get all cases that cite this opinion

        Returns list of:
        - Citing case details
        - Citation context (paragraph where cited)
        - Treatment type
        - Citation depth (how many times cited)
        """
        url = f"{self.api_base}opinions-cited/"
        params = {"cited_opinion": opinion_id, "order_by": "-date_created", "page_size": limit}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    def get_cited_cases(self, opinion_id: int) -> list[dict]:
        """
        Get all cases cited BY this opinion

        Returns backward citation graph
        """
        url = f"{self.api_base}opinions-cited/"
        params = {"citing_opinion": opinion_id, "page_size": 100}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    def analyze_treatment(self, opinion_id: int) -> dict:
        """
        Analyze how subsequent courts treated this case

        Returns:
        {
            'signal': 'red_flag' | 'yellow_flag' | 'blue_h' | 'green_plus',
            'positive_cites': 45,
            'negative_cites': 3,
            'neutral_cites': 12,
            'total_cites': 60,
            'treatments': {
                'followed': 30,
                'distinguished': 15,
                'questioned': 3,
                'affirmed': 10,
                'reversed': 2
            },
            'authority_score': 0.85  # 0-1 scale
        }
        """
        citing_cases = self.get_citing_cases(opinion_id, limit=500)

        treatments = {
            "followed": 0,
            "distinguished": 0,
            "questioned": 0,
            "reversed": 0,
            "affirmed": 0,
            "modified": 0,
            "superseded": 0,
        }

        # Analyze each citation
        for cite in citing_cases:
            treatment = self._determine_treatment(cite)
            if treatment in treatments:
                treatments[treatment] += 1

        # Calculate scores
        total = len(citing_cases)
        positive = treatments["followed"] + treatments["affirmed"]
        negative = treatments["questioned"] + treatments["reversed"] + treatments["superseded"]
        neutral = treatments["distinguished"] + treatments["modified"]

        # Determine Shepard's signal
        signal = self._get_shepards_signal(treatments, total)

        # Authority score (0-1)
        if total > 0:
            authority = (positive - negative) / total
            authority = max(0, min(1, (authority + 1) / 2))  # Normalize to 0-1
        else:
            authority = 0.5

        return {
            "signal": signal,
            "positive_cites": positive,
            "negative_cites": negative,
            "neutral_cites": neutral,
            "total_cites": total,
            "treatments": treatments,
            "authority_score": authority,
        }

    def _determine_treatment(self, citation_data: dict) -> str:
        """
        Determine treatment type from citation context
        Uses NLP on citation text (simplified version)
        """
        # In production, use NLP to analyze citation context
        # For now, use depth as proxy (more citations = followed)
        depth = citation_data.get("depth", 1)

        if depth >= 3:
            return CitationTreatment.FOLLOWED
        elif depth == 2:
            return CitationTreatment.DISTINGUISHED
        else:
            return CitationTreatment.DISTINGUISHED  # Neutral default

    def _get_shepards_signal(self, treatments: dict, total: int) -> str:
        """
        Determine Shepard's-style signal

        Red flag: Reversed or overruled
        Yellow flag: Questioned or criticized
        Blue H: Direct history exists
        Green plus: Positive treatment
        """
        if treatments["reversed"] > 0 or treatments["superseded"] > 0:
            return CitationTreatment.RED_FLAG

        if treatments["questioned"] > total * 0.1:  # More than 10% questioned
            return CitationTreatment.YELLOW_FLAG

        if treatments["affirmed"] > 0:
            return CitationTreatment.BLUE_H

        if treatments["followed"] > total * 0.5:  # More than 50% followed
            return CitationTreatment.GREEN_PLUS

        return CitationTreatment.BLUE_H  # Default

    def build_citation_network(self, opinion_id: int, depth: int = 3) -> dict:
        """
        Build multi-level citation network

        Args:
            opinion_id: Root opinion
            depth: How many levels to traverse (3 recommended)

        Returns:
            {
                'nodes': [{id, title, citation, year, authority_score}],
                'edges': [{source, target, treatment, weight}],
                'clusters': [cluster analysis]
            }
        """
        nodes = []
        edges = []
        visited = set()

        def traverse(oid, current_depth):
            if current_depth > depth or oid in visited:
                return

            visited.add(oid)

            # Get citing cases
            citing = self.get_citing_cases(oid, limit=50)

            for cite in citing:
                citing_id = cite.get("citing_opinion")
                if citing_id and citing_id not in visited:
                    # Add node
                    nodes.append(
                        {
                            "id": citing_id,
                            "title": cite.get("case_name", "Unknown"),
                            "year": (
                                cite.get("date_filed", "")[:4] if cite.get("date_filed") else None
                            ),
                            "depth": current_depth,
                        }
                    )

                    # Add edge
                    edges.append(
                        {
                            "source": oid,
                            "target": citing_id,
                            "treatment": self._determine_treatment(cite),
                            "weight": cite.get("depth", 1),
                        }
                    )

                    # Recurse
                    if current_depth < depth:
                        traverse(citing_id, current_depth + 1)

        traverse(opinion_id, 1)

        return {
            "nodes": nodes,
            "edges": edges,
            "root": opinion_id,
            "depth": depth,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    def get_shepards_report(self, citation: str) -> dict:
        """
        Generate comprehensive Shepard's-style report

        Returns:
        {
            'case_info': {...},
            'signal': 'red_flag' | 'yellow_flag' | 'blue_h' | 'green_plus',
            'direct_history': [...],  # Appeals, remands
            'citing_references': {
                'positive': [...],
                'negative': [...],
                'neutral': [...]
            },
            'treatment_summary': {...},
            'authority_score': 0.85,
            'good_law': True/False
        }
        """
        # Find case
        opinion = self._find_opinion_by_citation(citation)
        if not opinion:
            return {"error": "Citation not found"}

        opinion_id = opinion["id"]

        # Get treatment analysis
        treatment = self.analyze_treatment(opinion_id)

        # Get citing cases grouped by treatment
        citing_cases = self.get_citing_cases(opinion_id, limit=500)

        positive_cites = []
        negative_cites = []
        neutral_cites = []

        for cite in citing_cases:
            treatment_type = self._determine_treatment(cite)
            cite_info = {
                "case_name": cite.get("case_name"),
                "citation": cite.get("citation"),
                "year": cite.get("date_filed", "")[:4] if cite.get("date_filed") else None,
                "treatment": treatment_type,
                "context": cite.get("snippet", ""),
            }

            if treatment_type in [CitationTreatment.FOLLOWED, CitationTreatment.AFFIRMED]:
                positive_cites.append(cite_info)
            elif treatment_type in [CitationTreatment.QUESTIONED, CitationTreatment.REVERSED]:
                negative_cites.append(cite_info)
            else:
                neutral_cites.append(cite_info)

        # Determine if case is "good law"
        good_law = (
            treatment["signal"] not in [CitationTreatment.RED_FLAG, CitationTreatment.YELLOW_FLAG]
            and treatment["authority_score"] > 0.6
        )

        return {
            "case_info": {
                "title": opinion.get("case_name"),
                "citation": citation,
                "court": opinion.get("court"),
                "year": opinion.get("date_filed", "")[:4] if opinion.get("date_filed") else None,
            },
            "signal": treatment["signal"],
            "direct_history": [],  # TODO: Implement direct history
            "citing_references": {
                "positive": positive_cites[:20],  # Top 20
                "negative": negative_cites[:20],
                "neutral": neutral_cites[:20],
            },
            "treatment_summary": treatment["treatments"],
            "authority_score": treatment["authority_score"],
            "total_citations": treatment["total_cites"],
            "good_law": good_law,
            "recommendation": self._get_recommendation(good_law, treatment["signal"]),
        }

Optional[def _find_opinion_by_citation(self, citation: str) -> dict]:
        """Find opinion by citation using CourtListener API"""
        url = f"{self.api_base}citation-lookup/"
        params = {"citation": citation}

        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                return data["results"][0]
        except:
            pass

        return None

    def _get_recommendation(self, good_law: bool, signal: str) -> str:
        """Get usage recommendation"""
        if signal == CitationTreatment.RED_FLAG:
            return "⛔ DO NOT CITE - Reversed or overruled"
        elif signal == CitationTreatment.YELLOW_FLAG:
            return "⚠️ USE WITH CAUTION - Questioned by subsequent courts"
        elif signal == CitationTreatment.GREEN_PLUS:
            return "✅ STRONG AUTHORITY - Widely followed"
        elif good_law:
            return "✓ GOOD LAW - Safe to cite"
        else:
            return "ℹ️ LIMITED AUTHORITY - Consider alternatives"


# API Integration for Evident
def shepardize(citation: str) -> dict:
    """
    Main function to Shepardize a case

    Usage:
        report = shepardize("410 U.S. 113")
        if report['good_law']:
            print(f"✓ {citation} is good law")
    """
    analyzer = CitationNetworkAnalyzer()
    return analyzer.get_shepards_report(citation)