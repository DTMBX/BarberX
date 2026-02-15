import { Source, IngestionRun, Document, Entity, Relationship, AuditEvent, SearchResult } from './types'
import { createHash } from './utils'

export function generateSampleSources(): Source[] {
  return [
    {
      id: 'source-doj-epstein',
      name: 'DOJ Epstein Library (Official)',
      baseUrl: 'https://www.justice.gov/epstein',
      description: 'Official Department of Justice public document releases related to United States v. Jeffrey Epstein. All materials are lawfully published by DOJ and subject to their access policies including age verification gates and Queue-it traffic management.',
      crawlRules: {
        maxDepth: 3,
        rateLimit: 5,
        allowedDomains: ['justice.gov'],
        respectQueueIt: true,
        respectAgeGate: true
      },
      status: 'active',
      createdAt: '2024-01-15T10:00:00Z',
      lastRunAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
    },
    {
      id: 'source-doj-disclosures',
      name: 'DOJ Epstein Disclosures (Subfolder)',
      baseUrl: 'https://www.justice.gov/epstein/doj-disclosures',
      description: 'Specific subfolder of the DOJ Epstein Library containing additional disclosure documents. Crawler respects the same access controls and rate limits as parent source.',
      crawlRules: {
        maxDepth: 2,
        rateLimit: 5,
        allowedDomains: ['justice.gov'],
        respectQueueIt: true,
        respectAgeGate: true
      },
      status: 'active',
      createdAt: '2024-01-18T14:20:00Z',
      lastRunAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString()
    }
  ]
}

export function generateSampleIngestionRuns(): IngestionRun[] {
  const now = Date.now()
  return [
    {
      id: 'run-doj-initial',
      sourceId: 'source-doj-epstein',
      startedAt: new Date(now - 1000 * 60 * 60 * 24 * 7).toISOString(),
      endedAt: new Date(now - 1000 * 60 * 60 * 24 * 6).toISOString(),
      status: 'completed',
      discovered: 2847,
      downloaded: 2819,
      processed: 2801,
      errors: 18,
      notes: 'Initial discovery and ingestion from justice.gov/epstein root. Respected Queue-it controls and age gate. 18 documents failed OCR due to handwriting or image quality.'
    },
    {
      id: 'run-doj-disclosures',
      sourceId: 'source-doj-disclosures',
      startedAt: new Date(now - 1000 * 60 * 60 * 24 * 5).toISOString(),
      endedAt: new Date(now - 1000 * 60 * 60 * 24 * 5 + 1000 * 60 * 60 * 3).toISOString(),
      status: 'completed',
      discovered: 456,
      downloaded: 448,
      processed: 442,
      errors: 6,
      notes: 'Ingestion from doj-disclosures subfolder. 6 documents had corrupted PDF structures and were quarantined for manual review.'
    },
    {
      id: 'run-doj-incremental',
      sourceId: 'source-doj-epstein',
      startedAt: new Date(now - 1000 * 60 * 60 * 2).toISOString(),
      status: 'running',
      discovered: 23,
      downloaded: 19,
      processed: 12,
      errors: 0,
      throttleInfo: {
        active: true,
        resumeAt: new Date(now + 1000 * 60 * 15).toISOString(),
        reason: 'Polite rate limiting (5 req/min) to respect DOJ server load'
      },
      notes: 'Incremental crawl to detect new releases. Currently throttled to maintain compliance with site policies.'
    }
  ]
}

