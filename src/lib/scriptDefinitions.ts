import { AnalysisScript, ScriptCategory, ScriptTrigger, UserRole } from './types'
import { createHash } from './utils'

export const SCRIPT_DEFINITIONS: Record<string, AnalysisScript> = {
  'pattern-scanner-v1': {
    id: 'pattern-scanner-v1',
    name: 'Keyword & Phrase Pattern Scanner',
    category: 'pattern-scanner',
    version: '1.0.0',
    versionHash: createHash('pattern-scanner-v1.0.0'),
    description: 'Scans documents for configurable keyword dictionaries, phrases, and regex patterns grouped by category. Outputs findings with exact offsets, snippets, and severity tags. Includes false-positive controls.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-index', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['document', 'chunks', 'config.dictionaries'],
      optional: ['config.negativePatterns', 'config.contextWindow']
    },
    outputs: ['findings'],
    requiredPermissions: ['read:documents', 'write:findings'],
    config: {
      dictionaries: [
        {
          category: 'Financial',
          severity: 'medium',
          terms: ['wire transfer', 'offshore account', 'cash payment'],
          phrases: ['paid in cash', 'transferred funds'],
          regex: []
        },
        {
          category: 'Travel',
          severity: 'info',
          terms: ['flight', 'airport', 'traveled to'],
          phrases: ['departed from', 'arrived at'],
          regex: []
        }
      ],
      negativePatterns: [],
      contextWindow: 100,
      minConfidence: 0.5
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'entity-alias-detector-v1': {
    id: 'entity-alias-detector-v1',
    name: 'Entity Alias & Variant Detector',
    category: 'entity-enrichment',
    version: '1.0.0',
    versionHash: createHash('entity-alias-detector-v1.0.0'),
    description: 'Uses fuzzy matching and context windows to propose entity aliases (name variants, initials, OCR misspellings) without auto-merging. Outputs merge proposals requiring Reviewer approval.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['entities', 'mentions', 'chunks'],
      optional: ['config.fuzzyThreshold', 'config.contextWindowSize']
    },
    outputs: ['proposals'],
    requiredPermissions: ['read:entities', 'write:proposals'],
    config: {
      fuzzyThreshold: 0.85,
      contextWindowSize: 50,
      minMentionCount: 2,
      requireReviewerApproval: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'timeline-builder-v1': {
    id: 'timeline-builder-v1',
    name: 'Date Normalization & Timeline Builder',
    category: 'timeline-builder',
    version: '1.0.0',
    versionHash: createHash('timeline-builder-v1.0.0'),
    description: 'Extracts dates and temporal phrases, normalizes to ISO dates with confidence scoring. Generates per-entity and per-document timelines. Never guesses missing years.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['documents', 'chunks', 'entities'],
      optional: ['config.dateFormats', 'config.uncertainDateHandling']
    },
    outputs: ['timelineEvents'],
    requiredPermissions: ['read:documents', 'read:entities', 'write:timeline'],
    config: {
      dateFormats: ['MM/DD/YYYY', 'DD-MMM-YYYY', 'YYYY-MM-DD'],
      uncertainDateHandling: 'flag-uncertain',
      minConfidence: 0.6,
      requireExplicitYear: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'similarity-linker-v1': {
    id: 'similarity-linker-v1',
    name: 'Document Similarity Linker',
    category: 'similarity-linker',
    version: '1.0.0',
    versionHash: createHash('similarity-linker-v1.0.0'),
    description: 'Computes embedding-based similarity between document chunks and generates SIMILAR_TO edges above configurable threshold. Provides explainable matches with overlapping concepts.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-index', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['documents', 'chunks', 'embeddings'],
      optional: ['config.similarityThreshold', 'config.boilerplateFilter']
    },
    outputs: ['similarities', 'relationships'],
    requiredPermissions: ['read:documents', 'read:embeddings', 'write:similarities'],
    config: {
      similarityThreshold: 0.75,
      maxLinksPerDocument: 10,
      boilerplateFilter: true,
      minChunkLength: 100
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'relationship-engine-v1': {
    id: 'relationship-engine-v1',
    name: 'Evidence-Backed Relationship Engine',
    category: 'relationship-engine',
    version: '1.0.0',
    versionHash: createHash('relationship-engine-v1.0.0'),
    description: 'Generates neutral relationship edges (CO_OCCURS_WITH, REFERENCED_IN, COMMUNICATED_WITH, ASSOCIATED_WITH) only when explicit evidence exists. Never uses accusatory labels. Requires reviewer gating for high-impact edges.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['entities', 'mentions', 'chunks'],
      optional: ['config.relationshipTemplates', 'config.confidenceThresholds']
    },
    outputs: ['relationships', 'proposals'],
    requiredPermissions: ['read:entities', 'write:relationships', 'write:proposals'],
    config: {
      relationshipTemplates: [
        {
          type: 'co-occurs',
          pattern: 'proximity',
          maxDistance: 100,
          minOccurrences: 3,
          requiresReview: false
        },
        {
          type: 'referenced-in',
          pattern: 'mention',
          requiresReview: false
        },
        {
          type: 'associated-with',
          pattern: 'explicit-language',
          requiresReview: true,
          minConfidence: 0.8
        }
      ],
      prohibitedLabels: ['criminal', 'perpetrator', 'victim', 'guilty', 'accomplice'],
      requireEvidenceSnippets: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'summarization-v1': {
    id: 'summarization-v1',
    name: 'Navigation Summarization (Non-Accusatory)',
    category: 'summarization',
    version: '1.0.0',
    versionHash: createHash('summarization-v1.0.0'),
    description: 'Generates document abstracts with objective descriptors only (topics, entities, date ranges, document type). Prohibits speculative language. Includes key passage extraction with citations.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['document', 'chunks', 'entities'],
      optional: ['config.maxAbstractLength', 'config.keyPassageCount']
    },
    outputs: ['summary'],
    requiredPermissions: ['read:documents', 'read:entities', 'write:summaries'],
    config: {
      maxAbstractLength: 500,
      keyPassageCount: 5,
      prohibitedLanguage: ['alleged', 'guilty', 'criminal', 'perpetrator', 'suspect'],
      includeWarning: true,
      objectiveDescriptorsOnly: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'export-generator-v1': {
    id: 'export-generator-v1',
    name: 'Redaction-Aware Export Generator',
    category: 'export-generator',
    version: '1.0.0',
    versionHash: createHash('export-generator-v1.0.0'),
    description: 'Generates reports with citations, file hashes, and provenance. Includes configurable redaction mode for PII (phones/emails/addresses). Never exports entire corpus—only selected evidence slices.',
    allowedRoles: ['Admin', 'Analyst', 'Reviewer'],
    triggers: ['manual'],
    executionMode: 'manual-only',
    inputs: {
      required: ['findings', 'entities', 'relationships', 'config.exportScope'],
      optional: ['config.redactionMode', 'config.includeHashes']
    },
    outputs: ['exportPackage'],
    requiredPermissions: ['read:all', 'export:reports'],
    config: {
      redactionMode: 'automatic',
      redactPatterns: ['phone', 'email', 'address', 'ssn'],
      includeHashes: true,
      includeProvenance: true,
      maxEvidenceSliceLength: 1000,
      citationFormat: 'full'
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'quality-scorer-v1': {
    id: 'quality-scorer-v1',
    name: 'OCR/Text Quality Scoring',
    category: 'pattern-scanner',
    version: '1.0.0',
    versionHash: createHash('quality-scorer-v1.0.0'),
    description: 'Computes per-page and per-document quality metrics including text density, OCR confidence proxies, character error heuristics, layout quality, and readability. Tags low-quality pages for re-OCR or manual review.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-extraction', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['document', 'pages', 'text'],
      optional: ['config.qualityThresholds']
    },
    outputs: ['qualityMetrics', 'reviewQueue'],
    requiredPermissions: ['read:documents', 'write:quality-metrics'],
    config: {
      textDensityThreshold: 50,
      minOcrConfidence: 0.7,
      maxCharErrorRate: 0.15,
      flagForReviewThreshold: 0.5,
      reprocessThreshold: 0.3
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'deduplicator-v1': {
    id: 'deduplicator-v1',
    name: 'Near-Duplicate Detection & Canonicalization',
    category: 'pattern-scanner',
    version: '1.0.0',
    versionHash: createHash('deduplicator-v1.0.0'),
    description: 'Detects identical or near-identical PDFs/pages/chunks using hashes and similarity fingerprints. Collapses duplicates into canonical document records while preserving all source URLs and download events.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-index', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['documents', 'hashes'],
      optional: ['config.similarityThreshold', 'config.chunkDeduplication']
    },
    outputs: ['duplicateGroups', 'canonicalMapping'],
    requiredPermissions: ['read:documents', 'write:duplicates'],
    config: {
      exactHashMatching: true,
      similarityThreshold: 0.95,
      preserveAllProvenance: true,
      chunkLevelDeduplication: true,
      minChunkLength: 200
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'structured-extractor-v1': {
    id: 'structured-extractor-v1',
    name: 'Structured Table/Form Extraction',
    category: 'entity-enrichment',
    version: '1.0.0',
    versionHash: createHash('structured-extractor-v1.0.0'),
    description: 'Detects tables and common form layouts (headers, checkboxes, stamped fields) and extracts them into structured JSON. Links extracted fields back to page coordinates. Enables querying by specific fields.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-extraction', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['document', 'pages', 'layout'],
      optional: ['config.formTemplates']
    },
    outputs: ['structuredExtractions', 'reviewQueue'],
    requiredPermissions: ['read:documents', 'write:structured-data'],
    config: {
      detectTables: true,
      detectForms: true,
      minimumConfidence: 0.6,
      preserveCoordinates: true,
      linkToPageIndex: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'language-detector-v1': {
    id: 'language-detector-v1',
    name: 'Multilingual Detection & Translation Workflow',
    category: 'entity-enrichment',
    version: '1.0.0',
    versionHash: createHash('language-detector-v1.0.0'),
    description: 'Auto-detects language per chunk and optionally translates into analyst language while preserving originals. Translations clearly labeled as machine-generated with confidence. Never overwrites originals.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-chunking', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['chunks'],
      optional: ['config.targetLanguage', 'config.autoTranslate']
    },
    outputs: ['languageDetections', 'translations', 'reviewQueue'],
    requiredPermissions: ['read:chunks', 'write:translations'],
    config: {
      targetLanguage: 'en',
      autoTranslate: false,
      confidenceThreshold: 0.7,
      preserveOriginal: true,
      labelMachineGenerated: true,
      supportedLanguages: ['en', 'es', 'fr', 'de', 'zh', 'ar', 'ru']
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'temporal-normalizer-v1': {
    id: 'temporal-normalizer-v1',
    name: 'Temporal Normalization & Uncertainty Model',
    category: 'timeline-builder',
    version: '1.0.0',
    versionHash: createHash('temporal-normalizer-v1.0.0'),
    description: 'Represents dates with uncertainty (year unknown, month-only, range) and supports timeline filtering by confidence. Avoids false precision. Shows raw date phrase alongside normalized value.',
    allowedRoles: ['Admin', 'Analyst'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['chunks', 'dateEntities'],
      optional: ['config.uncertaintyModel']
    },
    outputs: ['temporalEntities', 'timeline'],
    requiredPermissions: ['read:entities', 'write:temporal'],
    config: {
      handleUncertainty: true,
      requireExplicitYear: false,
      supportRanges: true,
      showRawPhrase: true,
      neverGuessYear: true
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  },

  'relationship-explainer-v1': {
    id: 'relationship-explainer-v1',
    name: 'Relationship Edge Explainer',
    category: 'relationship-engine',
    version: '1.0.0',
    versionHash: createHash('relationship-explainer-v1.0.0'),
    description: 'For every graph edge, computes and displays a short neutral explanation with evidence snippets. Requires at least one evidence snippet per edge. Improves trust and reduces hallucinated connections.',
    allowedRoles: ['Admin', 'Analyst', 'Reviewer'],
    triggers: ['post-entity', 'manual'],
    executionMode: 'automatic',
    inputs: {
      required: ['relationships', 'chunks', 'entities'],
      optional: ['config.explanationDepth']
    },
    outputs: ['relationshipExplainers'],
    requiredPermissions: ['read:relationships', 'write:explainers'],
    config: {
      neutralLanguageOnly: true,
      requireEvidenceSnippets: true,
      minSnippetsPerEdge: 1,
      maxExplanationLength: 200,
      prohibitedTerms: ['criminal', 'guilty', 'suspect', 'perpetrator', 'victim']
    },
    enabled: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'system'
  }
}

export function getScriptById(scriptId: string): AnalysisScript | undefined {
  return SCRIPT_DEFINITIONS[scriptId]
}

export function getScriptsByCategory(category: ScriptCategory): AnalysisScript[] {
  return Object.values(SCRIPT_DEFINITIONS).filter(s => s.category === category)
}

export function getScriptsByTrigger(trigger: ScriptTrigger): AnalysisScript[] {
  return Object.values(SCRIPT_DEFINITIONS).filter(s => 
    s.triggers.includes(trigger) && s.enabled && s.executionMode === 'automatic'
  )
}

export function getAllScripts(): AnalysisScript[] {
  return Object.values(SCRIPT_DEFINITIONS)
}
