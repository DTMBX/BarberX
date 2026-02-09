# E-Discovery Legal System - Complete Implementation Guide

## Overview

This document provides a complete implementation guide for the Evident e-discovery legal system. The system is built with comprehensive models and services for managing document discovery, production, compliance, and litigation holds.

## Architecture Components

### 1. **E-Discovery Models** (`models/ediscovery.py`)

Core models for discovery management:

#### Discovery Request Management

- **DiscoveryRequest**: Tracks incoming discovery requests (interrogatories, requests for production, etc.)
  - Stores request text, received date, response deadline
  - Tracks status (pending, responded, objected, etc.)
  - Manages extensions and partial responses
  - Links to assigned attorneys

#### Responsive Document Tracking

- **ResponsiveDocument**: Links evidence to discovery requests
  - Tracks whether documents are responsive
  - Manages Bates numbering for production
  - Handles redaction versions
  - Documents production status

#### Production Management

- **ProductionSet**: Represents a production of documents
  - Tracks production number, date, and delivery method
  - Maintains document counts and size metrics
  - Manages designations (CONFIDENTIAL, AEO, etc.)
  - Supports multiple production formats

- **ProductionItem**: Individual items in a production
  - Bates numbering and sequencing
  - Page counts and file sizes
  - Designation tracking
  - Production notes

#### Privilege Protection

- **PrivilegeLog**: Maintains privilege log for withheld documents
  - Documents claimed privilege basis
  - Records parties (from/to/cc)
  - Provides general subject without revealing content
  - Tracks attorney involvement

#### Litigation Holds

- **LitigationHold**: Legal holds across organization
- **Custodian**: Individual custodians under hold
- **HoldNotice**: Notices sent to custodians

#### Document Metadata

- **DocumentMetadata**: Extracted metadata from documents
  - File creation/modification dates
  - Email metadata (from, to, cc, subject, dates)
  - Page/word counts
  - Extracted entities (persons, organizations, locations)
  - Language detection

#### Search & ESI

- **DocumentSearchQuery**: Saved discovery search queries
- **ESIProtocol**: ESI protocol agreements defining how parties handle ESI

### 2. **Document Processing Models** (`models/document_processing.py`)

Advanced processing and QA models:

#### Task Management

- **DocumentProcessingTask**: Tracks processing jobs
  - Task type (OCR, transcription, entity extraction, etc.)
  - Status tracking (queued, processing, completed, failed)
  - Resource utilization and cost tracking
  - Processing engine and model information

#### OCR Processing

- **OCRResult**: Stores OCR results
  - Extracted text with confidence scores
  - Page processing status
  - Language detection
  - Quality metrics (accuracy, word accuracy)

#### Transcription

- **TranscriptionResult**: Audio/video transcription
  - Full transcript with optional timecoding
  - Speaker identification and diarization
  - Confidence scores
  - QA review workflow

#### Redaction Management

- **RedactionRule**: Automated redaction rules
  - Pattern-based or entity-based rules
  - Applies to specific document types
  - Customizable redaction styles
  - Priority and activation control

- **RedactionInstance**: Individual redactions
  - Manual or automatic application
  - Location information (page, line)
  - Approval workflow
  - Justification tracking

#### Quality Assurance

- **ComplianceReview**: QA reviews of processed documents
  - Review type (OCR quality, transcription accuracy, redaction, etc.)
  - Quality scores (accuracy, completeness, compliance)
  - Issue detection and tracking
  - Reprocessing requirements

#### Content Indexing

- **ContentExtractionIndex**: Full-text search index
  - Extracted content for searching
  - Entity information (NER results)
  - Sentiment analysis
  - Key phrase extraction

#### Batch Processing

- **BatchProcessingQueue**: Batch processing jobs
  - Document selection and counting
  - Progress tracking
  - Cost estimation
  - Completion status

### 3. **Compliance Models** (`models/compliance.py`)

Compliance and regulatory tracking:

#### Compliance Tracking

- **ComplianceObligation**: Specific case obligations
  - Obligation type (disclosure, preservation, production, certification)
  - Deadlines and extensions
  - Status and certification
  - Risk assessment

- **DeadlineTracker**: All case deadlines
  - Court-ordered deadlines
  - Regulatory requirements
  - Status (pending, met, missed, extended)
  - Alert notifications

#### Audit & Documentation

