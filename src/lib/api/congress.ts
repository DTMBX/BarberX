// ============================================================================
// Congress.gov API Client
// https://api.congress.gov/
// ============================================================================
// Free API key from api.data.gov – covers bills, members, committees,
// treaties, Congressional Record, nominations, and more.
//
// IMPORTANT: This is a public educational app. API key is optional.
// Without a key, the app links users directly to congress.gov.
// ============================================================================

import { z } from 'zod'

const BASE_URL = 'https://api.congress.gov/v3'

// ---------------------------------------------------------------------------
// API Key Management (user-provided, stored in localStorage)
// ---------------------------------------------------------------------------

const STORAGE_KEY = 'civics-stack:congress-api-key'

export function getCongressApiKey(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

export function setCongressApiKey(key: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, key)
  } catch {
    // localStorage unavailable
  }
}

export function clearCongressApiKey(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // localStorage unavailable
  }
}

export function hasCongressApiKey(): boolean {
  return !!getCongressApiKey()
}

// ---------------------------------------------------------------------------
// Zod Schemas
// ---------------------------------------------------------------------------

export const BillSchema = z.object({
  congress: z.number().optional(),
  latestAction: z.object({
    actionDate: z.string().optional(),
    text: z.string().optional(),
  }).optional(),
  number: z.string().optional(),
  originChamber: z.string().optional(),
  originChamberCode: z.string().optional(),
  title: z.string().optional(),
  type: z.string().optional(),
  updateDate: z.string().optional(),
  url: z.string().optional(),
})

export const BillDetailSchema = z.object({
  bill: z.object({
    actions: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    amendments: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    cboCostEstimates: z.array(z.any()).optional(),
    committeeReports: z.array(z.any()).optional(),
    committees: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    congress: z.number().optional(),
    constitutionalAuthorityStatementText: z.string().nullable().optional(),
    cosponsors: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    introducedDate: z.string().optional(),
    latestAction: z.object({ actionDate: z.string().optional(), text: z.string().optional() }).optional(),
    laws: z.array(z.object({ number: z.string().optional(), type: z.string().optional() })).optional(),
    number: z.string().optional(),
    originChamber: z.string().optional(),
    policyArea: z.object({ name: z.string().optional() }).nullable().optional(),
    sponsors: z.array(z.object({
      bioguideId: z.string().optional(),
      district: z.number().nullable().optional(),
      firstName: z.string().optional(),
      lastName: z.string().optional(),
      fullName: z.string().optional(),
      party: z.string().optional(),
      state: z.string().optional(),
    })).optional(),
    subjects: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    summaries: z.object({ count: z.number().optional(), url: z.string().optional() }).optional(),
    title: z.string().optional(),
    type: z.string().optional(),
    updateDate: z.string().optional(),
  }),
})

export const MemberSchema = z.object({
  bioguideId: z.string(),
  depiction: z.object({
    attribution: z.string().nullable().optional(),
    imageUrl: z.string().nullable().optional(),
  }).nullable().optional(),
  district: z.number().nullable().optional(),
  name: z.string().optional(),
  party: z.string().optional(),
  state: z.string().optional(),
  terms: z.object({ item: z.array(z.any()).optional() }).optional(),
  updateDate: z.string().optional(),
  url: z.string().optional(),
})

export const CongressionalRecordSchema = z.object({
  issueDate: z.string().optional(),
  issueNumber: z.string().optional(),
  volumeNumber: z.string().optional(),
  congress: z.number().optional(),
  sessionNumber: z.number().optional(),
  url: z.string().optional(),
  updateDate: z.string().optional(),
  links: z.object({
    fullRecord: z.object({ pdf: z.string().optional() }).optional(),
  }).optional(),
})

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type Bill = z.infer<typeof BillSchema>
export type BillDetail = z.infer<typeof BillDetailSchema>
export type Member = z.infer<typeof MemberSchema>
export type CongressionalRecord = z.infer<typeof CongressionalRecordSchema>

