import { 
  AnalysisScript, 
  ScriptRun, 
  ScriptRunStatus, 
  Finding, 
  TimelineEvent, 
  Proposal,
  DocumentSimilarity,
  Document,
  Entity,
  TextChunk,
  AuditEvent
} from './types'
import { createHash } from './utils'

export interface ScriptExecutionContext {
  scriptRun: ScriptRun
  documents: Document[]
  entities: Entity[]
  chunks: TextChunk[]
  existingFindings: Finding[]
  existingTimeline: TimelineEvent[]
}

export interface ScriptExecutionResult {
  runId: string
  status: ScriptRunStatus
  findings?: Finding[]
  timelineEvents?: TimelineEvent[]
  proposals?: Proposal[]
  similarities?: DocumentSimilarity[]
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
}

export class ScriptRunner {
  private runningScripts: Map<string, AbortController> = new Map()

  async executeScript(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    triggeredBy: string
  ): Promise<ScriptExecutionResult> {
    const runId = `run-${Date.now()}-${createHash(script.id)}`
    const abortController = new AbortController()
    
    this.runningScripts.set(runId, abortController)

    const startTime = Date.now()
    const result: ScriptExecutionResult = {
      runId,
      status: 'running',
      errors: [],
      metrics: {}
    }

    try {
      switch (script.category) {
        case 'pattern-scanner':
          result.findings = await this.executePatternScanner(script, context, abortController.signal)
          break
        case 'entity-enrichment':
          result.proposals = await this.executeAliasDetector(script, context, abortController.signal)
          break
        case 'timeline-builder':
          result.timelineEvents = await this.executeTimelineBuilder(script, context, abortController.signal)
          break
        case 'similarity-linker':
          result.similarities = await this.executeSimilarityLinker(script, context, abortController.signal)
          break
        case 'relationship-engine':
          result.proposals = await this.executeRelationshipEngine(script, context, abortController.signal)
          break
        case 'summarization':
          break
        case 'export-generator':
          break
      }

      const endTime = Date.now()
      result.metrics.avgTimePerDocument = context.documents.length > 0 
        ? (endTime - startTime) / context.documents.length 
        : 0

      result.status = 'completed'
    } catch (error) {
      result.status = 'failed'
      result.errors.push({
        timestamp: new Date().toISOString(),
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      })
    } finally {
      this.runningScripts.delete(runId)
    }

    return result
  }

  private async executePatternScanner(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    signal: AbortSignal
  ): Promise<Finding[]> {
    const findings: Finding[] = []
    const config = script.config as any
    const dictionaries = config.dictionaries || []
    const contextWindow = config.contextWindow || 100

    for (const doc of context.documents) {
      if (signal.aborted) break

      const docChunks = context.chunks.filter(c => c.documentId === doc.id)

      for (const chunk of docChunks) {
        for (const dict of dictionaries) {
          const patterns = [
            ...(dict.terms || []),
            ...(dict.phrases || [])
          ]

          for (const pattern of patterns) {
            const regex = new RegExp(pattern, 'gi')
            let match

            while ((match = regex.exec(chunk.text)) !== null) {
              const offset: [number, number] = [match.index, match.index + match[0].length]
              const snippetStart = Math.max(0, match.index - contextWindow)
              const snippetEnd = Math.min(chunk.text.length, match.index + match[0].length + contextWindow)
              
              findings.push({
                id: `finding-${Date.now()}-${createHash(`${doc.id}-${offset[0]}`)}`,
                scriptRunId: context.scriptRun.id,
                documentId: doc.id,
                chunkId: chunk.id,
                category: dict.category,
                pattern,
                snippet: chunk.text.substring(snippetStart, snippetEnd),
                offset,
                severity: dict.severity || 'info',
                confidence: 0.85,
                context: chunk.text.substring(snippetStart, snippetEnd),
                metadata: {
                  dictionary: dict.category,
                  matchType: 'exact'
                },
                reviewStatus: 'pending',
                createdAt: new Date().toISOString()
              })
            }
          }
        }
      }
    }

    return findings
  }

  private async executeAliasDetector(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    signal: AbortSignal
  ): Promise<Proposal[]> {
    const proposals: Proposal[] = []
    const config = script.config as any
    const fuzzyThreshold = config.fuzzyThreshold || 0.85

    for (let i = 0; i < context.entities.length; i++) {
      if (signal.aborted) break

      for (let j = i + 1; j < context.entities.length; j++) {
        const entityA = context.entities[i]
        const entityB = context.entities[j]

        if (entityA.type !== entityB.type) continue

        const similarity = this.calculateStringSimilarity(
          entityA.canonicalName.toLowerCase(),
          entityB.canonicalName.toLowerCase()
        )

        if (similarity >= fuzzyThreshold) {
          proposals.push({
            id: `proposal-${Date.now()}-${createHash(`${entityA.id}-${entityB.id}`)}`,
            scriptRunId: context.scriptRun.id,
            type: 'entity-merge',
            status: 'pending',
            confidence: similarity,
            evidenceSnippets: [],
            proposedChange: {
              mergeFrom: entityB.id,
              mergeTo: entityA.id,
              reason: 'name-similarity',
              similarity
            },
            justification: `Entity names are ${(similarity * 100).toFixed(1)}% similar. Suggested merge requires Reviewer approval.`,
            reversible: true,
            createdAt: new Date().toISOString()
          })
        }
      }
    }

    return proposals
  }

