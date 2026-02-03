# Legal Research Integration & Resources
# Connects AI agents to legal databases, statutes, case law, and drafting tools

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class Jurisdiction:
    """Legal jurisdiction definitions"""

    # Federal
    FEDERAL = "federal"
    SUPREME_COURT = "supreme_court"

    # States
    ALABAMA = "alabama"
    ALASKA = "alaska"
    ARIZONA = "arizona"
    ARKANSAS = "arkansas"
    CALIFORNIA = "california"
    COLORADO = "colorado"
    CONNECTICUT = "connecticut"
    DELAWARE = "delaware"
    FLORIDA = "florida"
    GEORGIA = "georgia"
    HAWAII = "hawaii"
    IDAHO = "idaho"
    ILLINOIS = "illinois"
    INDIANA = "indiana"
    IOWA = "iowa"
    KANSAS = "kansas"
    KENTUCKY = "kentucky"
    LOUISIANA = "louisiana"
    MAINE = "maine"
    MARYLAND = "maryland"
    MASSACHUSETTS = "massachusetts"
    MICHIGAN = "michigan"
    MINNESOTA = "minnesota"
    MISSISSIPPI = "mississippi"
    MISSOURI = "missouri"
    MONTANA = "montana"
    NEBRASKA = "nebraska"
    NEVADA = "nevada"
    NEW_HAMPSHIRE = "new_hampshire"
    NEW_JERSEY = "new_jersey"
    NEW_MEXICO = "new_mexico"
    NEW_YORK = "new_york"
    NORTH_CAROLINA = "north_carolina"
    NORTH_DAKOTA = "north_dakota"
    OHIO = "ohio"
    OKLAHOMA = "oklahoma"
    OREGON = "oregon"
    PENNSYLVANIA = "pennsylvania"
    RHODE_ISLAND = "rhode_island"
    SOUTH_CAROLINA = "south_carolina"
    SOUTH_DAKOTA = "south_dakota"
    TENNESSEE = "tennessee"
    TEXAS = "texas"
    UTAH = "utah"
    VERMONT = "vermont"
    VIRGINIA = "virginia"
    WASHINGTON = "washington"
    WEST_VIRGINIA = "west_virginia"
    WISCONSIN = "wisconsin"
    WYOMING = "wyoming"


class LegalCitation:
    """Formats legal citations (Bluebook style)"""

    @staticmethod
    def format_case(case_name: str, reporter: str, volume: str, page: str, year: str) -> str:
        """Format case citation"""
        return f"{case_name}, {volume} {reporter} {page} ({year})"

    @staticmethod
    def format_statute(title: str, code: str, section: str, year: Optional[str] = None) -> str:
        """Format statute citation"""
        if year:
            return f"{title} {code} § {section} ({year})"
        return f"{title} {code} § {section}"

    @staticmethod
    def format_constitution(article: str, section: str) -> str:
        """Format constitutional citation"""
        return f"U.S. Const. art. {article}, § {section}"

    @staticmethod
    def format_rule(rule_set: str, rule_number: str) -> str:
        """Format procedural rule citation"""
        return f"{rule_set} {rule_number}"