- **AuditLog**: Comprehensive audit trail
  - All system activities (view, edit, delete, export)
  - User information and IP addressed
  - Change tracking (old/new values)
  - Success/failure recording

- **CustodyAffidavit**: Custodian affidavits
  - Sworn statements of custody
  - Materials description
  - Administration of oath
  - Signature and notarization

- **CertificationOfCustody**: Official custody certifications
  - Formal certification statements
  - Integrity assurances
  - Digital signatures and notarization
  - Filing status

#### Reporting

- **ComplianceReport**: Automated compliance reports
  - Report type (discovery, production, privilege log, hold, etc.)
  - Compliance assessment and status
  - Issue tracking and remediation
  - Approval workflow

- **RiskAssessment**: Risk assessments for litigation
  - Risk area and level
  - Probability and impact analysis
  - Risk score calculation
  - Mitigation strategy and monitoring

#### Record Retention

- **DocumentRetention**: Document retention and destruction
  - Retention policy and period
  - Legal hold status
  - Destruction approval and completion
  - Destruction certificates

- **LegalHold_Evidence**: Junction table
  - Links holds to specific evidence
  - Preservation method tracking
  - Release status and reason

## Service Layer (`services/`)

### EDiscoveryService (`ediscovery_service.py`)

**DiscoveryService**

```python
# Create discovery request
request = DiscoveryService.create_discovery_request(case_id, request_data, user)

# Update request status
DiscoveryService.update_discovery_request(request_id, new_data, user)

# Link responsive documents
docs = DiscoveryService.link_responsive_documents(request_id, evidence_ids, user)

# Get discovery statistics
stats = DiscoveryService.get_discovery_stats(case_id)
```

**ProductionService**

```python
# Create production set
production = ProductionService.create_production(case_id, production_data, user)

# Add document with Bates numbering
item = ProductionService.add_document_to_production(production_id, evidence_id, "ACME-00001", "ACME-00005", user)

# Apply designations
ProductionService.apply_designation(production_id, document_ids, "CONFIDENTIAL - AEO", user)

# Export load file
load_file = ProductionService.export_production_load_file(production_id, format='csv')
```

**PrivilegeService**

```python
# Create privilege log entry
entry = PrivilegeService.create_privilege_log_entry(case_id, evidence_id, privilege_data, user)

# Get complete privilege log
log = PrivilegeService.get_privilege_log(case_id)

# Validate privilege log
validation = PrivilegeService.validate_privilege_log(case_id)
```

**LitigationHoldService**

```python
# Create litigation hold
hold = LitigationHoldService.create_litigation_hold(case_id, hold_data, user)

# Add custodian
custodian = LitigationHoldService.add_custodian_to_hold(hold_id, custodian_data, user)

# Send hold notice
notice = LitigationHoldService.send_hold_notice(custodian_id, hold_id, notice_text, user)

# Record acknowledgment
LitigationHoldService.acknowledge_hold(custodian_id)

# Record certification
LitigationHoldService.certify_compliance(custodian_id)

# Get hold status report
status = LitigationHoldService.get_hold_status(hold_id)
```

### Document Processing Service (`document_processing_service.py`)

**ProcessingTaskService**

```python
# Create processing task
task = ProcessingTaskService.create_processing_task(
    evidence_id, case_id, 'ocr', user, parameters, priority)

# Update task status
ProcessingTaskService.update_task_status(task_id, 'completed', user, result_data)

# Get task queue
tasks = ProcessingTaskService.get_task_queue(case_id, limit=50)
```

**OCRService**

```python
# Process OCR result
result = OCRService.process_ocr_result(evidence_id, task_id, extracted_text, confidence)

# Get OCR results
results = OCRService.get_ocr_results(evidence_id)
```

**TranscriptionService**

```python
# Create transcription result
transcript = TranscriptionService.create_transcription_result(
    evidence_id, task_id, transcript_data, user)

# Flag for review
TranscriptionService.flag_for_review(transcription_id, review_notes)

# Approve transcription
TranscriptionService.approve_transcription(transcription_id, user, corrected_text)

# Get transcription
transcript = TranscriptionService.get_transcription(evidence_id)
```

**RedactionService**

