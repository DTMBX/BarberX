# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

# Legal Document Drafting Agents
# Specialized agents for creating motions, briefs, letters using proper legal citations

from datetime import datetime
from typing import Any

from legal_ai_agents import AgentCapability, AgentStatus, LegalAIAgent
from legal_research_integration import Jurisdiction, LegalCitation, legal_research


class MotionDrafterAgent(LegalAIAgent):
    """Agent for drafting legal motions with proper citations"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Motion Drafter",
            capability=AgentCapability.DOCUMENT_ANALYSIS,
            user_id=user_id,
        )

        self.config = {
            "motion_type": "motion_to_dismiss",
            "jurisdiction": Jurisdiction.FEDERAL,
            "include_case_law": True,
            "include_statutes": True,
            "citation_style": "bluebook",
            "tone": "professional",
        }

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Draft a legal motion"""
        self.status = AgentStatus.PROCESSING

        motion_type = input_data.get("motion_type", self.config["motion_type"])
        jurisdiction = input_data.get("jurisdiction", self.config["jurisdiction"])
        facts = input_data.get("facts", "")
        legal_arguments = input_data.get("legal_arguments", [])

        # Get template
        template = legal_research.get_legal_form(motion_type, jurisdiction)

        if not template:
            return {"error": f"Template not found for {motion_type}"}

        # Research supporting case law
        case_law = []
        if self.config.get("include_case_law"):
            for argument in legal_arguments:
                cases = legal_research.search_case_law(
                    query=argument.get("query", ""), jurisdiction=jurisdiction, limit=3
                )
                case_law.extend(cases)

        # Research applicable statutes
        statutes = []
        if self.config.get("include_statutes"):
            for statute_ref in input_data.get("statute_refs", []):
                statute = legal_research.get_statute(
                    jurisdiction=jurisdiction,
                    title=statute_ref.get("title"),
                    section=statute_ref.get("section"),
                )
                if statute:
                    statutes.append(statute)

        # Fill template
        drafted_motion = self._fill_template(
            template=template,
            case_info=input_data.get("case_info", {}),
            facts=facts,
            legal_arguments=legal_arguments,
            case_law=case_law,
            statutes=statutes,
        )

        # Format citations
        drafted_motion = self._format_citations(drafted_motion, case_law, statutes)

        results = {
            "motion_type": motion_type,
            "jurisdiction": jurisdiction,
            "drafted_document": drafted_motion,
            "supporting_case_law": case_law,
            "cited_statutes": statutes,
            "word_count": len(drafted_motion.split()),
            "page_estimate": len(drafted_motion.split()) // 250,  # ~250 words per page
            "citations_count": len(case_law) + len(statutes),
        }

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _fill_template(
        self,
        template: str,
        case_info: dict,
        facts: str,
        legal_arguments: list[dict],
        case_law: list[dict],
        statutes: list[dict],
    ) -> str:
        """Fill motion template with case-specific information"""

        # Replace placeholders
        motion = template

        # Case information
        motion = motion.replace("[COURT NAME]", case_info.get("court", "[COURT NAME]"))
        motion = motion.replace("[COUNTY/DISTRICT]", case_info.get("district", "[DISTRICT]"))
        motion = motion.replace("[CASE NUMBER]", case_info.get("case_number", "[CASE NUMBER]"))
        motion = motion.replace("[PLAINTIFF NAME]", case_info.get("plaintiff", "[PLAINTIFF]"))
        motion = motion.replace("[PLAINTIFF]", case_info.get("plaintiff", "[PLAINTIFF]"))
        motion = motion.replace("[DEFENDANT NAME]", case_info.get("defendant", "[DEFENDANT]"))
        motion = motion.replace("[DEFENDANT]", case_info.get("defendant", "[DEFENDANT]"))

        # Attorney information
        motion = motion.replace(
            "[ATTORNEY NAME]", case_info.get("attorney_name", "[ATTORNEY NAME]")
        )
        motion = motion.replace("[BAR NUMBER]", case_info.get("bar_number", "[BAR NUMBER]"))
        motion = motion.replace("[FIRM NAME]", case_info.get("firm_name", "[FIRM NAME]"))
        motion = motion.replace("[ADDRESS]", case_info.get("address", "[ADDRESS]"))
        motion = motion.replace("[PHONE]", case_info.get("phone", "[PHONE]"))
        motion = motion.replace("[EMAIL]", case_info.get("email", "[EMAIL]"))

        # Procedural rule (Fed.R.Civ.P. or state equivalent)
        rule = case_info.get("rule", "12(b)(6)")
        motion = motion.replace("[RULE]", rule)

        # Facts section
        if facts:
            motion = motion.replace("[Relevant facts from complaint]", facts)
            motion = motion.replace(
                "[Brief overview of the case and grounds for dismissal]",
                f"This motion seeks dismissal based on {facts[:200]}...",
            )

        # Legal arguments
        if legal_arguments:
            arguments_text = ""
            for i, arg in enumerate(legal_arguments, 1):
                heading = arg.get("heading", f"Argument {i}")
                content = arg.get("content", "")

                # Add supporting case citations
                relevant_cases = [
                    c
                    for c in case_law
                    if any(
                        keyword in c.get("summary", "").lower()
                        for keyword in arg.get("keywords", [])
                    )
                ]

                citations = "\n\n".join(
                    [
                        f"{c['case_name']}, {c['citation']} ({c['holding']})"
                        for c in relevant_cases[:3]
                    ]
                )

                arguments_text += f"\n\n{chr(64 + i)}. {heading}\n\n{content}\n\n{citations}\n"

            motion = motion.replace("[Legal argument with case citations]", arguments_text)
            motion = motion.replace(
                "[First Ground for Dismissal]", legal_arguments[0].get("heading", "")
            )
            if len(legal_arguments) > 1:
                motion = motion.replace(
                    "[Second Ground for Dismissal]", legal_arguments[1].get("heading", "")
                )

        # Date
        motion = motion.replace("[DATE]", datetime.now().strftime("%B %d, %Y"))

        return motion

    def _format_citations(self, text: str, cases: list[dict], statutes: list[dict]) -> str:
        """Format legal citations in Bluebook style"""

        # Replace case placeholders with proper citations
        for case in cases:
            placeholder = "[CASE CITATION]"
            citation = LegalCitation.format_case(
                case_name=case["case_name"],
                reporter=case["citation"].split()[1],
                volume=case["citation"].split()[0],
                page=case["citation"].split()[2],
                year=case["year"],
            )
            text = text.replace(placeholder, citation, 1)

        # Replace statute placeholders
        for statute in statutes:
            placeholder = "[STATUTE CITATION]"
            citation = statute.get("citation", "")
            text = text.replace(placeholder, citation, 1)

        return text


