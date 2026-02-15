export type UserRole = 'Admin' | 'Analyst' | 'Reviewer' | 'ReadOnly'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  avatarUrl?: string
}

export interface Source {
  id: string
  name: string
  baseUrl: string
  description: string
  crawlRules: {
    maxDepth: number
    rateLimit: number
    allowedDomains: string[]
    respectQueueIt?: boolean
    respectAgeGate?: boolean
  }
  status: 'active' | 'paused' | 'disabled'
  createdAt: string
  lastRunAt?: string
}

export interface IngestionRun {
  id: string
  sourceId: string
  startedAt: string
  endedAt?: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused'
  discovered: number
  downloaded: number
  processed: number
  errors: number
  throttleInfo?: {
    active: boolean
    resumeAt?: string
    reason?: string
  }
  notes?: string
}

export interface Document {
  id: string
  sourceId: string
  runId: string
  title: string
  url: string
  sha256: string
  fileSize: number
  mimeType: string
  downloadedAt: string
  pageCount: number
  status: 'downloaded' | 'extracting' | 'extracted' | 'ocr' | 'indexed' | 'error'
  ocrUsed: boolean
  language?: string
  confidence: number
}

export interface Page {
  id: string
  documentId: string
  pageNo: number
  text: string
  ocrUsed: boolean
  ocrConfidence?: number
  imagePath?: string
}

export interface TextChunk {
  id: string
  documentId: string
  pageRange: [number, number]
  text: string
  embedding?: number[]
}

export type EntityType = 'person' | 'organization' | 'location' | 'date' | 'identifier'

export interface Entity {
  id: string
  type: EntityType
  canonicalName: string
  aliases: string[]
  confidence: number
  mentionCount: number
  disambiguationStatus: 'auto' | 'needs-review' | 'reviewed'
  notes?: string
  reviewedBy?: string
  reviewedAt?: string
}

export interface Mention {
  id: string
  entityId: string
  chunkId: string
  documentId: string
  snippet: string
  offset: [number, number]
  confidence: number
  context: string
}

export type RelationshipType = 'co-occurs' | 'referenced-in' | 'associated-with' | 'same-as'

export interface Relationship {
  id: string
  entityAId: string
  entityBId: string
  type: RelationshipType
  confidence: number
  evidenceChunkIds: string[]
  reviewStatus: 'auto' | 'needs-review' | 'approved'
  reviewedBy?: string
  reviewedAt?: string
  notes?: string
}

export interface AuditEvent {
  id: string
  timestamp: string
  actor: string
  action: string
  objectType: string
  objectId: string
  details: Record<string, unknown>
  ipAddress?: string
}

export interface SearchFilters {
  sourceId?: string
  dateRange?: [string, string]
  ocrUsed?: boolean
  entityTypes?: EntityType[]
  minConfidence?: number
  status?: Document['status'][]
}

export interface SearchResult {
  documentId: string
  title: string
  snippet: string
  highlights: Array<{ text: string; offset: [number, number] }>
  pageNo: number
  confidence: number
  relevanceScore: number
}

export interface GraphNode {
  id: string
  label: string
  type: EntityType
  mentionCount: number
  confidence: number
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: RelationshipType
  confidence: number
  evidenceCount: number
}

export type ScriptTrigger = 'post-download' | 'post-extraction' | 'post-chunking' | 'post-index' | 'post-entity' | 'manual'
export type ScriptCategory = 'pattern-scanner' | 'entity-enrichment' | 'timeline-builder' | 'similarity-linker' | 'relationship-engine' | 'summarization' | 'export-generator'
export type ScriptExecutionMode = 'automatic' | 'manual-only'

export interface AnalysisScript {
  id: string
  name: string
  category: ScriptCategory
  version: string
  versionHash: string
  description: string
  allowedRoles: UserRole[]
  triggers: ScriptTrigger[]
  executionMode: ScriptExecutionMode
  inputs: {
    required: string[]
    optional: string[]
  }
  outputs: string[]
  requiredPermissions: string[]
  config: Record<string, unknown>
  enabled: boolean
  createdAt: string
  updatedAt: string
  createdBy: string
}

export type ScriptRunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface ScriptRun {
  id: string
  scriptId: string
  scriptVersion: string
  startedAt: string
  endedAt?: string
  status: ScriptRunStatus
  config: Record<string, unknown>
  configHash: string
  inputHashes: Record<string, string>
  outputHashes: Record<string, string>
  documentsProcessed: number
  findingsGenerated: number
  errors: Array<{
    timestamp: string
    documentId?: string
    message: string
    stack?: string
  }>
  metrics: {
    avgTimePerDocument?: number
    totalChunksProcessed?: number
  }
  triggeredBy: string
  canReplay: boolean
}

export type FindingSeverity = 'info' | 'low' | 'medium' | 'high'

export interface Finding {
  id: string
  scriptRunId: string
  documentId: string
  chunkId?: string
  pageNo?: number
  category: string
  pattern?: string
  snippet: string
  offset: [number, number]
  severity: FindingSeverity
  confidence: number
  context: string
  metadata: Record<string, unknown>
  reviewStatus: 'pending' | 'confirmed' | 'false-positive'
  reviewedBy?: string
  reviewedAt?: string
  createdAt: string
}

