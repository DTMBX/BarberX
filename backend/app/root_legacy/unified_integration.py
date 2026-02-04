# Unified Integration Layer
# Connects all Evident features: evidence analysis, AI agents, chat, scanning, and processing

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .ai_suggestions import smart_suggest
from .legal_ai_agents import AgentCapability, agent_manager
from .legal_document_agents import (BriefWriterAgent, LegalLetterAgent,
                                   MotionDrafterAgent)


class UnifiedWorkflowOrchestrator:
    """Orchestrates the complete evidence-to-document workflow"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.active_workflows = {}

    def process_evidence_intake(self, evidence_data: Dict) -> Dict[str, Any]:
        """
        Complete workflow:
        1. Evidence uploaded
        2. Auto-deploy discovery agent
        3. Process and categorize
        4. Enable AI chat for Q&A
        5. Suggest next actions
        """

        workflow_id = evidence_data.get("id", "")

        # Step 1: Auto-deploy discovery agent
        discovery_agent_id = agent_manager.deploy_agent(
            agent_type="discovery",
            user_id=self.user_id,
            config={
                "auto_categorize": True,
                "extract_entities": True,
                "detect_privileged": True,
                "OCR_documents": True,
            },
        )

        # Step 2: Execute discovery processing
        discovery_results = agent_manager.execute_agent(
            agent_id=discovery_agent_id,
            input_data={
                "files": evidence_data.get("files", []),
                "case_id": evidence_data.get("case_id", ""),
            },
        )

        # Step 3: Auto-deploy organizer if multiple documents
        organizer_agent_id = None
        if discovery_results.get("processed", 0) > 5:
            organizer_agent_id = agent_manager.deploy_agent(
                agent_type="organizer",
                user_id=self.user_id,
                config={"organization_scheme": "chronological", "link_related": True},
            )

        # Step 4: Build timeline from extracted events
        timeline_agent_id = None
        if discovery_results.get("timeline_events"):
            timeline_agent_id = agent_manager.deploy_agent(
                agent_type="timeline", user_id=self.user_id
            )

            timeline_results = agent_manager.execute_agent(
                agent_id=timeline_agent_id,
                input_data={"events": discovery_results["timeline_events"]},
            )

        # Step 5: Check compliance
        compliance_agent_id = agent_manager.deploy_agent(
            agent_type="compliance", user_id=self.user_id
        )

        compliance_results = agent_manager.execute_agent(
            agent_id=compliance_agent_id,
            input_data={
                "evidence": evidence_data.get("files", []),
                "case_type": evidence_data.get("case_type", "civil"),
            },
        )

        # Step 6: Prepare AI chat context
        chat_context = self._prepare_chat_context(
            discovery_results, compliance_results, evidence_data
        )

        # Step 7: Suggest next actions based on findings
        suggested_actions = self._suggest_next_actions(discovery_results, compliance_results)

        # Save workflow state
        self.active_workflows[workflow_id] = {
            "discovery_agent": discovery_agent_id,
            "organizer_agent": organizer_agent_id,
            "timeline_agent": timeline_agent_id,
            "compliance_agent": compliance_agent_id,
            "discovery_results": discovery_results,
            "compliance_results": compliance_results,
            "chat_context": chat_context,
            "status": "processed",
            "created_at": datetime.utcnow().isoformat(),
        }

        return {
            "workflow_id": workflow_id,
            "discovery": discovery_results,
            "compliance": compliance_results,
            "suggested_actions": suggested_actions,
            "chat_enabled": True,
            "chat_context": chat_context,
            "agents_deployed": {
                "discovery": discovery_agent_id,
                "organizer": organizer_agent_id,
                "timeline": timeline_agent_id,
                "compliance": compliance_agent_id,
            },
        }

    def process_ai_chat_query(self, workflow_id: str, query: str) -> Dict[str, Any]:
        """
        Process AI chat query with full context from evidence analysis
        """

        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        # Get context
        context = workflow.get("chat_context", {})
        discovery = workflow.get("discovery_results", {})
        compliance = workflow.get("compliance_results", {})

        # Process query based on intent
        response = self._generate_ai_response(query, context, discovery, compliance)

        return {
            "query": query,
            "response": response,
            "sources": self._get_relevant_sources(query, discovery),
            "suggested_follow_ups": self._generate_follow_up_questions(query, context),
        }

    def generate_document_from_analysis(
        self, workflow_id: str, document_type: str, custom_inputs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate legal document based on evidence analysis
        """

        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        discovery = workflow.get("discovery_results", {})
        compliance = workflow.get("compliance_results", {})

        # Determine which agent to use
        if document_type in [
            "motion_to_dismiss",
            "motion_for_summary_judgment",
            "motion_in_limine",
        ]:
            agent_type = "motion_drafter"
            agent_config = {
                "motion_type": document_type,
                "include_case_law": True,
                "include_statutes": True,
            }
        elif document_type in ["memorandum", "appellate_brief", "trial_brief"]:
            agent_type = "brief_writer"
            agent_config = {"brief_type": document_type, "include_table_of_authorities": True}
        elif document_type in ["demand_letter", "cease_and_desist", "opinion_letter"]:
            agent_type = "letter_writer"
            agent_config = {"letter_type": document_type, "tone": "firm"}
        else:
            return {"error": f"Unknown document type: {document_type}"}

        # Deploy document agent
        doc_agent_id = agent_manager.deploy_agent(
            agent_type=agent_type, user_id=self.user_id, config=agent_config
        )

        # Prepare input data from analysis
        input_data = self._prepare_document_input(
            document_type=document_type,
            discovery=discovery,
            compliance=compliance,
            custom_inputs=custom_inputs or {},
        )

        # Execute document generation
        result = agent_manager.execute_agent(doc_agent_id, input_data)

        # Save to workflow
        if "generated_documents" not in workflow:
            workflow["generated_documents"] = []

        workflow["generated_documents"].append(
            {
                "type": document_type,
                "agent_id": doc_agent_id,
                "result": result,
                "generated_at": datetime.utcnow().isoformat(),
            }
        )

        return result

    def scan_and_process_document(self, file_data: Dict) -> Dict[str, Any]:
        """
        Scan document (OCR if needed) and process with AI
        """

        # Step 1: Detect if OCR needed
        needs_ocr = self._check_if_ocr_needed(file_data)

        text_content = ""
        if needs_ocr:
            # In production, integrate with OCR service (Tesseract, AWS Textract, Google Vision)
            text_content = self._perform_ocr(file_data)
        else:
            text_content = file_data.get("content", "")

        # Step 2: Extract structured data
        extracted_data = self._extract_structured_data(text_content)

        # Step 3: Categorize document
        category = smart_suggest.auto_categorize(
            filename=file_data.get("name", ""), description=text_content[:500]
        )

        # Step 4: Extract entities
        entities = self._extract_entities_advanced(text_content)

        # Step 5: Suggest priority
        priority = smart_suggest.suggest_priority(text_content)

        return {
            "filename": file_data.get("name"),
            "ocr_performed": needs_ocr,
            "text_content": text_content,
            "category": category,
            "entities": entities,
            "suggested_priority": priority,
            "extracted_data": extracted_data,
            "ready_for_analysis": True,
        }

    def _prepare_chat_context(self, discovery: Dict, compliance: Dict, evidence: Dict) -> Dict:
        """Prepare context for AI chat"""

        return {
            "case_id": evidence.get("case_id", ""),
            "evidence_count": discovery.get("processed", 0),
            "categories": list(discovery.get("categorized", {}).keys()),
            "key_entities": discovery.get("entities_found", [])[:20],
            "privileged_docs": discovery.get("privileged_docs", []),
            "key_documents": discovery.get("key_documents", []),
            "timeline_events_count": len(discovery.get("timeline_events", [])),
            "compliance_status": {
                "compliant": compliance.get("compliant", 0),
                "violations": len(compliance.get("violations", [])),
                "warnings": len(compliance.get("warnings", [])),
            },
        }

    def _suggest_next_actions(self, discovery: Dict, compliance: Dict) -> List[Dict]:
        """Suggest next actions based on analysis"""

        actions = []

        # If privileged docs found
        if discovery.get("privileged_docs"):
            actions.append(
                {
                    "action": "review_privileged",
                    "priority": "high",
                    "description": f"Review {len(discovery['privileged_docs'])} privileged documents before production",
                    "icon": "🔒",
                }
            )

        # If key documents found
        if discovery.get("key_documents"):
            actions.append(
                {
                    "action": "review_key_docs",
                    "priority": "high",
                    "description": f"Review {len(discovery['key_documents'])} key documents",
                    "icon": "⭐",
                }
            )

        # If compliance violations
        if compliance.get("violations"):
            actions.append(
                {
                    "action": "fix_violations",
                    "priority": "critical",
                    "description": f"Fix {len(compliance['violations'])} compliance violations",
                    "icon": "⚠️",
                }
            )

        # If timeline events found
        if discovery.get("timeline_events"):
            actions.append(
                {
                    "action": "build_timeline",
                    "priority": "medium",
                    "description": "Build comprehensive case timeline",
                    "icon": "📅",
                }
            )

        # Suggest document generation
        actions.append(
            {
                "action": "generate_motion",
                "priority": "medium",
                "description": "Generate motion or brief based on evidence",
                "icon": "📄",
            }
        )

        return actions

    def _generate_ai_response(
        self, query: str, context: Dict, discovery: Dict, compliance: Dict
    ) -> str:
        """Generate AI response to chat query"""

        query_lower = query.lower()

        # Answer questions about discovery
        if "how many" in query_lower and "document" in query_lower:
            return f"I found {discovery.get('processed', 0)} documents. They are categorized as follows: {', '.join([f'{k}: {v}' for k, v in discovery.get('categorized', {}).items()])}."

        if "privileged" in query_lower:
            privileged = discovery.get("privileged_docs", [])
            if privileged:
                return f"I detected {len(privileged)} potentially privileged documents. You should review these before production: {', '.join([p['filename'] for p in privileged[:3]])}."
            else:
                return "I didn't detect any obvious attorney-client privileged communications. However, you should still manually review sensitive documents."

        if "key document" in query_lower or "important" in query_lower:
            key_docs = discovery.get("key_documents", [])
            if key_docs:
                return f"I identified {len(key_docs)} key documents: {', '.join([k['filename'] for k in key_docs[:3]])}. These appear to be critical to your case."
            else:
                return "I didn't automatically flag any documents as 'key', but you should review the categorized evidence for case-critical items."

        if "compliance" in query_lower or "violation" in query_lower:
            violations = compliance.get("violations", [])
            if violations:
                return f"⚠️ I found {len(violations)} compliance issues. Most serious: {violations[0]['type']} - {violations[0]['details']}"
            else:
                return f"✅ Good news! Your evidence appears compliant. Compliance rate: {compliance.get('compliance_rate', 0)}%"

        if "timeline" in query_lower:
            events = discovery.get("timeline_events", [])
            return f"I extracted {len(events)} timeline events from your evidence. Would you like me to build a comprehensive timeline?"

        if "suggest" in query_lower or "recommend" in query_lower:
            return "Based on your evidence, I recommend: 1) Review privileged documents, 2) Build a timeline, 3) Consider filing a motion based on the key documents found. What would you like to start with?"

        # Generic helpful response
        return f"I have analyzed {context.get('evidence_count', 0)} pieces of evidence. I can help you with: reviewing documents, checking compliance, building timelines, or generating legal documents. What would you like to know?"

    def _get_relevant_sources(self, query: str, discovery: Dict) -> List[Dict]:
        """Get relevant source documents for query"""

        sources = []
        query_words = set(query.lower().split())

        # Check key documents
        for doc in discovery.get("key_documents", []):
            if any(word in doc.get("filename", "").lower() for word in query_words):
                sources.append(
                    {
                        "type": "key_document",
                        "filename": doc["filename"],
                        "category": doc.get("category", ""),
                    }
                )

        return sources[:5]

    def _generate_follow_up_questions(self, query: str, context: Dict) -> List[str]:
        """Generate suggested follow-up questions"""

        return [
            "What are the key documents?",
            "Are there any compliance issues?",
            "Can you build a timeline?",
            "What documents should I review first?",
            "Generate a motion based on this evidence",
        ]

    def _prepare_document_input(
        self, document_type: str, discovery: Dict, compliance: Dict, custom_inputs: Dict
    ) -> Dict:
        """Prepare input for document generation"""

        # Extract facts from discovery
        facts = "\n\n".join(
            [
                f"On {event['date']}: {event['description']}"
                for event in discovery.get("timeline_events", [])[:10]
            ]
        )

        # Prepare legal arguments from key documents
        legal_arguments = []
        for doc in discovery.get("key_documents", []):
            legal_arguments.append(
                {
                    "heading": f"Evidence Shows {doc['category']}",
                    "content": f"As evidenced by {doc['filename']}, ...",
                    "keywords": ["evidence", doc["category"].lower()],
                }
            )

        input_data = {
            "case_info": custom_inputs.get("case_info", {}),
            "facts": custom_inputs.get("facts", facts),
            "legal_arguments": custom_inputs.get("legal_arguments", legal_arguments),
            "jurisdiction": custom_inputs.get("jurisdiction", "federal"),
        }

        # Add document-type specific data
        if document_type in ["motion_to_dismiss", "motion_for_summary_judgment"]:
            input_data["motion_type"] = document_type
        elif document_type in ["demand_letter", "cease_and_desist"]:
            input_data["letter_type"] = document_type

        return input_data

    def _check_if_ocr_needed(self, file_data: Dict) -> bool:
        """Check if document needs OCR"""

        filename = file_data.get("name", "").lower()

        # If image file, needs OCR
        if any(ext in filename for ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]):
            return True

        # If PDF with no text content
        if ".pdf" in filename and not file_data.get("content"):
            return True

        return False

    def _perform_ocr(self, file_data: Dict) -> str:
        """Perform OCR on document (placeholder for production OCR service)"""

        # In production, integrate with:
        # - Tesseract (open source)
        # - AWS Textract
        # - Google Cloud Vision
        # - Azure Computer Vision

        return "[OCR TEXT EXTRACTED] - In production, this would contain actual OCR results"

    def _extract_structured_data(self, text: str) -> Dict:
        """Extract structured data from text"""

        import re

        structured = {
            "dates": [],
            "names": [],
            "addresses": [],
            "amounts": [],
            "phone_numbers": [],
            "emails": [],
        }

        # Extract dates
        dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)
        structured["dates"] = list(set(dates))[:10]

        # Extract amounts
        amounts = re.findall(r"\$[\d,]+\.?\d*", text)
        structured["amounts"] = list(set(amounts))[:10]

        # Extract phone numbers
        phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text)
        structured["phone_numbers"] = list(set(phones))[:10]

        # Extract emails
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        structured["emails"] = list(set(emails))[:10]

        return structured

    def _extract_entities_advanced(self, text: str) -> List[Dict]:
        """Advanced entity extraction"""

        # In production, use spaCy or other NLP library
        # For now, use basic regex

        entities = []

        import re

        # Names (basic pattern)
        name_pattern = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
        names = re.findall(name_pattern, text)
        for name in set(names)[:10]:
            entities.append({"type": "PERSON", "value": name})

        # Organizations (look for Inc., LLC, Corp.)
        org_pattern = r"\b[A-Z][A-Za-z\s&]+(Inc\.|LLC|Corp\.|Corporation|Company)\b"
        orgs = re.findall(org_pattern, text)
        for org in set(orgs)[:10]:
            entities.append({"type": "ORGANIZATION", "value": org})

        return entities


# Global orchestrator instance
def get_orchestrator(user_id: str) -> UnifiedWorkflowOrchestrator:
    """Get or create orchestrator for user"""
    return UnifiedWorkflowOrchestrator(user_id)


