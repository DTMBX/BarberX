// ============================================================================
// Hash-Based Router – Deep-linkable URLs without external dependencies
// ============================================================================

import { useState, useEffect, useCallback } from 'react'
import type { RouteId, RouteState } from './types'

/**
 * Parse the current window.location.hash into a RouteState.
 *
 * Format: #/{route}?param1=value1&param2=value2
 * Examples:
 *   #/home
 *   #/section?id=us-const-amend14
 *   #/compare?left=us-const-amend1&right=ca-const-art1-s3
 *   #/search?q=due+process&level=federal
 *   #/my-jurisdiction?jid=us-ca
 */
export function parseHash(hash: string): RouteState {
  const cleaned = hash.replace(/^#\/?/, '')
  const [routePart, queryPart] = cleaned.split('?')

  const route = (routePart || 'home') as RouteId
  const params: Record<string, string> = {}

  if (queryPart) {
    const searchParams = new URLSearchParams(queryPart)
    searchParams.forEach((value, key) => {
      params[key] = value
    })
  }

  return { route, params }
}

/**
 * Serialize a RouteState back to a hash string.
 */
export function buildHash(route: RouteId, params?: Record<string, string>): string {
  let hash = `#/${route}`
  if (params && Object.keys(params).length > 0) {
    const search = new URLSearchParams(params)
    hash += `?${search.toString()}`
  }
  return hash
}

/**
 * Navigate to a route by updating window.location.hash.
 */
export function navigateTo(route: RouteId, params?: Record<string, string>): void {
  window.location.hash = buildHash(route, params)
}

/**
 * Build a shareable deep link for a specific section.
 */
export function buildSectionLink(sectionId: string): string {
  return `${window.location.origin}${window.location.pathname}${buildHash('section', { id: sectionId })}`
}

/**
 * Build a shareable deep link for a comparison view.
 */
export function buildCompareLink(leftId: string, rightId: string): string {
  return `${window.location.origin}${window.location.pathname}${buildHash('compare', { left: leftId, right: rightId })}`
}

/**
 * React hook that synchronizes component state with the URL hash.
 * Provides the current route and a navigate function.
 */
export function useHashRouter(): {
  routeState: RouteState
  navigate: (route: RouteId, params?: Record<string, string>) => void
  currentRoute: RouteId
  params: Record<string, string>
} {
  const [routeState, setRouteState] = useState<RouteState>(() =>
    parseHash(window.location.hash)
  )

  useEffect(() => {
    const handleHashChange = () => {
      setRouteState(parseHash(window.location.hash))
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const navigate = useCallback((route: RouteId, params?: Record<string, string>) => {
    navigateTo(route, params)
  }, [])

  return {
    routeState,
    navigate,
    currentRoute: routeState.route,
    params: routeState.params,
  }
}