```python
# Create redaction rule
rule = RedactionService.create_redaction_rule(case_id, rule_data, user)

# Record redaction
redaction = RedactionService.record_redaction(
    evidence_id, 'pii', rule_id, original_text, user)

# Approve redaction
RedactionService.approve_redaction(redaction_id, user)

# Get redactions
redactions = RedactionService.get_redactions_for_evidence(evidence_id, approved_only=True)
```

**ComplianceReviewService**

```python
# Create compliance review
review = ComplianceReviewService.create_compliance_review(
    evidence_id, case_id, review_data, user)

# Get compliance summary
summary = ComplianceReviewService.get_case_compliance_summary(case_id)
```

### Compliance Service (`compliance_service.py`)

**ComplianceService**

```python
# Create compliance obligation
obligation = ComplianceService.create_compliance_obligation(case_id, data, user)

# Update obligation status
ComplianceService.update_obligation_status(obligation_id, 'completed', user)

# Certify obligation
ComplianceService.certify_obligation(obligation_id, user)

# Get dashboard
dashboard = ComplianceService.get_compliance_dashboard(case_id)
```

**DeadlineService**

```python
# Create deadline
deadline = DeadlineService.create_deadline(case_id, deadline_data, user)

# Check for alerts
alerts = DeadlineService.check_deadline_alerts(case_id)
```

**AuditLogService**

```python
# Log action
AuditLogService.log_action(
    case_id=case_id,
    activity_type='edit',
    entity_type='EvidenceItem',
    user_id=user_id,
    description='Updated evidence metadata'
)

# Get audit logs
logs = AuditLogService.get_case_audit_log(case_id)
```

**CustodyService**

```python
# Create affidavit
affidavit = CustodyService.create_custody_affidavit(case_id, affidavit_data)

# Create certification
cert = CustodyService.create_certification_of_custody(case_id, cert_data, user)
```

**ComplianceReportingService**

```python
# Generate report
report = ComplianceReportingService.generate_compliance_report(
    case_id, 'discovery', report_data, user)

# Approve report
ComplianceReportingService.approve_report(report_id, user)

# Get reports
reports = ComplianceReportingService.get_case_reports(case_id)
```

**RiskAssessmentService**

```python
# Create assessment
assessment = RiskAssessmentService.create_risk_assessment(
    case_id, assessment_data, user)

# Update status
RiskAssessmentService.update_risk_status(assessment_id, 'mitigated')

# Get open risks
risks = RiskAssessmentService.get_open_risks(case_id)
```

**RetentionService**

```python
# Create retention plan
retention = RetentionService.create_retention_plan(evidence_id, case_id, data)

# Approve destruction
RetentionService.approve_destruction(retention_id, user)

# Complete destruction
RetentionService.complete_destruction(retention_id, 'shred', user)

# Get destruction candidates
candidates = RetentionService.get_candidates_for_destruction(case_id)
```

## Usage Examples

### Complete Discovery Workflow

