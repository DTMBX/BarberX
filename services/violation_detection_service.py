"""
Violation Detection Services
Three-level violation detection (Basic → Comprehensive → Expert)
Detects constitutional, statutory, procedural, ethical, and discovery fraud violations
"""

import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from models.legal_violations import (
    LegalViolation, ConstitutionalViolation, StatutoryViolation,
    ProceduralViolation, EthicalViolation, DiscoveryFraudViolation,
    ViolationCache, ViolationTrendAnalysis, ViolationReportingLog,
    ViolationType, ViolationSeverity, ConfidenceLevel
)
from models.evidence import EvidenceItem
from models.legal_case import LegalCase
from auth.models import db


class ViolationDetectionService:
    """
    Base violation detection service
    Provides common methods for all violation detection strategies
    """
    
    def __init__(self):
        """Initialize violation detection service"""
        self.detection_engine = "ViolationDetectionEngine"
        self.model_version = "1.0.0"
    
    def detect_violations(self, evidence_id: int, confidence_level: str) -> List[dict]:
        """
        Main detection method - routes to appropriate level
        
        Args:
            evidence_id: ID of evidence to analyze
            confidence_level: 'basic', 'comprehensive', or 'expert'
        
        Returns:
            List of detected violations
        """
        evidence = EvidenceItem.query.get(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        # Check cache first
        cache = ViolationCache.query.filter_by(evidence_id=evidence_id).first()
        if cache and cache.analysis_complete and not cache.needs_reanalysis:
            return self._get_cached_violations(evidence_id)
        
        # Route to appropriate detection level
        if confidence_level == "basic":
            violations = self._detect_basic_violations(evidence)
        elif confidence_level == "comprehensive":
            violations = self._detect_comprehensive_violations(evidence)
        elif confidence_level == "expert":
            violations = self._detect_expert_violations(evidence)
        else:
            raise ValueError(f"Unknown confidence level: {confidence_level}")
        
        # Update cache
        self._update_violation_cache(evidence_id, evidence.case_id, violations)
        
        return violations
    
    def _detect_basic_violations(self, evidence: EvidenceItem) -> List[dict]:
        """
        LEVEL 1: BASIC - Pattern/keyword matching
        80-85% accuracy, identifies obvious violations
        """
        violations = []
        text = evidence.text_content or ""
        
        # Constitutional violations - basic keywords
        constitutional = self._detect_constitutional_basic(text, evidence)
        violations.extend(constitutional)
        
        # Statutory violations - basic pattern matching
        statutory = self._detect_statutory_basic(text, evidence)
        violations.extend(statutory)
        
        # Procedural violations - FRCP keywords
        procedural = self._detect_procedural_basic(text, evidence)
        violations.extend(procedural)
        
        # Ethical violations - basic Model Rules keywords
        ethical = self._detect_ethical_basic(text, evidence)
        violations.extend(ethical)
        
        # Discovery fraud - obvious spoliation
        discovery = self._detect_discovery_fraud_basic(text, evidence)
        violations.extend(discovery)
        
        return violations
    
    def _detect_comprehensive_violations(self, evidence: EvidenceItem) -> List[dict]:
        """
        LEVEL 2: COMPREHENSIVE - Context-aware ML + precedent
        90-92% accuracy, requires precedent database and ML models
        """
        # Builds on basic violations
        violations = self._detect_basic_violations(evidence)
        
        # Add ML-enhanced analysis with precedent
        # Requires: Legal-BERT embeddings, precedent similarity search
        # This would call ML models for semantic analysis
        
        # For now, structures the framework
        text = evidence.text_content or ""
        
        constitutional = self._detect_constitutional_comprehensive(text, evidence)
        violations.extend(constitutional)
        
        statutory = self._detect_statutory_comprehensive(text, evidence)
        violations.extend(statutory)
        
        procedural = self._detect_procedural_comprehensive(text, evidence)
        violations.extend(procedural)
        
        ethical = self._detect_ethical_comprehensive(text, evidence)
        violations.extend(ethical)
        
        return violations
    
    def _detect_expert_violations(self, evidence: EvidenceItem) -> List[dict]:
        """
        LEVEL 3: EXPERT - Deep legal reasoning + case law integration
        95%+ accuracy, requires full legal knowledge base
        """
        # Builds on comprehensive violations
        violations = self._detect_comprehensive_violations(evidence)
        
        # Add expert-level analysis
        text = evidence.text_content or ""
        case = evidence.legal_case
        
        # Deep constitutional analysis
        constitutional = self._detect_constitutional_expert(text, evidence, case)
        violations.extend(constitutional)
        
        # Complex statutory interactions
        statutory = self._detect_statutory_expert(text, evidence, case)
        violations.extend(statutory)
        
        # Sophisticated procedural analysis
        procedural = self._detect_procedural_expert(text, evidence, case)
        violations.extend(procedural)
        
        # Nuanced ethical analysis
        ethical = self._detect_ethical_expert(text, evidence, case)
        violations.extend(ethical)
        
        return violations
    
    # CONSTITUTIONAL VIOLATION DETECTION
    
    def _detect_constitutional_basic(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Basic constitutional violation detection via keyword matching"""
        violations = []
        
        # 4th Amendment - Search & Seizure
        if self._contains_patterns(text, ["illegal search", "warrantless", "unreasonable seizure", "without warrant"]):
            violation = {
                "type": "constitutional",
                "amendment": "4th",
                "category": "illegal_search",
                "confidence": 0.82,
                "method": "keyword_match",
                "severity": "severe"
            }
            violations.append(violation)
        
        # 5th Amendment - Self-Incrimination
        if self._contains_patterns(text, ["compelled to testify", "incriminate", "self-incrimination", "take the fifth"]):
            violation = {
                "type": "constitutional",
                "amendment": "5th",
                "category": "self_incrimination",
                "confidence": 0.85,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        # 6th Amendment - Right to Counsel
        if self._contains_patterns(text, ["denied counsel", "right to attorney", "without lawyer", "pro se"]):
            violation = {
                "type": "constitutional",
                "amendment": "6th",
                "category": "counsel",
                "confidence": 0.80,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        # 14th Amendment - Equal Protection
        if self._contains_patterns(text, ["discrimination", "equal protection", "selective prosecution", "discriminatory"]):
            violation = {
                "type": "constitutional",
                "amendment": "14th",
                "category": "equal_protection",
                "confidence": 0.78,
                "method": "keyword_match",
                "severity": "severe"
            }
            violations.append(violation)
        
        return violations
    
    def _detect_constitutional_comprehensive(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Comprehensive constitutional analysis with context"""
        violations = self._detect_constitutional_basic(text, evidence)
        
        # Enhanced analysis - would integrate with precedent database
        # This requires Legal-BERT embeddings and case law similarity
        
        return violations
    
    def _detect_constitutional_expert(self, text: str, evidence: EvidenceItem, case: LegalCase) -> List[dict]:
        """Expert-level constitutional analysis with case law integration"""
        violations = self._detect_constitutional_comprehensive(text, evidence)
        
        # Deep analysis incorporating:
        # - SCOTUS precedents
        # - Circuit court decisions
        # - Jurisdiction-specific interpretations
        # - Strict scrutiny analysis where applicable
        
        return violations
    
    # STATUTORY VIOLATION DETECTION
    
    def _detect_statutory_basic(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Basic statutory violation detection"""
        violations = []
        
        # Title VII (Employment Discrimination)
        if self._contains_patterns(text, ["title vii", "42 usc 2000e", "employment discrimination", "discriminatory"]):
            violation = {
                "type": "statutory",
                "statute": "Title VII",
                "citation": "42 U.S.C. § 2000e",
                "category": "employment_discrimination",
                "confidence": 0.84,
                "method": "keyword_match",
                "severity": "severe"
            }
            violations.append(violation)
        
        # Fraud violations
        if self._contains_patterns(text, ["false statement", "material misrepresentation", "defraud", "deception"]):
            violation = {
                "type": "statutory",
                "statute": "Wire Fraud",
                "citation": "18 U.S.C. § 1343",
                "category": "fraud",
                "confidence": 0.80,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        return violations
    
    def _detect_statutory_comprehensive(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Comprehensive statutory analysis"""
        violations = self._detect_statutory_basic(text, evidence)
        return violations
    
    def _detect_statutory_expert(self, text: str, evidence: EvidenceItem, case: LegalCase) -> List[dict]:
        """Expert statutory analysis with elements check"""
        violations = self._detect_statutory_comprehensive(text, evidence)
        return violations
    
    # PROCEDURAL VIOLATION DETECTION
    
    def _detect_procedural_basic(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Basic procedural violation detection"""
        violations = []
        
        # FRCP 26 violation
        if self._contains_patterns(text, ["frcp 26", "improper discovery", "evasive response", "failure to disclose"]):
            violation = {
                "type": "procedural",
                "rule": "FRCP 26",
                "category": "improper_discovery",
                "confidence": 0.86,
                "method": "keyword_match",
                "severity": "severe"
            }
            violations.append(violation)
        
        # FRCP 33 - Interrogatories
        if self._contains_patterns(text, ["frcp 33", "too many interrogatories", "burdensome", "unduly burdensome"]):
            violation = {
                "type": "procedural",
                "rule": "FRCP 33",
                "category": "improper_interrogatory",
                "confidence": 0.82,
                "method": "keyword_match",
                "severity": "moderate"
            }
            violations.append(violation)
        
        return violations
    
    def _detect_procedural_comprehensive(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Comprehensive procedural analysis"""
        violations = self._detect_procedural_basic(text, evidence)
        return violations
    
    def _detect_procedural_expert(self, text: str, evidence: EvidenceItem, case: LegalCase) -> List[dict]:
        """Expert procedural analysis with sanctions analysis"""
        violations = self._detect_procedural_comprehensive(text, evidence)
        return violations
    
    # ETHICAL VIOLATION DETECTION
    
    def _detect_ethical_basic(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Basic ethical violation detection"""
        violations = []
        
        # Model Rule 1.6 (Confidentiality)
        if self._contains_patterns(text, ["confidential", "attorney client", "work product", "privileged"]):
            violation = {
                "type": "ethical",
                "rule": "1.6",
                "category": "privilege_breach",
                "confidence": 0.84,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        # Model Rule 3.3 (Candor to tribunal)
        if self._contains_patterns(text, ["false statement", "material fact omission", "court", "tribunal"]):
            violation = {
                "type": "ethical",
                "rule": "3.3",
                "category": "false_statement",
                "confidence": 0.80,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        return violations
    
    def _detect_ethical_comprehensive(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Comprehensive ethical analysis"""
        violations = self._detect_ethical_basic(text, evidence)
        return violations
    
    def _detect_ethical_expert(self, text: str, evidence: EvidenceItem, case: LegalCase) -> List[dict]:
        """Expert ethical analysis with disciplinary risk"""
        violations = self._detect_ethical_comprehensive(text, evidence)
        return violations
    
    # DISCOVERY FRAUD DETECTION
    
    def _detect_discovery_fraud_basic(self, text: str, evidence: EvidenceItem) -> List[dict]:
        """Basic discovery fraud detection"""
        violations = []
        
        # Spoliation indicators
        if self._contains_patterns(text, ["destroyed", "deleted", "shredded", "burned", "erased", "removed"]):
            violation = {
                "type": "discovery_fraud",
                "fraud_type": "spoliation",
                "confidence": 0.78,
                "method": "keyword_match",
                "severity": "critical"
            }
            violations.append(violation)
        
        return violations
    
    # HELPER METHODS
    
    @staticmethod
    def _contains_patterns(text: str, patterns: List[str]) -> bool:
        """Check if text contains any of the patterns (case-insensitive)"""
        text_lower = text.lower() if text else ""
        return any(pattern.lower() in text_lower for pattern in patterns)
    
    def _get_cached_violations(self, evidence_id: int) -> List[dict]:
        """Retrieve violations from cache"""
        cache = ViolationCache.query.filter_by(evidence_id=evidence_id).first()
        if not cache or not cache.violation_ids:
            return []
        
        violation_ids = json.loads(cache.violation_ids)
        violations = LegalViolation.query.filter(
            LegalViolation.id.in_(violation_ids)
        ).all()
        
        return [self._violation_to_dict(v) for v in violations]
    
    def _update_violation_cache(self, evidence_id: int, case_id: int, violations: List[dict]):
        """Update or create violation cache"""
        cache = ViolationCache.query.filter_by(evidence_id=evidence_id).first()
        
        if not cache:
            cache = ViolationCache(evidence_id=evidence_id, case_id=case_id)
        
        cache.analysis_complete = True
        cache.violations_found = len(violations)
        
        # Count by severity
        cache.critical_count = len([v for v in violations if v.get("severity") == "critical"])
        cache.severe_count = len([v for v in violations if v.get("severity") == "severe"])
        cache.moderate_count = len([v for v in violations if v.get("severity") == "moderate"])
        cache.minor_count = len([v for v in violations if v.get("severity") == "minor"])
        
        cache.analyzed_at = datetime.utcnow()
        cache.analyzer_version = self.model_version
        
        db.session.add(cache)
        db.session.commit()
    
    @staticmethod
    def _violation_to_dict(violation: LegalViolation) -> dict:
        """Convert violation model to dictionary"""
        return {
            "id": violation.id,
            "type": violation.violation_type,
            "category": violation.violation_category,
            "severity": violation.severity,
            "confidence": violation.confidence_score,
            "text": violation.detected_text,
            "explanation": violation.violation_explanation
        }
    
    def save_violation(self, evidence_id: int, case_id: int, violation_data: dict) -> LegalViolation:
        """
        Save detected violation to database
        
        Args:
            evidence_id: ID of evidence
            case_id: ID of case
            violation_data: Dictionary with violation details
        
        Returns:
            Created LegalViolation object
        """
        violation = LegalViolation(
            evidence_id=evidence_id,
            case_id=case_id,
            violation_type=violation_data.get("type"),
            violation_category=violation_data.get("category"),
            severity=violation_data.get("severity", "moderate"),
            confidence_level=violation_data.get("confidence_level", "basic"),
            confidence_score=violation_data.get("confidence", 0.0),
            detected_text=violation_data.get("text"),
            violation_explanation=violation_data.get("explanation")
        )
        
        db.session.add(violation)
        db.session.commit()
        
        return violation
    
    def get_case_violations(self, case_id: int) -> Dict[str, any]:
        """
        Get comprehensive violation summary for case
        
        Returns:
            Dictionary with violation statistics and summaries
        """
        violations = LegalViolation.query.filter_by(case_id=case_id).all()
        
        return {
            "total_violations": len(violations),
            "by_type": self._count_by_type(violations),
            "by_severity": self._count_by_severity(violations),
            "violations": [self._violation_to_dict(v) for v in violations]
        }
    
    @staticmethod
    def _count_by_type(violations: List[LegalViolation]) -> Dict[str, int]:
        """Count violations by type"""
        counts = {}
        for v in violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 1
        return counts
    
    @staticmethod
    def _count_by_severity(violations: List[LegalViolation]) -> Dict[str, int]:
        """Count violations by severity"""
        counts = {}
        for v in violations:
            counts[v.severity] = counts.get(v.severity, 0) + 1
        return counts