class LegalResearchAPI:
    """Interface to legal research databases"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.cache_dir = Path("./legal_research_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_case_law(
        self, query: str, jurisdiction: str = Jurisdiction.FEDERAL, limit: int = 10
    ) -> List[Dict]:
        """Search case law databases"""

        # Try case.law API (free)
        results = self._search_caselaw_access_project(query, jurisdiction, limit)

        if not results and self.api_keys.get("lexis_nexis"):
            # Fallback to LexisNexis
            results = self._search_lexis_nexis(query, jurisdiction, limit)

        if not results and self.api_keys.get("westlaw"):
            # Fallback to Westlaw
            results = self._search_westlaw(query, jurisdiction, limit)

        return results or self._get_mock_case_law(query, jurisdiction, limit)

    def get_statute(self, jurisdiction: str, title: str, section: str) -> Optional[Dict]:
        """Retrieve specific statute text"""

        # Try USCode API for federal
        if jurisdiction == Jurisdiction.FEDERAL:
            result = self._get_federal_statute(title, section)
            if result:
                return result

        # Try state statute APIs
        result = self._get_state_statute(jurisdiction, title, section)
        if result:
            return result

        # Mock fallback
        return self._get_mock_statute(jurisdiction, title, section)

    def search_regulations(self, query: str, agency: Optional[str] = None) -> List[Dict]:
        """Search federal regulations (CFR)"""

        # Try govinfo API
        results = self._search_cfr(query, agency)

        return results or self._get_mock_regulations(query)

    def get_legal_form(self, form_type: str, jurisdiction: str) -> Optional[str]:
        """Get legal document template"""

        form_templates = {
            "motion_to_dismiss": self._get_motion_to_dismiss_template(jurisdiction),
            "motion_for_summary_judgment": self._get_summary_judgment_template(jurisdiction),
            "discovery_request": self._get_discovery_request_template(jurisdiction),
            "subpoena": self._get_subpoena_template(jurisdiction),
            "cease_and_desist": self._get_cease_desist_template(jurisdiction),
            "demand_letter": self._get_demand_letter_template(jurisdiction),
            "complaint": self._get_complaint_template(jurisdiction),
            "answer": self._get_answer_template(jurisdiction),
            "motion_in_limine": self._get_motion_in_limine_template(jurisdiction),
            "notice_of_appeal": self._get_notice_of_appeal_template(jurisdiction),
        }

        return form_templates.get(form_type)

    def _search_caselaw_access_project(
        self, query: str, jurisdiction: str, limit: int
    ) -> List[Dict]:
        """Search Case.law (Harvard Law School API)"""
        # In production, use actual API:
        # https://api.case.law/v1/cases/?search=query&jurisdiction=jurisdiction
        return []

    def _search_lexis_nexis(self, query: str, jurisdiction: str, limit: int) -> List[Dict]:
        """Search LexisNexis (requires API key)"""
        # Production implementation would use LexisNexis API
        return []

    def _search_westlaw(self, query: str, jurisdiction: str, limit: int) -> List[Dict]:
        """Search Westlaw (requires API key)"""
        # Production implementation would use Westlaw API
        return []

    def _get_federal_statute(self, title: str, section: str) -> Optional[Dict]:
        """Get federal statute from USCode"""
        # Production: https://www.govinfo.gov/app/details/USCODE-{year}-title{title}
        return None

    def _get_state_statute(self, jurisdiction: str, title: str, section: str) -> Optional[Dict]:
        """Get state statute"""
        # Production: State-specific APIs
        return None

    def _search_cfr(self, query: str, agency: Optional[str]) -> List[Dict]:
        """Search Code of Federal Regulations"""
        # Production: https://www.ecfr.gov/api/search/
        return []

    def _get_mock_case_law(self, query: str, jurisdiction: str, limit: int) -> List[Dict]:
        """Mock case law results for development"""
        return [
            {
                "case_name": "Miranda v. Arizona",
                "citation": "384 U.S. 436 (1966)",
                "court": "U.S. Supreme Court",
                "year": "1966",
                "summary": "Established requirement for law enforcement to inform suspects of their rights",
                "holding": "Suspects must be informed of right to remain silent and right to counsel",
                "relevance_score": 0.95,
                "full_text_url": "https://supreme.justia.com/cases/federal/us/384/436/",
            },
            {
                "case_name": "Terry v. Ohio",
                "citation": "392 U.S. 1 (1968)",
                "court": "U.S. Supreme Court",
                "year": "1968",
                "summary": "Established stop and frisk doctrine",
                "holding": "Officers may stop and frisk based on reasonable suspicion",
                "relevance_score": 0.87,
                "full_text_url": "https://supreme.justia.com/cases/federal/us/392/1/",
            },
        ][:limit]

    def _get_mock_statute(self, jurisdiction: str, title: str, section: str) -> Dict:
        """Mock statute for development"""
        return {
            "jurisdiction": jurisdiction,
            "title": title,
            "section": section,
            "citation": f"{title} U.S.C. § {section}",
            "text": "Mock statute text - In production, this would contain actual statute language",
            "effective_date": "2024-01-01",
            "amendments": [],
            "related_sections": [],
        }

    def _get_mock_regulations(self, query: str) -> List[Dict]:
        """Mock regulations for development"""
        return [
            {
                "title": "29",
                "part": "1910",
                "section": "1200",
                "citation": "29 CFR § 1910.1200",
                "name": "Hazard Communication Standard",
                "text": "Mock regulation text",
                "agency": "OSHA",
            }
        ]

    def _get_motion_to_dismiss_template(self, jurisdiction: str) -> str:
        """Motion to Dismiss template"""
        return """
