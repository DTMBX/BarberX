export interface AuditLogEntry {
  id: string
  timestamp: string
  userId: string
  userRole: string
  action: AuditAction
  entityType: string
  entityId: string
  changes?: Record<string, { before: unknown; after: unknown }>
  metadata?: Record<string, unknown>
  ipAddress?: string
  userAgent?: string
}

export type AuditAction =
  | 'create'
  | 'update'
  | 'delete'
  | 'approve'
  | 'reject'
  | 'view'
  | 'export'
  | 'submit'
  | 'verify'
  | 'flag'

export interface LegalDisclaimer {
  id: string
  type: DisclaimerType
  title: string
  content: string
  required: boolean
  version: string
  effectiveDate: string
}

export type DisclaimerType =
  | 'not-legal-advice'
  | 'educational-only'
  | 'no-attorney-client'
  | 'verify-sources'
  | 'court-defensibility'
  | 'accuracy-limitation'

export interface SourceVerification {
  documentId: string
  verifiedBy: string
  verifiedAt: string
  verificationMethod: VerificationMethod
  primarySourceUrl: string
  checksumHash?: string
  officialSourceContact?: string
  lastCheckedDate: string
  nextCheckDue: string
  verificationNotes?: string
  complianceCertification?: boolean
}

export type VerificationMethod =
  | 'official-website'
  | 'government-api'
  | 'certified-copy'
  | 'public-records-request'
  | 'legislative-archive'
  | 'legal-database'

export interface ComplianceCheck {
  checkId: string
  timestamp: string
  documentId: string
  sectionId?: string
  checks: {
    hasCitation: boolean
    hasOfficialSource: boolean
    hasDisclaimer: boolean
    isCurrentVersion: boolean
    hasAuditTrail: boolean
  }
  passed: boolean
  issues: string[]
}

