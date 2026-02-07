from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Smart Tools - Free AI capabilities for enhanced chat

Features:
1. Web Search (DuckDuckGo - free, no API key required)
2. Math Engine (sympy for symbolic math, built-in eval for basic)
3. Legal Knowledge Base (built-in definitions and concepts)
4. Wikipedia Quick Lookup
5. Unit Conversion
6. Date/Time Calculations
"""

import json
import logging
import math
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from a tool invocation"""

    tool: str
    success: bool
    data: Any
    source: str = ""
    confidence: float = 1.0
Optional[error: str] = None


class SmartTools:
    """
    Free smart tools for enhanced chat capabilities

    All tools are free and don't require API keys:
    - DuckDuckGo Instant Answer API
    - Built-in math engine
    - Legal knowledge base
    - Wikipedia API
    """

    # Built-in legal knowledge base
    LEGAL_KNOWLEDGE = {
        # Criminal Law Terms
        "jaywalking": {
            "definition": "Jaywalking is the act of crossing a street outside of a designated crosswalk or against traffic signals. It is a minor traffic violation in most jurisdictions.",
            "elements": [
                "Crossing street illegally",
                "Outside crosswalk or against signal",
                "Pedestrian violation",
            ],
            "penalties": "Typically a fine ranging from $20-$250 depending on jurisdiction. Some cities have decriminalized it.",
            "related": ["traffic violation", "pedestrian laws", "crosswalk"],
            "source": "General traffic law principles",
        },
        "probable cause": {
            "definition": "Probable cause is a reasonable basis for believing that a crime may have been committed (for an arrest) or that evidence of a crime is present (for a search). It requires more than mere suspicion but less than proof beyond a reasonable doubt.",
            "elements": [
                "Reasonable belief",
                "Based on facts and circumstances",
                "Would lead prudent person to believe",
            ],
            "legal_standard": "Fourth Amendment requirement for arrests and searches",
            "key_cases": ["Illinois v. Gates (1983)", "Brinegar v. United States (1949)"],
            "source": "Fourth Amendment jurisprudence",
        },
        "miranda rights": {
            "definition": "Miranda rights are constitutional rights that must be read to criminal suspects in police custody before interrogation. They include the right to remain silent and the right to an attorney.",
            "elements": [
                "Right to remain silent",
                "Anything said can be used against you",
                "Right to attorney",
                "Attorney provided if cannot afford one",
            ],
            "key_case": "Miranda v. Arizona, 384 U.S. 436 (1966)",
            "when_required": "Before custodial interrogation",
            "source": "Fifth Amendment, Miranda v. Arizona",
        },
        "habeas corpus": {
            "definition": "Habeas corpus (Latin for 'you shall have the body') is a legal action through which a person can seek relief from unlawful detention. It requires authorities to bring a prisoner before a court to determine if detention is lawful.",
            "purpose": "Protect against illegal imprisonment",
            "constitutional_basis": "Article I, Section 9 of U.S. Constitution",
            "source": "Constitutional law",
        },
        "beyond reasonable doubt": {
            "definition": "Beyond a reasonable doubt is the highest standard of proof in the legal system, required to convict a defendant in a criminal case. It means the evidence must be so convincing that a reasonable person would have no reasonable doubt about the defendant's guilt.",
            "applies_to": "Criminal prosecutions",
            "comparison": "Higher than 'preponderance of evidence' (civil) and 'clear and convincing evidence'",
            "source": "Criminal procedure",
        },
        "plea bargain": {
            "definition": "A plea bargain is a negotiated agreement between a prosecutor and defendant where the defendant pleads guilty to a lesser charge or receives a reduced sentence in exchange for avoiding trial.",
            "types": ["Charge bargaining", "Sentence bargaining", "Fact bargaining"],
            "statistics": "Approximately 90-95% of criminal cases are resolved through plea bargains",
            "source": "Criminal procedure",
        },
        "statute of limitations": {
            "definition": "A statute of limitations is a law that sets the maximum time after an event within which legal proceedings may be initiated. Once the period expires, the claim is time-barred.",
            "purpose": "Encourage timely prosecution, protect defendants from stale claims",
            "varies_by": "Type of crime/civil action and jurisdiction",
            "exceptions": "Murder typically has no statute of limitations",
            "source": "Civil and criminal procedure",
        },
        "double jeopardy": {
            "definition": "Double jeopardy is a constitutional protection that prevents a person from being prosecuted twice for the same offense after acquittal or conviction. It is guaranteed by the Fifth Amendment.",
            "protections": [
                "Second prosecution after acquittal",
                "Second prosecution after conviction",
                "Multiple punishments for same offense",
            ],
            "exceptions": ["Separate sovereigns doctrine", "Mistrials", "Appeals"],
            "source": "Fifth Amendment",
        },
        "due process": {
            "definition": "Due process is the constitutional requirement that legal proceedings be fair and follow established rules. It includes procedural due process (fair procedures) and substantive due process (fundamental rights).",
            "types": ["Procedural due process", "Substantive due process"],
            "amendments": "Fifth Amendment (federal), Fourteenth Amendment (states)",
            "source": "Constitutional law",
        },
        "exculpatory evidence": {
            "definition": "Exculpatory evidence is evidence that tends to clear or justify a defendant, proving innocence or reducing culpability. Prosecutors have a constitutional duty to disclose such evidence to the defense.",
            "key_case": "Brady v. Maryland, 373 U.S. 83 (1963)",
            "brady_rule": "Prosecution must disclose material exculpatory evidence",
            "source": "Criminal procedure, Brady doctrine",
        },
        "arraignment": {
            "definition": "An arraignment is a court proceeding where a criminal defendant is formally charged and asked to enter a plea (guilty, not guilty, or no contest).",
            "timing": "Typically within 48-72 hours of arrest",
            "purposes": [
                "Inform defendant of charges",
                "Enter plea",
                "Set bail",
                "Appoint counsel if needed",
            ],
            "source": "Criminal procedure",
        },
        "indictment": {
            "definition": "An indictment is a formal accusation of a serious crime, issued by a grand jury after reviewing evidence presented by the prosecutor.",
            "requirement": "Fifth Amendment requires indictment for federal felonies",
            "grand_jury": "Typically 16-23 citizens who determine if probable cause exists",
            "source": "Fifth Amendment, criminal procedure",
        },
        "hearsay": {
            "definition": "Hearsay is an out-of-court statement offered to prove the truth of the matter asserted. It is generally inadmissible as evidence due to reliability concerns.",
            "rule": "Federal Rules of Evidence 801-807",
            "exceptions": [
                "Excited utterance",
                "Present sense impression",
                "Business records",
                "Dying declaration",
            ],
            "source": "Evidence law",
        },
        "mens rea": {
            "definition": "Mens rea (Latin for 'guilty mind') is the mental element of a crime - the intent or knowledge of wrongdoing. Most crimes require both mens rea and actus reus (guilty act).",
            "levels": ["Intentional/Purposeful", "Knowing", "Reckless", "Negligent"],
            "strict_liability": "Some crimes don't require mens rea",
            "source": "Criminal law",
        },
        "actus reus": {
            "definition": "Actus reus (Latin for 'guilty act') is the physical element of a crime - the actual criminal act or omission. Combined with mens rea, it forms the basis for criminal liability.",
            "components": ["Voluntary act", "Omission (when duty exists)", "Possession"],
            "source": "Criminal law",
        },
        # Civil Law Terms
        "tort": {
            "definition": "A tort is a civil wrong that causes harm or loss, resulting in legal liability. Unlike crimes (prosecuted by the state), torts are addressed through civil lawsuits for damages.",
            "types": ["Intentional torts", "Negligence", "Strict liability"],
            "remedies": ["Compensatory damages", "Punitive damages", "Injunctions"],
            "source": "Tort law",
        },
        "negligence": {
            "definition": "Negligence is failure to exercise the care that a reasonably prudent person would exercise in similar circumstances, resulting in harm to another.",
            "elements": ["Duty of care", "Breach of duty", "Causation", "Damages"],
            "standard": "Reasonable person standard",
            "source": "Tort law",
        },
        "preponderance of evidence": {
            "definition": "Preponderance of the evidence is the standard of proof in most civil cases, requiring that the evidence show it is 'more likely than not' (greater than 50%) that the claim is true.",
            "comparison": "Lower than 'clear and convincing' and 'beyond reasonable doubt'",
            "applies_to": "Most civil cases",
            "source": "Civil procedure",
        },
        # Constitutional Terms
        "first amendment": {
            "definition": "The First Amendment protects freedoms of religion, speech, press, assembly, and petition. It prohibits Congress from establishing religion or restricting its free exercise.",
            "protections": [
                "Freedom of speech",
                "Freedom of religion",
                "Freedom of press",
                "Freedom of assembly",
                "Right to petition",
            ],
            "limitations": ["Incitement", "Defamation", "Obscenity", "True threats"],
            "source": "U.S. Constitution",
        },
        "fourth amendment": {
            "definition": "The Fourth Amendment protects against unreasonable searches and seizures, requiring warrants to be supported by probable cause and to particularly describe the place to be searched.",
            "protections": [
                "Privacy in persons, houses, papers, effects",
                "Warrant requirement",
                "Probable cause",
            ],
            "exclusionary_rule": "Evidence obtained in violation may be excluded",
            "source": "U.S. Constitution",
        },
        "fifth amendment": {
            "definition": "The Fifth Amendment provides several protections including the right against self-incrimination, double jeopardy, and the requirement of due process and just compensation for takings.",
            "protections": [
                "Self-incrimination privilege",
                "Double jeopardy",
                "Due process",
                "Grand jury requirement",
                "Just compensation",
            ],
            "source": "U.S. Constitution",
        },
        "sixth amendment": {
            "definition": "The Sixth Amendment guarantees rights in criminal prosecutions including speedy trial, jury trial, confrontation of witnesses, and assistance of counsel.",
            "rights": [
                "Speedy trial",
                "Public trial",
                "Impartial jury",
                "Know charges",
                "Confront witnesses",
                "Compel witnesses",
                "Counsel",
            ],
            "source": "U.S. Constitution",
        },
        # Additional Common Terms
        "bail": {
            "definition": "Bail is money or property deposited with the court to ensure a defendant appears for trial. If the defendant fails to appear, bail is forfeited.",
            "types": ["Cash bail", "Surety bond", "Property bond", "Release on recognizance (ROR)"],
            "eighth_amendment": "Prohibits excessive bail",
            "source": "Criminal procedure",
        },
        "warrant": {
            "definition": "A warrant is a court order authorizing law enforcement to take specific action, such as arresting a person (arrest warrant) or searching a location (search warrant).",
            "requirements": ["Probable cause", "Oath or affirmation", "Particular description"],
            "exceptions": [
                "Consent",
                "Plain view",
                "Exigent circumstances",
                "Search incident to arrest",
            ],
            "source": "Fourth Amendment",
        },
        "subpoena": {
            "definition": "A subpoena is a legal document ordering a person to appear in court to testify (subpoena ad testificandum) or to produce documents (subpoena duces tecum).",
            "types": ["Subpoena ad testificandum (testimony)", "Subpoena duces tecum (documents)"],
            "failure_to_comply": "May result in contempt of court",
            "source": "Civil and criminal procedure",
        },
        "discovery": {
            "definition": "Discovery is the pre-trial process where parties exchange information, documents, and evidence relevant to the case. It prevents surprise and promotes fair resolution.",
            "methods": [
                "Interrogatories",
                "Depositions",
                "Requests for production",
                "Requests for admission",
            ],
            "criminal_discovery": "Brady rule requires disclosure of exculpatory evidence",
            "source": "Civil and criminal procedure",
        },
        "felony": {
            "definition": "A felony is a serious crime typically punishable by imprisonment for more than one year or death. Examples include murder, rape, robbery, and burglary.",
            "vs_misdemeanor": "More serious than misdemeanors, which are punishable by up to one year",
            "consequences": [
                "Prison time",
                "Fines",
                "Loss of voting rights",
                "Firearm restrictions",
            ],
            "source": "Criminal law",
        },
        "misdemeanor": {
            "definition": "A misdemeanor is a criminal offense less serious than a felony, typically punishable by fines or imprisonment for up to one year in local jail.",
            "examples": [
                "Simple assault",
                "Petty theft",
                "DUI (first offense)",
                "Disorderly conduct",
            ],
            "vs_felony": "Less serious than felonies",
            "source": "Criminal law",
        },
        "jurisdiction": {
            "definition": "Jurisdiction is the authority of a court to hear and decide cases. It can be based on geography (territorial), subject matter, or the parties involved.",
            "types": [
                "Subject matter jurisdiction",
                "Personal jurisdiction",
                "Territorial jurisdiction",
            ],
            "federal_vs_state": "Federal courts handle federal law; state courts handle state law",
            "source": "Constitutional and procedural law",
        },
        "contempt of court": {
            "definition": "Contempt of court is willful disobedience of a court order or disrespectful conduct in the courtroom. It can be civil (failure to comply) or criminal (disruption).",
            "types": [
                "Civil contempt",
                "Criminal contempt",
                "Direct contempt",
                "Indirect contempt",
            ],
            "penalties": ["Fines", "Imprisonment until compliance", "Both"],
            "source": "Court procedure",
        },
        "injunction": {
            "definition": "An injunction is a court order requiring a party to do or refrain from doing a specific act. It is an equitable remedy used to prevent irreparable harm.",
            "types": [
                "Temporary restraining order (TRO)",
                "Preliminary injunction",
                "Permanent injunction",
            ],
            "requirements": [
                "Likelihood of success",
                "Irreparable harm",
                "Balance of hardships",
                "Public interest",
            ],
            "source": "Equity and civil procedure",
        },
        "class action": {
            "definition": "A class action is a lawsuit filed by one or more plaintiffs on behalf of a larger group (class) with similar claims. It allows efficient resolution of cases with many similarly situated parties.",
            "requirements": ["Numerosity", "Commonality", "Typicality", "Adequate representation"],
            "rule": "Federal Rule of Civil Procedure 23",
            "source": "Civil procedure",
        },
        "settlement": {
            "definition": "A settlement is an agreement between parties to resolve a dispute without going to trial. Most civil cases settle before trial.",
            "benefits": ["Cost savings", "Time savings", "Certainty", "Privacy"],
            "statistics": "Over 95% of civil cases settle",
            "source": "Civil procedure",
        },
        "verdict": {
            "definition": "A verdict is the formal decision or finding made by a jury (or judge in a bench trial) on matters of fact submitted during trial.",
            "types": [
                "Guilty/Not guilty (criminal)",
                "Liable/Not liable (civil)",
                "General verdict",
                "Special verdict",
            ],
            "vs_judgment": "Verdict is jury's finding; judgment is court's final order",
            "source": "Trial procedure",
        },
        "appeal": {
            "definition": "An appeal is a request to a higher court to review and change a lower court's decision. Appellate courts review for legal errors, not facts.",
            "grounds": ["Error of law", "Abuse of discretion", "Constitutional violation"],
            "standard_of_review": ["De novo", "Abuse of discretion", "Clearly erroneous"],
            "source": "Appellate procedure",
        },
        "precedent": {
            "definition": "Precedent (or stare decisis) is the legal principle that courts should follow decisions of higher courts in similar cases. It promotes consistency and predictability.",
            "binding_vs_persuasive": "Binding precedent must be followed; persuasive may influence",
            "overruling": "Courts can overrule precedent in certain circumstances",
            "source": "Common law system",
        },
    }

    # Math constants and functions
    MATH_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": float("inf"),
        "golden_ratio": (1 + math.sqrt(5)) / 2,
    }

    MATH_FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
        "pow": pow,
        "factorial": math.factorial,
        "gcd": math.gcd,
    }

    def __init__(self):
        """Initialize smart tools"""
        self.cache: dict[str, ToolResult] = {}
        logger.info("SmartTools initialized with web search, math, and knowledge base")

    def detect_intent(self, query: str) -> list[str]:
        """
        Detect what tools might be useful for this query

        Returns list of tool names that could help
        """
        query_lower = query.lower()
        tools = []

        # Math detection
        math_patterns = [
            r"\d+\s*[\+\-\*\/\^]\s*\d+",  # Basic arithmetic
            r"calculate|compute|solve|math",
            r"what is \d+",
            r"square root|sqrt|factorial",
            r"percent|percentage",
            r"convert .* to",
        ]
        if any(re.search(p, query_lower) for p in math_patterns):
            tools.append("math")

        # Legal knowledge detection
        legal_patterns = [
            r"what is|define|meaning of|definition",
            r"legal|law|court|crime|criminal",
            r"amendment|constitutional|rights",
        ]
        if any(re.search(p, query_lower) for p in legal_patterns):
            tools.append("legal_knowledge")

        # Web search detection (fallback for general questions)
        if "search" in query_lower or "find" in query_lower or "look up" in query_lower:
            tools.append("web_search")

        # Wikipedia detection
        wiki_patterns = [
            r"who is|who was",
            r"what is a|what are",
            r"history of|when did",
            r"wikipedia",
        ]
        if any(re.search(p, query_lower) for p in wiki_patterns):
            tools.append("wikipedia")

        # Date/time detection
        time_patterns = [
            r"days? (until|since|between)",
            r"how (long|many days)",
            r"date|time|calendar",
        ]
        if any(re.search(p, query_lower) for p in time_patterns):
            tools.append("datetime")

        return tools or ["web_search"]  # Default to web search

    def process_query(self, query: str) -> list[ToolResult]:
        """
        Process a query using appropriate tools

        Returns list of results from relevant tools
        """
        tools = self.detect_intent(query)
        results = []

        for tool in tools:
            try:
                if tool == "math":
                    result = self.calculate(query)
                elif tool == "legal_knowledge":
                    result = self.lookup_legal_term(query)
                elif tool == "web_search":
                    result = self.web_search(query)
                elif tool == "wikipedia":
                    result = self.wikipedia_search(query)
                elif tool == "datetime":
                    result = self.datetime_calc(query)
                else:
                    continue

                if result.success:
                    results.append(result)
            except Exception as e:
                logger.error(f"Tool {tool} failed: {e}")

        return results

    def calculate(self, query: str) -> ToolResult:
        """
        Evaluate mathematical expressions

        Supports:
        - Basic arithmetic (+, -, *, /, ^, %)
        - Scientific functions (sin, cos, sqrt, log, etc.)
        - Constants (pi, e, etc.)
        - Unit conversions
        """
        try:
            # Extract mathematical expression
            expr = self._extract_math_expression(query)
            if not expr:
                return ToolResult(
                    tool="math", success=False, data=None, error="No mathematical expression found"
                )

            # Clean and evaluate
            expr = expr.replace("^", "**")  # Convert ^ to Python power
            expr = expr.replace("×", "*").replace("÷", "/")

            # Create safe evaluation context
            safe_dict = {**self.MATH_CONSTANTS, **self.MATH_FUNCTIONS}

            # Handle percentage calculations
            if "%" in expr:
                expr = self._handle_percentage(expr)

            result = eval(expr, {"__builtins__": {}}, safe_dict)

            # Format result nicely
            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 10)

            return ToolResult(
                tool="math",
                success=True,
                data={"expression": expr, "result": result, "formatted": f"{expr} = {result}"},
                source="Built-in math engine",
                confidence=1.0,
            )
        except Exception as e:
            return ToolResult(tool="math", success=False, data=None, error=str(e))

