import { ReadingPlan } from './types'

export const readingPlans: ReadingPlan[] = [
  {
    id: 'one-year-canonical',
    name: 'One Year - Canonical Order',
    description: 'Read through the entire Bible in one year, following traditional book order from Genesis to Revelation.',
    duration: 365,
    category: 'canonical',
    days: generateOneYearCanonicalPlan()
  },
  {
    id: 'ninety-day-new-testament',
    name: '90 Days - New Testament',
    description: 'Complete the New Testament in 90 days with 3 chapters per day.',
    duration: 90,
    category: 'canonical',
    days: generateNinetyDayNewTestamentPlan()
  },
  {
    id: 'one-year-chronological',
    name: 'One Year - Chronological',
    description: 'Read the Bible in the order events occurred, not in canonical book order.',
    duration: 365,
    category: 'chronological',
    days: generateOneYearChronologicalPlan()
  },
  {
    id: 'gospels-thirty-days',
    name: '30 Days - Four Gospels',
    description: 'Journey through Matthew, Mark, Luke, and John in one month.',
    duration: 30,
    category: 'thematic',
    days: generateGospelsThirtyDaysPlan()
  },
  {
    id: 'psalms-psalms-proverbs',
    name: 'Psalms & Proverbs - 31 Days',
    description: 'Read 5 Psalms and 1 Proverbs chapter daily for a month of wisdom.',
    duration: 31,
    category: 'devotional',
    days: generatePsalmsPrverbsPlan()
  },
  {
    id: 'pauline-epistles',
    name: 'Pauline Epistles - 45 Days',
    description: "Study all of Paul's letters in depth over 45 days.",
    duration: 45,
    category: 'thematic',
    days: generatePaulineEpistlesPlan()
  }
]

function generateOneYearCanonicalPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  const books = [
    { id: 'gen', chapters: 50 },
    { id: 'exo', chapters: 40 },
    { id: 'lev', chapters: 27 },
    { id: 'num', chapters: 36 },
    { id: 'deu', chapters: 34 },
    { id: 'jos', chapters: 24 },
    { id: 'jdg', chapters: 21 },
    { id: 'rut', chapters: 4 },
    { id: '1sa', chapters: 31 },
    { id: '2sa', chapters: 24 },
    { id: '1ki', chapters: 22 },
    { id: '2ki', chapters: 25 },
    { id: '1ch', chapters: 29 },
    { id: '2ch', chapters: 36 },
    { id: 'ezr', chapters: 10 },
    { id: 'neh', chapters: 13 },
    { id: 'est', chapters: 10 },
    { id: 'job', chapters: 42 },
    { id: 'psa', chapters: 150 },
    { id: 'pro', chapters: 31 },
    { id: 'ecc', chapters: 12 },
    { id: 'sng', chapters: 8 },
    { id: 'isa', chapters: 66 },
    { id: 'jer', chapters: 52 },
    { id: 'lam', chapters: 5 },
    { id: 'ezk', chapters: 48 },
    { id: 'dan', chapters: 12 },
    { id: 'hos', chapters: 14 },
    { id: 'jol', chapters: 3 },
    { id: 'amo', chapters: 9 },
    { id: 'oba', chapters: 1 },
    { id: 'jon', chapters: 4 },
    { id: 'mic', chapters: 7 },
    { id: 'nam', chapters: 3 },
    { id: 'hab', chapters: 3 },
    { id: 'zep', chapters: 3 },
    { id: 'hag', chapters: 2 },
    { id: 'zec', chapters: 14 },
    { id: 'mal', chapters: 4 },
    { id: 'mat', chapters: 28 },
    { id: 'mrk', chapters: 16 },
    { id: 'luk', chapters: 24 },
    { id: 'jhn', chapters: 21 },
    { id: 'act', chapters: 28 },
    { id: 'rom', chapters: 16 },
    { id: '1co', chapters: 16 },
    { id: '2co', chapters: 13 },
    { id: 'gal', chapters: 6 },
    { id: 'eph', chapters: 6 },
    { id: 'php', chapters: 4 },
    { id: 'col', chapters: 4 },
    { id: '1th', chapters: 5 },
    { id: '2th', chapters: 3 },
    { id: '1ti', chapters: 6 },
    { id: '2ti', chapters: 4 },
    { id: 'tit', chapters: 3 },
    { id: 'phm', chapters: 1 },
    { id: 'heb', chapters: 13 },
    { id: 'jas', chapters: 5 },
    { id: '1pe', chapters: 5 },
    { id: '2pe', chapters: 3 },
    { id: '1jn', chapters: 5 },
    { id: '2jn', chapters: 1 },
    { id: '3jn', chapters: 1 },
    { id: 'jud', chapters: 1 },
    { id: 'rev', chapters: 22 }
  ]
  
  const totalChapters = books.reduce((sum, book) => sum + book.chapters, 0)
  const chaptersPerDay = Math.ceil(totalChapters / 365)
  
  let dayNum = 1
  let currentChapter = 0
  
  for (const book of books) {
    for (let chapter = 1; chapter <= book.chapters; chapter++) {
      if (currentChapter % chaptersPerDay === 0 && dayNum <= 365) {
        plan.push({
          day: dayNum,
          readings: []
        })
      }
      
      if (plan[dayNum - 1]) {
        plan[dayNum - 1].readings.push({
          workId: book.id,
          chapterNumber: chapter,
          verseNumber: 1
        })
      }
      
      currentChapter++
      if (currentChapter % chaptersPerDay === 0) {
        dayNum++
      }
    }
  }
  
  return plan
}

function generateNinetyDayNewTestamentPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  const ntBooks = [
    { id: 'mat', chapters: 28 },
    { id: 'mrk', chapters: 16 },
    { id: 'luk', chapters: 24 },
    { id: 'jhn', chapters: 21 },
    { id: 'act', chapters: 28 },
    { id: 'rom', chapters: 16 },
    { id: '1co', chapters: 16 },
    { id: '2co', chapters: 13 },
    { id: 'gal', chapters: 6 },
    { id: 'eph', chapters: 6 },
    { id: 'php', chapters: 4 },
    { id: 'col', chapters: 4 },
    { id: '1th', chapters: 5 },
    { id: '2th', chapters: 3 },
    { id: '1ti', chapters: 6 },
    { id: '2ti', chapters: 4 },
    { id: 'tit', chapters: 3 },
    { id: 'phm', chapters: 1 },
    { id: 'heb', chapters: 13 },
    { id: 'jas', chapters: 5 },
    { id: '1pe', chapters: 5 },
    { id: '2pe', chapters: 3 },
    { id: '1jn', chapters: 5 },
    { id: '2jn', chapters: 1 },
    { id: '3jn', chapters: 1 },
    { id: 'jud', chapters: 1 },
    { id: 'rev', chapters: 22 }
  ]
  
  let dayNum = 1
  let chaptersToday = 0
  const chaptersPerDay = 3
  
  plan.push({ day: dayNum, readings: [] })
  
  for (const book of ntBooks) {
    for (let chapter = 1; chapter <= book.chapters; chapter++) {
      if (chaptersToday >= chaptersPerDay && dayNum < 90) {
        dayNum++
        chaptersToday = 0
        plan.push({ day: dayNum, readings: [] })
      }
      
      plan[dayNum - 1].readings.push({
        workId: book.id,
        chapterNumber: chapter,
        verseNumber: 1
      })
      
      chaptersToday++
    }
  }
  
  return plan
}

function generateOneYearChronologicalPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  const chronologicalOrder = [
    { id: 'gen', start: 1, end: 11 },
    { id: 'job', start: 1, end: 42 },
    { id: 'gen', start: 12, end: 50 },
    { id: 'exo', start: 1, end: 40 },
    { id: 'lev', start: 1, end: 27 },
    { id: 'num', start: 1, end: 36 },
    { id: 'deu', start: 1, end: 34 },
    { id: 'jos', start: 1, end: 24 },
    { id: 'jdg', start: 1, end: 21 },
    { id: 'rut', start: 1, end: 4 },
    { id: '1sa', start: 1, end: 31 },
    { id: '2sa', start: 1, end: 24 },
    { id: '1ki', start: 1, end: 22 },
    { id: '2ki', start: 1, end: 25 },
    { id: 'isa', start: 1, end: 66 },
    { id: 'jer', start: 1, end: 52 },
    { id: 'lam', start: 1, end: 5 },
    { id: 'ezk', start: 1, end: 48 },
    { id: 'dan', start: 1, end: 12 },
    { id: 'hos', start: 1, end: 14 },
    { id: 'jol', start: 1, end: 3 },
    { id: 'amo', start: 1, end: 9 },
    { id: 'oba', start: 1, end: 1 },
    { id: 'jon', start: 1, end: 4 },
    { id: 'mic', start: 1, end: 7 },
    { id: 'neh', start: 1, end: 13 },
    { id: 'ezr', start: 1, end: 10 },
    { id: 'est', start: 1, end: 10 },
    { id: 'mat', start: 1, end: 28 },
    { id: 'mrk', start: 1, end: 16 },
    { id: 'luk', start: 1, end: 24 },
    { id: 'jhn', start: 1, end: 21 },
    { id: 'act', start: 1, end: 28 },
    { id: 'jas', start: 1, end: 5 },
    { id: 'gal', start: 1, end: 6 },
    { id: '1th', start: 1, end: 5 },
    { id: '2th', start: 1, end: 3 },
    { id: '1co', start: 1, end: 16 },
    { id: '2co', start: 1, end: 13 },
    { id: 'rom', start: 1, end: 16 },
    { id: 'eph', start: 1, end: 6 },
    { id: 'php', start: 1, end: 4 },
    { id: 'col', start: 1, end: 4 },
    { id: 'phm', start: 1, end: 1 },
    { id: '1ti', start: 1, end: 6 },
    { id: 'tit', start: 1, end: 3 },
    { id: '2ti', start: 1, end: 4 },
    { id: '1pe', start: 1, end: 5 },
    { id: '2pe', start: 1, end: 3 },
    { id: 'heb', start: 1, end: 13 },
    { id: 'jud', start: 1, end: 1 },
    { id: '1jn', start: 1, end: 5 },
    { id: '2jn', start: 1, end: 1 },
    { id: '3jn', start: 1, end: 1 },
    { id: 'rev', start: 1, end: 22 }
  ]
  
  let dayNum = 1
  let chaptersToday = 0
  const chaptersPerDay = 3
  
  plan.push({ day: dayNum, readings: [] })
  
  for (const section of chronologicalOrder) {
    for (let chapter = section.start; chapter <= section.end; chapter++) {
      if (chaptersToday >= chaptersPerDay && dayNum < 365) {
        dayNum++
        chaptersToday = 0
        plan.push({ day: dayNum, readings: [] })
      }
      
      plan[dayNum - 1].readings.push({
        workId: section.id,
        chapterNumber: chapter,
        verseNumber: 1
      })
      
      chaptersToday++
    }
  }
  
  return plan
}

function generateGospelsThirtyDaysPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  const gospels = [
    { id: 'mat', chapters: 28 },
    { id: 'mrk', chapters: 16 },
    { id: 'luk', chapters: 24 },
    { id: 'jhn', chapters: 21 }
  ]
  
  const totalChapters = 89
  const chaptersPerDay = 3
  
  let dayNum = 1
  let chaptersToday = 0
  
  plan.push({ day: dayNum, readings: [] })
  
  for (const gospel of gospels) {
    for (let chapter = 1; chapter <= gospel.chapters; chapter++) {
      if (chaptersToday >= chaptersPerDay && dayNum < 30) {
        dayNum++
        chaptersToday = 0
        plan.push({ day: dayNum, readings: [] })
      }
      
      plan[dayNum - 1].readings.push({
        workId: gospel.id,
        chapterNumber: chapter,
        verseNumber: 1
      })
      
      chaptersToday++
    }
  }
  
  return plan
}

function generatePsalmsPrverbsPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  for (let day = 1; day <= 31; day++) {
    const readings: ReadingPlan['days'][0]['readings'] = []
    
    for (let i = 0; i < 5; i++) {
      const psalmNum = ((day - 1) * 5 + i + 1)
      if (psalmNum <= 150) {
        readings.push({
          workId: 'psa',
          chapterNumber: psalmNum,
          verseNumber: 1
        })
      }
    }
    
    if (day <= 31) {
      readings.push({
        workId: 'pro',
        chapterNumber: day,
        verseNumber: 1
      })
    }
    
    plan.push({ day, readings })
  }
  
  return plan
}

function generatePaulineEpistlesPlan(): ReadingPlan['days'] {
  const plan: ReadingPlan['days'] = []
  
  const paulineEpistles = [
    { id: 'rom', chapters: 16 },
    { id: '1co', chapters: 16 },
    { id: '2co', chapters: 13 },
    { id: 'gal', chapters: 6 },
    { id: 'eph', chapters: 6 },
    { id: 'php', chapters: 4 },
    { id: 'col', chapters: 4 },
    { id: '1th', chapters: 5 },
    { id: '2th', chapters: 3 },
    { id: '1ti', chapters: 6 },
    { id: '2ti', chapters: 4 },
    { id: 'tit', chapters: 3 },
    { id: 'phm', chapters: 1 }
  ]
  
  let dayNum = 1
  let chaptersToday = 0
  const chaptersPerDay = 2
  
  plan.push({ day: dayNum, readings: [] })
  
  for (const epistle of paulineEpistles) {
    for (let chapter = 1; chapter <= epistle.chapters; chapter++) {
      if (chaptersToday >= chaptersPerDay && dayNum < 45) {
        dayNum++
        chaptersToday = 0
        plan.push({ day: dayNum, readings: [] })
      }
      
      plan[dayNum - 1].readings.push({
        workId: epistle.id,
        chapterNumber: chapter,
        verseNumber: 1
      })
      
      chaptersToday++
    }
  }
  
  return plan
}

export function getBookDisplayName(bookId: string): string {
  const bookNames: Record<string, string> = {
    'gen': 'Genesis', 'exo': 'Exodus', 'lev': 'Leviticus', 'num': 'Numbers', 'deu': 'Deuteronomy',
    'jos': 'Joshua', 'jdg': 'Judges', 'rut': 'Ruth', '1sa': '1 Samuel', '2sa': '2 Samuel',
    '1ki': '1 Kings', '2ki': '2 Kings', '1ch': '1 Chronicles', '2ch': '2 Chronicles',
    'ezr': 'Ezra', 'neh': 'Nehemiah', 'est': 'Esther', 'job': 'Job', 'psa': 'Psalms',
    'pro': 'Proverbs', 'ecc': 'Ecclesiastes', 'sng': 'Song of Solomon', 'isa': 'Isaiah',
    'jer': 'Jeremiah', 'lam': 'Lamentations', 'ezk': 'Ezekiel', 'dan': 'Daniel',
    'hos': 'Hosea', 'jol': 'Joel', 'amo': 'Amos', 'oba': 'Obadiah', 'jon': 'Jonah',
    'mic': 'Micah', 'nam': 'Nahum', 'hab': 'Habakkuk', 'zep': 'Zephaniah',
    'hag': 'Haggai', 'zec': 'Zechariah', 'mal': 'Malachi',
    'mat': 'Matthew', 'mrk': 'Mark', 'luk': 'Luke', 'jhn': 'John', 'act': 'Acts',
    'rom': 'Romans', '1co': '1 Corinthians', '2co': '2 Corinthians', 'gal': 'Galatians',
    'eph': 'Ephesians', 'php': 'Philippians', 'col': 'Colossians', '1th': '1 Thessalonians',
    '2th': '2 Thessalonians', '1ti': '1 Timothy', '2ti': '2 Timothy', 'tit': 'Titus',
    'phm': 'Philemon', 'heb': 'Hebrews', 'jas': 'James', '1pe': '1 Peter', '2pe': '2 Peter',
    '1jn': '1 John', '2jn': '2 John', '3jn': '3 John', 'jud': 'Jude', 'rev': 'Revelation'
  }
  
  return bookNames[bookId] || bookId.toUpperCase()
}