class BriefWriterAgent(LegalAIAgent):
    """Agent for writing legal briefs and memoranda"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Brief Writer",
            capability=AgentCapability.DOCUMENT_ANALYSIS,
            user_id=user_id,
        )

        self.config = {
            "brief_type": "memorandum",  # memorandum, appellate_brief, trial_brief
            "jurisdiction": Jurisdiction.FEDERAL,
            "max_pages": 25,
            "include_table_of_authorities": True,
            "research_depth": "comprehensive",  # basic, standard, comprehensive
        }

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Write a legal brief"""
        self.status = AgentStatus.PROCESSING

        brief_type = input_data.get("brief_type", self.config["brief_type"])
        jurisdiction = input_data.get("jurisdiction", self.config["jurisdiction"])
        issue = input_data.get("issue", "")
        facts = input_data.get("facts", "")
        arguments = input_data.get("arguments", [])

        # Research case law
        research_results = self._conduct_legal_research(issue, arguments, jurisdiction)

        # Structure brief
        brief_structure = self._create_brief_structure(
            brief_type=brief_type,
            issue=issue,
            facts=facts,
            arguments=arguments,
            research=research_results,
        )

        # Draft each section
        drafted_brief = self._draft_brief(brief_structure, research_results)

        # Create table of authorities
        table_of_authorities = ""
        if self.config.get("include_table_of_authorities"):
            table_of_authorities = self._create_table_of_authorities(research_results)

        results = {
            "brief_type": brief_type,
            "drafted_brief": drafted_brief,
            "table_of_authorities": table_of_authorities,
            "case_law_cited": len(research_results.get("cases", [])),
            "statutes_cited": len(research_results.get("statutes", [])),
            "word_count": len(drafted_brief.split()),
            "page_estimate": len(drafted_brief.split()) // 250,
        }

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _conduct_legal_research(self, issue: str, arguments: list[dict], jurisdiction: str) -> dict:
        """Conduct comprehensive legal research"""

        results = {"cases": [], "statutes": [], "regulations": [], "secondary_sources": []}

        # Search case law for each argument
        for arg in arguments:
            query = arg.get("query", issue)
            cases = legal_research.search_case_law(query, jurisdiction, limit=5)
            results["cases"].extend(cases)

        # Search for applicable statutes
        # (In production, would parse issue to identify relevant statutes)

        # Search regulations if federal issue
        if jurisdiction == Jurisdiction.FEDERAL:
            regs = legal_research.search_regulations(issue)
            results["regulations"].extend(regs)

        return results

    def _create_brief_structure(
        self, brief_type: str, issue: str, facts: str, arguments: list[dict], research: dict
    ) -> dict:
        """Create outline structure for brief"""

        structure = {
            "caption": {},
            "table_of_contents": [],
            "table_of_authorities": [],
            "statement_of_issues": [issue],
            "statement_of_facts": facts,
            "summary_of_argument": "",
            "argument": arguments,
            "conclusion": "",
        }

        return structure

    def _draft_brief(self, structure: dict, research: dict) -> str:
        """Draft the full brief"""

        brief = """
MEMORANDUM OF LAW

I. STATEMENT OF ISSUES

{issues}

II. STATEMENT OF FACTS

{facts}

III. SUMMARY OF ARGUMENT

{summary}

IV. ARGUMENT

{arguments}

V. CONCLUSION

{conclusion}
"""

        # Fill in sections
        issues_text = "\n".join(
            [f"{i + 1}. {issue}" for i, issue in enumerate(structure["statement_of_issues"])]
        )

        arguments_text = ""
        for i, arg in enumerate(structure["argument"], 1):
            heading = arg.get("heading", f"Point {i}")
            content = arg.get("content", "")

            # Add supporting case law
            supporting_cases = research["cases"][:2] if i == 1 else research["cases"][2:4]
            case_discussion = "\n\n".join(
                [
                    f"In {case['case_name']}, {case['citation']}, the court held that {case['holding']}. {case['summary']}"
                    for case in supporting_cases
                ]
            )

            arguments_text += f"\n\n{chr(64 + i)}. {heading}\n\n{content}\n\n{case_discussion}\n"

        brief = brief.format(
            issues=issues_text,
            facts=structure["statement_of_facts"],
            summary="[Summary will be generated]",
            arguments=arguments_text,
            conclusion="For the foregoing reasons, the Court should [REQUESTED RELIEF].",
        )

        return brief

    def _create_table_of_authorities(self, research: dict) -> str:
        """Create table of authorities"""

        toa = "TABLE OF AUTHORITIES\n\nCases\n\n"

        for case in sorted(research.get("cases", []), key=lambda x: x["case_name"]):
            toa += f"{case['case_name']}, {case['citation']} ..................... [PAGE]\n"

        toa += "\n\nStatutes\n\n"

        for statute in sorted(research.get("statutes", []), key=lambda x: x.get("citation", "")):
            toa += f"{statute.get('citation', '')} ..................... [PAGE]\n"

        return toa