```python
from services.ediscovery_service import (
    DiscoveryService, ProductionService, PrivilegeService
)
from services.document_processing_service import RedactionService
from services.compliance_service import ComplianceService

# 1. Create discovery request
request = DiscoveryService.create_discovery_request(
    case_id=1,
    request_data={
        'request_number': 'RFC-001',
        'request_type': 'request_for_production',
        'request_text': 'Produce all emails from January 1, 2024 to present...',
        'requesting_party': 'Plaintiff',
        'receiving_party': 'Defendant',
        'received_date': datetime(2024, 2, 1),
        'response_due_date': datetime(2024, 3, 1)
    },
    created_by_user=user
)

# 2. Link responsive documents
responsive_docs = DiscoveryService.link_responsive_documents(
    discovery_request_id=request.id,
    evidence_ids=[100, 101, 102, 103],
    linked_by_user=user
)

# 3. Create redaction rules for sensitive content
rule = RedactionService.create_redaction_rule(
    case_id=1,
    rule_data={
        'rule_name': 'Redact Social Security Numbers',
        'rule_type': 'regex',
        'pattern': r'\d{3}-\d{2}-\d{4}',
        'redaction_style': 'blackout',
        'replacement_text': '[SSN REDACTED]'
    },
    created_by_user=user
)

# 4. Create privileged items
privilege_entry = PrivilegeService.create_privilege_log_entry(
    case_id=1,
    evidence_id=105,
    privilege_data={
        'document_title': 'Email: Legal Advice Re: Settlement',
        'document_type': 'email',
        'privilege_claimed': 'attorney_client',
        'privilege_description': 'Confidential attorney-client communication',
        'from_party': 'John Doe',
        'to_party': 'Jane Attorney',
        'general_subject': 'Legal advice concerning settlement negotiations',
        'attorney_involved': 'Jane Attorney',
        'seeks_legal_advice': True
    },
    created_by_user=user
)

# 5. Create production set
production = ProductionService.create_production(
    case_id=1,
    production_data={
        'production_number': 'Production 1',
        'produced_to_party': 'Plaintiff',
        'description': 'First complete production of responsive documents',
        'delivery_format': 'pdf',
        'delivery_method': 'portal'
    },
    created_by_user=user
)

# 6. Add documents to production with Bates numbers
bates_start = 1
for doc_id in [100, 101, 102, 103]:
    ProductionService.add_document_to_production(
        production_id=production.id,
        evidence_id=doc_id,
        bates_start=f"ACME-{bates_start:05d}",
        added_by_user=user
    )
    bates_start += 5

# 7. Apply designations
ProductionService.apply_designation(
    production_id=production.id,
    document_ids=[105],  # The privileged document
    designation='CONFIDENTIAL - ATTORNEY-CLIENT PRIVILEGED',
    applied_by_user=user
)

# 8. Generate load file for production
load_file = ProductionService.export_production_load_file(
    production_id=production.id,
    format='csv'
)

# 9. Update discovery request status
DiscoveryService.update_discovery_request(
    request_id=request.id,
    request_data={'status': 'responded'},
    updated_by_user=user
)

# 10. Get discovery statistics
stats = DiscoveryService.get_discovery_stats(case_id=1)
print(f"Total requests: {stats['total_requests']}")
print(f"Pending: {stats['pending']}")
print(f"Responded: {stats['responded']}")
```

### Litigation Hold Workflow

```python
from services.ediscovery_service import LitigationHoldService
from services.compliance_service import HoldEvidenceLinkService

# 1. Create litigation hold
hold = LitigationHoldService.create_litigation_hold(
    case_id=1,
    hold_data={
        'hold_name': 'Commencement of Litigation Hold - Case 123',
        'initiating_event': 'Notice of litigation filed',
        'hold_scope': 'All documents related to Product X from 2023-01-01 to present',
        'affected_systems': json.dumps(['Email (Exchange)', 'File Shares (SharePoint)', 'Teams']),
        'retention_instructions': 'Preserve all evidence in original form'
    },
    issued_by_user=user
)

# 2. Add custodians
custodians = [
    {
        'name': 'John Smith',
        'title': 'Product Manager',
        'department': 'Product',
        'email': 'john.smith@company.com',
        'email_account': 'john.smith@company.com',
        'phone': '555-1234',
        'file_locations': json.dumps([
            '\\\\server\shares\product_team',
            'C:\Users\jsmith\Documents'
        ])
    },
    {
        'name': 'Jane Doe',
        'title': 'Director of Engineering',
        'department': 'Engineering',
        'email': 'jane.doe@company.com',
        'email_account': 'jane.doe@company.com',
        'phone': '555-5678'
    }
]

for cust_data in custodians:
    custodian = LitigationHoldService.add_custodian_to_hold(
        hold_id=hold.id,
        custodian_data=cust_data,
        added_by_user=user
    )

# 3. Send hold notices to custodians
hold_notice_text = """
You are required to immediately place a legal hold on all documents
and communications related to Product X...
"""

for custodian in hold.custodies:
    notice = LitigationHoldService.send_hold_notice(
        custodian_id=custodian.id,
        hold_id=hold.id,
        notice_text=hold_notice_text,
        sent_by_user=user
    )

# 4. Link evidence items to hold
evidence_ids = [100, 101, 102, 103]
HoldEvidenceLinkService.link_evidence_to_hold(
    hold_id=hold.id,
    evidence_ids=evidence_ids,
    preservation_method='snapshot'
)

# 5. Record custodian acknowledgments
for custodian in hold.custodies:
    LitigationHoldService.acknowledge_hold(custodian.id)

# 6. Monitor hold compliance
for custodian in hold.custodies:
    LitigationHoldService.certify_compliance(custodian.id)

# 7. Get hold status report
status = LitigationHoldService.get_hold_status(hold.id)
print(f"Total custodians: {status['total_custodians']}")
print(f"Acknowledged: {status['acknowledged']}")
print(f"Compliant: {status['compliant']}")
```