  private async executeTimelineBuilder(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    signal: AbortSignal
  ): Promise<TimelineEvent[]> {
    const events: TimelineEvent[] = []
    const datePatterns = [
      /\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b/g,
      /\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b/g,
      /\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b/gi
    ]

    for (const doc of context.documents) {
      if (signal.aborted) break

      const docChunks = context.chunks.filter(c => c.documentId === doc.id)

      for (const chunk of docChunks) {
        for (const pattern of datePatterns) {
          let match

          while ((match = pattern.exec(chunk.text)) !== null) {
            const rawDateText = match[0]
            const normalizedDate = this.normalizeDate(match)
            
            if (normalizedDate) {
              events.push({
                id: `timeline-${Date.now()}-${createHash(`${doc.id}-${rawDateText}`)}`,
                scriptRunId: context.scriptRun.id,
                documentId: doc.id,
                chunkId: chunk.id,
                normalizedDate: normalizedDate.date,
                dateConfidence: normalizedDate.confidence,
                rawDateText,
                eventDescription: 'Date extracted from document',
                snippet: chunk.text.substring(
                  Math.max(0, match.index - 50),
                  Math.min(chunk.text.length, match.index + rawDateText.length + 50)
                ),
                metadata: {
                  pattern: pattern.source
                },
                createdAt: new Date().toISOString()
              })
            }
          }
        }
      }
    }

    return events
  }

  private async executeSimilarityLinker(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    signal: AbortSignal
  ): Promise<DocumentSimilarity[]> {
    const similarities: DocumentSimilarity[] = []
    const config = script.config as any
    const threshold = config.similarityThreshold || 0.75

    for (let i = 0; i < context.documents.length; i++) {
      if (signal.aborted) break

      for (let j = i + 1; j < context.documents.length; j++) {
        const docA = context.documents[i]
        const docB = context.documents[j]
        
        const chunksA = context.chunks.filter(c => c.documentId === docA.id)
        const chunksB = context.chunks.filter(c => c.documentId === docB.id)

        const similarity = this.calculateDocumentSimilarity(chunksA, chunksB)

        if (similarity.score >= threshold) {
          similarities.push({
            id: `similarity-${Date.now()}-${createHash(`${docA.id}-${docB.id}`)}`,
            scriptRunId: context.scriptRun.id,
            documentAId: docA.id,
            documentBId: docB.id,
            similarityScore: similarity.score,
            matchedConcepts: similarity.concepts,
            snippetPairs: similarity.snippetPairs,
            createdAt: new Date().toISOString()
          })
        }
      }
    }

    return similarities
  }

  private async executeRelationshipEngine(
    script: AnalysisScript,
    context: ScriptExecutionContext,
    signal: AbortSignal
  ): Promise<Proposal[]> {
    const proposals: Proposal[] = []

    return proposals
  }

  private calculateStringSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2
    const shorter = str1.length > str2.length ? str2 : str1
    
    if (longer.length === 0) return 1.0
    
    const editDistance = this.levenshteinDistance(longer, shorter)
    return (longer.length - editDistance) / longer.length
  }

  private levenshteinDistance(str1: string, str2: string): number {
    const matrix: number[][] = []

    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i]
    }

    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j
    }

    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1]
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          )
        }
      }
    }

    return matrix[str2.length][str1.length]
  }

  private normalizeDate(match: RegExpMatchArray): { date: string; confidence: number } | null {
    try {
      let year: number, month: number, day: number

      if (match[3] && match[3].length === 4) {
        if (isNaN(Number(match[1]))) {
          const monthNames = ['january', 'february', 'march', 'april', 'may', 'june', 
                             'july', 'august', 'september', 'october', 'november', 'december']
          month = monthNames.indexOf(match[1].toLowerCase()) + 1
          day = Number(match[2])
          year = Number(match[3])
        } else {
          month = Number(match[1])
          day = Number(match[2])
          year = Number(match[3])
        }
      } else if (match[1] && match[1].length === 4) {
        year = Number(match[1])
        month = Number(match[2])
        day = Number(match[3])
      } else {
        return null
      }

      if (month < 1 || month > 12 || day < 1 || day > 31) {
        return null
      }

      const date = new Date(year, month - 1, day)
      if (isNaN(date.getTime())) {
        return null
      }

      return {
        date: date.toISOString().split('T')[0],
        confidence: 0.9
      }
    } catch {
      return null
    }
  }

  private calculateDocumentSimilarity(
    chunksA: TextChunk[],
    chunksB: TextChunk[]
  ): { score: number; concepts: string[]; snippetPairs: any[] } {
    const textA = chunksA.map(c => c.text).join(' ').toLowerCase()
    const textB = chunksB.map(c => c.text).join(' ').toLowerCase()

    const wordsA = new Set(textA.split(/\s+/).filter(w => w.length > 3))
    const wordsB = new Set(textB.split(/\s+/).filter(w => w.length > 3))

    const intersection = new Set([...wordsA].filter(x => wordsB.has(x)))
    const union = new Set([...wordsA, ...wordsB])

    const score = union.size > 0 ? intersection.size / union.size : 0

    return {
      score,
      concepts: Array.from(intersection).slice(0, 10),
      snippetPairs: []
    }
  }

  cancelScriptRun(runId: string): boolean {
    const controller = this.runningScripts.get(runId)
    if (controller) {
      controller.abort()
      this.runningScripts.delete(runId)
      return true
    }
    return false
  }

  isRunning(runId: string): boolean {
    return this.runningScripts.has(runId)
  }
}

export const scriptRunner = new ScriptRunner()