class LegalLetterAgent(LegalAIAgent):
    """Agent for drafting legal letters (demand, cease & desist, etc.)"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Legal Letter Writer",
            capability=AgentCapability.DOCUMENT_ANALYSIS,
            user_id=user_id,
        )

        self.config = {
            "letter_type": "demand_letter",  # demand_letter, cease_and_desist, opinion_letter
            "tone": "firm",  # firm, diplomatic, aggressive
            "include_legal_citations": True,
        }

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Draft a legal letter"""
        self.status = AgentStatus.PROCESSING

        letter_type = input_data.get("letter_type", self.config["letter_type"])
        jurisdiction = input_data.get("jurisdiction", Jurisdiction.FEDERAL)

        # Get template
        template = legal_research.get_legal_form(letter_type, jurisdiction)

        # Fill template
        letter = self._fill_letter_template(
            template=template,
            client_info=input_data.get("client_info", {}),
            recipient_info=input_data.get("recipient_info", {}),
            facts=input_data.get("facts", ""),
            legal_basis=input_data.get("legal_basis", []),
            demands=input_data.get("demands", []),
        )

        # Add legal citations if requested
        if self.config.get("include_legal_citations"):
            letter = self._add_citations(
                letter, input_data.get("causes_of_action", []), jurisdiction
            )

        results = {
            "letter_type": letter_type,
            "drafted_letter": letter,
            "word_count": len(letter.split()),
        }

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _fill_letter_template(
        self,
        template: str,
        client_info: dict,
        recipient_info: dict,
        facts: str,
        legal_basis: list[str],
        demands: list[str],
    ) -> str:
        """Fill letter template"""

        letter = template

        # Date
        letter = letter.replace("[DATE]", datetime.now().strftime("%B %d, %Y"))

        # Recipient
        letter = letter.replace("[RECIPIENT NAME]", recipient_info.get("name", "[NAME]"))
        letter = letter.replace("[RECIPIENT]", recipient_info.get("name", "[NAME]"))
        letter = letter.replace("[ADDRESS]", recipient_info.get("address", "[ADDRESS]"))
        letter = letter.replace("[NAME]", recipient_info.get("name", "[NAME]"))

        # Client
        letter = letter.replace("[CLIENT NAME]", client_info.get("name", "[CLIENT]"))

        # Matter description
        letter = letter.replace("[MATTER]", client_info.get("matter", "Legal Matter"))
        letter = letter.replace(
            "[DESCRIPTION OF CLAIM]", client_info.get("claim_description", "the matter at issue")
        )

        # Facts
        letter = letter.replace("[Detailed factual background establishing liability]", facts)
        letter = letter.replace("[Description of conduct and harm]", facts)
        letter = letter.replace(
            "[CONDUCT]", client_info.get("prohibited_conduct", "the conduct at issue")
        )

        # Legal basis
        if legal_basis:
            legal_text = "\n".join([f"{i + 1}. {basis}" for i, basis in enumerate(legal_basis)])
            letter = letter.replace(
                "[First basis for liability with legal support]",
                legal_basis[0] if legal_basis else "",
            )
            letter = letter.replace(
                "[Second basis for liability]", legal_basis[1] if len(legal_basis) > 1 else ""
            )
            letter = letter.replace(
                "[First violation with legal citation]", legal_basis[0] if legal_basis else ""
            )
            letter = letter.replace(
                "[Second violation with legal citation]",
                legal_basis[1] if len(legal_basis) > 1 else "",
            )

        # Demands
        if demands:
            demands_text = "\n".join([f"{i + 1}. {demand}" for i, demand in enumerate(demands)])
            letter = letter.replace("[Additional demands]", demands_text)

        # Attorney info
        letter = letter.replace("[ATTORNEY NAME]", client_info.get("attorney_name", "[ATTORNEY]"))
        letter = letter.replace("[FIRM]", client_info.get("firm_name", "[FIRM]"))
        letter = letter.replace("[CONTACT INFO]", client_info.get("contact", "[CONTACT]"))

        # Amounts
        letter = letter.replace("[AMOUNT]", client_info.get("demand_amount", "TBD"))

        # Deadlines
        letter = letter.replace("[5]", str(client_info.get("response_days", 5)))
        letter = letter.replace("[14]", str(client_info.get("payment_days", 14)))

        return letter

    def _add_citations(self, letter: str, causes_of_action: list[str], jurisdiction: str) -> str:
        """Add legal citations to letter"""

        for cause in causes_of_action:
            # Search for supporting case law
            cases = legal_research.search_case_law(cause, jurisdiction, limit=1)

            if cases:
                case = cases[0]
                citation = f" See {case['case_name']}, {case['citation']}."

                # Add citation after cause of action mention
                letter = letter.replace("[CAUSE OF ACTION]", f"{cause}.{citation}", 1)
                letter = letter.replace(
                    "constitutes [CAUSE OF ACTION]", f"constitutes {cause}.{citation}", 1
                )

        return letter


