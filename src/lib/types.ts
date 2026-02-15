// ============================================================================
// Civics Hierarchy Platform – Court-Defensible Type System
// ============================================================================

// ---------------------------------------------------------------------------
// Enums & Union Types
// ---------------------------------------------------------------------------

export type AuthorityLevel = 'federal' | 'state' | 'territory' | 'local'

/** Ordered hierarchy for display and comparison */
export const AUTHORITY_HIERARCHY: readonly AuthorityLevel[] = [
  'federal',
  'state',
  'territory',
  'local',
] as const

export type DocumentType =
  | 'constitution'
  | 'amendment'
  | 'treaty'
  | 'statute'
  | 'regulation'
  | 'code'
  | 'ordinance'
  | 'organic-act'
  | 'executive-order'

/** Ordered hierarchy of document authority within a level */
export const DOCUMENT_TYPE_HIERARCHY: readonly DocumentType[] = [
  'constitution',
  'amendment',
  'treaty',
  'statute',
  'regulation',
  'code',
  'executive-order',
  'ordinance',
  'organic-act',
] as const

export type VerificationStatus = 'unverified' | 'verified' | 'official'

export type UserRole = 'reader' | 'contributor' | 'curator' | 'admin'

export type CitationStyle =
  | 'bluebook'
  | 'alwd'
  | 'apa'
  | 'mla'
  | 'chicago'
  | 'plain'
  | 'court-filing'
  | 'bibtex'
  | 'json'

export type AuditAction =
  | 'view'
  | 'create'
  | 'update'
  | 'delete'
  | 'approve'
  | 'reject'
  | 'verify'
  | 'export'
  | 'submit'
  | 'flag'
  | 'acknowledge'

export type EntityType =
  | 'application'
  | 'document'
  | 'section'
  | 'bookmark'
  | 'citation'
  | 'note'
  | 'submission'
  | 'disclaimer'
  | 'collection'
  | 'source-registry'
  | 'version-snapshot'

export type TreatyStatus = 'pending' | 'ratified' | 'terminated' | 'suspended' | 'signed-not-ratified'

export type PreemptionType = 'express' | 'conflict' | 'field' | 'none'

export type SeparationOfPowersCategory = 'legislative' | 'executive' | 'judicial'

// ---------------------------------------------------------------------------
// Hash-based routing
// ---------------------------------------------------------------------------

export type RouteId =
  | 'home'
  | 'supreme-law'
  | 'my-jurisdiction'
  | 'local'
  | 'search'
  | 'treaties'
  | 'analyzer'
  | 'learn'
  | 'citations'
  | 'section'
  | 'document'
  | 'compare'
  | 'case-law'
  | 'federal-register'
  | 'legal-resources'
  | 'admin-observability'

export interface RouteState {
  route: RouteId
  params: Record<string, string>
}

// ---------------------------------------------------------------------------
// Core Entities
// ---------------------------------------------------------------------------

export interface Jurisdiction {
  id: string
  name: string
  type: 'federal' | 'state' | 'territory' | 'county' | 'municipality'
  abbreviation?: string
  parentId?: string
  fipsCode?: string
}

export interface SourceRegistryEntry {
  id: string
  officialUrl: string
  publisher: string
  retrievalMethod: 'manual' | 'api' | 'scrape' | 'certified-copy'
  retrievedAt: string
  checksum?: string
  isOfficialSource: boolean
  mirrorUrl?: string
  curatorJustification?: string
  lastVerified?: string
  contentHash?: string
}

export interface VersionSnapshot {
  id: string
  documentId: string
  effectiveStart: string
  effectiveEnd?: string
  content: string
  sourceRegistryId: string
  checksum: string
  createdAt: string
  createdBy: string
  notes?: string
  supersededBy?: string
}

export interface Document {
  id: string
  title: string
  type: DocumentType
  authorityLevel: AuthorityLevel
  jurisdictionId: string
  effectiveDate?: string
  supersededDate?: string
  verificationStatus: VerificationStatus
  sourceUrl?: string
  lastChecked?: string
  description?: string
  sourceRegistryIds?: string[]
  currentVersionId?: string
  hierarchyPosition?: number
  retrievalMetadata?: {
    retrievedAt: string
    sourceUrl: string
    checksum: string
    parsingMethod: string
  }
}