export function generateSampleDocuments(): Document[] {
  const docs: Document[] = []
  
  const sampleDocs = [
    {
      title: 'DOJ Disclosure - Court Filing 1:08-cv-80736 (SDFL)',
      pageCount: 234,
      fileSize: 4567890,
      status: 'indexed' as const,
      ocrUsed: false,
      confidence: 0.95,
      sourceUrl: 'https://www.justice.gov/epstein/doj-disclosures'
    },
    {
      title: 'Released Document - Travel Records 2001-2002',
      pageCount: 87,
      fileSize: 2345678,
      status: 'indexed' as const,
      ocrUsed: true,
      confidence: 0.78,
      sourceUrl: 'https://www.justice.gov/epstein'
    },
    {
      title: 'DOJ Release - Deposition Transcript Excerpts',
      pageCount: 156,
      fileSize: 3456789,
      status: 'indexed' as const,
      ocrUsed: true,
      confidence: 0.82,
      sourceUrl: 'https://www.justice.gov/epstein/doj-disclosures'
    },
    {
      title: 'Official Release - Financial Documentation Bundle',
      pageCount: 412,
      fileSize: 8901234,
      status: 'indexed' as const,
      ocrUsed: false,
      confidence: 0.92,
      sourceUrl: 'https://www.justice.gov/epstein'
    },
    {
      title: 'Court Record - Legal Correspondence 1998-2005',
      pageCount: 67,
      fileSize: 1234567,
      status: 'extracted' as const,
      ocrUsed: false,
      confidence: 0.88,
      sourceUrl: 'https://www.justice.gov/epstein/doj-disclosures'
    },
    {
      title: 'DOJ Document - Property Transaction Records',
      pageCount: 94,
      fileSize: 2567890,
      status: 'indexed' as const,
      ocrUsed: false,
      confidence: 0.94,
      sourceUrl: 'https://www.justice.gov/epstein'
    },
    {
      title: 'Released Filing - Employment Documentation',
      pageCount: 178,
      fileSize: 4123456,
      status: 'ocr' as const,
      ocrUsed: true,
      confidence: 0.71,
      sourceUrl: 'https://www.justice.gov/epstein/doj-disclosures'
    },
    {
      title: 'Court Filing - Motion Documents Case 08-cv-4775',
      pageCount: 45,
      fileSize: 1567890,
      status: 'indexed' as const,
      ocrUsed: false,
      confidence: 0.97,
      sourceUrl: 'https://www.justice.gov/epstein'
    }
  ]
  
  sampleDocs.forEach((doc, idx) => {
    const id = `doj-doc-${(idx + 1).toString().padStart(4, '0')}`
    const sourceId = doc.sourceUrl.includes('doj-disclosures') ? 'source-doj-disclosures' : 'source-doj-epstein'
    const runId = doc.sourceUrl.includes('doj-disclosures') ? 'run-doj-disclosures' : 'run-doj-initial'
    docs.push({
      id,
      sourceId,
      runId,
      title: doc.title,
      url: `${doc.sourceUrl}/${id}.pdf`,
      sha256: createHash(`${doc.title}-${id}`).padEnd(64, '0'),
      fileSize: doc.fileSize,
      mimeType: 'application/pdf',
      downloadedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * (7 - idx)).toISOString(),
      pageCount: doc.pageCount,
      status: doc.status,
      ocrUsed: doc.ocrUsed,
      language: 'en',
      confidence: doc.confidence
    })
  })
  
  return docs
}