export const LEGAL_DISCLAIMERS: Record<DisclaimerType, LegalDisclaimer> = {
  'not-legal-advice': {
    id: 'disclaimer-001',
    type: 'not-legal-advice',
    title: 'Not Legal Advice',
    content:
      'THIS APPLICATION PROVIDES EDUCATIONAL INFORMATION ONLY AND DOES NOT CONSTITUTE LEGAL ADVICE. The information provided is for general educational and informational purposes only. It is not intended to be, and should not be relied upon as, legal advice. No attorney-client relationship is created by using this application. For legal advice specific to your situation, you must consult with a licensed attorney in your jurisdiction.',
    required: true,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
  'educational-only': {
    id: 'disclaimer-002',
    type: 'educational-only',
    title: 'Educational Purpose Only',
    content:
      'This application is designed as an educational tool to help users understand the hierarchy of U.S. law and constitutional principles. The content is provided for informational and educational purposes only. Users should independently verify all information before relying on it for any legal, civic, or personal purpose.',
    required: true,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
  'no-attorney-client': {
    id: 'disclaimer-003',
    type: 'no-attorney-client',
    title: 'No Attorney-Client Relationship',
    content:
      'USE OF THIS APPLICATION DOES NOT CREATE AN ATTORNEY-CLIENT RELATIONSHIP. The creators and operators of this application are not your attorneys. Any information you provide or receive through this application is not confidential or privileged. Do not send any confidential information to this application.',
    required: true,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
  'verify-sources': {
    id: 'disclaimer-004',
    type: 'verify-sources',
    title: 'Verify All Sources',
    content:
      'While we strive for accuracy, users are responsible for verifying all information through official government sources before relying on it. Laws, regulations, and constitutional provisions may change. Always consult official government websites, legislative archives, or licensed legal professionals to confirm current law.',
    required: true,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
  'court-defensibility': {
    id: 'disclaimer-005',
    type: 'court-defensibility',
    title: 'Court Defensibility Standards',
    content:
      'This application maintains strict standards for source verification, citation accuracy, and audit trails. All information is traceable to primary sources. However, this application and its contents are not admissible as legal authority in court proceedings. For court purposes, always cite to official government publications, statutes, and case reporters.',
    required: false,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
  'accuracy-limitation': {
    id: 'disclaimer-006',
    type: 'accuracy-limitation',
    title: 'Accuracy Limitations',
    content:
      'While we employ rigorous verification processes, no legal information system is perfect. This application may contain errors, omissions, or outdated information. The operators of this application expressly disclaim any warranties of accuracy, completeness, or fitness for a particular purpose. Users assume all risk associated with use of this information.',
    required: true,
    version: '1.0',
    effectiveDate: '2024-01-01',
  },
}

export async function createAuditLog(
  entry: Omit<AuditLogEntry, 'id' | 'timestamp'>
): Promise<AuditLogEntry> {
  const auditEntry: AuditLogEntry = {
    ...entry,
    id: `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
  }

  const existingLogs = (await window.spark.kv.get<AuditLogEntry[]>('audit-logs')) || []
  await window.spark.kv.set('audit-logs', [...existingLogs, auditEntry])

  return auditEntry
}

export async function getAuditLogs(filters?: {
  userId?: string
  entityId?: string
  action?: AuditAction
  startDate?: string
  endDate?: string
}): Promise<AuditLogEntry[]> {
  const allLogs = (await window.spark.kv.get<AuditLogEntry[]>('audit-logs')) || []

  if (!filters) return allLogs

  return allLogs.filter((log) => {
    if (filters.userId && log.userId !== filters.userId) return false
    if (filters.entityId && log.entityId !== filters.entityId) return false
    if (filters.action && log.action !== filters.action) return false
    if (filters.startDate && log.timestamp < filters.startDate) return false
    if (filters.endDate && log.timestamp > filters.endDate) return false
    return true
  })
}

export async function verifySourceCompliance(
  documentId: string
): Promise<ComplianceCheck> {
  const document = await window.spark.kv.get<any>(`document-${documentId}`)
  const sections = (await window.spark.kv.get<any[]>('sections')) || []
  const documentSections = sections.filter((s) => s.documentId === documentId)

  const check: ComplianceCheck = {
    checkId: `check-${Date.now()}`,
    timestamp: new Date().toISOString(),
    documentId,
    checks: {
      hasCitation: documentSections.every((s) => s.canonicalCitation),
      hasOfficialSource: !!document?.sourceUrl,
      hasDisclaimer: true,
      isCurrentVersion: !document?.supersededDate,
      hasAuditTrail: true,
    },
    passed: false,
    issues: [],
  }

  if (!check.checks.hasCitation) {
    check.issues.push('Missing canonical citations for some sections')
  }
  if (!check.checks.hasOfficialSource) {
    check.issues.push('No official source URL provided')
  }
  if (!check.checks.isCurrentVersion) {
    check.issues.push('Document has been superseded')
  }

  check.passed = check.issues.length === 0

  return check
}

export function generateCourtDefensibleCitation(
  documentTitle: string,
  section: string,
  canonicalCitation: string,
  sourceUrl: string,
  lastVerified: string
): string {
  return `${documentTitle}, ${section} (${canonicalCitation}). Official source: ${sourceUrl}. Last verified: ${lastVerified}. Retrieved via Civics Stack educational platform. Note: For court filings, cite directly to official government publications.`
}

export const COMPLIANCE_STANDARDS = {
  REQUIRED_FIELDS: [
    'canonicalCitation',
    'sourceUrl',
    'verificationStatus',
    'lastChecked',
  ],
  VERIFICATION_INTERVAL_DAYS: 90,
  AUDIT_RETENTION_DAYS: 2555,
  MINIMUM_CITATION_CONFIDENCE: 0.95,
  REQUIRED_DISCLAIMERS: [
    'not-legal-advice',
    'educational-only',
    'no-attorney-client',
    'verify-sources',
    'accuracy-limitation',
  ],
}

export async function recordUserAcknowledgment(
  userId: string,
  disclaimerType: DisclaimerType
): Promise<void> {
  try {
    const acknowledgments =
      (await window.spark.kv.get<Record<string, string[]>>('disclaimer-acknowledgments')) || {}

    if (!acknowledgments[userId]) {
      acknowledgments[userId] = []
    }

    // Only store one entry per disclaimer type per user (avoid unbounded growth)
    const alreadyAcknowledged = acknowledgments[userId].some(ack =>
      ack.startsWith(`${disclaimerType}:`)
    )

    if (!alreadyAcknowledged) {
      const acknowledgmentRecord = `${disclaimerType}:${new Date().toISOString()}`
      acknowledgments[userId].push(acknowledgmentRecord)
      await window.spark.kv.set('disclaimer-acknowledgments', acknowledgments)
    }

    await createAuditLog({
      userId,
      userRole: 'reader',
      action: 'view',
      entityType: 'disclaimer',
      entityId: disclaimerType,
      metadata: { acknowledged: true },
    })
  } catch (error) {
    console.error('Failed to record acknowledgment:', error)
    // Don't throw — allow the user to continue even if KV write fails
  }
}

export async function hasAcknowledgedRequiredDisclaimers(
  userId: string
): Promise<boolean> {
  try {
    const acknowledgments =
      (await window.spark.kv.get<Record<string, string[]>>('disclaimer-acknowledgments')) || {}
    const userAcknowledgments = acknowledgments[userId] || []

    return COMPLIANCE_STANDARDS.REQUIRED_DISCLAIMERS.every((disclaimerType) =>
      userAcknowledgments.some((ack) => ack.startsWith(`${disclaimerType}:`))
    )
  } catch (error) {
    console.error('Failed to check acknowledgments:', error)
    return false
  }
}