### Document Processing Workflow

```python
from services.document_processing_service import (
    ProcessingTaskService, OCRService, TranscriptionService,
    RedactionService, ComplianceReviewService
)

# 1. Create OCR task for image-based document
ocr_task = ProcessingTaskService.create_processing_task(
    evidence_id=100,
    case_id=1,
    task_type='ocr',
    created_by_user=user,
    parameters={'language': 'en', 'engine': 'tesseract'},
    priority='high'
)

# 2. Process OCR result
ocr_result = OCRService.process_ocr_result(
    evidence_id=100,
    task_id=ocr_task.id,
    extracted_text='The extracted text from the image...',
    confidence_score=0.92,
    pages_processed=5
)

# 3. Create transcription task
transcription_task = ProcessingTaskService.create_processing_task(
    evidence_id=200,
    case_id=1,
    task_type='transcription',
    created_by_user=user,
    parameters={'model': 'whisper-v2', 'language': 'en'},
    priority='normal'
)

# 4. Process transcription
transcript = TranscriptionService.create_transcription_result(
    evidence_id=200,
    task_id=transcription_task.id,
    transcript_data={
        'full_transcript': 'The transcribed audio...',
        'duration_seconds': 3600,
        'confidence': 0.88,
        'language': 'en',
        'speakers': [{'name': 'John', 'id': 'Speaker1'}]
    },
    created_by_user=user
)

# 5. Flag transcription for review
TranscriptionService.flag_for_review(
    transcript.id,
    'Please review pronunciation of technical terms'
)

# 6. Approve transcription after review
TranscriptionService.approve_transcription(
    transcript.id,
    user,
    corrected_text='Corrected transcription text...'
)

# 7. Create compliance review
review = ComplianceReviewService.create_compliance_review(
    evidence_id=100,
    case_id=1,
    review_data={
        'review_type': 'ocr_quality',
        'findings': 'OCR quality is good with minor errors',
        'accuracy_score': 92,
        'completeness_score': 95,
        'compliance_score': 90,
        'has_ocr_errors': False,
        'requires_reprocessing': False
    },
    reviewed_by_user=user
)

# 8. Get compliance summary
summary = ComplianceReviewService.get_case_compliance_summary(case_id=1)
print(f"Average accuracy: {summary['average_accuracy']:.1f}%")
print(f"Average compliance: {summary['average_compliance']:.1f}%")
```

## Database Integration

All models integrate with Flask-SQLAlchemy ORM. To use:

1. **Initialize database:**

```python
from auth.models import db
db.create_all()
```

2. **Query examples:**

```python
# Find all discovery requests for a case
requests = DiscoveryRequest.query.filter_by(case_id=1).all()

# Find overdue obligations
overdue = ComplianceObligation.query.filter(
    ComplianceObligation.deadline < datetime.utcnow(),
    ComplianceObligation.status != 'completed'
).all()

# Find production sets by party
productions = ProductionSet.query.filter_by(
    case_id=1,
    produced_to_party='Plaintiff'
).all()
```

## Key Features

✅ **Complete Discovery Management** - Request tracking, response management, objections
✅ **Document Production** - Bates numbering, designations, load file generation
✅ **Privilege Protection** - Privilege logs, privilege claims documentation
✅ **Litigation Holds** - Hold creation, custodian management, notice distribution
✅ **Document Processing** - OCR, transcription, entity extraction, analysis
✅ **Redaction Management** - Automated and manual redactions with approval workflow
✅ **Quality Assurance** - Compliance reviews, accuracy scoring
✅ **Compliance Tracking** - Obligations, deadlines, risk assessment
✅ **Audit Trail** - Complete audit logging of all activities
✅ **Chain of Custody** - Affidavits, certifications, documentation
✅ **Reporting** - Automated compliance reports
✅ **Record Retention** - Retention policies and destruction tracking

## Future Enhancements

- Integration with professional e-discovery ESI platforms
- Machine learning for privilege detection
- Advanced analytics and reporting dashboards
- Integration with court filing systems
- Blockchain-based chain of custody verification
- Advanced search and analytics
- Integration with video/audio processing APIs
- Multi-jurisdiction compliance rules engine