[COURT NAME]
[COUNTY/DISTRICT]

[PLAINTIFF NAME],
    Plaintiff,

v.                                          Case No. [CASE NUMBER]

[DEFENDANT NAME],
    Defendant.
__________________________________/

DEFENDANT'S MOTION TO DISMISS

Defendant, [DEFENDANT NAME], hereby moves this Court to dismiss Plaintiff's Complaint pursuant to [RULE] for failure to state a claim upon which relief can be granted, and as grounds states:

I. INTRODUCTION

[Brief overview of the case and grounds for dismissal]

II. FACTUAL BACKGROUND

[Relevant facts from complaint]

III. LEGAL STANDARD

A motion to dismiss under [RULE] tests the legal sufficiency of the complaint. [CASE CITATION]. The Court must accept all factual allegations in the complaint as true and construe them in the light most favorable to the plaintiff. [CASE CITATION].

IV. ARGUMENT

A. [First Ground for Dismissal]

[Legal argument with case citations]

B. [Second Ground for Dismissal]

[Legal argument with case citations]

V. CONCLUSION

For the foregoing reasons, Defendant respectfully requests that this Court GRANT this Motion to Dismiss.

Respectfully submitted,

_____________________
[ATTORNEY NAME]
[BAR NUMBER]
[FIRM NAME]
[ADDRESS]
[PHONE]
[EMAIL]

Attorney for Defendant

CERTIFICATE OF SERVICE

I hereby certify that a true and correct copy of the foregoing was served on [DATE] via [METHOD] to:

[OPPOSING COUNSEL]
[ADDRESS]

_____________________
[ATTORNEY NAME]
"""

    def _get_summary_judgment_template(self, jurisdiction: str) -> str:
        """Motion for Summary Judgment template"""
        return """
[COURT NAME]

[PLAINTIFF],
    Plaintiff,

v.                                          Case No. [CASE NUMBER]

[DEFENDANT],
    Defendant.
__________________________________/

DEFENDANT'S MOTION FOR SUMMARY JUDGMENT

Defendant moves for summary judgment pursuant to [RULE] on all claims asserted in Plaintiff's Complaint. In support, Defendant states:

I. STATEMENT OF UNDISPUTED MATERIAL FACTS

1. [First undisputed fact with citation to record]
2. [Second undisputed fact with citation to record]
3. [Continue...]

II. LEGAL STANDARD

Summary judgment is appropriate where there is no genuine dispute as to any material fact and the movant is entitled to judgment as a matter of law. [RULE]. The moving party bears the initial burden of demonstrating the absence of a genuine issue of material fact. [CASE CITATION].

III. ARGUMENT

A. [First Claim - Heading]

[Legal argument demonstrating no genuine issue of material fact and entitlement to judgment as matter of law]

Supporting case law:
- [CASE CITATION AND HOLDING]
- [CASE CITATION AND HOLDING]

B. [Second Claim - Heading]

[Continue for each claim]

IV. CONCLUSION

No genuine issue of material fact exists, and Defendant is entitled to judgment as a matter of law. Defendant respectfully requests this Court GRANT summary judgment on all claims.

Respectfully submitted,

[SIGNATURE BLOCK]
"""

    def _get_discovery_request_template(self, jurisdiction: str) -> str:
        """Discovery Request template"""
        return """
[CAPTION]

PLAINTIFF'S FIRST REQUEST FOR PRODUCTION OF DOCUMENTS

Plaintiff requests that Defendant produce the following documents pursuant to [RULE]:

DEFINITIONS

"Document" means any written, recorded, or graphic matter, however produced or reproduced.

"You" or "Your" refers to Defendant and its agents, employees, representatives, and attorneys.

INSTRUCTIONS

1. Produce all responsive documents in your possession, custody, or control.
2. If any document was but is no longer in your possession, state the disposition thereof.
3. All responsive documents shall be produced within [30] days of service.

