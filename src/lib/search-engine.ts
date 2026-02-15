import { Section, Document, AuthorityLevel, DocumentType, VerificationStatus, TreatyStatus } from './types'

// ============================================================================
// Stemming – lightweight English suffix stripping (no external dependencies)
// ============================================================================

const STEM_EXCEPTIONS: Record<string, string> = {
  amendment: 'amend', amendments: 'amend', amending: 'amend',
  constitutional: 'constitution', constitutions: 'constitution',
  jurisdiction: 'jurisdict', jurisdictions: 'jurisdict',
  separation: 'separ', separated: 'separ',
  protection: 'protect', protections: 'protect', protective: 'protect',
  regulation: 'regulat', regulations: 'regulat',
  establishment: 'establish', established: 'establish',
  ratification: 'ratif', ratified: 'ratif',
  incorporation: 'incorpor', incorporated: 'incorpor',
  enforcement: 'enforc', enforced: 'enforc',
}

function stem(word: string): string {
  if (STEM_EXCEPTIONS[word]) return STEM_EXCEPTIONS[word]
  // Simple suffix stripping (good enough for legal corpus)
  return word
    .replace(/ies$/, 'y')
    .replace(/tion$/, '')
    .replace(/sion$/, '')
    .replace(/ment$/, '')
    .replace(/ness$/, '')
    .replace(/izing$/, 'ize')
    .replace(/ised$/, 'ise')
    .replace(/ised$/, 'ise')
    .replace(/ative$/, 'ate')
    .replace(/ously$/, 'ous')
    .replace(/ings$/, '')
    .replace(/ing$/, '')
    .replace(/ful$/, '')
    .replace(/ous$/, '')
    .replace(/ble$/, '')
    .replace(/ed$/, '')
    .replace(/er$/, '')
    .replace(/ly$/, '')
    .replace(/s$/, '')
}

// ============================================================================
// Search Interfaces
// ============================================================================

export interface SearchResult {
  section: Section
  document: Document
  relevanceScore: number
  matchedText: string
  matchPosition: number
  /** Authority level badge for display */
  authorityLevel: AuthorityLevel
  /** Verification status of the source document */
  verificationStatus: VerificationStatus
}

export interface SearchFilters {
  authorityLevels?: AuthorityLevel[]
  documentTypes?: DocumentType[]
  jurisdictionIds?: string[]
  effectiveDateFrom?: string
  effectiveDateTo?: string
  /** Filter by document verification status */
  verificationStatuses?: VerificationStatus[]
  /** Filter by treaty status (for treaty documents) */
  treatyStatuses?: TreatyStatus[]
}

// ============================================================================
// Full-Text Search Engine
// ============================================================================

export class FullTextSearchEngine {
  private sections: Section[]
  private documents: Document[]
  private sectionIndex: Map<string, Section>
  private documentIndex: Map<string, Document>
  /** Pre-computed stemmed tokens for each section (keyed by section.id) */
  private stemmedIndex: Map<string, string[]>

  constructor(sections: Section[], documents: Document[]) {
    this.sections = sections
    this.documents = documents
    this.sectionIndex = new Map(sections.map(s => [s.id, s]))
    this.documentIndex = new Map(documents.map(d => [d.id, d]))

    // Pre-compute stemmed indices for fast search
    this.stemmedIndex = new Map()
    for (const section of sections) {
      const raw = `${section.title} ${section.text} ${section.canonicalCitation}`
      this.stemmedIndex.set(section.id, this.tokenizeAndStem(raw.toLowerCase()))
    }
  }

