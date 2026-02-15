export interface ObservabilityMetrics {
  ingestion: {
    throughput: number
    ocrRate: number
    parsingErrors: number
    queueDepth: number
    similarityJobRuntime: number
    searchLatency: number
  }
  timestamp: string
  correlationId: string
}

export interface MetricsHistoryPoint {
  timestamp: string
  value: number
  anomaly?: boolean
  severity?: 'info' | 'warning' | 'critical'
}

export interface StructuredLog {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warn' | 'error' | 'critical'
  correlationId: string
  userId?: string
  action: string
  component: string
  message: string
  metadata?: Record<string, unknown>
  stackTrace?: string
  traceChain?: string[]
}

export interface ProvenanceDiff {
  evidenceItemId: string
  parserVersionA: string
  parserVersionB: string
  structuralChanges: StructuralChange[]
  stringDifferences: StringDifference[]
  metadataShifts: MetadataShift[]
  generatedAt: string
  diffHash: string
}

export interface StructuralChange {
  type: 'added' | 'removed' | 'modified'
  path: string
  beforeValue?: unknown
  afterValue?: unknown
  impactScore: number
}

export interface StringDifference {
  field: string
  beforeValue: string
  afterValue: string
  editDistance: number
  charDiff: {
    type: 'insert' | 'delete' | 'replace'
    position: number
    value: string
  }[]
}

export interface MetadataShift {
  key: string
  beforeValue: unknown
  afterValue: unknown
  dataType: string
  semanticImpact: 'none' | 'low' | 'medium' | 'high'
}

export interface PolicyRule {
  id: string
  name: string
  type: 'source-restriction' | 'format-restriction' | 'rate-limit' | 'content-filter'
  enabled: boolean
  conditions: PolicyCondition[]
  actions: PolicyAction[]
  priority: number
  createdAt: string
  createdBy: string
  lastModified: string
}

export interface PolicyCondition {
  field: string
  operator: 'equals' | 'contains' | 'matches' | 'exceeds' | 'below'
  value: unknown
}

export interface PolicyAction {
  type: 'allow' | 'block' | 'warn' | 'throttle' | 'log'
  parameters?: Record<string, unknown>
}

export interface ComplianceReport {
  id: string
  runId: string
  generatedAt: string
  policies: PolicyRule[]
  results: ComplianceResult[]
  overallStatus: 'compliant' | 'violations' | 'warnings'
  manifestHash: string
}

export interface ComplianceResult {
  policyId: string
  policyName: string
  status: 'compliant' | 'violation' | 'warning'
  violations: PolicyViolation[]
  itemsChecked: number
  itemsPassed: number
  itemsFailed: number
}