export function generateSampleEntities(): Entity[] {
  return [
    {
      id: 'entity-person-001',
      type: 'person',
      canonicalName: 'Individual A (Plaintiff)',
      aliases: ['Person A', 'Plaintiff A'],
      confidence: 0.95,
      mentionCount: 847,
      disambiguationStatus: 'reviewed',
      notes: 'Referenced across multiple court filings and deposition transcripts from DOJ releases',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString()
    },
    {
      id: 'entity-person-002',
      type: 'person',
      canonicalName: 'Individual B (Defendant)',
      aliases: ['Person B', 'Defendant B'],
      confidence: 0.97,
      mentionCount: 1234,
      disambiguationStatus: 'reviewed',
      notes: 'Named in federal court records released by DOJ',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString()
    },
    {
      id: 'entity-person-003',
      type: 'person',
      canonicalName: 'Individual C (Defendant)',
      aliases: ['Person C', 'Subject C'],
      confidence: 0.98,
      mentionCount: 2156,
      disambiguationStatus: 'reviewed',
      notes: 'Primary subject of United States v. Epstein case files',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString()
    },
    {
      id: 'entity-org-001',
      type: 'organization',
      canonicalName: 'Financial Entity Alpha',
      aliases: ['Entity Alpha', 'Company A'],
      confidence: 0.89,
      mentionCount: 267,
      disambiguationStatus: 'reviewed',
      notes: 'Financial institution mentioned in transaction records',
      reviewedBy: 'analyst-002',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString()
    },
    {
      id: 'entity-loc-001',
      type: 'location',
      canonicalName: 'Property Location - US Virgin Islands',
      aliases: ['USVI Property', 'Island Location'],
      confidence: 0.92,
      mentionCount: 456,
      disambiguationStatus: 'reviewed',
      notes: 'Property referenced in real estate transaction documents',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString()
    },
    {
      id: 'entity-org-002',
      type: 'organization',
      canonicalName: 'Business Entity Beta',
      aliases: ['Beta Corp', 'Company B'],
      confidence: 0.85,
      mentionCount: 189,
      disambiguationStatus: 'needs-review',
      notes: 'Business entity requiring disambiguation - may overlap with other registered entities'
    },
    {
      id: 'entity-loc-002',
      type: 'location',
      canonicalName: 'Florida Residence (Palm Beach County)',
      aliases: ['Palm Beach Address', 'Florida Property A'],
      confidence: 0.94,
      mentionCount: 523,
      disambiguationStatus: 'reviewed',
      notes: 'Residential property mentioned in court documents',
      reviewedBy: 'analyst-002',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString()
    },
    {
      id: 'entity-person-004',
      type: 'person',
      canonicalName: 'Individual D (Legal Representative)',
      aliases: ['Attorney D', 'Counsel D'],
      confidence: 0.91,
      mentionCount: 312,
      disambiguationStatus: 'reviewed',
      notes: 'Legal representative mentioned in case filings',
      reviewedBy: 'analyst-003',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString()
    }
  ]
}

export function generateSampleRelationships(): Relationship[] {
  return [
    {
      id: 'rel-001',
      entityAId: 'entity-person-003',
      entityBId: 'entity-person-002',
      type: 'co-occurs',
      confidence: 0.96,
      evidenceChunkIds: ['chunk-doj-001', 'chunk-doj-005', 'chunk-doj-012', 'chunk-doj-023'],
      reviewStatus: 'approved',
      notes: 'Co-occurrence documented in multiple released court filings',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString()
    },
    {
      id: 'rel-002',
      entityAId: 'entity-person-001',
      entityBId: 'entity-person-002',
      type: 'referenced-in',
      confidence: 0.94,
      evidenceChunkIds: ['chunk-doj-007', 'chunk-doj-015', 'chunk-doj-034'],
      reviewStatus: 'approved',
      notes: 'References found in deposition transcript excerpts',
      reviewedBy: 'analyst-001',
      reviewedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString()
    },
    {
      id: 'rel-003',
      entityAId: 'entity-person-003',
      entityBId: 'entity-loc-001',
      type: 'associated-with',
      confidence: 0.91,
      evidenceChunkIds: ['chunk-doj-018', 'chunk-doj-029', 'chunk-doj-041'],
      reviewStatus: 'approved',
      notes: 'Association documented in property transaction records',
      reviewedBy: 'analyst-002',
      reviewedAt: '2024-03-18T15:30:00Z'
    },
    {
      id: 'rel-4',
      entityAId: 'entity-3',
      entityBId: 'entity-4',
      type: 'associated-with',
      confidence: 0.87,
      evidenceChunkIds: ['chunk-22', 'chunk-31'],
      reviewStatus: 'approved',
      reviewedBy: 'analyst-002',
      reviewedAt: '2024-03-18T16:00:00Z'
    },
    {
      id: 'rel-5',
      entityAId: 'entity-8',
      entityBId: 'entity-3',
      type: 'referenced-in',
      confidence: 0.89,
      evidenceChunkIds: ['chunk-45', 'chunk-52'],
      reviewStatus: 'needs-review'
    },
    {
      id: 'rel-6',
      entityAId: 'entity-2',
      entityBId: 'entity-5',
      type: 'co-occurs',
      confidence: 0.88,
      evidenceChunkIds: ['chunk-19', 'chunk-28'],
      reviewStatus: 'approved',
      reviewedBy: 'analyst-001',
      reviewedAt: '2024-03-18T14:45:00Z'
    }
  ]
}

