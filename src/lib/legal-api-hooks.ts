// ============================================================================
// React Query Hooks for Legal Data APIs
// ============================================================================
// Centralizes all data-fetching with proper caching, error handling,
// and loading states via @tanstack/react-query.
// ============================================================================

import { useQuery, useInfiniteQuery } from '@tanstack/react-query'

import {
  searchOpinions,
  getScotusOpinions,
  getOpinionClusters,
  getCourts,
  verifyCitation,
} from './api/court-listener'

import {
  searchDocuments as searchFRDocuments,
  getExecutiveOrders,
  getRecentRules,
  getDocument as getFRDocument,
  getAgencies,
  type FRDocumentType,
} from './api/federal-register'

import {
  getRecentBills,
  getBillDetail,
  getMembers,
  hasCongressApiKey,
  type BillType,
} from './api/congress'

// ---------------------------------------------------------------------------
// CourtListener Hooks
// ---------------------------------------------------------------------------

export function useCaseLawSearch(
  query: string,
  options?: {
    court?: string
    filed_after?: string
    filed_before?: string
    cited_gt?: number
    order_by?: string
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['courtlistener', 'search', query, options],
    queryFn: ({ signal }) => searchOpinions(query, options, signal),
    enabled: enabled && query.length >= 2,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export function useScotusOpinions(
  options?: {
    filed_after?: string
    filed_before?: string
    order_by?: string
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['courtlistener', 'scotus', options],
    queryFn: ({ signal }) => getScotusOpinions(options, signal),
    enabled,
    staleTime: 15 * 60 * 1000,
  })
}

export function useOpinionClusters(
  params?: {
    docket__court?: string
    date_filed__gte?: string
    date_filed__lte?: string
    fields?: string
    order_by?: string
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['courtlistener', 'clusters', params],
    queryFn: ({ signal }) => getOpinionClusters(params, signal),
    enabled,
    staleTime: 15 * 60 * 1000,
  })
}

export function useCourts(
  options?: { jurisdiction?: string },
  enabled = true
) {
  return useQuery({
    queryKey: ['courtlistener', 'courts', options],
    queryFn: ({ signal }) => getCourts(options, signal),
    enabled,
    staleTime: 60 * 60 * 1000, // Courts rarely change
  })
}

export function useCitationVerification(
  citation: string,
  enabled = true
) {
  return useQuery({
    queryKey: ['courtlistener', 'citation-verify', citation],
    queryFn: ({ signal }) => verifyCitation(citation, signal),
    enabled: enabled && citation.length >= 3,
    staleTime: 30 * 60 * 1000,
  })
}

// ---------------------------------------------------------------------------
// Federal Register Hooks
// ---------------------------------------------------------------------------

export function useFederalRegisterSearch(
  query: string,
  options?: {
    type?: FRDocumentType[]
    agencies?: string[]
    order?: 'relevance' | 'newest' | 'oldest'
    per_page?: number
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['federal-register', 'search', query, options],
    queryFn: ({ signal }) => searchFRDocuments(query, options, signal),
    enabled: enabled && query.length >= 2,
    staleTime: 10 * 60 * 1000,
  })
}

export function useExecutiveOrders(
  options?: {
    president?: string
    year?: number
    per_page?: number
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['federal-register', 'executive-orders', options],
    queryFn: ({ signal }) => getExecutiveOrders(options, signal),
    enabled,
    staleTime: 15 * 60 * 1000,
  })
}

export function useRecentRules(
  options?: {
    significant_only?: boolean
    per_page?: number
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['federal-register', 'rules', options],
    queryFn: ({ signal }) => getRecentRules(options, signal),
    enabled,
    staleTime: 10 * 60 * 1000,
  })
}

export function useFRDocument(
  documentNumber: string,
  enabled = true
) {
  return useQuery({
    queryKey: ['federal-register', 'document', documentNumber],
    queryFn: ({ signal }) => getFRDocument(documentNumber, signal),
    enabled: enabled && !!documentNumber,
    staleTime: 60 * 60 * 1000,
  })
}

export function useFederalAgencies(enabled = true) {
  return useQuery({
    queryKey: ['federal-register', 'agencies'],
    queryFn: ({ signal }) => getAgencies(signal),
    enabled,
    staleTime: 24 * 60 * 60 * 1000, // 24 hours
  })
}

// ---------------------------------------------------------------------------
// Congress.gov Hooks
// ---------------------------------------------------------------------------

export function useRecentBills(
  congress?: number,
  options?: { limit?: number; offset?: number },
  enabled = true
) {
  return useQuery({
    queryKey: ['congress', 'bills', congress, options],
    queryFn: ({ signal }) => getRecentBills(congress, options, signal),
    enabled: enabled && hasCongressApiKey(),
    staleTime: 10 * 60 * 1000,
  })
}

export function useBillDetail(
  congress: number,
  billType: BillType,
  billNumber: string,
  enabled = true
) {
  return useQuery({
    queryKey: ['congress', 'bill', congress, billType, billNumber],
    queryFn: ({ signal }) => getBillDetail(congress, billType, billNumber, signal),
    enabled: enabled && hasCongressApiKey() && !!billNumber,
    staleTime: 30 * 60 * 1000,
  })
}

export function useMembers(
  options?: {
    congress?: number
    state?: string
    limit?: number
    offset?: number
  },
  enabled = true
) {
  return useQuery({
    queryKey: ['congress', 'members', options],
    queryFn: ({ signal }) => getMembers(options, signal),
    enabled: enabled && hasCongressApiKey(),
    staleTime: 60 * 60 * 1000,
  })
}
