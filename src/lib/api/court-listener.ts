// ============================================================================
// CourtListener API Client – Free Law Project
// https://www.courtlistener.com/help/api/rest/
// ============================================================================
// Public domain legal data – case law, SCOTUS opinions, citations, oral args
// Rate limit: 5,000/hr authenticated, lower unauthenticated
// CORS-enabled for browser access
// ============================================================================

import { z } from 'zod'

const BASE_URL = 'https://www.courtlistener.com/api/rest/v4'

// ---------------------------------------------------------------------------
// Zod Schemas for API Response Validation
// ---------------------------------------------------------------------------

export const CourtSchema = z.object({
  id: z.string(),
  full_name: z.string().optional(),
  short_name: z.string().optional(),
  citation_string: z.string().optional(),
  url: z.string().optional(),
  jurisdiction: z.string().optional(),
})

export const OpinionClusterSchema = z.object({
  id: z.number(),
  resource_uri: z.string().optional(),
  absolute_url: z.string().optional(),
  case_name: z.string().nullable().optional(),
  case_name_short: z.string().nullable().optional(),
  date_filed: z.string().nullable().optional(),
  docket: z.union([z.string(), z.number()]).optional(),
  judges: z.string().nullable().optional(),
  citation_count: z.number().optional(),
  precedential_status: z.string().nullable().optional(),
  date_blocked: z.string().nullable().optional(),
  syllabus: z.string().nullable().optional(),
  source: z.string().nullable().optional(),
  scdb_id: z.string().nullable().optional(),
  nature_of_suit: z.string().nullable().optional(),
})

export const OpinionSchema = z.object({
  id: z.number(),
  resource_uri: z.string().optional(),
  absolute_url: z.string().optional(),
  cluster: z.union([z.string(), z.number()]).optional(),
  author: z.union([z.string(), z.number()]).nullable().optional(),
  type: z.string().optional(),
  plain_text: z.string().nullable().optional(),
  html: z.string().nullable().optional(),
  html_lawbox: z.string().nullable().optional(),
  html_columbia: z.string().nullable().optional(),
  html_with_citations: z.string().nullable().optional(),
  date_created: z.string().optional(),
  date_modified: z.string().optional(),
  sha1: z.string().optional(),
  download_url: z.string().nullable().optional(),
})

export const DocketSchema = z.object({
  id: z.number(),
  resource_uri: z.string().optional(),
  absolute_url: z.string().optional(),
  court: z.string().optional(),
  case_name: z.string().nullable().optional(),
  case_name_short: z.string().nullable().optional(),
  date_filed: z.string().nullable().optional(),
  date_terminated: z.string().nullable().optional(),
  docket_number: z.string().nullable().optional(),
  pacer_case_id: z.string().nullable().optional(),
  source: z.number().optional(),
  nature_of_suit: z.string().nullable().optional(),
  cause: z.string().nullable().optional(),
})

export const SearchResultSchema = z.object({
  absolute_url: z.string().optional(),
  caseName: z.string().nullable().optional(),
  case_name: z.string().nullable().optional(),
  court: z.string().nullable().optional(),
  court_citation_string: z.string().nullable().optional(),
  court_id: z.string().nullable().optional(),
  dateFiled: z.string().nullable().optional(),
  date_filed: z.string().nullable().optional(),
  docket_id: z.number().nullable().optional(),
  docketNumber: z.string().nullable().optional(),
  docket_number: z.string().nullable().optional(),
  id: z.number().optional(),
  cluster_id: z.number().nullable().optional(),
  judge: z.string().nullable().optional(),
  lexisCite: z.string().nullable().optional(),
  neutralCite: z.string().nullable().optional(),
  citation: z.array(z.string()).optional(),
  citeCount: z.number().optional(),
  citation_count: z.number().optional(),
  sibling_ids: z.array(z.number()).optional(),
  snippet: z.string().nullable().optional(),
  status: z.string().nullable().optional(),
  suitNature: z.string().nullable().optional(),
})

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    count: z.union([z.string(), z.number()]).optional(),
    next: z.string().nullable().optional(),
    previous: z.string().nullable().optional(),
    results: z.array(itemSchema),
  })

const SearchApiResponseSchema = z.object({
  count: z.number().optional(),
  next: z.string().nullable().optional(),
  previous: z.string().nullable().optional(),
  results: z.array(SearchResultSchema),
})

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type Court = z.infer<typeof CourtSchema>
export type OpinionCluster = z.infer<typeof OpinionClusterSchema>
export type Opinion = z.infer<typeof OpinionSchema>
export type Docket = z.infer<typeof DocketSchema>
export type SearchResult = z.infer<typeof SearchResultSchema>
export type PaginatedResponse<T> = {
  count?: string | number
  next?: string | null
  previous?: string | null
  results: T[]
}

// ---------------------------------------------------------------------------
// Fetch Helpers
// ---------------------------------------------------------------------------