export function generateSampleSearchResults(): SearchResult[] {
  return [
    {
      documentId: 'doc-1',
      title: 'Giuffre v. Maxwell - Deposition Transcript Vol. 1',
      snippet: '...testified under oath regarding events that occurred between 1999 and 2002, including multiple trips aboard private aircraft...',
      highlights: [
        { text: 'testified', offset: [0, 9] },
        { text: 'private aircraft', offset: [89, 105] }
      ],
      pageNo: 45,
      confidence: 0.94,
      relevanceScore: 0.89
    },
    {
      documentId: 'doc-2',
      title: 'Flight Logs - Private Aircraft N908JE (2001-2002)',
      snippet: '...passenger manifest for flight departing Teterboro Airport on March 15, 2001, destination Little St. James, USVI...',
      highlights: [
        { text: 'passenger manifest', offset: [0, 18] },
        { text: 'Little St. James', offset: [89, 105] }
      ],
      pageNo: 23,
      confidence: 0.82,
      relevanceScore: 0.91
    },
    {
      documentId: 'doc-3',
      title: 'Address Book - Palm Beach Residence',
      snippet: '...contact information including phone numbers for legal counsel, financial advisors, and property management staff...',
      highlights: [
        { text: 'contact information', offset: [0, 19] },
        { text: 'legal counsel', offset: [50, 63] }
      ],
      pageNo: 12,
      confidence: 0.78,
      relevanceScore: 0.76
    }
  ]
}

export function generateSampleAuditEvents(): AuditEvent[] {
  return [
    {
      id: 'audit-1',
      timestamp: '2024-03-18T14:00:00Z',
      actor: 'analyst-001@example.gov',
      action: 'APPROVE_RELATIONSHIP',
      objectType: 'relationship',
      objectId: 'rel-1',
      details: {
        entityA: 'Jeffrey Epstein',
        entityB: 'Ghislaine Maxwell',
        type: 'co-occurs',
        confidence: 0.96
      },
      ipAddress: '10.0.2.15'
    },
    {
      id: 'audit-2',
      timestamp: '2024-03-18T14:10:00Z',
      actor: 'analyst-001@example.gov',
      action: 'APPROVE_RELATIONSHIP',
      objectType: 'relationship',
      objectId: 'rel-2',
      details: {
        entityA: 'Virginia Giuffre',
        entityB: 'Ghislaine Maxwell',
        type: 'referenced-in'
      },
      ipAddress: '10.0.2.15'
    },
    {
      id: 'audit-3',
      timestamp: '2024-03-18T13:45:00Z',
      actor: 'analyst-002@example.gov',
      action: 'MERGE_ENTITY',
      objectType: 'entity',
      objectId: 'entity-4',
      details: {
        mergedFrom: ['entity-4a', 'entity-4b'],
        canonicalName: 'Southern Trust Company',
        reason: 'Same organization, different name variants'
      },
      ipAddress: '10.0.2.22'
    },
    {
      id: 'audit-4',
      timestamp: '2024-03-20T14:30:00Z',
      actor: 'admin-001@example.gov',
      action: 'START_INGESTION',
      objectType: 'ingestion_run',
      objectId: 'run-1',
      details: {
        sourceId: 'source-1',
        sourceName: 'DOJ Epstein Library'
      },
      ipAddress: '10.0.2.5'
    },
    {
      id: 'audit-5',
      timestamp: '2024-03-17T11:00:00Z',
      actor: 'analyst-003@example.gov',
      action: 'REVIEW_ENTITY',
      objectType: 'entity',
      objectId: 'entity-8',
      details: {
        action: 'approved',
        canonicalName: 'Alan Dershowitz',
        aliases: ['A. Dershowitz', 'Prof. Dershowitz']
      },
      ipAddress: '10.0.2.18'
    }
  ]
}