export interface Section {
  id: string
  documentId: string
  title: string
  number: string
  text: string
  canonicalCitation: string
  parentSectionId?: string
  order: number
  effectiveDate?: string
  amendedDate?: string
  topicTags?: string[]
  crossReferenceIds?: string[]
}

export interface CrossReference {
  id: string
  fromSectionId: string
  toSectionId: string
  relationshipType: 'supersedes' | 'implements' | 'references' | 'conflicts' | 'preempts' | 'incorporates' | 'amends'
  notes?: string
  bidirectional?: boolean
}

export interface TopicTag {
  id: string
  name: string
  category: 'constitutional' | 'legal-topic' | 'practice-area' | 'case-type' | 'jurisdiction' | 'custom'
  description?: string
  usageCount: number
}

// ---------------------------------------------------------------------------
// Treaty-Specific
// ---------------------------------------------------------------------------

export interface TreatyMetadata {
  id: string
  documentId: string
  ratificationDate?: string
  status: TreatyStatus
  implementingLegislation?: string[]
  signatories: string[]
  reservations?: string
  selfExecuting?: boolean
  senateTreatyDocNumber?: string
}

// ---------------------------------------------------------------------------
// Citation & Export
// ---------------------------------------------------------------------------

export interface Citation {
  id: string
  documentId: string
  sectionId?: string
  canonical: string
  url?: string
  format: 'bluebook' | 'plain' | 'url'
}

export interface SavedCitation {
  id: string
  sectionId: string
  documentId: string
  jurisdictionId: string
  title: string
  canonicalCitation: string
  tags: string[]
  notes: string
  collections: string[]
  createdAt: string
  updatedAt: string
  accessCount: number
  lastAccessed?: string
  isFavorite: boolean
}

export interface CitationCollection {
  id: string
  name: string
  description: string
  citationIds: string[]
  color: string
  createdAt: string
  updatedAt: string
  isPublic: boolean
}

// ---------------------------------------------------------------------------
// User & Interaction
// ---------------------------------------------------------------------------

export interface UserNote {
  id: string
  sectionId: string
  content: string
  isPrivate: boolean
  createdAt: string
  updatedAt: string
}

export interface Bookmark {
  id: string
  sectionId: string
  documentId: string
  createdAt: string
  note?: string
}

export interface UserSettings {
  selectedJurisdictionId: string
  secondaryJurisdictionIds: string[]
  offlinePacks: string[]
  analyticsOptIn: boolean
  fontSize: 'small' | 'medium' | 'large'
  preferredCitationStyle?: CitationStyle
}

// ---------------------------------------------------------------------------
// Analyzer
// ---------------------------------------------------------------------------

export interface AnalyzerSession {
  id: string
  createdAt: string
  title: string
  questions: Record<string, string>
  report?: AnalyzerReport
}

export interface AnalyzerReport {
  relevantProvisions: {
    sectionId: string
    citation: string
    snippet: string
    authorityLevel: AuthorityLevel
    relevanceReason?: string
  }[]
  preemptionCategories: string[]
  keyQuestions: string[]
  nextSteps: string[]
  disclaimer: string
  generatedAt?: string
}

// ---------------------------------------------------------------------------
// Submissions & Moderation
// ---------------------------------------------------------------------------

export interface LocalSubmission {
  id: string
  documentTitle: string
  jurisdictionId: string
  sourceUrl: string
  uploadedFile?: string
  submittedBy: string
  submittedAt: string
  verificationStatus: VerificationStatus
  curatorNotes?: string
  reviewedAt?: string
  reviewedBy?: string
}

// ---------------------------------------------------------------------------
// Provenance
// ---------------------------------------------------------------------------

export interface ProvenancePanel {
  sourceRegistryEntry: SourceRegistryEntry
  versionSnapshot?: VersionSnapshot
  retrievalMetadata: {
    retrievedAt: string
    sourceUrl: string
    checksum: string
    parsingMethod: string
  }
  verificationChain: {
    verifiedBy: string
    verifiedAt: string
    method: string
    notes: string
  }[]
}

