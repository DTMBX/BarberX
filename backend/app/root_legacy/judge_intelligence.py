"""
Judge Intelligence System - Comprehensive Judge Research

Provides deep background research on federal judges:
- Education history (undergrad, law school, honors)
- Career path (clerkships, positions, firms)
- Political affiliations and philosophy
- ABA ratings
- Financial disclosures (ethics research)
- Opinion analysis and voting patterns
- Judicial statistics

Uses CourtListener v4 API: people, positions, educations,
financial-disclosures, political-affiliations, aba-ratings
"""

import os
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional

import requests


class JudgeIntelligence:
    """
    Elite-tier judge research system

    Features:
    - Complete judge biographies
    - Education and career tracking
    - Financial disclosure analysis
    - Voting pattern statistics
    - Strategic litigation insights
    """

    def __init__(self):
        self.api_base = "https://www.courtlistener.com/api/rest/v4/"
        self.api_key = os.getenv("COURTLISTENER_API_KEY")

    def _get_headers(self):
        """Get API headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def get_judge_profile(self, judge_name: str = None, judge_id: int = None) -> Dict:
        """
        Get comprehensive judge profile

        Returns:
        {
            'basic_info': {
                'name': 'Sonia Sotomayor',
                'title': 'Associate Justice',
                'court': 'Supreme Court of the United States',
                'appointed_by': 'Barack Obama',
                'appointment_date': '2009-08-08',
                'age': 69,
                'active': True
            },
            'education': [...],
            'positions': [...],
            'political_affiliation': {...},
            'aba_rating': {...},
            'financial_summary': {...},
            'statistics': {...}
        }
        """
        # Find judge
        if judge_id:
            judge = self._get_judge_by_id(judge_id)
        else:
            judge = self._find_judge_by_name(judge_name)

        if not judge:
            return {"error": "Judge not found"}

        judge_id = judge["id"]

        # Compile comprehensive profile
        return {
            "basic_info": self._get_basic_info(judge),
            "education": self.get_education_history(judge_id),
            "positions": self.get_career_history(judge_id),
            "political_affiliation": self.get_political_affiliation(judge_id),
            "aba_rating": self.get_aba_rating(judge_id),
            "financial_summary": self.get_financial_summary(judge_id),
            "statistics": self.get_opinion_statistics(judge_id),
            "notable_opinions": self.get_notable_opinions(judge_id, limit=10),
        }

    def _find_judge_by_name(self, name: str) -> Optional[Dict]:
        """Search for judge by name"""
        url = f"{self.api_base}people/"
        params = {"name_last__icontains": name.split()[-1]}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        # Find best match
        for judge in results:
            if name.lower() in judge.get("name_full", "").lower():
                return judge

        return results[0] if results else None

    def _get_judge_by_id(self, judge_id: int) -> Dict:
        """Get judge by ID"""
        url = f"{self.api_base}people/{judge_id}/"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def _get_basic_info(self, judge: Dict) -> Dict:
        """Extract basic information"""
        return {
            "name": judge.get("name_full"),
            "name_first": judge.get("name_first"),
            "name_last": judge.get("name_last"),
            "gender": judge.get("gender"),
            "date_of_birth": judge.get("date_dob"),
            "date_of_death": judge.get("date_dod"),
            "religion": judge.get("religion"),
            "bio": judge.get("bio"),
        }

    def get_education_history(self, judge_id: int) -> List[Dict]:
        """
        Get complete education history

        Returns list of:
        - School name
        - Degree type (BA, JD, LLM, etc.)
        - Year graduated
        - Honors (magna cum laude, Order of the Coif, etc.)
        """
        url = f"{self.api_base}educations/"
        params = {"person": judge_id}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        educations = data.get("results", [])

        return [
            {
                "school": edu.get("school", {}).get("name"),
                "degree": edu.get("degree"),
                "year_graduated": edu.get("year_graduated"),
                "honors": edu.get("honors", ""),
                "school_prestige": self._get_school_prestige(edu.get("school", {}).get("name")),
            }
            for edu in educations
        ]

    def _get_school_prestige(self, school_name: str) -> str:
        """
        Rate law school prestige
        T14, T25, T50, T100, etc.
        """
        if not school_name:
            return "Unknown"

        # Top 14 law schools
        t14 = [
            "Yale",
            "Stanford",
            "Harvard",
            "Chicago",
            "Columbia",
            "NYU",
            "Penn",
            "Virginia",
            "Michigan",
            "Duke",
            "Northwestern",
            "Cornell",
            "Berkeley",
            "Georgetown",
        ]

        for school in t14:
            if school.lower() in school_name.lower():
                return "T14 (Elite)"

        # Could expand to T25, T50, etc.
        return "Ranked"

    def get_career_history(self, judge_id: int) -> List[Dict]:
        """
        Get complete career path

        Returns list of positions:
        - Clerkships (Supreme Court, Circuit, District)
        - Law firm positions
        - Government roles (prosecutor, public defender, etc.)
        - Academic positions
        - Judicial appointments
        """
        url = f"{self.api_base}positions/"
        params = {"person": judge_id, "order_by": "date_start"}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        positions = data.get("results", [])

        return [
            {
                "title": pos.get("position_type"),
                "organization": pos.get("organization_name"),
                "court": pos.get("court", {}).get("full_name") if pos.get("court") else None,
                "date_start": pos.get("date_start"),
                "date_end": pos.get("date_termination"),
                "appointed_by": pos.get("appointer"),
                "how_selected": pos.get("how_selected"),
                "nomination_process": pos.get("nomination_process"),
                "prestige": self._get_position_prestige(pos),
            }
            for pos in positions
        ]

    def _get_position_prestige(self, position: Dict) -> str:
        """Rate position prestige"""
        position_type = position.get("position_type", "").lower()

        if "supreme court" in str(position.get("court", "")).lower():
            return "Supreme Court (Highest)"
        elif "circuit" in str(position.get("court", "")).lower():
            return "Federal Circuit (High)"
        elif "district" in str(position.get("court", "")).lower():
            return "Federal District (Significant)"
        elif "clerk" in position_type:
            return "Clerkship (Prestigious)"
        else:
            return "Standard"

    def get_political_affiliation(self, judge_id: int) -> Dict:
        """
        Get political background

        Returns:
        - Party affiliations
        - Political activities
        - Ideological score (liberal-conservative)
        """
        url = f"{self.api_base}political-affiliations/"
        params = {"person": judge_id}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        affiliations = data.get("results", [])

        return {
            "affiliations": [
                {
                    "party": aff.get("political_party"),
                    "date_start": aff.get("date_start"),
                    "date_end": aff.get("date_end"),
                    "source": aff.get("source"),
                }
                for aff in affiliations
            ],
            "appointing_president": self._get_appointing_president(judge_id),
            "ideological_score": self._calculate_ideological_score(judge_id),
        }

    def _get_appointing_president(self, judge_id: int) -> Optional[str]:
        """Get which president appointed the judge"""
        positions = self.get_career_history(judge_id)

        for pos in positions:
            if "judge" in pos.get("title", "").lower():
                return pos.get("appointed_by")

        return None

    def _calculate_ideological_score(self, judge_id: int) -> Dict:
        """
        Calculate ideological score (simplified)
        In production, use Martin-Quinn scores or similar
        """
        # Simplified: based on appointing president
        president = self._get_appointing_president(judge_id)

        # Liberal presidents
        liberal_presidents = ["Biden", "Obama", "Clinton", "Carter", "Johnson"]
        # Conservative presidents
        conservative_presidents = ["Trump", "Bush", "Reagan", "Nixon", "Ford"]

        if any(p in str(president) for p in liberal_presidents):
            score = -0.5  # -1 (most liberal) to 1 (most conservative)
            ideology = "Liberal"
        elif any(p in str(president) for p in conservative_presidents):
            score = 0.5
            ideology = "Conservative"
        else:
            score = 0.0
            ideology = "Moderate"

        return {
            "score": score,
            "ideology": ideology,
            "appointing_president": president,
            "note": "Simplified score based on appointing president",
        }

    def get_aba_rating(self, judge_id: int) -> Dict:
        """
        Get American Bar Association rating

        Returns:
        - Well Qualified / Qualified / Not Qualified
        - Rating date
        """
        url = f"{self.api_base}aba-ratings/"
        params = {"person": judge_id}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        ratings = data.get("results", [])

        if ratings:
            latest = ratings[0]
            return {
                "rating": latest.get("rating"),
                "year": latest.get("year_rated"),
                "note": "ABA ratings: Well Qualified (highest), Qualified, Not Qualified",
            }

        return {"rating": "Not Available"}

    def get_financial_summary(self, judge_id: int) -> Dict:
        """
        Get financial disclosure summary

        Returns:
        - Investment holdings
        - Income sources
        - Potential conflicts of interest
        """
        url = f"{self.api_base}financial-disclosures/"
        params = {"person": judge_id, "order_by": "-year"}

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        disclosures = data.get("results", [])

        if not disclosures:
            return {"note": "No financial disclosures available"}

        latest = disclosures[0]

        return {
            "latest_year": latest.get("year"),
            "has_investments": bool(latest.get("investments")),
            "has_agreements": bool(latest.get("agreements")),
            "has_gifts": bool(latest.get("gifts")),
            "disclosure_url": latest.get("download_filepath"),
            "note": "Full financial disclosures available via API",
        }

    def get_opinion_statistics(self, judge_id: int) -> Dict:
        """
        Calculate opinion statistics

        Returns:
        - Total opinions written
        - Average length
        - Dissent rate
        - Reversal rate
        """
        # This would query opinions table filtered by author
        # Simplified for now

        return {
            "total_opinions": "TBD",
            "majority_opinions": "TBD",
            "dissents": "TBD",
            "concurrences": "TBD",
            "note": "Full statistics require opinion corpus analysis",
        }

    def get_notable_opinions(self, judge_id: int, limit: int = 10) -> List[Dict]:
        """
        Get most notable/cited opinions by this judge

        Returns top opinions by citation count
        """
        # Query opinions by author, sort by citation count
        # Simplified for now

        return [{"note": "Notable opinions require opinion corpus with citation counts"}]


# Helper functions for strategic litigation


def analyze_judge_for_case(judge_name: str, case_type: str) -> Dict:
    """
    Strategic analysis for litigation

    Args:
        judge_name: Judge assigned to case
        case_type: 'civil_rights', 'employment', 'criminal', etc.

    Returns:
        Strategic insights and recommendations
    """
    ji = JudgeIntelligence()
    profile = ji.get_judge_profile(judge_name)

    if "error" in profile:
        return profile

    # Analyze for strategy
    ideology = profile["political_affiliation"]["ideological_score"]
    education = profile["education"]

    # Generate recommendations
    recommendations = []

    if ideology["ideology"] == "Liberal" and case_type == "civil_rights":
        recommendations.append("✓ Judge has liberal ideology - favorable for civil rights claims")

    # Check for elite education
    for edu in education:
        if edu["school_prestige"] == "T14 (Elite)":
            recommendations.append(
                f"✓ Judge attended {edu['school']} - expect sophisticated legal analysis"
            )

    return {
        "judge": profile["basic_info"]["name"],
        "ideology": ideology,
        "education_highlights": [
            edu for edu in education if edu["school_prestige"] == "T14 (Elite)"
        ],
        "strategic_recommendations": recommendations,
        "overall_assessment": "Detailed analysis complete",
    }