export function generateSampleQualityMetrics(): any[] {
  return [
    {
      documentId: 'doc-1',
      overallScore: 0.94,
      textDensity: 0.92,
      ocrConfidenceProxy: 0.98,
      characterErrorRate: 0.02,
      layoutQuality: 0.95,
      languageConsistency: 0.96,
      readabilityScore: 0.91,
      flaggedForReview: false,
      reprocessRecommended: false,
      computedAt: '2024-03-20T15:30:00Z',
      scriptRunId: 'script-run-quality-1'
    },
    {
      documentId: 'doc-2',
      overallScore: 0.68,
      textDensity: 0.65,
      ocrConfidenceProxy: 0.72,
      characterErrorRate: 0.18,
      layoutQuality: 0.63,
      languageConsistency: 0.75,
      readabilityScore: 0.67,
      flaggedForReview: true,
      reprocessRecommended: false,
      computedAt: '2024-03-20T15:32:00Z',
      scriptRunId: 'script-run-quality-1'
    },
    {
      documentId: 'doc-6',
      pageNo: 45,
      overallScore: 0.28,
      textDensity: 0.22,
      ocrConfidenceProxy: 0.35,
      characterErrorRate: 0.42,
      layoutQuality: 0.31,
      languageConsistency: 0.19,
      readabilityScore: 0.25,
      flaggedForReview: true,
      reprocessRecommended: true,
      computedAt: '2024-03-20T15:35:00Z',
      scriptRunId: 'script-run-quality-1'
    }
  ]
}

export function generateSampleReviewQueue(): any[] {
  return [
    {
      id: 'queue-1',
      queueType: 'low-ocr-quality',
      objectType: 'document',
      objectId: 'doc-6',
      priority: 'high',
      status: 'pending',
      createdAt: '2024-03-20T15:35:00Z',
      metadata: {
        qualityScore: 0.28,
        pageNo: 45,
        reason: 'Text density below threshold'
      }
    },
    {
      id: 'queue-2',
      queueType: 'ambiguous-entities',
      objectType: 'entity',
      objectId: 'entity-6',
      priority: 'medium',
      status: 'in-progress',
      assignedTo: 'analyst-002',
      dueDate: '2024-03-25T17:00:00Z',
      createdAt: '2024-03-19T10:20:00Z',
      metadata: {
        possibleMatches: ['J. Smith', 'John Smith', 'Jonathan Smith'],
        confidence: 0.62
      }
    },
    {
      id: 'queue-3',
      queueType: 'relationship-proposals',
      objectType: 'proposal',
      objectId: 'prop-5',
      priority: 'urgent',
      status: 'pending',
      dueDate: '2024-03-22T12:00:00Z',
      createdAt: '2024-03-21T08:15:00Z',
      metadata: {
        relationshipType: 'associated-with',
        confidence: 0.89,
        evidenceCount: 8
      }
    },
    {
      id: 'queue-4',
      queueType: 'sensitive-content-flags',
      objectType: 'chunk',
      objectId: 'chunk-128',
      priority: 'high',
      status: 'pending',
      createdAt: '2024-03-20T16:42:00Z',
      metadata: {
        flagType: 'PII',
        reason: 'Potential phone numbers and addresses detected'
      }
    },
    {
      id: 'queue-5',
      queueType: 'translation-review',
      objectType: 'translation',
      objectId: 'trans-12',
      priority: 'low',
      status: 'completed',
      assignedTo: 'analyst-003',
      completedAt: '2024-03-20T11:30:00Z',
      reviewNotes: 'Translation verified, confidence high',
      createdAt: '2024-03-19T14:20:00Z',
      metadata: {
        sourceLanguage: 'es',
        targetLanguage: 'en',
        confidence: 0.91
      }
    }
  ]
}

