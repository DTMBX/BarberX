/**
 * localStorage-based drop-in replacement for @github/spark KV, user, and LLM APIs.
 * This lets the app run as a static site on GitHub Pages without the Spark backend.
 */

import { useState, useEffect, useCallback, useRef, useSyncExternalStore } from 'react'

// ── KV Store (replaces window.spark.kv) ──────────────────────────────────

const KV_PREFIX = 'civics-stack:'

function kvGet<T>(key: string): T | undefined {
  try {
    const raw = localStorage.getItem(KV_PREFIX + key)
    return raw ? (JSON.parse(raw) as T) : undefined
  } catch {
    return undefined
  }
}

function kvSet<T>(key: string, value: T): void {
  try {
    localStorage.setItem(KV_PREFIX + key, JSON.stringify(value))
    // Notify same-tab listeners
    window.dispatchEvent(new CustomEvent('kv-change', { detail: { key } }))
  } catch (e) {
    console.warn('localStorage write failed:', e)
  }
}

/** Async-compatible KV interface matching window.spark.kv */
export const localKV = {
  async get<T>(key: string): Promise<T | undefined> {
    return kvGet<T>(key)
  },
  async set<T>(key: string, value: T): Promise<void> {
    kvSet(key, value)
  },
}

// ── useKV hook (replaces @github/spark/hooks useKV) ──────────────────────

type Updater<T> = T | ((prev: T | undefined) => T)

/**
 * React hook that persists state in localStorage, matching the useKV API:
 *   const [value, setValue] = useKV<T>(key, defaultValue)
 */
export function useKV<T>(key: string, defaultValue: T): [T | undefined, (updater: Updater<T>) => void] {
  // Initialise from storage or default
  const [value, setValueInternal] = useState<T>(() => {
    const stored = kvGet<T>(key)
    if (stored !== undefined) return stored
    // Persist the default on first access
    kvSet(key, defaultValue)
    return defaultValue
  })

  // Listen for cross-component and cross-tab updates
  useEffect(() => {
    const onKvChange = (e: Event) => {
      const detail = (e as CustomEvent).detail
      if (detail?.key === key) {
        const fresh = kvGet<T>(key)
        if (fresh !== undefined) setValueInternal(fresh)
      }
    }
    const onStorage = (e: StorageEvent) => {
      if (e.key === KV_PREFIX + key && e.newValue) {
        try {
          setValueInternal(JSON.parse(e.newValue) as T)
        } catch { /* ignore */ }
      }
    }

    window.addEventListener('kv-change', onKvChange)
    window.addEventListener('storage', onStorage)
    return () => {
      window.removeEventListener('kv-change', onKvChange)
      window.removeEventListener('storage', onStorage)
    }
  }, [key])

  const setValue = useCallback(
    (updater: Updater<T>) => {
      setValueInternal(prev => {
        const next = typeof updater === 'function'
          ? (updater as (prev: T | undefined) => T)(prev)
          : updater
        kvSet(key, next)
        return next
      })
    },
    [key],
  )

  return [value, setValue]
}

// ── User stub (replaces window.spark.user()) ─────────────────────────────

export async function getUser(): Promise<{ id: string; login: string }> {
  // Generate a stable anonymous identity persisted in localStorage
  let userId = localStorage.getItem('civics-stack:user-id')
  if (!userId) {
    userId = `anon-${crypto.randomUUID?.() ?? Date.now()}`
    localStorage.setItem('civics-stack:user-id', userId)
  }
  return { id: userId, login: userId }
}

// ── LLM stub (replaces window.spark.llm) ─────────────────────────────────

export async function llmStub(_prompt: string, _model?: string, _json?: boolean): Promise<string> {
  // Without a Spark backend the LLM endpoint is unavailable.
  // Return a descriptive error so callers can show meaningful UI.
  throw new Error(
    'AI analysis requires the GitHub Spark runtime and is not available in the static deployment. ' +
    'Tag your citations manually or run this app inside GitHub Spark for AI-powered features.'
  )
}

// ── Install shim on window.spark ─────────────────────────────────────────

declare global {
  interface Window {
    spark: {
      kv: { get: <T>(key: string) => Promise<T | undefined>; set: <T>(key: string, value: T) => Promise<void> }
      user: () => Promise<{ id: string; login: string }>
      llm: (prompt: string, model?: string, json?: boolean) => Promise<string>
    }
  }
}

/**
 * Call once at app startup (before any component renders) to install the
 * localStorage-backed shim on window.spark so that all existing code
 * referencing window.spark.kv / window.spark.user() keeps working.
 */
export function installSparkShim(): void {
  if (typeof window === 'undefined') return

  window.spark = {
    kv: localKV,
    user: getUser,
    llm: llmStub,
  }
}