Optional[def _extract_math_expression(self, query: str) -> str]:
        """Extract mathematical expression from natural language"""
        # Remove common question words
        cleaned = re.sub(r"^(what is|calculate|compute|solve|evaluate|find)\s*", "", query.lower())

        # Look for expression patterns
        patterns = [
            r"([\d\.\+\-\*\/\^\(\)\s\%]+)",
            r"(\d+\s*(?:plus|minus|times|divided by|to the power of)\s*\d+)",
            r"(sqrt|sin|cos|tan|log)\s*\(?\s*[\d\.]+\s*\)?",
        ]

        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                expr = match.group(1).strip()
                # Convert words to operators
                expr = expr.replace(" plus ", "+")
                expr = expr.replace(" minus ", "-")
                expr = expr.replace(" times ", "*")
                expr = expr.replace(" divided by ", "/")
                expr = expr.replace(" to the power of ", "**")
                return expr

        return cleaned if any(c in cleaned for c in "0123456789+-*/") else None

    def _handle_percentage(self, expr: str) -> str:
        """Handle percentage calculations"""
        # "20% of 50" -> "0.20 * 50"
        match = re.search(r"([\d\.]+)\s*%\s*of\s*([\d\.]+)", expr)
        if match:
            return f"({match.group(1)} / 100) * {match.group(2)}"

        # "50 + 20%" -> "50 * 1.20"
        match = re.search(r"([\d\.]+)\s*\+\s*([\d\.]+)\s*%", expr)
        if match:
            return f"{match.group(1)} * (1 + {match.group(2)} / 100)"

        # Simple percentage "20%" -> "0.20"
        return re.sub(r"([\d\.]+)\s*%", r"(\1 / 100)", expr)

    def lookup_legal_term(self, query: str) -> ToolResult:
        """
        Look up legal terms in built-in knowledge base
        """
        query_lower = query.lower()

        # Extract the term being asked about
        term = None
        for key in self.LEGAL_KNOWLEDGE:
            if key in query_lower:
                term = key
                break

        # Try fuzzy matching if no exact match
        if not term:
            query_words = set(query_lower.split())
            best_match = None
            best_score = 0

            for key in self.LEGAL_KNOWLEDGE:
                key_words = set(key.split())
                overlap = len(query_words & key_words)
                if overlap > best_score:
                    best_score = overlap
                    best_match = key

            if best_score > 0:
                term = best_match

        if term and term in self.LEGAL_KNOWLEDGE:
            knowledge = self.LEGAL_KNOWLEDGE[term]
            return ToolResult(
                tool="legal_knowledge",
                success=True,
                data={
                    "term": term,
                    "definition": knowledge.get("definition", ""),
                    "elements": knowledge.get("elements", []),
                    "source": knowledge.get("source", "Legal knowledge base"),
                    "related": knowledge.get("related", []),
                    "key_cases": knowledge.get("key_cases", []),
                    "full_entry": knowledge,
                },
                source=knowledge.get("source", "Built-in legal knowledge base"),
                confidence=0.95,
            )

        return ToolResult(
            tool="legal_knowledge",
            success=False,
            data=None,
            error=f"Term not found in knowledge base. Available terms include: {', '.join(list(self.LEGAL_KNOWLEDGE.keys())[:10])}...",
        )

    def web_search(self, query: str, max_results: int = 5) -> ToolResult:
        """
        Search the web using DuckDuckGo Instant Answer API (free, no API key)
        """
        try:
            # DuckDuckGo Instant Answer API
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

            req = urllib.request.Request(url, headers={"User-Agent": "Evident Legal Assistant/1.0"})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            results = []

            # Abstract (main answer)
            if data.get("Abstract"):
                results.append(
                    {
                        "title": data.get("Heading", "Answer"),
                        "text": data["Abstract"],
                        "source": data.get("AbstractSource", "DuckDuckGo"),
                        "url": data.get("AbstractURL", ""),
                    }
                )

            # Definition
            if data.get("Definition"):
                results.append(
                    {
                        "title": "Definition",
                        "text": data["Definition"],
                        "source": data.get("DefinitionSource", "DuckDuckGo"),
                        "url": data.get("DefinitionURL", ""),
                    }
                )

            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(
                        {
                            "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "text": topic["Text"],
                            "source": "DuckDuckGo",
                            "url": topic.get("FirstURL", ""),
                        }
                    )

            if results:
                return ToolResult(
                    tool="web_search",
                    success=True,
                    data={
                        "query": query,
                        "results": results[:max_results],
                        "answer": data.get("Abstract") or (results[0]["text"] if results else None),
                    },
                    source="DuckDuckGo Instant Answers",
                    confidence=0.8,
                )

            return ToolResult(
                tool="web_search",
                success=False,
                data={"query": query},
                error="No instant answers found. Try rephrasing your question.",
            )

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ToolResult(
                tool="web_search", success=False, data=None, error=f"Search failed: {str(e)}"
            )

    def wikipedia_search(self, query: str) -> ToolResult:
        """
        Search Wikipedia for information (free API)
        """
        try:
            # Extract search term
            search_term = re.sub(
                r"^(who is|what is|tell me about|define)\s*", "", query, flags=re.IGNORECASE
            ).strip()

            encoded_term = urllib.parse.quote(search_term)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_term}"

            req = urllib.request.Request(url, headers={"User-Agent": "Evident Legal Assistant/1.0"})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            if data.get("extract"):
                return ToolResult(
                    tool="wikipedia",
                    success=True,
                    data={
                        "title": data.get("title", search_term),
                        "extract": data["extract"],
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "description": data.get("description", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source"),
                    },
                    source="Wikipedia",
                    confidence=0.85,
                )

            return ToolResult(
                tool="wikipedia", success=False, data=None, error="No Wikipedia article found"
            )

        except Exception as e:
            return ToolResult(tool="wikipedia", success=False, data=None, error=str(e))

    def datetime_calc(self, query: str) -> ToolResult:
        """
        Calculate dates and times
        """
        try:
            query_lower = query.lower()
            now = datetime.now()

            # Days until a date
            match = re.search(r"days?\s+until\s+(\w+\s+\d+(?:,?\s+\d+)?)", query_lower)
            if match:
                from dateutil import parser

                target = parser.parse(match.group(1))
                if target < now:
                    target = target.replace(year=now.year + 1)
                days = (target - now).days
                return ToolResult(
                    tool="datetime",
                    success=True,
                    data={
                        "calculation": f"Days until {target.strftime('%B %d, %Y')}",
                        "result": days,
                        "formatted": f"{days} days",
                    },
                    source="Date calculator",
                )

            # Days since a date
            match = re.search(r"days?\s+since\s+(\w+\s+\d+(?:,?\s+\d+)?)", query_lower)
            if match:
                from dateutil import parser

                target = parser.parse(match.group(1))
                days = (now - target).days
                return ToolResult(
                    tool="datetime",
                    success=True,
                    data={
                        "calculation": f"Days since {target.strftime('%B %d, %Y')}",
                        "result": days,
                        "formatted": f"{days} days",
                    },
                    source="Date calculator",
                )

            # What day is it / current date
            if "what day" in query_lower or "today" in query_lower or "current date" in query_lower:
                return ToolResult(
                    tool="datetime",
                    success=True,
                    data={
                        "date": now.strftime("%A, %B %d, %Y"),
                        "time": now.strftime("%I:%M %p"),
                        "timestamp": now.isoformat(),
                    },
                    source="System clock",
                )

            return ToolResult(
                tool="datetime", success=False, data=None, error="Could not parse date/time query"
            )

        except ImportError:
            # dateutil not available, use basic parsing
            return ToolResult(
                tool="datetime",
                success=True,
                data={
                    "date": datetime.now().strftime("%A, %B %d, %Y"),
                    "time": datetime.now().strftime("%I:%M %p"),
                    "note": "For advanced date calculations, install python-dateutil",
                },
                source="System clock",
            )
        except Exception as e:
            return ToolResult(tool="datetime", success=False, data=None, error=str(e))

    def format_response(self, results: list[ToolResult], query: str) -> str:
        """
        Format tool results into a coherent response
        """
        if not results:
            return f'I couldn\'t find specific information about "{query}". Try rephrasing your question or uploading relevant documents to your library.'

        response_parts = []

        for result in results:
            if not result.success:
                continue

            if result.tool == "legal_knowledge":
                data = result.data
                response_parts.append(f"**{data['term'].title()}**\n")
                response_parts.append(f"{data['definition']}\n")

                if data.get("elements"):
                    response_parts.append("\n**Key Elements:**")
                    for elem in data["elements"]:
                        response_parts.append(f"• {elem}")

                if data.get("key_cases"):
                    response_parts.append("\n**Key Cases:**")
                    for case in data["key_cases"]:
                        response_parts.append(f"• {case}")

                response_parts.append(f"\n*Source: {result.source}*")

            elif result.tool == "math":
                data = result.data
                response_parts.append("**Calculation Result:**\n")
                response_parts.append(f"`{data['formatted']}`")

            elif result.tool == "web_search":
                data = result.data
                if data.get("answer"):
                    response_parts.append(f"{data['answer']}\n")

                if data.get("results"):
                    response_parts.append("\n**Related Information:**")
                    for r in data["results"][:3]:
                        if r.get("text"):
                            response_parts.append(f"• {r['text'][:200]}...")

                response_parts.append(f"\n*Source: {result.source}*")

            elif result.tool == "wikipedia":
                data = result.data
                response_parts.append(f"**{data['title']}**\n")
                response_parts.append(f"{data['extract']}\n")
                if data.get("url"):
                    response_parts.append(f"\n[Read more on Wikipedia]({data['url']})")
                response_parts.append("\n*Source: Wikipedia*")

            elif result.tool == "datetime":
                data = result.data
                if "result" in data:
                    response_parts.append(f"**{data['calculation']}:** {data['formatted']}")
                else:
                    response_parts.append("**Current Date/Time:**")
                    response_parts.append(f"• Date: {data['date']}")
                    response_parts.append(f"• Time: {data['time']}")

        return "\n".join(response_parts)