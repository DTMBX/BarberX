import { VerseUnit } from './types'

export interface BibleApiSource {
  id: string
  name: string
  baseUrl: string
  license: string
  translationMapping: Record<string, string>
}

export const bibleApiSources: BibleApiSource[] = [
  {
    id: 'bolls',
    name: 'Bolls Life Bible API',
    baseUrl: 'https://bolls.life/get-verse',
    license: 'Public Domain',
    translationMapping: {
      'geneva': 'geneva',
      'kjv': 'kjv',
      'web': 'web',
      'ylt': 'ylt',
      'asv': 'asv',
      'basicenglish': 'basicenglish',
      'darby': 'darby',
      'douayrheims': 'douayrheims',
      'webster': 'webster',
      'akjv': 'akjv',
      'leb': 'leb',
      'rnkjv': 'rnkjv',
      'emphbbl': 'emphbbl',
      'wb': 'wb',
      'clementine': 'clementine',
      'almeida': 'almeida',
      'rccv': 'rccv',
      'byz': 'byz',
      'elzevir': 'elzevir',
      'kjva': 'kjva',
      'tisch': 'tisch',
      'tr': 'tr',
      'wh': 'wh',
      'lxx': 'lxx',
      'synodal': 'synodal',
      'rst': 'rst',
      'macarther': 'macarther',
      'finpr': 'finpr',
      'danish': 'danish',
      'esperanto': 'esperanto'
    }
  }
]

export interface BollsLifeResponse {
  book: string
  chapter: number
  verse: number
  text: string
}

export interface FetchVerseParams {
  translationId: string
  bookId: string
  chapter: number
  verse: number
}

export interface FetchChapterParams {
  translationId: string
  bookId: string
  chapter: number
}

const bookIdToName: Record<string, string> = {
  'gen': 'Genesis',
  'exo': 'Exodus',
  'lev': 'Leviticus',
  'num': 'Numbers',
  'deu': 'Deuteronomy',
  'jos': 'Joshua',
  'jdg': 'Judges',
  'rut': 'Ruth',
  '1sa': '1 Samuel',
  '2sa': '2 Samuel',
  '1ki': '1 Kings',
  '2ki': '2 Kings',
  '1ch': '1 Chronicles',
  '2ch': '2 Chronicles',
  'ezr': 'Ezra',
  'neh': 'Nehemiah',
  'est': 'Esther',
  'job': 'Job',
  'psa': 'Psalms',
  'pro': 'Proverbs',
  'ecc': 'Ecclesiastes',
  'sng': 'Song of Solomon',
  'isa': 'Isaiah',
  'jer': 'Jeremiah',
  'lam': 'Lamentations',
  'ezk': 'Ezekiel',
  'dan': 'Daniel',
  'hos': 'Hosea',
  'jol': 'Joel',
  'amo': 'Amos',
  'oba': 'Obadiah',
  'jon': 'Jonah',
  'mic': 'Micah',
  'nam': 'Nahum',
  'hab': 'Habakkuk',
  'zep': 'Zephaniah',
  'hag': 'Haggai',
  'zec': 'Zechariah',
  'mal': 'Malachi',
  'mat': 'Matthew',
  'mar': 'Mark',
  'luk': 'Luke',
  'joh': 'John',
  'act': 'Acts',
  'rom': 'Romans',
  '1co': '1 Corinthians',
  '2co': '2 Corinthians',
  'gal': 'Galatians',
  'eph': 'Ephesians',
  'php': 'Philippians',
  'col': 'Colossians',
  '1th': '1 Thessalonians',
  '2th': '2 Thessalonians',
  '1ti': '1 Timothy',
  '2ti': '2 Timothy',
  'tit': 'Titus',
  'phm': 'Philemon',
  'heb': 'Hebrews',
  'jas': 'James',
  '1pe': '1 Peter',
  '2pe': '2 Peter',
  '1jo': '1 John',
  '2jo': '2 John',
  '3jo': '3 John',
  'jud': 'Jude',
  'rev': 'Revelation'
}

export async function fetchVerse(params: FetchVerseParams): Promise<VerseUnit | null> {
  const { translationId, bookId, chapter, verse } = params
  const bookName = bookIdToName[bookId]
  
  if (!bookName) {
    console.error(`Unknown book ID: ${bookId}`)
    return null
  }

  try {
    const url = `https://bolls.life/get-verse/${translationId}/${chapter}/${verse}/${bookName}/`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json() as BollsLifeResponse
    
    return {
      id: `${bookId}-${chapter}-${verse}-${translationId}`,
      workId: bookId,
      chapterNumber: chapter,
      verseNumber: verse,
      translationId,
      text: data.text
    }
  } catch (error) {
    console.error('Error fetching verse:', error)
    return null
  }
}

export async function fetchChapter(params: FetchChapterParams): Promise<VerseUnit[]> {
  const { translationId, bookId, chapter } = params
  const bookName = bookIdToName[bookId]
  
  if (!bookName) {
    console.error(`Unknown book ID: ${bookId}`)
    return []
  }

  try {
    const url = `https://bolls.life/get-chapter/${translationId}/${chapter}/${bookName}/`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json() as BollsLifeResponse[]
    
    return data.map((item) => ({
      id: `${bookId}-${chapter}-${item.verse}-${translationId}`,
      workId: bookId,
      chapterNumber: chapter,
      verseNumber: item.verse,
      translationId,
      text: item.text
    }))
  } catch (error) {
    console.error('Error fetching chapter:', error)
    return []
  }
}

export async function fetchMultipleTranslations(
  bookId: string,
  chapter: number,
  verse: number,
  translationIds: string[]
): Promise<VerseUnit[]> {
  const promises = translationIds.map(translationId =>
    fetchVerse({ translationId, bookId, chapter, verse })
  )
  
  const results = await Promise.all(promises)
  return results.filter((v): v is VerseUnit => v !== null)
}

export async function searchBible(
  query: string,
  translationId: string = 'kjv'
): Promise<VerseUnit[]> {
  try {
    const url = `https://bolls.life/search/${translationId}/${encodeURIComponent(query)}/`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json() as Array<{
      book: string
      chapter: number
      verse: number
      text: string
    }>
    
    return data.map((item) => {
      const bookId = Object.entries(bookIdToName).find(
        ([_, name]) => name.toLowerCase() === item.book.toLowerCase()
      )?.[0] || 'unknown'
      
      return {
        id: `${bookId}-${item.chapter}-${item.verse}-${translationId}`,
        workId: bookId,
        chapterNumber: item.chapter,
        verseNumber: item.verse,
        translationId,
        text: item.text
      }
    })
  } catch (error) {
    console.error('Error searching Bible:', error)
    return []
  }
}