export function generateSampleAnnotations(): any[] {
  return [
    {
      id: 'ann-1',
      documentId: 'doc-1',
      chunkId: 'chunk-45',
      type: 'evidence-quote',
      content: 'I was approximately 15 years old at the time of the first alleged incident.',
      citations: [
        {
          documentId: 'doc-1',
          chunkId: 'chunk-45',
          snippet: 'I was approximately 15 years old at the time of the first alleged incident.',
          pageNo: 45,
          required: true
        }
      ],
      createdBy: 'analyst-001',
      createdAt: '2024-03-18T10:30:00Z',
      updatedAt: '2024-03-18T10:30:00Z',
      tags: ['age', 'timeline', 'testimony'],
      linkedAnnotations: []
    },
    {
      id: 'ann-2',
      documentId: 'doc-2',
      chunkId: 'chunk-23',
      type: 'interpretation',
      content: 'The flight logs show a pattern of regular trips between Teterboro and USVI locations during 2001-2002.',
      citations: [
        {
          documentId: 'doc-2',
          chunkId: 'chunk-23',
          snippet: 'Multiple entries showing departures from TETETR to STT/TISX between Jan 2001 and Dec 2002.',
          pageNo: 23,
          required: false
        }
      ],
      createdBy: 'analyst-002',
      createdAt: '2024-03-19T14:15:00Z',
      updatedAt: '2024-03-19T14:15:00Z',
      tags: ['travel', 'pattern-analysis'],
      linkedAnnotations: ['ann-1']
    },
    {
      id: 'ann-3',
      documentId: 'doc-5',
      chunkId: 'chunk-89',
      type: 'hypothesis',
      content: 'The timing of wire transfers may correlate with documented travel dates. Requires cross-referencing banking records with flight logs.',
      citations: [],
      createdBy: 'analyst-001',
      createdAt: '2024-03-20T09:45:00Z',
      updatedAt: '2024-03-20T09:45:00Z',
      tags: ['financial', 'travel', 'investigation'],
      linkedAnnotations: ['ann-2']
    },
    {
      id: 'ann-4',
      documentId: 'doc-7',
      chunkId: 'chunk-156',
      type: 'to-verify',
      content: 'Claim of employment at Mar-a-Lago during 1998-1999 period. Need to verify against employment records.',
      citations: [
        {
          documentId: 'doc-7',
          chunkId: 'chunk-156',
          snippet: 'Subject stated they worked at Mar-a-Lago resort from approximately 1998 to 1999.',
          pageNo: 78,
          required: false
        }
      ],
      createdBy: 'analyst-003',
      createdAt: '2024-03-20T16:20:00Z',
      updatedAt: '2024-03-20T16:20:00Z',
      tags: ['employment', 'verification-needed', 'timeline'],
      linkedAnnotations: []
    }
  ]
}