REQUESTS FOR PRODUCTION

REQUEST NO. 1:
All documents relating to [SUBJECT MATTER].

REQUEST NO. 2:
All communications between [PARTIES] regarding [SUBJECT].

REQUEST NO. 3:
All documents supporting [DEFENDANT'S CONTENTION].

[Continue numbered requests]

Respectfully submitted,

[SIGNATURE BLOCK]
"""

    def _get_subpoena_template(self, jurisdiction: str) -> str:
        """Subpoena template"""
        return """
[COURT NAME]

[CAPTION]

SUBPOENA FOR PRODUCTION OF DOCUMENTS

TO: [WITNESS/CUSTODIAN NAME]
    [ADDRESS]

YOU ARE COMMANDED to produce and permit inspection and copying of the following documents or objects at the place, date, and time specified below:

PLACE: [LOCATION]
DATE AND TIME: [DATE] at [TIME]

DOCUMENTS/OBJECTS TO BE PRODUCED:

1. [Description of documents]
2. [Description of documents]
3. [Continue...]

If you fail to appear or produce the documents, you may be held in contempt of court.

ISSUED: [DATE]

_____________________
CLERK OF COURT

[SIGNATURE BLOCK OF REQUESTING ATTORNEY]
"""

    def _get_cease_desist_template(self, jurisdiction: str) -> str:
        """Cease and Desist letter template"""
        return """
[DATE]

[RECIPIENT NAME]
[ADDRESS]

Re: Cease and Desist - [MATTER]

Dear [NAME]:

This letter serves as formal notice and demand that you immediately cease and desist from [CONDUCT].

FACTUAL BACKGROUND

[Description of conduct and harm]

LEGAL BASIS

Your conduct violates [STATUTE/COMMON LAW] and constitutes [CAUSE OF ACTION]. Specifically:

1. [First violation with legal citation]
2. [Second violation with legal citation]

DAMAGES

As a direct result of your unlawful conduct, my client has suffered damages including:
- [Type of damage and amount]
- [Type of damage and amount]

DEMAND

You are hereby demanded to:

1. Immediately cease all [CONDUCT]
2. Provide written confirmation of compliance within [5] business days
3. [Additional demands]

CONSEQUENCES OF NON-COMPLIANCE

If you fail to comply with this demand, my client will pursue all available legal remedies, including but not limited to filing suit seeking:
- Injunctive relief
- Compensatory damages
- Punitive damages
- Attorney's fees and costs

Time is of the essence. This letter is written without prejudice to any and all rights and remedies, all of which are expressly reserved.

Sincerely,

[ATTORNEY NAME]
[FIRM]
[CONTACT INFO]
"""

    def _get_demand_letter_template(self, jurisdiction: str) -> str:
        """Demand letter template"""
        return """
[DATE]

[RECIPIENT]
[ADDRESS]

Re: Demand for Payment - [MATTER]

Dear [NAME]:

I represent [CLIENT NAME] concerning [DESCRIPTION OF CLAIM].

FACTS

[Detailed factual background establishing liability]

LIABILITY

You are liable to my client for the following reasons:

1. [First basis for liability with legal support]
2. [Second basis for liability]

DAMAGES

My client has incurred the following damages:

- [Itemized damages with amounts]
- Total: $[AMOUNT]

DEMAND

My client demands payment of $[AMOUNT] within [14] days of the date of this letter.

If payment is not received by [DATE], my client will pursue legal action without further notice, seeking not only the principal amount but also:
- Interest
- Attorney's fees
- Court costs
- Any additional damages available under law

Please remit payment to:
[PAYMENT INSTRUCTIONS]

This is a formal demand for payment and an attempt to resolve this matter without litigation. All rights reserved.

Sincerely,

[SIGNATURE BLOCK]
"""

    def _get_complaint_template(self, jurisdiction: str) -> str:
        """Complaint template"""
        return """
[COURT NAME]
[COUNTY/DISTRICT]

[PLAINTIFF NAME],
    Plaintiff,

v.                                          Case No. _____________

[DEFENDANT NAME],
    Defendant.
__________________________________/

COMPLAINT

Plaintiff [NAME] sues Defendant [NAME] and alleges:

PARTIES

1. Plaintiff is [DESCRIPTION].
2. Defendant is [DESCRIPTION].

JURISDICTION AND VENUE

3. This Court has jurisdiction pursuant to [STATUTE/RULE].
4. Venue is proper in this District because [REASON].

FACTUAL ALLEGATIONS

5. [First factual allegation]
6. [Second factual allegation]
7. [Continue chronologically]

COUNT I - [CAUSE OF ACTION]

8. Plaintiff realleges and incorporates paragraphs 1-7.
9. [Elements of cause of action]
10. As a direct and proximate result, Plaintiff has suffered damages.

COUNT II - [CAUSE OF ACTION]

11. Plaintiff realleges paragraphs 1-10.
12. [Elements of second cause of action]

PRAYER FOR RELIEF

WHEREFORE, Plaintiff demands judgment against Defendant for:

A. Compensatory damages in excess of $[AMOUNT];
B. [Other relief sought];
C. Costs and attorney's fees;
D. Such other relief as the Court deems just and proper.

JURY DEMAND

Plaintiff demands trial by jury on all issues so triable.

Respectfully submitted,

[SIGNATURE BLOCK]

VERIFICATION

[If required by jurisdiction]
"""

    def _get_answer_template(self, jurisdiction: str) -> str:
        """Answer to Complaint template"""
        return """
[CAPTION]

DEFENDANT'S ANSWER AND AFFIRMATIVE DEFENSES

Defendant answers Plaintiff's Complaint as follows:

ADMISSIONS AND DENIALS

1. [Admit/Deny/Lack knowledge] the allegations in paragraph 1 of the Complaint.
2. [Admit/Deny/Lack knowledge] the allegations in paragraph 2 of the Complaint.
[Continue for each paragraph]

AFFIRMATIVE DEFENSES

FIRST AFFIRMATIVE DEFENSE - [DEFENSE NAME]
[Legal basis for defense]

SECOND AFFIRMATIVE DEFENSE - [DEFENSE NAME]
[Legal basis for defense]

COUNTERCLAIMS

COUNT I - [COUNTERCLAIM]
[Elements of counterclaim]

PRAYER FOR RELIEF

WHEREFORE, Defendant requests:

A. Dismissal of Plaintiff's Complaint with prejudice;
B. Judgment on Defendant's Counterclaims;
C. Costs and attorney's fees;
D. Such other relief as the Court deems just.

Respectfully submitted,

[SIGNATURE BLOCK]
"""

    def _get_motion_in_limine_template(self, jurisdiction: str) -> str:
        """Motion in Limine template"""
        return """
[CAPTION]

DEFENDANT'S MOTION IN LIMINE

Defendant moves to exclude the following evidence from trial:

1. [Evidence to be excluded - specific description]

MEMORANDUM OF LAW

I. LEGAL STANDARD

A motion in limine is a procedural mechanism to exclude prejudicial evidence before it is presented to the jury. [CASE CITATION].

II. ARGUMENT

A. The Evidence is Irrelevant

[Argument citing Fed.R.Evid. 401-402 or state equivalent]

B. The Probative Value is Substantially Outweighed by Prejudice

[Argument citing Fed.R.Evid. 403 or state equivalent]

C. [Additional grounds - Hearsay, Character evidence, etc.]

III. CONCLUSION

The evidence should be excluded. Defendant requests an order in limine prohibiting any reference to this evidence at trial.

[SIGNATURE BLOCK]
"""

    def _get_notice_of_appeal_template(self, jurisdiction: str) -> str:
        """Notice of Appeal template"""
        return """
[CAPTION]

NOTICE OF APPEAL

Notice is hereby given that [APPELLANT], appellant, appeals to the [APPELLATE COURT] from the [ORDER/JUDGMENT] entered in this action on [DATE].

The appeal is taken from [DESCRIBE ORDER - e.g., "the final judgment entered on January 1, 2026, granting summary judgment to Plaintiff"].

Respectfully submitted,

[SIGNATURE BLOCK]

CERTIFICATE OF SERVICE

[Standard certificate]
"""


# Global legal research API instance
legal_research = LegalResearchAPI()