export type BillType = 'hr' | 's' | 'hjres' | 'sjres' | 'hconres' | 'sconres' | 'hres' | 'sres'

// ---------------------------------------------------------------------------
// Fetch Helper
// ---------------------------------------------------------------------------

async function congressFetch<T>(
  endpoint: string,
  schema: z.ZodType<T>,
  params?: Record<string, string>,
  signal?: AbortSignal
): Promise<T> {
  const apiKey = getCongressApiKey()
  if (!apiKey) {
    throw new Error('Congress.gov API key required. Get a free key at api.data.gov.')
  }

  const url = new URL(`${BASE_URL}${endpoint}`)
  url.searchParams.set('api_key', apiKey)
  url.searchParams.set('format', 'json')
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (res.status === 429) {
    throw new Error('Rate limit exceeded. Please wait a moment and try again.')
  }
  if (res.status === 403) {
    throw new Error('Invalid API key. Please check your Congress.gov API key.')
  }
  if (!res.ok) {
    throw new Error(`Congress.gov API error: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  return schema.parse(data)
}

// ---------------------------------------------------------------------------
// Public API Functions
// ---------------------------------------------------------------------------

/** Get list of recent bills */
export async function getRecentBills(
  congress?: number,
  options?: { limit?: number; offset?: number },
  signal?: AbortSignal
): Promise<{ bills: Bill[] }> {
  const endpoint = congress ? `/bill/${congress}` : '/bill'
  const params: Record<string, string> = {
    limit: String(options?.limit ?? 20),
  }
  if (options?.offset) params.offset = String(options.offset)

  return congressFetch(
    endpoint,
    z.object({ bills: z.array(BillSchema) }),
    params,
    signal
  )
}

/** Get bill detail */
export async function getBillDetail(
  congress: number,
  billType: BillType,
  billNumber: string,
  signal?: AbortSignal
): Promise<BillDetail> {
  return congressFetch(
    `/bill/${congress}/${billType}/${billNumber}`,
    BillDetailSchema,
    undefined,
    signal
  )
}

/** Search bills by keyword (Congress.gov doesn't have a direct search endpoint,
 *  so we use list + client-side filter, or direct users to congress.gov search) */
export function buildCongressSearchUrl(query: string): string {
  return `https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22${encodeURIComponent(query)}%22%7D`
}

/** Get members of Congress */
export async function getMembers(
  options?: {
    congress?: number
    state?: string
    limit?: number
    offset?: number
  },
  signal?: AbortSignal
): Promise<{ members: Member[] }> {
  let endpoint = '/member'
  if (options?.congress) {
    endpoint = `/member/congress/${options.congress}`
  }
  if (options?.state && !options?.congress) {
    endpoint = `/member/${options.state}`
  }

  const params: Record<string, string> = {
    limit: String(options?.limit ?? 20),
  }
  if (options?.offset) params.offset = String(options.offset)

  return congressFetch(
    endpoint,
    z.object({ members: z.array(MemberSchema) }),
    params,
    signal
  )
}

/** Get recent Congressional Record issues */
export async function getCongressionalRecord(
  signal?: AbortSignal
): Promise<{ congressionalRecord: CongressionalRecord[] }> {
  return congressFetch(
    '/congressional-record',
    z.object({ congressionalRecord: z.array(CongressionalRecordSchema) }),
    { limit: '10' },
    signal
  )
}

// ---------------------------------------------------------------------------
// Direct Links (no API key needed)
// ---------------------------------------------------------------------------

export function buildBillUrl(congress: number, billType: string, number: string): string {
  return `https://www.congress.gov/bill/${toOrdinal(congress)}-congress/${billType.toLowerCase()}/${number}`
}

export function buildMemberUrl(bioguideId: string): string {
  return `https://www.congress.gov/member/${bioguideId}`
}

function toOrdinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}