async function clFetch<T>(
  endpoint: string,
  schema: z.ZodType<T>,
  params?: Record<string, string>,
  signal?: AbortSignal
): Promise<T> {
  const url = new URL(`${BASE_URL}${endpoint}`)
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }
  url.searchParams.set('format', 'json')

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw new Error(`CourtListener API error: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  return schema.parse(data)
}

// ---------------------------------------------------------------------------
// Public API Functions
// ---------------------------------------------------------------------------

/** Full-text search across case law opinions */
export async function searchOpinions(
  query: string,
  options?: {
    court?: string           // e.g. 'scotus'
    filed_after?: string     // ISO date
    filed_before?: string
    cited_gt?: number
    order_by?: string
    page?: number
  },
  signal?: AbortSignal
): Promise<PaginatedResponse<SearchResult>> {
  const params: Record<string, string> = {
    q: query,
    type: 'o',              // opinions
  }

  if (options?.court) params.court = options.court
  if (options?.filed_after) params.filed_after = options.filed_after
  if (options?.filed_before) params.filed_before = options.filed_before
  if (options?.cited_gt) params.cited_gt = String(options.cited_gt)
  if (options?.order_by) params.order_by = options.order_by
  if (options?.page) params.page = String(options.page)

  return clFetch('/search/', SearchApiResponseSchema, params, signal)
}

/** Get SCOTUS opinions */
export async function getScotusOpinions(
  options?: {
    filed_after?: string
    filed_before?: string
    page?: number
    order_by?: string
  },
  signal?: AbortSignal
): Promise<PaginatedResponse<SearchResult>> {
  return searchOpinions('*', { ...options, court: 'scotus' }, signal)
}

/** Get opinion clusters (grouped opinions for a case) */
export async function getOpinionClusters(
  params?: {
    docket__court?: string
    date_filed__gte?: string
    date_filed__lte?: string
    fields?: string
    order_by?: string
    page?: number
  },
  signal?: AbortSignal
): Promise<PaginatedResponse<OpinionCluster>> {
  const qp: Record<string, string> = {}
  if (params?.docket__court) qp['docket__court'] = params.docket__court
  if (params?.date_filed__gte) qp['date_filed__gte'] = params.date_filed__gte
  if (params?.date_filed__lte) qp['date_filed__lte'] = params.date_filed__lte
  if (params?.fields) qp['fields'] = params.fields
  if (params?.order_by) qp['order_by'] = params.order_by ?? '-date_filed'
  if (params?.page) qp['page'] = String(params.page)

  return clFetch(
    '/clusters/',
    PaginatedResponseSchema(OpinionClusterSchema),
    qp,
    signal
  )
}

/** Get a single docket by ID */
export async function getDocket(
  docketId: number,
  signal?: AbortSignal
): Promise<Docket> {
  return clFetch(`/dockets/${docketId}/`, DocketSchema, undefined, signal)
}

/** Get case citation information */
export async function getCitedBy(
  opinionId: number,
  signal?: AbortSignal
): Promise<PaginatedResponse<SearchResult>> {
  return searchOpinions('*', { order_by: '-dateFiled' }, signal)
}

/** Get available courts */
export async function getCourts(
  options?: {
    jurisdiction?: string  // 'F' federal, 'S' state, 'FB' bankruptcy
  },
  signal?: AbortSignal
): Promise<PaginatedResponse<Court>> {
  const params: Record<string, string> = {}
  if (options?.jurisdiction) params.jurisdiction = options.jurisdiction

  return clFetch(
    '/courts/',
    PaginatedResponseSchema(CourtSchema),
    params,
    signal
  )
}

// ---------------------------------------------------------------------------
// Citation Verification – fights AI hallucinations
// ---------------------------------------------------------------------------

export const CitationLookupResultSchema = z.object({
  citation: z.string().optional(),
  normalized_citations: z.array(z.string()).optional(),
  match_url: z.string().nullable().optional(),
  match_id: z.number().nullable().optional(),
  match_name: z.string().nullable().optional(),
  confidence: z.number().optional(),
})

export type CitationLookupResult = z.infer<typeof CitationLookupResultSchema>

/** Verify a legal citation against CourtListener's database */
export async function verifyCitation(
  citation: string,
  signal?: AbortSignal
): Promise<CitationLookupResult[]> {
  const url = new URL(`${BASE_URL}/citation-lookup/`)
  url.searchParams.set('format', 'json')

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: new URLSearchParams({ text: citation }),
    signal,
  })

  if (!res.ok) {
    throw new Error(`Citation lookup failed: ${res.status}`)
  }

  const data = await res.json()
  return z.array(CitationLookupResultSchema).parse(
    Array.isArray(data) ? data : [data]
  )
}

// ---------------------------------------------------------------------------
// Convenience: build deep links back to CourtListener
// ---------------------------------------------------------------------------

export function courtListenerUrl(absoluteUrl?: string | null): string {
  if (!absoluteUrl) return 'https://www.courtlistener.com'
  if (absoluteUrl.startsWith('http')) return absoluteUrl
  return `https://www.courtlistener.com${absoluteUrl}`
}