  /**
   * Primary search – supports phrase queries ("due process"), boolean NOT (-term),
   * stemming, and hierarchical authority boosting.
   */
  search(query: string, filters?: SearchFilters, limit: number = 50): SearchResult[] {
    if (!query.trim()) return []

    const { positive, negative, phrase } = this.parseQuery(query)
    const stemmedPositive = positive.map(stem)
    const results: SearchResult[] = []

    for (const section of this.sections) {
      const document = this.documentIndex.get(section.documentId)
      if (!document) continue

      if (filters && !this.matchesFilters(document, filters)) continue

      const rawText = `${section.title} ${section.text} ${section.canonicalCitation}`
      const lowerText = rawText.toLowerCase()

      // Exclude negative terms
      if (negative.some(neg => lowerText.includes(neg))) continue

      // Phrase match check
      if (phrase && !lowerText.includes(phrase.toLowerCase())) continue

      const stemmedTokens = this.stemmedIndex.get(section.id) || []
      let score = this.calculateRelevance(lowerText, stemmedTokens, stemmedPositive, positive)

      // Phrase match bonus
      if (phrase && lowerText.includes(phrase.toLowerCase())) {
        score += 30
      }

      // Authority hierarchy boost (higher authority = small boost)
      if (document.authorityLevel === 'federal') score += 3
      else if (document.authorityLevel === 'state') score += 1

      // Topic tag match boost
      if (section.topicTags) {
        const tagMatches = positive.filter(term =>
          section.topicTags!.some(tag => tag.toLowerCase().includes(term))
        )
        score += tagMatches.length * 5
      }

      if (score > 0) {
        const matchPosition = lowerText.indexOf(positive[0] || '')
        const matchedText = this.extractMatchSnippet(section.text, query, 200)

        results.push({
          section,
          document,
          relevanceScore: score,
          matchedText,
          matchPosition,
          authorityLevel: document.authorityLevel,
          verificationStatus: document.verificationStatus,
        })
      }
    }

    return results
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
      .slice(0, limit)
  }

  searchByDocument(query: string, documentId: string, limit: number = 20): SearchResult[] {
    const { positive, phrase } = this.parseQuery(query)
    const stemmedPositive = positive.map(stem)
    const results: SearchResult[] = []

    const document = this.documentIndex.get(documentId)
    if (!document) return []

    for (const section of this.sections) {
      if (section.documentId !== documentId) continue

      const rawText = `${section.title} ${section.text} ${section.canonicalCitation}`
      const lowerText = rawText.toLowerCase()

      if (phrase && !lowerText.includes(phrase.toLowerCase())) continue

      const stemmedTokens = this.stemmedIndex.get(section.id) || []
      let score = this.calculateRelevance(lowerText, stemmedTokens, stemmedPositive, positive)

      if (phrase && lowerText.includes(phrase.toLowerCase())) score += 30

      if (score > 0) {
        const matchPosition = lowerText.indexOf(positive[0] || '')
        const matchedText = this.extractMatchSnippet(section.text, query, 200)

        results.push({
          section,
          document,
          relevanceScore: score,
          matchedText,
          matchPosition,
          authorityLevel: document.authorityLevel,
          verificationStatus: document.verificationStatus,
        })
      }
    }

    return results
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
      .slice(0, limit)
  }

  // ── Query Parser ─────────────────────────────────────────────────────
  private parseQuery(query: string): {
    positive: string[]
    negative: string[]
    phrase: string | null
  } {
    let phrase: string | null = null
    let remaining = query

    // Extract phrase in double quotes
    const phraseMatch = query.match(/"([^"]+)"/)
    if (phraseMatch) {
      phrase = phraseMatch[1]
      remaining = remaining.replace(/"[^"]*"/, '')
    }

    const tokens = this.tokenize(remaining.toLowerCase())
    const positive: string[] = []
    const negative: string[] = []

    for (const token of tokens) {
      if (token.startsWith('-') && token.length > 1) {
        negative.push(token.slice(1))
      } else {
        positive.push(token)
      }
    }