export function generateSampleRelationshipExplainers(): any[] {
  return [
    {
      relationshipId: 'rel-1',
      explanation: 'Linked because both entities appear together in the same paragraphs across multiple documents with consistent contextual proximity.',
      evidenceSnippets: [
        {
          chunkId: 'chunk-1',
          snippet: 'According to the deposition, Jeffrey Epstein and Ghislaine Maxwell were present at the Palm Beach residence on multiple occasions during the 2000-2002 period.',
          documentId: 'doc-1',
          pageNo: 45,
          highlightedTerms: ['Jeffrey Epstein', 'Ghislaine Maxwell']
        },
        {
          chunkId: 'chunk-5',
          snippet: 'Flight manifests indicate Epstein and Maxwell traveled together on private aircraft N908JE to various locations including the Virgin Islands.',
          documentId: 'doc-2',
          pageNo: 23,
          highlightedTerms: ['Epstein', 'Maxwell']
        }
      ],
      computationMethod: 'Co-occurrence analysis with proximity threshold of 100 characters',
      confidence: 0.96,
      neutralLanguageVerified: true
    },
    {
      relationshipId: 'rel-2',
      explanation: 'Linked because one entity explicitly references the other in sworn testimony and court documents.',
      evidenceSnippets: [
        {
          chunkId: 'chunk-7',
          snippet: 'Giuffre testified that she was introduced to Maxwell at Mar-a-Lago resort when she was working there as a spa attendant.',
          documentId: 'doc-1',
          pageNo: 12,
          highlightedTerms: ['Giuffre', 'Maxwell']
        },
        {
          chunkId: 'chunk-15',
          snippet: 'The deposition includes multiple references to interactions between Virginia Giuffre and Ghislaine Maxwell during the relevant time period.',
          documentId: 'doc-1',
          pageNo: 67,
          highlightedTerms: ['Virginia Giuffre', 'Ghislaine Maxwell']
        }
      ],
      computationMethod: 'Explicit mention detection in sworn testimony',
      confidence: 0.94,
      neutralLanguageVerified: true
    },
    {
      relationshipId: 'rel-3',
      explanation: 'Linked because both entities share document identifiers and appear in structured records (flight logs, address books) indicating professional or organizational connection.',
      evidenceSnippets: [
        {
          chunkId: 'chunk-18',
          snippet: 'Contact entry for Southern Trust Company lists Jeffrey Epstein as beneficial owner with account management details.',
          documentId: 'doc-3',
          pageNo: 89,
          highlightedTerms: ['Southern Trust Company', 'Jeffrey Epstein']
        }
      ],
      computationMethod: 'Structured record analysis with shared identifier extraction',
      confidence: 0.91,
      neutralLanguageVerified: true
    }
  ]
}

export async function initializeSampleData() {
  const sources = generateSampleSources()
  const runs = generateSampleIngestionRuns()
  const documents = generateSampleDocuments()
  const entities = generateSampleEntities()
  const relationships = generateSampleRelationships()
  const searchResults = generateSampleSearchResults()
  const auditEvents = generateSampleAuditEvents()
  const qualityMetrics = generateSampleQualityMetrics()
  const reviewQueue = generateSampleReviewQueue()
  const annotations = generateSampleAnnotations()
  const relationshipExplainers = generateSampleRelationshipExplainers()
  
  await window.spark.kv.set('sources', sources)
  await window.spark.kv.set('ingestion-runs', runs)
  await window.spark.kv.set('documents', documents)
  await window.spark.kv.set('entities', entities)
  await window.spark.kv.set('relationships', relationships)
  await window.spark.kv.set('search-results', searchResults)
  await window.spark.kv.set('audit-events', auditEvents)
  await window.spark.kv.set('review-queue-items', reviewQueue)
  await window.spark.kv.set('annotations', annotations)
  
  qualityMetrics.forEach(async (qm) => {
    await window.spark.kv.set(`quality-${qm.documentId}`, qm)
  })
  
  relationshipExplainers.forEach(async (exp) => {
    await window.spark.kv.set(`explainer-${exp.relationshipId}`, exp)
  })
  
  return {
    sources: sources.length,
    runs: runs.length,
    documents: documents.length,
    entities: entities.length,
    relationships: relationships.length,
    searchResults: searchResults.length,
    auditEvents: auditEvents.length,
    qualityMetrics: qualityMetrics.length,
    reviewQueue: reviewQueue.length,
    annotations: annotations.length,
    relationshipExplainers: relationshipExplainers.length
  }
}
