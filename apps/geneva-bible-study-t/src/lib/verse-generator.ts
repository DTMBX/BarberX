import { VerseUnit } from './types'

const sampleTexts: Record<string, Record<number, string[]>> = {
  gen: {
    1: [
      'In the beginning God created the heaven and the earth.',
      'And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.',
      'And God said, Let there be light: and there was light.',
      'And God saw the light, that it was good: and God divided the light from the darkness.',
      'And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.',
      'And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters.',
      'And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so.',
      'And God called the firmament Heaven. And the evening and the morning were the second day.',
      'And God said, Let the waters under the heaven be gathered together unto one place, and let the dry land appear: and it was so.',
      'And God called the dry land Earth; and the gathering together of the waters called he Seas: and God saw that it was good.'
    ]
  }
}

export function generateChapterVerses(
  bookId: string,
  chapter: number,
  translationId: string
): VerseUnit[] {
  const cachedVerses = sampleTexts[bookId]?.[chapter]
  if (cachedVerses) {
    return cachedVerses.map((text, index) => ({
      id: `${bookId}-${chapter}-${index + 1}-${translationId}`,
      workId: bookId,
      chapterNumber: chapter,
      verseNumber: index + 1,
      translationId,
      text
    }))
  }

  return Array.from({ length: 25 }, (_, i) => ({
    id: `${bookId}-${chapter}-${i + 1}-${translationId}`,
    workId: bookId,
    chapterNumber: chapter,
    verseNumber: i + 1,
    translationId,
    text: `This is verse ${i + 1} of ${bookId} chapter ${chapter}. The full text would be loaded here from the ${translationId} translation. In a production environment, this would contain the actual biblical text from a comprehensive database.`
  }))
}

export async function generateChapterVersesAsync(
  bookId: string,
  chapter: number,
  translationId: string
): Promise<VerseUnit[]> {
  try {
    const promptText = `Generate exactly 25 verses for the book ${bookId} chapter ${chapter} in ${translationId} translation style. Use archaic English for geneva, modern formal for esv, contemporary for niv. Return as valid JSON: {"verses": [{"verseNumber": 1, "text": "..."}, ...]}`

    const response = await window.spark.llm(promptText, 'gpt-4o-mini', true)
    const data = JSON.parse(response)
    
    if (data.verses && Array.isArray(data.verses)) {
      return data.verses.map((v: { verseNumber: number; text: string }) => ({
        id: `${bookId}-${chapter}-${v.verseNumber}-${translationId}`,
        workId: bookId,
        chapterNumber: chapter,
        verseNumber: v.verseNumber,
        translationId,
        text: v.text
      }))
    }
  } catch (error) {
    console.error('Error generating verses:', error)
  }

  return generateChapterVerses(bookId, chapter, translationId)
}
