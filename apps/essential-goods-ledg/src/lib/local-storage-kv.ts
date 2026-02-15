/**
 * localStorage-based drop-in replacement for @github/spark KV, user, and LLM APIs.
 * This lets the app run as a static site on GitHub Pages without the Spark backend.
 * 
 * Essential Goods Ledger — prefix: essential-goods:
 */

import { useState, useEffect, useCallback } from 'react'

// ── KV Store (replaces window.spark.kv) ──────────────────────────────────

const KV_PREFIX = 'essential-goods:'

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
    window.dispatchEvent(new CustomEvent('kv-change', { detail: { key } }))
  } catch (e) {
    console.warn('localStorage write failed:', e)
  }
}

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

export function useKV<T>(key: string, defaultValue: T): [T | undefined, (updater: Updater<T>) => void] {
  const [value, setValueInternal] = useState<T>(() => {
    const stored = kvGet<T>(key)
    if (stored !== undefined) return stored
    kvSet(key, defaultValue)
    return defaultValue
  })

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

// ── User stub ────────────────────────────────────────────────────────────

export async function getUser(): Promise<{ id: string; login: string }> {
  let userId = localStorage.getItem('essential-goods:user-id')
  if (!userId) {
    userId = `anon-${crypto.randomUUID?.() ?? Date.now()}`
    localStorage.setItem('essential-goods:user-id', userId)
  }
  return { id: userId, login: userId }
}

// ── LLM stub ─────────────────────────────────────────────────────────────

export async function llmStub(_prompt: string): Promise<string> {
  throw new Error(
    'AI analysis requires the GitHub Spark runtime and is not available in the static deployment.'
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

export function installSparkShim(): void {
  if (typeof window === 'undefined') return
  window.spark = {
    kv: localKV,
    user: getUser,
    llm: llmStub,
  }
}
