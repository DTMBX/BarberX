// ============================================================================
// Hierarchy Ladder Utilities – Build & traverse the authority hierarchy
// ============================================================================

import type {
  Document,
  Section,
  Jurisdiction,
  HierarchyNode,
  AuthorityLevel,
  DocumentType,
  AUTHORITY_HIERARCHY,
} from './types'

/**
 * Labels for each rung of the hierarchy ladder,
 * ordered from highest to lowest authority.
 */
export const HIERARCHY_LADDER_RUNGS = [
  { level: 1, label: 'U.S. Constitution', authorityLevel: 'federal' as AuthorityLevel, documentType: 'constitution' as DocumentType },
  { level: 2, label: 'Constitutional Amendments', authorityLevel: 'federal' as AuthorityLevel, documentType: 'amendment' as DocumentType },
  { level: 3, label: 'Treaties', authorityLevel: 'federal' as AuthorityLevel, documentType: 'treaty' as DocumentType },
  { level: 4, label: 'Federal Statutes', authorityLevel: 'federal' as AuthorityLevel, documentType: 'statute' as DocumentType },
  { level: 5, label: 'Federal Regulations', authorityLevel: 'federal' as AuthorityLevel, documentType: 'regulation' as DocumentType },
  { level: 6, label: 'State Constitution', authorityLevel: 'state' as AuthorityLevel, documentType: 'constitution' as DocumentType },
  { level: 7, label: 'State Statutes', authorityLevel: 'state' as AuthorityLevel, documentType: 'statute' as DocumentType },
  { level: 8, label: 'State Regulations', authorityLevel: 'state' as AuthorityLevel, documentType: 'regulation' as DocumentType },
  { level: 9, label: 'Local Authority', authorityLevel: 'local' as AuthorityLevel, documentType: 'ordinance' as DocumentType },
] as const

/**
 * Build a hierarchy tree from documents and sections for a given jurisdiction.
 */
export function buildHierarchyTree(
  documents: Document[],
  sections: Section[],
  selectedJurisdictionId?: string
): HierarchyNode[] {
  const nodes: HierarchyNode[] = []

  for (const rung of HIERARCHY_LADDER_RUNGS) {
    const matchingDocs = documents.filter(d => {
      // For federal items, always include
      if (rung.authorityLevel === 'federal') {
        if (rung.documentType === 'constitution') {
          return d.id === 'us-constitution'
        }
        return d.authorityLevel === 'federal' && d.type === rung.documentType
      }

      // For state/local items, filter by jurisdiction
      if (selectedJurisdictionId) {
        return (
          d.authorityLevel === rung.authorityLevel &&
          d.type === rung.documentType &&
          d.jurisdictionId === selectedJurisdictionId
        )
      }

      return d.authorityLevel === rung.authorityLevel && d.type === rung.documentType
    })

    const sectionCount = matchingDocs.reduce((count, doc) => {
      return count + sections.filter(s => s.documentId === doc.id).length
    }, 0)

    const children: HierarchyNode[] = matchingDocs.map(doc => ({
      level: rung.level,
      label: doc.title,
      authorityLevel: doc.authorityLevel,
      documentType: doc.type,
      documentId: doc.id,
      sectionCount: sections.filter(s => s.documentId === doc.id).length,
      children: [],
      effectiveDate: doc.effectiveDate,
    }))

    // Only show amendments as children of the constitution node
    if (rung.documentType === 'constitution' && rung.authorityLevel === 'federal') {
      const amendmentSections = sections.filter(
        s => s.documentId === 'us-constitution' && s.number.startsWith('Amend.')
      )
      nodes.push({
        level: rung.level,
        label: rung.label,
        authorityLevel: rung.authorityLevel,
        documentType: rung.documentType,
        documentId: 'us-constitution',
        sectionCount: sections.filter(s => s.documentId === 'us-constitution').length,
        children: [],
        effectiveDate: '1789-03-04',
      })
      // Amendments as separate rung
      nodes.push({
        level: 2,
        label: `Amendments (${amendmentSections.length})`,
        authorityLevel: 'federal',
        documentType: 'amendment',
        documentId: 'us-constitution',
        sectionCount: amendmentSections.length,
        children: [],
      })
      continue
    }

    if (rung.documentType === 'amendment' && rung.authorityLevel === 'federal') {
      // Already handled above
      continue
    }

    if (sectionCount > 0 || children.length > 0) {
      nodes.push({
        level: rung.level,
        label: rung.label,
        authorityLevel: rung.authorityLevel,
        documentType: rung.documentType,
        sectionCount,
        children,
        effectiveDate: matchingDocs[0]?.effectiveDate,
      })
    }
  }

  return nodes
}

/**
 * Generate breadcrumb trail from a section back to the top of the hierarchy.
 */
export function buildBreadcrumbs(
  section: Section,
  document: Document,
  jurisdiction: Jurisdiction | undefined,
  documents: Document[],
): { label: string; route?: string; params?: Record<string, string> }[] {
  const crumbs: { label: string; route?: string; params?: Record<string, string> }[] = [
    { label: 'U.S. Constitution', route: 'supreme-law' },
  ]

  if (document.authorityLevel === 'federal') {
    if (document.type === 'constitution') {
      // Within the US Constitution
      if (section.parentSectionId) {
        crumbs.push({ label: document.title, route: 'supreme-law' })
      }
    } else if (document.type === 'treaty') {
      crumbs.push({ label: 'Treaties', route: 'treaties' })
      crumbs.push({ label: document.title, route: 'document', params: { id: document.id } })
    } else {
      crumbs.push({ label: 'Federal Statutes', route: 'supreme-law' })
      crumbs.push({ label: document.title, route: 'document', params: { id: document.id } })
    }
  } else if (document.authorityLevel === 'state' || document.authorityLevel === 'territory') {
    if (jurisdiction) {
      crumbs.push({ label: jurisdiction.name, route: 'my-jurisdiction', params: { jid: jurisdiction.id } })
    }
    crumbs.push({ label: document.title, route: 'document', params: { id: document.id } })
  } else {
    crumbs.push({ label: 'Local Authority', route: 'local' })
    crumbs.push({ label: document.title, route: 'document', params: { id: document.id } })
  }

  crumbs.push({ label: section.title })

  return crumbs
}

/**
 * Determine the hierarchy position number for a document.
 * Lower numbers = higher authority.
 */
export function getHierarchyPosition(doc: Document): number {
  const rung = HIERARCHY_LADDER_RUNGS.find(
    r => r.authorityLevel === doc.authorityLevel && r.documentType === doc.type
  )
  return rung?.level ?? 99
}

/**
 * Compare two documents' authority levels.
 * Returns negative if a is higher authority, positive if b is higher.
 */
export function compareAuthority(a: Document, b: Document): number {
  return getHierarchyPosition(a) - getHierarchyPosition(b)
}