// ---------------------------------------------------------------------------
// Version & Update Strategy
// ---------------------------------------------------------------------------

export interface UpdateStrategy {
  documentId: string
  refreshSchedule: string
  lastSuccessfulRefresh: string
  lastAttemptedRefresh: string
  failureCount: number
  isStale: boolean
  staleWarningThreshold: number
  fallbackSnapshotId?: string
}

// ---------------------------------------------------------------------------
// Supreme Overlay / Compare View
// ---------------------------------------------------------------------------

export interface CompareView {
  leftSection: Section
  rightSection: Section
  similarities: string[]
  differences: string[]
  neutralSummary: string
  disclaimerText: string
}

export interface OverlayMapping {
  id: string
  federalSectionId: string
  stateSectionId: string
  topicAlignment: string
  comparisonNotes: string
}

// ---------------------------------------------------------------------------
// Education
// ---------------------------------------------------------------------------

export interface LearningModule {
  id: string
  title: string
  category: string
  description: string
  content: string
  relatedSectionIds: string[]
  prerequisites?: string[]
  order: number
}

export interface ExplanationArticle {
  id: string
  title: string
  content: string
  relatedSectionIds: string[]
  citations: string[]
  authorRole: UserRole
  createdAt: string
  updatedAt: string
  reviewedBy?: string
  isPublished: boolean
}

// ---------------------------------------------------------------------------
// Audit & RBAC
// ---------------------------------------------------------------------------

export interface AuditLogEntry {
  id: string
  userId: string
  userRole: UserRole
  action: AuditAction
  entityType: EntityType
  entityId: string
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface RolePermissions {
  role: UserRole
  canRead: boolean
  canCreate: boolean
  canEdit: boolean
  canDelete: boolean
  canApprove: boolean
  canExport: boolean
  canManageUsers: boolean
}

export const ROLE_PERMISSIONS: Record<UserRole, RolePermissions> = {
  reader: {
    role: 'reader',
    canRead: true,
    canCreate: false,
    canEdit: false,
    canDelete: false,
    canApprove: false,
    canExport: true,
    canManageUsers: false,
  },
  contributor: {
    role: 'contributor',
    canRead: true,
    canCreate: true,
    canEdit: false,
    canDelete: false,
    canApprove: false,
    canExport: true,
    canManageUsers: false,
  },
  curator: {
    role: 'curator',
    canRead: true,
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canApprove: true,
    canExport: true,
    canManageUsers: false,
  },
  admin: {
    role: 'admin',
    canRead: true,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canApprove: true,
    canExport: true,
    canManageUsers: true,
  },
}

// ---------------------------------------------------------------------------
// Content Safeguards
// ---------------------------------------------------------------------------

export interface ContentSafeguardResult {
  isClean: boolean
  violations: string[]
  sanitizedContent?: string
}

// ---------------------------------------------------------------------------
// Hierarchy Ladder
// ---------------------------------------------------------------------------

export interface HierarchyNode {
  level: number
  label: string
  authorityLevel: AuthorityLevel
  documentType?: DocumentType
  documentId?: string
  sectionCount: number
  children: HierarchyNode[]
  isActive?: boolean
  effectiveDate?: string
}

// ---------------------------------------------------------------------------
// Smart Tags & Batch Analysis
// ---------------------------------------------------------------------------

export interface SmartTagSuggestion {
  tagName: string
  confidence: 'high' | 'medium' | 'low'
  reason: string
  category: TopicTag['category']
  autoApplied: boolean
}

export interface BatchAnalysisJob {
  id: string
  citationIds: string[]
  startedAt: string
  completedAt?: string
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
  progress: {
    total: number
    completed: number
    failed: number
    skipped: number
  }
  results: BatchAnalysisResult[]
  options: {
    autoApplyHighConfidence: boolean
    skipThreshold: number
    analysisMode: 'deep' | 'quick'
  }
}

export interface BatchAnalysisResult {
  citationId: string
  status: 'analyzing' | 'completed' | 'failed' | 'skipped'
  suggestions: SmartTagSuggestion[]
  error?: string
  processingTime: number
  legalConcepts: string[]
  practiceAreas: string[]
  constitutionalIssues: string[]
}