export interface TimelineEvent {
  id: string
  scriptRunId: string
  entityId?: string
  documentId: string
  chunkId: string
  normalizedDate: string
  dateConfidence: number
  rawDateText: string
  eventDescription: string
  snippet: string
  pageNo?: number
  metadata: Record<string, unknown>
  createdAt: string
}

export type ProposalType = 'entity-merge' | 'entity-split' | 'alias-addition' | 'relationship-upgrade'
export type ProposalStatus = 'pending' | 'approved' | 'rejected'

export interface Proposal {
  id: string
  scriptRunId: string
  type: ProposalType
  status: ProposalStatus
  confidence: number
  evidenceSnippets: Array<{
    documentId: string
    chunkId: string
    snippet: string
    pageNo?: number
  }>
  proposedChange: Record<string, unknown>
  justification: string
  reviewedBy?: string
  reviewedAt?: string
  reviewNotes?: string
  reversible: boolean
  reverseActionId?: string
  createdAt: string
}

export interface DocumentSimilarity {
  id: string
  scriptRunId: string
  documentAId: string
  documentBId: string
  similarityScore: number
  matchedConcepts: string[]
  snippetPairs: Array<{
    chunkAId: string
    chunkBId: string
    snippetA: string
    snippetB: string
  }>
  createdAt: string
}

export interface DocumentAnalysis {
  documentId: string
  findings: Finding[]
  timelineEvents: TimelineEvent[]
  similarities: DocumentSimilarity[]
  graphEdges: Relationship[]
  summary?: {
    scriptRunId: string
    abstract: string
    topics: string[]
    keyEntities: string[]
    dateRange?: [string, string]
    documentType?: string
    keyPassages: Array<{
      snippet: string
      pageNo: number
      reason: string
    }>
    isProbabilistic: boolean
  }
}

export interface QualityMetrics {
  documentId: string
  pageNo?: number
  overallScore: number
  textDensity: number
  ocrConfidenceProxy: number
  characterErrorRate: number
  layoutQuality: number
  languageConsistency: number
  readabilityScore: number
  flaggedForReview: boolean
  reprocessRecommended: boolean
  computedAt: string
  scriptRunId: string
}

export interface DuplicateGroup {
  id: string
  canonicalDocumentId: string
  duplicateDocumentIds: string[]
  similarityScore: number
  matchType: 'exact-hash' | 'near-duplicate' | 'partial-match'
  detectedAt: string
  preservedMetadata: Array<{
    documentId: string
    sourceUrl: string
    downloadedAt: string
    sha256: string
  }>
}

export interface StructuredExtraction {
  id: string
  documentId: string
  pageNo: number
  extractionType: 'table' | 'form' | 'list' | 'header'
  structure: Record<string, unknown>
  coordinates: Array<{
    field: string
    x: number
    y: number
    width: number
    height: number
    pageIndex: number
  }>
  confidence: number
  scriptRunId: string
  createdAt: string
}

export interface TemporalEntity {
  id: string
  rawText: string
  normalizedDate?: string
  uncertainty: 'certain' | 'year-only' | 'month-only' | 'approximate' | 'range' | 'unknown'
  confidence: number
  evidenceChunkId: string
  documentId: string
  pageNo?: number
  metadata: {
    yearKnown: boolean
    monthKnown: boolean
    dayKnown: boolean
    rangeStart?: string
    rangeEnd?: string
  }
}

export interface LanguageDetection {
  documentId: string
  chunkId?: string
  detectedLanguage: string
  confidence: number
  scriptCode: string
  translationAvailable: boolean
  translationId?: string
}

export interface Translation {
  id: string
  sourceChunkId: string
  sourceLanguage: string
  targetLanguage: string
  translatedText: string
  originalText: string
  confidence: number
  modelUsed: string
  isMachineGenerated: true
  translatedAt: string
}

export type AnnotationType = 'evidence-quote' | 'interpretation' | 'hypothesis' | 'to-verify'

export interface Annotation {
  id: string
  documentId: string
  chunkId: string
  type: AnnotationType
  content: string
  citations: Array<{
    documentId: string
    chunkId: string
    snippet: string
    pageNo?: number
    required: boolean
  }>
  createdBy: string
  createdAt: string
  updatedAt: string
  tags: string[]
  linkedAnnotations: string[]
}

export type ReviewQueueType = 
  | 'low-ocr-quality' 
  | 'ambiguous-entities' 
  | 'relationship-proposals' 
  | 'sensitive-content-flags' 
  | 'export-requests'
  | 'translation-review'
  | 'structured-extraction-review'

export type ReviewQueueStatus = 'pending' | 'in-progress' | 'completed' | 'escalated'

export interface ReviewQueueItem {
  id: string
  queueType: ReviewQueueType
  objectType: string
  objectId: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: ReviewQueueStatus
  assignedTo?: string
  dueDate?: string
  createdAt: string
  completedAt?: string
  reviewNotes?: string
  metadata: Record<string, unknown>
}

export interface RelationshipExplainer {
  relationshipId: string
  explanation: string
  evidenceSnippets: Array<{
    chunkId: string
    snippet: string
    documentId: string
    pageNo?: number
    highlightedTerms: string[]
  }>
  computationMethod: string
  confidence: number
  neutralLanguageVerified: boolean
}
