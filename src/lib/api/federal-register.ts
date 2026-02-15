// ============================================================================
// Federal Register API Client
// https://www.federalregister.gov/developers/documentation/api/v1
// ============================================================================
// Free, no authentication required, CORS-enabled
// Provides access to the daily journal of the U.S. Government:
//   - Presidential Documents (Executive Orders, Proclamations)
//   - Rules & Regulations (from federal agencies)
//   - Proposed Rules (notice-and-comment rulemaking)
//   - Notices
// ============================================================================

import { z } from 'zod'

const BASE_URL = 'https://www.federalregister.gov/api/v1'

// ---------------------------------------------------------------------------
// Zod Schemas
// ---------------------------------------------------------------------------

export const FRDocumentSchema = z.object({
  abstract: z.string().nullable().optional(),
  action: z.string().nullable().optional(),
  agencies: z.array(z.object({
    raw_name: z.string().optional(),
    name: z.string().optional(),
    id: z.number().optional(),
    url: z.string().optional(),
    slug: z.string().optional(),
    parent_id: z.number().nullable().optional(),
  })).optional(),
  body_html_url: z.string().nullable().optional(),
  citation: z.string().nullable().optional(),
  comment_url: z.string().nullable().optional(),
  corrections: z.array(z.any()).optional(),
  dates: z.string().nullable().optional(),
  document_number: z.string(),
  end_page: z.number().nullable().optional(),
  excerpts: z.string().nullable().optional(),
  executive_order_notes: z.string().nullable().optional(),
  executive_order_number: z.number().nullable().optional(),
  full_text_xml_url: z.string().nullable().optional(),
  html_url: z.string().nullable().optional(),
  json_url: z.string().nullable().optional(),
  pdf_url: z.string().nullable().optional(),
  president: z.object({
    name: z.string().optional(),
    identifier: z.string().optional(),
  }).nullable().optional(),
  publication_date: z.string().optional(),
  regulation_id_number_info: z.record(z.any()).optional(),
  signing_date: z.string().nullable().optional(),
  start_page: z.number().nullable().optional(),
  subtype: z.string().nullable().optional(),
  title: z.string(),
  toc_doc: z.string().nullable().optional(),
  toc_subject: z.string().nullable().optional(),
  type: z.string().optional(),
  volume: z.number().nullable().optional(),
})

export const FRSearchResponseSchema = z.object({
  count: z.number(),
  description: z.string().optional(),
  total_pages: z.number().optional(),
  next_page_url: z.string().nullable().optional(),
  previous_page_url: z.string().nullable().optional(),
  results: z.array(FRDocumentSchema),
})

export const FRAgencySchema = z.object({
  id: z.number(),
  name: z.string(),
  short_name: z.string().nullable().optional(),
  slug: z.string(),
  url: z.string().optional(),
  description: z.string().nullable().optional(),
  recent_articles_url: z.string().nullable().optional(),
  parent_id: z.number().nullable().optional(),
  logo: z.string().nullable().optional(),
})

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type FRDocument = z.infer<typeof FRDocumentSchema>
export type FRSearchResponse = z.infer<typeof FRSearchResponseSchema>
export type FRAgency = z.infer<typeof FRAgencySchema>

export type FRDocumentType =
  | 'RULE'           // Final rules
  | 'PRORULE'        // Proposed rules
  | 'NOTICE'         // Notices
  | 'PRESDOCU'       // Presidential documents

export const FR_DOC_TYPE_LABELS: Record<FRDocumentType, string> = {
  RULE: 'Final Rule',
  PRORULE: 'Proposed Rule',
  NOTICE: 'Notice',
  PRESDOCU: 'Presidential Document',
}

// ---------------------------------------------------------------------------
// Fetch Helper
// ---------------------------------------------------------------------------