class ContractDrafterAgent(LegalAIAgent):
    """Agent for drafting contracts and agreements"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Contract Drafter",
            capability=AgentCapability.DOCUMENT_ANALYSIS,
            user_id=user_id,
        )

        self.config = {
            "contract_type": "nda",  # nda, service_agreement, employment, purchase
            "jurisdiction": Jurisdiction.FEDERAL,
            "include_boilerplate": True,
            "favor_client": True,  # true = favor drafter's client
        }

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Draft a contract"""
        self.status = AgentStatus.PROCESSING

        contract_type = input_data.get("contract_type", self.config["contract_type"])

        # Get base template
        template = self._get_contract_template(contract_type)

        # Customize for parties
        contract = self._customize_contract(
            template=template,
            party1=input_data.get("party1", {}),
            party2=input_data.get("party2", {}),
            terms=input_data.get("terms", {}),
            special_provisions=input_data.get("special_provisions", []),
        )

        results = {
            "contract_type": contract_type,
            "drafted_contract": contract,
            "word_count": len(contract.split()),
            "page_estimate": len(contract.split()) // 250,
        }

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _get_contract_template(self, contract_type: str) -> str:
        """Get contract template"""

        # Simplified NDA template
        if contract_type == "nda":
            return """
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of [DATE] by and between:

[PARTY1_NAME] ("Disclosing Party")
and
[PARTY2_NAME] ("Receiving Party")

WHEREAS, the parties wish to explore a business opportunity and will share confidential information;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree:

1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means [DEFINITION]

2. OBLIGATIONS OF RECEIVING PARTY
   The Receiving Party agrees to:
   a) Maintain confidentiality
   b) Use information only for [PURPOSE]
   c) Limit disclosure to necessary personnel

3. EXCLUSIONS
   Confidential Information does not include information that:
   [EXCLUSIONS]

4. TERM
   This Agreement shall remain in effect for [TERM] years.

5. RETURN OF MATERIALS
   Upon termination, Receiving Party shall return all materials.

6. NO LICENSE
   No license or ownership rights are granted.

7. GOVERNING LAW
   This Agreement shall be governed by the laws of [JURISDICTION].

IN WITNESS WHEREOF, the parties have executed this Agreement.

[SIGNATURE BLOCKS]
"""

        return "[CONTRACT TEMPLATE]"

    def _customize_contract(
        self, template: str, party1: dict, party2: dict, terms: dict, special_provisions: list[str]
    ) -> str:
        """Customize contract for specific parties"""

        contract = template

        # Parties
        contract = contract.replace("[PARTY1_NAME]", party1.get("name", "[PARTY 1]"))
        contract = contract.replace("[PARTY2_NAME]", party2.get("name", "[PARTY 2]"))

        # Date
        contract = contract.replace("[DATE]", datetime.now().strftime("%B %d, %Y"))

        # Terms
        contract = contract.replace(
            "[DEFINITION]", terms.get("confidential_info_definition", "all information disclosed")
        )
        contract = contract.replace(
            "[PURPOSE]", terms.get("purpose", "evaluation of business opportunity")
        )
        contract = contract.replace("[TERM]", str(terms.get("term_years", 2)))
        contract = contract.replace("[JURISDICTION]", terms.get("jurisdiction", "Delaware"))

        # Special provisions
        if special_provisions:
            provisions_text = "\n\n".join([f"  {prov}" for prov in special_provisions])
            contract = contract.replace("[EXCLUSIONS]", provisions_text)

        return contract


# Export document drafting agents
__all__ = ["MotionDrafterAgent", "BriefWriterAgent", "LegalLetterAgent", "ContractDrafterAgent"]
