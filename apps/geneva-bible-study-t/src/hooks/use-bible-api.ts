import { useState, useEffect } from 'react'
import { VerseUnit } from '@/lib/types'
import {
  fetchVerse,
  fetchChapter,
  fetchMultipleTranslations,
  searchBible,
  FetchVerseParams,
  FetchChapterParams
} from '@/lib/bibleApi'
import { useKV } from '@github/spark/hooks'

export function useBibleVerse(params: FetchVerseParams | null) {
  const [verse, setVerse] = useState<VerseUnit | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!params) {
      setVerse(null)
      return
    }

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchVerse(params)
        setVerse(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch verse')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [params?.translationId, params?.bookId, params?.chapter, params?.verse])

  return { verse, loading, error }
}

export function useBibleChapter(params: FetchChapterParams | null) {
  const [verses, setVerses] = useState<VerseUnit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [cache, setCache] = useKV<Record<string, VerseUnit[]>>('bible-chapter-cache', {})

  useEffect(() => {
    if (!params) {
      setVerses([])
      return
    }

    const cacheKey = `${params.translationId}-${params.bookId}-${params.chapter}`

    const fetchData = async () => {
      if (cache && cache[cacheKey]) {
        setVerses(cache[cacheKey])
        return
      }

      setLoading(true)
      setError(null)
      try {
        const data = await fetchChapter(params)
        setVerses(data)
        
        if (data.length > 0 && cache) {
          setCache((currentCache) => ({
            ...currentCache,
            [cacheKey]: data
          }))
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch chapter')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [params?.translationId, params?.bookId, params?.chapter])

  return { verses, loading, error }
}

export function useCompareVerses(
  bookId: string | null,
  chapter: number | null,
  verse: number | null,
  translationIds: string[]
) {
  const [verses, setVerses] = useState<VerseUnit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!bookId || !chapter || !verse || translationIds.length === 0) {
      setVerses([])
      return
    }

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchMultipleTranslations(bookId, chapter, verse, translationIds)
        setVerses(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch verses')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [bookId, chapter, verse, translationIds.join(',')])

  return { verses, loading, error }
}

export function useBibleSearch(query: string, translationId: string = 'kjv') {
  const [results, setResults] = useState<VerseUnit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!query || query.length < 3) {
      setResults([])
      return
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await searchBible(query, translationId)
        setResults(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed')
      } finally {
        setLoading(false)
      }
    }, 500)

    return () => clearTimeout(timeoutId)
  }, [query, translationId])

  return { results, loading, error }
}