async function frFetch<T>(
  endpoint: string,
  schema: z.ZodType<T>,
  params?: Record<string, string>,
  signal?: AbortSignal
): Promise<T> {
  const url = new URL(`${BASE_URL}${endpoint}`)
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw new Error(`Federal Register API error: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  return schema.parse(data)
}

// ---------------------------------------------------------------------------
// Public API Functions
// ---------------------------------------------------------------------------

/** Search Federal Register documents */
export async function searchDocuments(
  query: string,
  options?: {
    type?: FRDocumentType[]        // Filter by document type
    agencies?: string[]            // Filter by agency slug
    page?: number
    per_page?: number              // Max 1000
    order?: 'relevance' | 'newest' | 'oldest' | 'executive_order_number'
  },
  signal?: AbortSignal
): Promise<FRSearchResponse> {
  const params: Record<string, string> = {}

  if (query) params['conditions[term]'] = query
  if (options?.page) params.page = String(options.page)
  if (options?.per_page) params.per_page = String(options.per_page ?? 20)
  if (options?.order) params.order = options.order

  if (options?.type?.length) {
    options.type.forEach((t, i) => {
      params[`conditions[type][]`] = t // only last one wins with this approach
    })
    // Actually need to build URL manually for array params
  }

  // Build URL with proper array param handling
  const url = new URL(`${BASE_URL}/documents.json`)
  if (query) url.searchParams.set('conditions[term]', query)
  if (options?.page) url.searchParams.set('page', String(options.page))
  url.searchParams.set('per_page', String(options?.per_page ?? 20))
  if (options?.order) url.searchParams.set('order', options.order)

  if (options?.type?.length) {
    options.type.forEach(t => url.searchParams.append('conditions[type][]', t))
  }
  if (options?.agencies?.length) {
    options.agencies.forEach(a => url.searchParams.append('conditions[agencies][]', a))
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw new Error(`Federal Register search error: ${res.status}`)
  }

  const data = await res.json()
  return FRSearchResponseSchema.parse(data)
}

/** Get Executive Orders */
export async function getExecutiveOrders(
  options?: {
    president?: string  // e.g. 'joe-biden', 'donald-trump'
    year?: number
    page?: number
    per_page?: number
  },
  signal?: AbortSignal
): Promise<FRSearchResponse> {
  const url = new URL(`${BASE_URL}/documents.json`)
  url.searchParams.set('conditions[type][]', 'PRESDOCU')
  url.searchParams.set('conditions[presidential_document_type][]', 'executive_order')
  url.searchParams.set('per_page', String(options?.per_page ?? 20))
  url.searchParams.set('order', 'newest')

  if (options?.president) {
    url.searchParams.set('conditions[president][]', options.president)
  }
  if (options?.year) {
    url.searchParams.set('conditions[publication_date][year]', String(options.year))
  }
  if (options?.page) {
    url.searchParams.set('page', String(options.page))
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw new Error(`Federal Register EO error: ${res.status}`)
  }

  const data = await res.json()
  return FRSearchResponseSchema.parse(data)
}

/** Get recent significant rules & regulations */
export async function getRecentRules(
  options?: {
    significant_only?: boolean
    page?: number
    per_page?: number
  },
  signal?: AbortSignal
): Promise<FRSearchResponse> {
  const url = new URL(`${BASE_URL}/documents.json`)
  url.searchParams.set('conditions[type][]', 'RULE')
  url.searchParams.set('per_page', String(options?.per_page ?? 20))
  url.searchParams.set('order', 'newest')

  if (options?.significant_only) {
    url.searchParams.set('conditions[significant]', '1')
  }
  if (options?.page) {
    url.searchParams.set('page', String(options.page))
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw new Error(`Federal Register rules error: ${res.status}`)
  }

  const data = await res.json()
  return FRSearchResponseSchema.parse(data)
}

/** Get a specific document by number */
export async function getDocument(
  documentNumber: string,
  signal?: AbortSignal
): Promise<FRDocument> {
  return frFetch(
    `/documents/${documentNumber}.json`,
    FRDocumentSchema,
    undefined,
    signal
  )
}

/** Get list of federal agencies */
export async function getAgencies(
  signal?: AbortSignal
): Promise<FRAgency[]> {
  return frFetch('/agencies.json', z.array(FRAgencySchema), undefined, signal)
}