    return { positive, negative, phrase }
  }

  // ── Tokenizer ────────────────────────────────────────────────────────
  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2)
  }

  private tokenizeAndStem(text: string): string[] {
    return this.tokenize(text).map(stem)
  }

  // ── Relevance Scoring ────────────────────────────────────────────────
  private calculateRelevance(
    text: string,
    stemmedTokens: string[],
    stemmedQuery: string[],
    rawQueryTerms: string[]
  ): number {
    let score = 0

    // Exact term matches (highest weight)
    for (const term of rawQueryTerms) {
      const exactMatches = (text.match(new RegExp(`\\b${this.escapeRegex(term)}\\b`, 'g')) || []).length
      const partialMatches = (text.match(new RegExp(this.escapeRegex(term), 'g')) || []).length - exactMatches
      score += exactMatches * 10
      score += partialMatches * 3
      if (text.startsWith(term)) score += 5
    }

    // Stemmed matches (catch morphological variants)
    const stemmedSet = new Set(stemmedTokens)
    for (const sq of stemmedQuery) {
      if (stemmedSet.has(sq)) score += 4
    }

    // All terms present bonus
    const allTermsPresent = rawQueryTerms.every(term => text.includes(term))
    if (allTermsPresent && rawQueryTerms.length > 1) {
      score += 20
    }

    // Proximity bonus: if consecutive query terms appear near each other
    if (rawQueryTerms.length >= 2) {
      for (let i = 0; i < rawQueryTerms.length - 1; i++) {
        const idx1 = text.indexOf(rawQueryTerms[i])
        const idx2 = text.indexOf(rawQueryTerms[i + 1])
        if (idx1 !== -1 && idx2 !== -1 && Math.abs(idx2 - idx1) < 50) {
          score += 8
        }
      }
    }

    return score
  }

  private escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  // ── Snippet Extraction ───────────────────────────────────────────────
  private extractMatchSnippet(text: string, query: string, maxLength: number): string {
    const queryLower = query.toLowerCase().replace(/"([^"]+)"/, '$1')
    const textLower = text.toLowerCase()
    const firstTerm = queryLower.split(' ')[0]
    const matchIndex = textLower.indexOf(firstTerm)

    if (matchIndex === -1) {
      return text.substring(0, maxLength) + (text.length > maxLength ? '...' : '')
    }

    const start = Math.max(0, matchIndex - Math.floor(maxLength / 3))
    const end = Math.min(text.length, start + maxLength)
    
    let snippet = text.substring(start, end)
    
    if (start > 0) snippet = '...' + snippet
    if (end < text.length) snippet = snippet + '...'

    return snippet
  }

  // ── Filters ──────────────────────────────────────────────────────────
  private matchesFilters(document: Document, filters: SearchFilters): boolean {
    if (filters.authorityLevels && !filters.authorityLevels.includes(document.authorityLevel)) {
      return false
    }

    if (filters.documentTypes && !filters.documentTypes.includes(document.type)) {
      return false
    }

    if (filters.jurisdictionIds && !filters.jurisdictionIds.includes(document.jurisdictionId)) {
      return false
    }

    if (filters.effectiveDateFrom && document.effectiveDate) {
      if (document.effectiveDate < filters.effectiveDateFrom) return false
    }

    if (filters.effectiveDateTo && document.effectiveDate) {
      if (document.effectiveDate > filters.effectiveDateTo) return false
    }

    if (filters.verificationStatuses && !filters.verificationStatuses.includes(document.verificationStatus)) {
      return false
    }

    if (filters.treatyStatuses && document.treatyMetadata?.status) {
      if (!filters.treatyStatuses.includes(document.treatyMetadata.status)) {
        return false
      }
    }

    return true
  }

  // ── Utility Methods ──────────────────────────────────────────────────
  getDocumentsByJurisdiction(jurisdictionId: string): Document[] {
    return this.documents.filter(d => d.jurisdictionId === jurisdictionId)
  }

  getDocumentsByType(type: DocumentType): Document[] {
    return this.documents.filter(d => d.type === type)
  }

  getSectionsByDocument(documentId: string): Section[] {
    return this.sections.filter(s => s.documentId === documentId)
  }
}