export interface PolicyViolation {
  itemId: string
  itemType: string
  violationType: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface TamperEvidentEvent {
  id: string
  eventType: string
  timestamp: string
  userId: string
  action: string
  entityType: string
  entityId: string
  payload: Record<string, unknown>
  previousHash: string
  currentHash: string
  chainValid: boolean
}

export interface LedgerVerification {
  valid: boolean
  totalEvents: number
  verifiedEvents: number
  brokenLinks: number[]
  firstBreak?: number
  lastVerifiedEvent?: number
  verificationTime: number
}

export interface RetentionPolicy {
  id: string
  name: string
  targetType: 'artifacts' | 'logs' | 'versions' | 'audit-logs'
  retentionDays: number
  enabled: boolean
  gracePeriodDays: number
  archiveBeforeDelete: boolean
  archiveLocation?: string
}

export interface RetentionSimulation {
  policyId: string
  dryRun: boolean
  targetType: string
  itemsToDelete: RetentionItem[]
  totalCount: number
  totalSize: number
  oldestItem: string
  newestItem: string
  estimatedDuration: number
}

export interface RetentionItem {
  id: string
  type: string
  createdAt: string
  size: number
  reason: string
  dependencies?: string[]
  canDelete: boolean
  warnings?: string[]
}

export interface RoleSimulation {
  id: string
  adminUserId: string
  simulatedRole: string
  startedAt: string
  endedAt?: string
  actionsPerformed: string[]
  active: boolean
}

export interface ConfigurationVersion {
  id: string
  version: number
  createdAt: string
  createdBy: string
  configType: 'crawler' | 'search' | 'parsing' | 'security' | 'retention'
  configuration: Record<string, unknown>
  previousVersionId?: string
  changesSummary: string
  effectiveFor?: string[]
}

export interface ConfigurationDiff {
  versionA: ConfigurationVersion
  versionB: ConfigurationVersion
  changes: ConfigChange[]
  diffHash: string
}

export interface ConfigChange {
  path: string
  type: 'added' | 'removed' | 'modified'
  oldValue?: unknown
  newValue?: unknown
  impact: 'breaking' | 'major' | 'minor' | 'patch'
}

export interface ExportManifest {
  id: string
  exportedAt: string
  exportedBy: string
  toolVersion: string
  redactionMode: 'none' | 'partial' | 'full'
  sourceRestriction: string[]
  citationIncluded: boolean
  items: ExportItem[]
  checksums: Record<string, string>
  signatureHash: string
}

export interface ExportItem {
  itemId: string
  itemType: string
  hash: string
  timestamp: string
  auditTrailId?: string
}

export interface BackgroundJob {
  id: string
  type: 'ingestion' | 'parsing' | 'indexing' | 'similarity' | 'export' | 'cleanup'
  status: 'queued' | 'running' | 'retrying' | 'failed' | 'completed'
  priority: number
  createdAt: string
  startedAt?: string
  completedAt?: string
  retryCount: number
  maxRetries: number
  errorStack?: string
  progress: number
  estimatedCost?: number
  dependencies?: string[]
  result?: Record<string, unknown>
}

export interface SecurityHardeningStatus {
  tlsStatus: TLSStatus
  secretStorageHealth: SecretHealth
  tokenExpiryStatus: TokenStatus
  rateLimitStats: RateLimitStats
  blockedRequests: BlockedRequest[]
}

export interface TLSStatus {
  enabled: boolean
  version: string
  certificateExpiry: string
  daysUntilExpiry: number
  isValid: boolean
  issuer: string
  warnings: string[]
}

export interface SecretHealth {
  totalSecrets: number
  encryptedSecrets: number
  unencryptedSecrets: number
  expiredSecrets: number
  rotationRequired: string[]
  lastRotation: Record<string, string>
}

export interface TokenStatus {
  totalTokens: number
  activeTokens: number
  expiredTokens: number
  expiringWithin7Days: number
  expiringWithin30Days: number
  tokensNeedingRotation: string[]
}

export interface RateLimitStats {
  totalRequests: number
  limitedRequests: number
  uniqueIPs: number
  averageRequestsPerSecond: number
  peakRequestsPerSecond: number
  topOffenders: { ip: string; count: number }[]
}

export interface BlockedRequest {
  timestamp: string
  ip: string
  endpoint: string
  reason: string
  userId?: string
  userAgent: string
}

export interface DependencyInfo {
  name: string
  version: string
  type: 'parser' | 'embedding-model' | 'runtime' | 'library'
  hash: string
  lastUpdated: string
  vulnerabilities?: SecurityVulnerability[]
}

export interface SecurityVulnerability {
  id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  fixAvailable: boolean
  fixVersion?: string
}

export interface SystemBillOfMaterials {
  generatedAt: string
  systemVersion: string
  dependencies: DependencyInfo[]
  buildHash: string
  deploymentEnvironment: string
  sbomVersion: string
}

export interface DataLineageNode {
  id: string
  type: 'raw-file' | 'parsed-model' | 'extracted-strings' | 'indexed-chunks' | 'search-result'
  timestamp: string
  hash: string
  metadata: Record<string, unknown>
  parentIds: string[]
  transformationApplied?: string
}

export interface DataLineageGraph {
  rootArtifactId: string
  nodes: DataLineageNode[]
  edges: { from: string; to: string; transformation: string }[]
  generatedAt: string
}

export interface SandboxNamespace {
  id: string
  name: string
  createdAt: string
  createdBy: string
  isolationLevel: 'full' | 'partial'
  allowedFileTypes: string[]
  autoCleanupAfterHours: number
  active: boolean
}

export interface SandboxTest {
  id: string
  namespaceId: string
  uploadedFileHash: string
  testStarted: string
  testCompleted?: string
  status: 'running' | 'completed' | 'failed'
  parsingResults?: Record<string, unknown>
  indexingResults?: Record<string, unknown>
  errors?: string[]
}

export interface HealthCheckSuite {
  id: string
  ranAt: string
  checks: HealthCheck[]
  overallStatus: 'healthy' | 'degraded' | 'critical'
  duration: number
}

export interface HealthCheck {
  name: string
  category: 'parser' | 'search' | 'graph' | 'database' | 'network'
  status: 'green' | 'yellow' | 'red'
  message: string
  details?: Record<string, unknown>
  executionTime: number
}

export interface ChangeImpactAnalysis {
  changeDescription: string
  ruleId: string
  impactedDocuments: ImpactedDocument[]
  totalImpacted: number
  estimatedMigrationTime: number
  riskLevel: 'low' | 'medium' | 'high'
  mitigationSteps: string[]
}

export interface ImpactedDocument {
  documentId: string
  documentTitle: string
  currentNodeCount: number
  estimatedNewNodeCount: number
  changeMagnitude: 'minor' | 'moderate' | 'major'
  previewUrl?: string
}

export interface GovernanceReport {
  id: string
  generatedAt: string
  format: 'pdf' | 'html' | 'json'
  sections: {
    architecture: string
    policies: string
    dataFlow: string
    auditControls: string
    dependencies: string
    security: string
  }
  metadata: Record<string, unknown>
}

export interface PerformanceTuningRecommendation {
  id: string
  category: 'concurrency' | 'indexing' | 'caching' | 'query-optimization'
  currentValue: unknown
  recommendedValue: unknown
  reasoning: string
  impact: 'low' | 'medium' | 'high'
  confidence: number
  estimatedImprovement: string
  risks: string[]
}

export interface IncidentTimelineEvent {
  id: string
  timestamp: string
  eventType: 'config-change' | 'ingestion-run' | 'error' | 'access-attempt' | 'system-event'
  severity: 'info' | 'warning' | 'error' | 'critical'
  userId?: string
  projectId?: string
  component: string
  description: string
  metadata: Record<string, unknown>
  correlationId?: string
  relatedEventIds?: string[]
}

export interface IncidentTimeline {
  startTime: string
  endTime: string
  events: IncidentTimelineEvent[]
  filters: {
    projectId?: string
    userId?: string
    severity?: string[]
    eventTypes?: string[]
  }
  totalEvents: number
  criticalEvents: number
}
