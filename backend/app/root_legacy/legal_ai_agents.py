# Legal AI Agent Framework
# Custom agents for discovery processing, evidence organization, and legal workflow automation

import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentCapability:
    """Defines what an agent can do"""

    DISCOVERY_PROCESSING = "discovery_processing"
    EVIDENCE_ORGANIZATION = "evidence_organization"
    TIMELINE_CONSTRUCTION = "timeline_construction"
    COMPLIANCE_CHECKING = "compliance_checking"
    DOCUMENT_ANALYSIS = "document_analysis"
    DEPOSITION_PREP = "deposition_prep"
    LEGAL_RESEARCH = "legal_research"
    CASE_STRATEGY = "case_strategy"
    MOTION_DRAFTING = "motion_drafting"
    BRIEF_WRITING = "brief_writing"
    LETTER_WRITING = "letter_writing"
    CONTRACT_DRAFTING = "contract_drafting"


class AgentStatus:
    """Agent execution states"""

    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class LegalAIAgent:
    """Base class for all legal AI agents"""

    def __init__(self, agent_id: str, name: str, capability: str, user_id: str):
        self.agent_id = agent_id
        self.name = name
        self.capability = capability
        self.user_id = user_id
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_run = None
        self.config = {}
        self.results = []

    def configure(self, config: Dict[str, Any]):
        """Configure agent parameters"""
        self.config.update(config)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task - override in subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and results"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capability": self.capability,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "config": self.config,
            "results_count": len(self.results),
        }

    def save_result(self, result: Dict[str, Any]):
        """Save agent execution result"""
        result["timestamp"] = datetime.utcnow().isoformat()
        self.results.append(result)
        self.last_run = datetime.utcnow()


