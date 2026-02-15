// ============================================================================
// Source Registry Data – Populated provenance for all seed documents
// ============================================================================

import type { SourceRegistryEntry } from './types'

/**
 * Pre-populated source registry entries for all constitutional documents.
 * Each entry records the official source URL, publisher, retrieval method,
 * and verification metadata.
 *
 * This data is loaded into KV storage on first run to populate the
 * provenance panel for every document.
 */
export const sourceRegistryData: SourceRegistryEntry[] = [
  // ── U.S. Constitution ────────────────────────────────────────────────
  {
    id: 'src-us-constitution',
    officialUrl: 'https://www.archives.gov/founding-docs/constitution-transcript',
    publisher: 'National Archives and Records Administration (NARA)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'nara-const-2025',
    isOfficialSource: true,
    mirrorUrl: 'https://constitution.congress.gov/constitution/',
    curatorJustification: 'Official transcript maintained by NARA, the custodial agency for the original document.',
    lastVerified: '2025-01-15T00:00:00Z',
  },

  // ── Federal Statutes ─────────────────────────────────────────────────
  {
    id: 'src-usc-title-18',
    officialUrl: 'https://uscode.house.gov/view.xhtml?path=/prelim@title18&edition=prelim',
    publisher: 'Office of the Law Revision Counsel, U.S. House of Representatives',
    retrievalMethod: 'api',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'olrc-t18-2025',
    isOfficialSource: true,
    curatorJustification: 'OLRC is the official publisher of the United States Code.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-usc-title-42',
    officialUrl: 'https://uscode.house.gov/view.xhtml?path=/prelim@title42&edition=prelim',
    publisher: 'Office of the Law Revision Counsel, U.S. House of Representatives',
    retrievalMethod: 'api',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'olrc-t42-2025',
    isOfficialSource: true,
    curatorJustification: 'OLRC is the official publisher of the United States Code.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-civil-rights-act',
    officialUrl: 'https://www.archives.gov/milestone-documents/civil-rights-act',
    publisher: 'National Archives and Records Administration (NARA)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'nara-cra-2025',
    isOfficialSource: true,
    curatorJustification: 'NARA milestone document with authenticated text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-voting-rights-act',
    officialUrl: 'https://www.archives.gov/milestone-documents/voting-rights-act',
    publisher: 'National Archives and Records Administration (NARA)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'nara-vra-2025',
    isOfficialSource: true,
    curatorJustification: 'NARA milestone document with authenticated text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-ada',
    officialUrl: 'https://www.ada.gov/law-and-regs/ada/',
    publisher: 'U.S. Department of Justice',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'doj-ada-2025',
    isOfficialSource: true,
    curatorJustification: 'DOJ is the primary enforcement agency and maintains official ADA text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-foia',
    officialUrl: 'https://www.foia.gov/',
    publisher: 'U.S. Department of Justice, Office of Information Policy',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'doj-foia-2025',
    isOfficialSource: true,
    curatorJustification: 'Official FOIA.gov portal maintained by DOJ OIP.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-privacy-act',
    officialUrl: 'https://www.justice.gov/opcl/privacy-act-1974',
    publisher: 'U.S. Department of Justice, Office of Privacy and Civil Liberties',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'doj-pa-2025',
    isOfficialSource: true,
    curatorJustification: 'DOJ OPCL is the authoritative federal source for Privacy Act text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },

  // ── Treaties ─────────────────────────────────────────────────────────
  {
    id: 'src-un-charter',
    officialUrl: 'https://www.un.org/en/about-us/un-charter',
    publisher: 'United Nations',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'un-charter-2025',
    isOfficialSource: true,
    curatorJustification: 'Official UN website hosts the authenticated Charter text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-geneva-conventions',
    officialUrl: 'https://www.icrc.org/en/war-and-law/treaties-customary-law/geneva-conventions',
    publisher: 'International Committee of the Red Cross (ICRC)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'icrc-gc-2025',
    isOfficialSource: true,
    curatorJustification: 'ICRC is the depositary for the Geneva Conventions.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-nato-treaty',
    officialUrl: 'https://www.nato.int/cps/en/natolive/official_texts_17120.htm',
    publisher: 'North Atlantic Treaty Organization (NATO)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'nato-treaty-2025',
    isOfficialSource: true,
    curatorJustification: 'Official NATO website with authenticated treaty text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-udhr',
    officialUrl: 'https://www.un.org/en/about-us/universal-declaration-of-human-rights',
    publisher: 'United Nations',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'un-udhr-2025',
    isOfficialSource: true,
    curatorJustification: 'Official UN UDHR page.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
  {
    id: 'src-iccpr',
    officialUrl: 'https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights',
    publisher: 'UN Office of the High Commissioner for Human Rights (OHCHR)',
    retrievalMethod: 'manual',
    retrievedAt: '2025-01-15T00:00:00Z',
    checksum: 'ohchr-iccpr-2025',
    isOfficialSource: true,
    curatorJustification: 'OHCHR hosts the authenticated ICCPR text.',
    lastVerified: '2025-01-15T00:00:00Z',
  },
]

/**
 * Map document IDs to their source registry entry IDs.
 */
export const documentSourceMap: Record<string, string> = {
  'us-constitution': 'src-us-constitution',
  'usc-title-18': 'src-usc-title-18',
  'usc-title-42': 'src-usc-title-42',
  'civil-rights-act-1964': 'src-civil-rights-act',
  'voting-rights-act-1965': 'src-voting-rights-act',
  'ada-1990': 'src-ada',
  'foia': 'src-foia',
  'privacy-act-1974': 'src-privacy-act',
  'treaty-un-charter': 'src-un-charter',
  'treaty-geneva-conventions': 'src-geneva-conventions',
  'treaty-nato': 'src-nato-treaty',
  'treaty-udhr': 'src-udhr',
  'treaty-iccpr': 'src-iccpr',
}

/**
 * Get the source registry entry for a document.
 */
export function getSourceForDocument(documentId: string): SourceRegistryEntry | undefined {
  const sourceId = documentSourceMap[documentId]
  if (!sourceId) {
    // For state constitutions, create a generic entry based on the document's source URL
    return undefined
  }
  return sourceRegistryData.find(s => s.id === sourceId)
}

/**
 * Initialize the source registry in KV storage (idempotent).
 */
export async function initializeSourceRegistry(): Promise<void> {
  const existing = await window.spark.kv.get<SourceRegistryEntry[]>('source-registry')
  if (!existing || existing.length === 0) {
    await window.spark.kv.set('source-registry', sourceRegistryData)
  }
}
