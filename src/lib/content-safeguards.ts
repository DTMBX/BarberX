// ============================================================================
// Content Safeguards – Enforce neutral, educational tone
// ============================================================================

import type { ContentSafeguardResult } from './types'

/**
 * Prohibited patterns that indicate inflammatory rhetoric, calls to action
 * against individuals, or violent framing. These are checked case-insensitively.
 */
const PROHIBITED_PATTERNS: RegExp[] = [
  // Direct calls to violence
  /\b(kill|murder|assassinate|attack|shoot|bomb|destroy)\s+(the\s+)?(president|governor|senator|judge|officer|official|politician)/i,
  // Calls to overthrow (outside educational/historical context)
  /\b(overthrow|armed\s+rebellion|take\s+up\s+arms\s+against|violent\s+revolution)\b/i,
  // Hate speech indicators
  /\b(racial\s+supremacy|ethnic\s+cleansing|genocide\s+is\s+(good|justified|necessary))\b/i,
  // Doxxing / targeting individuals
  /\b(home\s+address|personal\s+phone|find\s+where\s+they\s+live)\b/i,
  // Incitement framing
  /\b(we\s+must\s+(fight|war|eliminate|eradicate)\s+(them|those\s+people))\b/i,
]

/**
 * Educational context phrases that should NOT be flagged even if they
 * contain words that might otherwise match prohibited patterns.
 */
const EDUCATIONAL_CONTEXT_PHRASES: RegExp[] = [
  /historical\s+context/i,
  /educational\s+purpose/i,
  /the\s+constitution\s+(states|provides|establishes)/i,
  /according\s+to\s+the\s+(supreme\s+court|constitution|statute)/i,
  /for\s+informational\s+purposes/i,
]

/**
 * Scan content for prohibited rhetoric and return a safeguard result.
 * This runs client-side as a first pass; production deployment should
 * also validate server-side before persisting user-generated content.
 */
export function checkContentSafeguards(content: string): ContentSafeguardResult {
  if (!content || content.trim().length === 0) {
    return { isClean: true, violations: [] }
  }

  // Check if content is in clear educational context
  const isEducational = EDUCATIONAL_CONTEXT_PHRASES.some(p => p.test(content))

  const violations: string[] = []

  for (const pattern of PROHIBITED_PATTERNS) {
    if (pattern.test(content)) {
      // If in educational context, add a note but don't flag
      if (isEducational) continue
      violations.push(
        `Content contains language that may violate platform guidelines: "${content.match(pattern)?.[0]}"`
      )
    }
  }

  return {
    isClean: violations.length === 0,
    violations,
    sanitizedContent: violations.length > 0
      ? '[Content removed – this platform maintains a neutral, educational tone focused on lawful civic engagement.]'
      : undefined,
  }
}

/**
 * Standard disclaimer text that must accompany all analyzer output,
 * explanatory content, and comparison summaries.
 */
export const STANDARD_DISCLAIMERS = {
  notLegalAdvice:
    'This content is for educational and informational purposes only. It does not constitute legal advice. Consult a qualified attorney for legal guidance specific to your situation.',
  neutralTone:
    'This platform presents constitutional and statutory text in a neutral, non-political framework. Content is sourced from official government repositories and is not editorialized.',
  verificationNotice:
    'All legal text displayed on this platform includes source attribution. Users should verify text against official sources before relying on it for any legal purpose.',
  comparisonDisclaimer:
    'Side-by-side comparisons highlight textual similarities and differences for educational purposes. They do not represent legal analysis of constitutional conflicts or preemption.',
  analyzerDisclaimer:
    'The Issue Spotter generates educational summaries to help users identify potential legal questions. It does not analyze the legality or constitutionality of any law, action, or policy. Results should be reviewed by a qualified attorney.',
} as const

/**
 * Validate that user-submitted content (local ordinances, notes, etc.)
 * meets platform standards before storage.
 */
export function validateUserContent(content: string, maxLength: number = 10000): {
  isValid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (content.length > maxLength) {
    errors.push(`Content exceeds maximum length of ${maxLength} characters.`)
  }

  const safeguardResult = checkContentSafeguards(content)
  if (!safeguardResult.isClean) {
    errors.push(...safeguardResult.violations)
  }

  return {
    isValid: errors.length === 0,
    errors,
  }
}