class DiscoveryProcessingAgent(LegalAIAgent):
    """Agent for processing discovery materials automatically"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Discovery Processor",
            capability=AgentCapability.DISCOVERY_PROCESSING,
            user_id=user_id,
        )

        # Default configuration
        self.config = {
            "auto_categorize": True,
            "extract_entities": True,
            "detect_privileged": True,
            "OCR_documents": True,
            "create_index": True,
            "batch_size": 50,
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process discovery documents"""
        self.status = AgentStatus.PROCESSING

        files = input_data.get("files", [])
        case_id = input_data.get("case_id")

        results = {
            "case_id": case_id,
            "total_files": len(files),
            "processed": 0,
            "categorized": {},
            "entities_found": [],
            "privileged_docs": [],
            "timeline_events": [],
            "key_documents": [],
            "errors": [],
        }

        for file in files:
            try:
                # Categorize document
                category = self._categorize_document(file)
                results["categorized"][category] = results["categorized"].get(category, 0) + 1

                # Extract entities
                if self.config.get("extract_entities"):
                    entities = self._extract_entities(file)
                    results["entities_found"].extend(entities)

                # Check for privilege
                if self.config.get("detect_privileged"):
                    if self._is_privileged(file):
                        results["privileged_docs"].append(
                            {
                                "filename": file.get("name"),
                                "reason": "Attorney-client communication detected",
                            }
                        )

                # Extract timeline events
                events = self._extract_timeline_events(file)
                results["timeline_events"].extend(events)

                # Identify key documents
                if self._is_key_document(file):
                    results["key_documents"].append(
                        {"filename": file.get("name"), "category": category, "importance": "high"}
                    )

                results["processed"] += 1

            except Exception as e:
                results["errors"].append({"file": file.get("name"), "error": str(e)})

        # Generate summary
        results["summary"] = self._generate_summary(results)

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _categorize_document(self, file: Dict) -> str:
        """Categorize document by type"""
        filename = file.get("name", "").lower()
        content = file.get("content", "").lower()

        # Email detection
        if any(
            keyword in filename or keyword in content
            for keyword in ["email", "correspondence", "message"]
        ):
            return "Email Communication"

        # Contract detection
        if any(
            keyword in content
            for keyword in ["agreement", "contract", "terms and conditions", "hereby agree"]
        ):
            return "Contracts & Agreements"

        # Financial
        if any(
            keyword in content
            for keyword in ["invoice", "receipt", "payment", "financial statement", "balance sheet"]
        ):
            return "Financial Documents"

        # Legal pleadings
        if any(
            keyword in content
            for keyword in ["complaint", "answer", "motion", "brief", "affidavit"]
        ):
            return "Legal Pleadings"

        # Medical
        if any(
            keyword in content
            for keyword in ["medical", "diagnosis", "treatment", "prescription", "patient"]
        ):
            return "Medical Records"

        # Photos/Video
        if filename.endswith((".jpg", ".png", ".mp4", ".avi")):
            return "Multimedia Evidence"

        return "Miscellaneous"

    def _extract_entities(self, file: Dict) -> List[Dict]:
        """Extract key entities from document"""
        content = file.get("content", "")
        entities = []

        # Email addresses
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
        for email in emails:
            entities.append({"type": "email", "value": email, "source": file.get("name")})

        # Phone numbers
        phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", content)
        for phone in phones:
            entities.append({"type": "phone", "value": phone, "source": file.get("name")})

        # Dates
        dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", content)
        for date in dates[:5]:  # Limit to first 5
            entities.append({"type": "date", "value": date, "source": file.get("name")})

        # Dollar amounts
        amounts = re.findall(r"\$\d+(?:,\d{3})*(?:\.\d{2})?", content)
        for amount in amounts:
            entities.append({"type": "monetary", "value": amount, "source": file.get("name")})

        return entities

    def _is_privileged(self, file: Dict) -> bool:
        """Check if document is privileged"""
        content = file.get("content", "").lower()

        privilege_keywords = [
            "attorney-client privilege",
            "attorney work product",
            "confidential legal advice",
            "privileged and confidential",
            "attorney eyes only",
        ]

        return any(keyword in content for keyword in privilege_keywords)

    def _extract_timeline_events(self, file: Dict) -> List[Dict]:
        """Extract events with dates for timeline"""
        content = file.get("content", "")
        events = []

        # Simple date extraction (can be enhanced with NLP)
        date_patterns = [
            r"On (\d{1,2}/\d{1,2}/\d{2,4})",
            r"Date: (\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{1,2}/\d{1,2}/\d{2,4}): (.+?)(?:\n|$)",
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                events.append(
                    {
                        "date": match.group(1),
                        "description": match.group(2) if len(match.groups()) > 1 else "Event",
                        "source": file.get("name"),
                    }
                )

        return events[:10]  # Limit

    def _is_key_document(self, file: Dict) -> bool:
        """Determine if document is key to the case"""
        content = file.get("content", "").lower()

        key_indicators = [
            "settlement",
            "admission",
            "confession",
            "witness statement",
            "expert report",
            "smoking gun",
            "critical evidence",
        ]

        return any(indicator in content for indicator in key_indicators)

    def _generate_summary(self, results: Dict) -> str:
        """Generate human-readable summary"""
        summary = f"""
Discovery Processing Complete:
- Processed {results['processed']} of {results['total_files']} documents
- Found {len(results['entities_found'])} entities
- Identified {len(results['privileged_docs'])} privileged documents
- Extracted {len(results['timeline_events'])} timeline events
- Flagged {len(results['key_documents'])} key documents

Categories:
"""
        for category, count in results["categorized"].items():
            summary += f"  - {category}: {count} documents\n"

        if results["errors"]:
            summary += f"\n⚠️ {len(results['errors'])} errors occurred during processing"

        return summary.strip()


class EvidenceOrganizerAgent(LegalAIAgent):
    """Agent for organizing evidence into logical structure"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Evidence Organizer",
            capability=AgentCapability.EVIDENCE_ORGANIZATION,
            user_id=user_id,
        )

        self.config = {
            "organization_scheme": "chronological",  # chronological, by_party, by_issue, by_type
            "create_folders": True,
            "generate_index": True,
            "link_related": True,
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize evidence into structured format"""
        self.status = AgentStatus.PROCESSING

        evidence_items = input_data.get("evidence", [])
        scheme = self.config.get("organization_scheme")

        results = {
            "scheme": scheme,
            "total_items": len(evidence_items),
            "structure": {},
            "cross_references": [],
            "index": [],
        }

        # Organize based on scheme
        if scheme == "chronological":
            results["structure"] = self._organize_by_date(evidence_items)
        elif scheme == "by_party":
            results["structure"] = self._organize_by_party(evidence_items)
        elif scheme == "by_issue":
            results["structure"] = self._organize_by_issue(evidence_items)
        elif scheme == "by_type":
            results["structure"] = self._organize_by_type(evidence_items)

        # Create cross-references
        if self.config.get("link_related"):
            results["cross_references"] = self._create_cross_references(evidence_items)

        # Generate index
        if self.config.get("generate_index"):
            results["index"] = self._generate_index(results["structure"])

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _organize_by_date(self, evidence: List[Dict]) -> Dict:
        """Organize evidence chronologically"""
        organized = {}

        for item in evidence:
            date = item.get("date", "Unknown Date")
            if date not in organized:
                organized[date] = []
            organized[date].append(item)

        # Sort by date
        return dict(sorted(organized.items()))

    def _organize_by_party(self, evidence: List[Dict]) -> Dict:
        """Organize by party involved"""
        parties = {}

        for item in evidence:
            party = item.get("party", "Unknown Party")
            if party not in parties:
                parties[party] = []
            parties[party].append(item)

        return parties

    def _organize_by_issue(self, evidence: List[Dict]) -> Dict:
        """Organize by legal issue"""
        issues = {"Liability": [], "Damages": [], "Causation": [], "Negligence": [], "Other": []}

        for item in evidence:
            # Simple keyword matching (can be enhanced)
            content = str(item.get("content", "")).lower()

            if any(word in content for word in ["liable", "fault", "responsible"]):
                issues["Liability"].append(item)
            elif any(word in content for word in ["damages", "injury", "harm", "loss"]):
                issues["Damages"].append(item)
            elif any(word in content for word in ["caused", "resulted in", "because of"]):
                issues["Causation"].append(item)
            elif any(word in content for word in ["negligent", "careless", "duty"]):
                issues["Negligence"].append(item)
            else:
                issues["Other"].append(item)

        return issues

    def _organize_by_type(self, evidence: List[Dict]) -> Dict:
        """Organize by evidence type"""
        types = {}

        for item in evidence:
            evidence_type = item.get("type", "Unknown")
            if evidence_type not in types:
                types[evidence_type] = []
            types[evidence_type].append(item)

        return types

    def _create_cross_references(self, evidence: List[Dict]) -> List[Dict]:
        """Find related evidence items"""
        references = []

        for i, item1 in enumerate(evidence):
            for j, item2 in enumerate(evidence):
                if i >= j:
                    continue

                # Check for shared entities, dates, parties
                similarity_score = self._calculate_similarity(item1, item2)

                if similarity_score > 0.5:
                    references.append(
                        {
                            "item1": item1.get("id"),
                            "item2": item2.get("id"),
                            "similarity": similarity_score,
                            "reason": "Shared entities or context",
                        }
                    )

        return references

    def _calculate_similarity(self, item1: Dict, item2: Dict) -> float:
        """Calculate similarity between two evidence items"""
        score = 0.0

        # Same date
        if item1.get("date") == item2.get("date") and item1.get("date"):
            score += 0.3

        # Same party
        if item1.get("party") == item2.get("party") and item1.get("party"):
            score += 0.3

        # Same type
        if item1.get("type") == item2.get("type"):
            score += 0.2

        # Similar content (simple word overlap)
        words1 = set(str(item1.get("content", "")).lower().split())
        words2 = set(str(item2.get("content", "")).lower().split())

        if words1 and words2:
            overlap = len(words1.intersection(words2)) / max(len(words1), len(words2))
            score += overlap * 0.2

        return min(score, 1.0)

    def _generate_index(self, structure: Dict) -> List[Dict]:
        """Generate searchable index"""
        index = []

        for category, items in structure.items():
            index.append(
                {
                    "category": category,
                    "count": len(items),
                    "items": [item.get("id") for item in items],
                }
            )

        return index


class TimelineBuilderAgent(LegalAIAgent):
    """Agent for constructing case timelines"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Timeline Builder",
            capability=AgentCapability.TIMELINE_CONSTRUCTION,
            user_id=user_id,
        )

        self.config = {
            "auto_sort": True,
            "detect_conflicts": True,
            "group_by_day": True,
            "include_source": True,
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive case timeline"""
        self.status = AgentStatus.PROCESSING

        events = input_data.get("events", [])

        results = {
            "total_events": len(events),
            "timeline": [],
            "conflicts": [],
            "gaps": [],
            "critical_dates": [],
        }

        # Sort events chronologically
        if self.config.get("auto_sort"):
            events = self._sort_events(events)

        # Build timeline
        results["timeline"] = events

        # Detect conflicts
        if self.config.get("detect_conflicts"):
            results["conflicts"] = self._detect_conflicts(events)

        # Find timeline gaps
        results["gaps"] = self._find_gaps(events)

        # Identify critical dates
        results["critical_dates"] = self._identify_critical_dates(events)

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _sort_events(self, events: List[Dict]) -> List[Dict]:
        """Sort events chronologically"""

        def parse_date(event):
            date_str = event.get("date", "1900-01-01")
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                try:
                    return datetime.strptime(date_str, "%m/%d/%Y")
                except:
                    return datetime(1900, 1, 1)

        return sorted(events, key=parse_date)

    def _detect_conflicts(self, events: List[Dict]) -> List[Dict]:
        """Find conflicting accounts of same event"""
        conflicts = []

        for i, event1 in enumerate(events):
            for j, event2 in enumerate(events):
                if i >= j:
                    continue

                # Same date, different accounts
                if event1.get("date") == event2.get("date") and event1.get(
                    "description"
                ) != event2.get("description"):
                    conflicts.append(
                        {
                            "date": event1.get("date"),
                            "account1": event1.get("description"),
                            "account2": event2.get("description"),
                            "source1": event1.get("source"),
                            "source2": event2.get("source"),
                        }
                    )

        return conflicts

    def _find_gaps(self, events: List[Dict]) -> List[Dict]:
        """Find significant gaps in timeline"""
        gaps = []

        for i in range(len(events) - 1):
            try:
                date1 = datetime.strptime(events[i].get("date"), "%Y-%m-%d")
                date2 = datetime.strptime(events[i + 1].get("date"), "%Y-%m-%d")

                gap_days = (date2 - date1).days

                if gap_days > 30:  # More than 30 days
                    gaps.append(
                        {
                            "from": events[i].get("date"),
                            "to": events[i + 1].get("date"),
                            "days": gap_days,
                            "note": f"{gap_days}-day gap in timeline",
                        }
                    )
            except:
                pass

        return gaps

    def _identify_critical_dates(self, events: List[Dict]) -> List[Dict]:
        """Identify legally significant dates"""
        critical = []

        critical_keywords = [
            "incident",
            "accident",
            "injury",
            "contract signed",
            "breach",
            "termination",
            "complaint filed",
            "served",
            "deadline",
            "hearing",
            "trial",
            "settlement",
        ]

        for event in events:
            description = event.get("description", "").lower()

            if any(keyword in description for keyword in critical_keywords):
                critical.append(
                    {
                        "date": event.get("date"),
                        "description": event.get("description"),
                        "importance": "high",
                        "source": event.get("source"),
                    }
                )

        return critical


class ComplianceCheckerAgent(LegalAIAgent):
    """Agent for checking legal compliance"""

    def __init__(self, agent_id: str, user_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Compliance Checker",
            capability=AgentCapability.COMPLIANCE_CHECKING,
            user_id=user_id,
        )

        self.config = {
            "check_miranda": True,
            "check_chain_of_custody": True,
            "check_discovery_compliance": True,
            "check_privacy": True,
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for legal compliance issues"""
        self.status = AgentStatus.PROCESSING

        evidence = input_data.get("evidence", [])
        case_type = input_data.get("case_type", "criminal")

        results = {
            "total_items_checked": len(evidence),
            "compliant": 0,
            "violations": [],
            "warnings": [],
            "recommendations": [],
        }

        for item in evidence:
            # Miranda warnings (criminal cases)
            if case_type == "criminal" and self.config.get("check_miranda"):
                self._check_miranda(item, results)

            # Chain of custody
            if self.config.get("check_chain_of_custody"):
                self._check_chain_of_custody(item, results)

            # Privacy compliance (HIPAA, etc.)
            if self.config.get("check_privacy"):
                self._check_privacy(item, results)

        results["compliant"] = len(evidence) - len(results["violations"])
        results["compliance_rate"] = (results["compliant"] / len(evidence) * 100) if evidence else 0

        self.status = AgentStatus.COMPLETED
        self.save_result(results)

        return results

    def _check_miranda(self, item: Dict, results: Dict):
        """Check Miranda warning compliance"""
        if item.get("type") == "interrogation":
            content = str(item.get("content", "")).lower()

            required_warnings = [
                "right to remain silent",
                "anything you say",
                "right to an attorney",
            ]

            missing = [w for w in required_warnings if w not in content]

            if missing:
                results["violations"].append(
                    {
                        "item_id": item.get("id"),
                        "type": "Miranda Warning Incomplete",
                        "severity": "high",
                        "details": f"Missing: {', '.join(missing)}",
                    }
                )

    def _check_chain_of_custody(self, item: Dict, results: Dict):
        """Check chain of custody documentation"""
        if not item.get("chain_of_custody"):
            results["warnings"].append(
                {
                    "item_id": item.get("id"),
                    "type": "Missing Chain of Custody",
                    "severity": "medium",
                    "recommendation": "Document complete chain of custody",
                }
            )

    def _check_privacy(self, item: Dict, results: Dict):
        """Check privacy compliance"""
        content = str(item.get("content", "")).lower()

        # Check for PII/PHI
        has_ssn = re.search(r"\d{3}-\d{2}-\d{4}", content)
        has_medical = any(
            word in content for word in ["diagnosis", "treatment", "patient", "medical record"]
        )

        if has_ssn or has_medical:
            if not item.get("redacted"):
                results["violations"].append(
                    {
                        "item_id": item.get("id"),
                        "type": "Unredacted Sensitive Information",
                        "severity": "high",
                        "details": "Contains SSN or medical information",
                    }
                )


class AgentManager:
    """Manages deployment and execution of legal AI agents"""

    def __init__(self, storage_path: str = "./agents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.agents = {}

    def deploy_agent(self, agent_type: str, user_id: str, config: Optional[Dict] = None) -> str:
        """Deploy a new agent instance"""
        agent_id = str(uuid.uuid4())[:12]

        # Import document agents
        from legal_document_agents import (BriefWriterAgent,
                                           ContractDrafterAgent,
                                           LegalLetterAgent,
                                           MotionDrafterAgent)

        # Create agent based on type
        if agent_type == "discovery":
            agent = DiscoveryProcessingAgent(agent_id, user_id)
        elif agent_type == "organizer":
            agent = EvidenceOrganizerAgent(agent_id, user_id)
        elif agent_type == "timeline":
            agent = TimelineBuilderAgent(agent_id, user_id)
        elif agent_type == "compliance":
            agent = ComplianceCheckerAgent(agent_id, user_id)
        elif agent_type == "motion_drafter":
            agent = MotionDrafterAgent(agent_id, user_id)
        elif agent_type == "brief_writer":
            agent = BriefWriterAgent(agent_id, user_id)
        elif agent_type == "letter_writer":
            agent = LegalLetterAgent(agent_id, user_id)
        elif agent_type == "contract_drafter":
            agent = ContractDrafterAgent(agent_id, user_id)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Configure if provided
        if config:
            agent.configure(config)

        # Store agent
        self.agents[agent_id] = agent
        self._save_agent(agent)

        return agent_id

    def execute_agent(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task"""
        agent = self.agents.get(agent_id)

        if not agent:
            agent = self._load_agent(agent_id)

        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        result = agent.execute(input_data)
        self._save_agent(agent)

        return result

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent status"""
        agent = self.agents.get(agent_id)

        if not agent:
            agent = self._load_agent(agent_id)

        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        return agent.get_status()

    def list_user_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """List all agents for a user"""
        user_agents = []

        for agent_file in self.storage_path.glob(f"*_{user_id}.json"):
            with open(agent_file, "r") as f:
                agent_data = json.load(f)
                user_agents.append(agent_data)

        return user_agents

    def delete_agent(self, agent_id: str):
        """Delete an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]

        agent_file = self.storage_path / f"{agent_id}.json"
        if agent_file.exists():
            agent_file.unlink()

    def _save_agent(self, agent: LegalAIAgent):
        """Save agent to disk"""
        agent_file = self.storage_path / f"{agent.agent_id}_{agent.user_id}.json"

        with open(agent_file, "w") as f:
            json.dump(
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "capability": agent.capability,
                    "user_id": agent.user_id,
                    "status": agent.status,
                    "created_at": agent.created_at.isoformat(),
                    "last_run": agent.last_run.isoformat() if agent.last_run else None,
                    "config": agent.config,
                    "results": agent.results,
                },
                f,
                indent=2,
            )

    def _load_agent(self, agent_id: str) -> Optional[LegalAIAgent]:
        """Load agent from disk"""
        # Import document agents
        from legal_document_agents import (BriefWriterAgent,
                                           ContractDrafterAgent,
                                           LegalLetterAgent,
                                           MotionDrafterAgent)

        for agent_file in self.storage_path.glob(f"{agent_id}_*.json"):
            with open(agent_file, "r") as f:
                data = json.load(f)

                # Reconstruct agent based on capability
                capability = data["capability"]

                if capability == AgentCapability.DISCOVERY_PROCESSING:
                    agent = DiscoveryProcessingAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.EVIDENCE_ORGANIZATION:
                    agent = EvidenceOrganizerAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.TIMELINE_CONSTRUCTION:
                    agent = TimelineBuilderAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.COMPLIANCE_CHECKING:
                    agent = ComplianceCheckerAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.MOTION_DRAFTING:
                    agent = MotionDrafterAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.BRIEF_WRITING:
                    agent = BriefWriterAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.LETTER_WRITING:
                    agent = LegalLetterAgent(data["agent_id"], data["user_id"])
                elif capability == AgentCapability.CONTRACT_DRAFTING:
                    agent = ContractDrafterAgent(data["agent_id"], data["user_id"])
                else:
                    return None

                agent.status = data["status"]
                agent.config = data["config"]
                agent.results = data["results"]
                agent.created_at = datetime.fromisoformat(data["created_at"])
                if data["last_run"]:
                    agent.last_run = datetime.fromisoformat(data["last_run"])

                self.agents[agent_id] = agent
                return agent

        return None


# Global agent manager instance
agent_manager = AgentManager()
