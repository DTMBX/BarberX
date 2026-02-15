# Bible API Integration Documentation

## Overview

This application integrates with the **Bolls Life Bible API** to provide authentic, verified Bible text from public domain sources. This API offers free, unlimited access to 16+ public domain Bible translations with complete Old and New Testament coverage (66 books), without requiring API keys or attribution.

## API Source Details

### Bolls Life Bible API
- **Website**: https://bolls.life
- **Base URL**: `https://bolls.life/`
- **License**: Public Domain
- **Attribution**: Not Required
- **API Key**: Not Required
- **Rate Limiting**: None (free unlimited access)
- **Cost**: Free

### Available Public Domain Translations

All translations below are available with full text access for Old and New Testament:

#### English Translations
1. **Geneva Bible (1560)** - `geneva` - The Bible of the Protestant Reformation with Reformed theology notes
2. **King James Version (1611)** - `kjv` - Most influential English Bible with majestic prose
3. **King James Version with Apocrypha (1611)** - `kjva` - Complete KJV including Deuterocanonical books
4. **World English Bible (2000)** - `web` - Modern public domain translation
5. **Young's Literal Translation (1862)** - `ylt` - Extremely literal word-for-word translation
6. **American Standard Version (1901)** - `asv` - Scholarly American revision of the KJV
7. **Bible in Basic English (1949)** - `basicenglish` - Simple English using only 850 basic words
8. **Darby Translation (1890)** - `darby` - Precise translation by Plymouth Brethren founder
9. **Douay-Rheims Bible (1609)** - `douayrheims` - Catholic Bible translated from Latin Vulgate
10. **Webster's Bible (1833)** - `webster` - Noah Webster's KJV revision with modern language
11. **American King James Version (1999)** - `akjv` - KJV with modern American spelling
12. **Lexham English Bible (2012)** - `leb` - Modern literal translation emphasizing transparency
13. **World Messianic Bible (2014)** - `wb` - WEB variant using Messianic Jewish terminology

#### Other Language Translations
14. **Clementine Vulgate (1592)** - `clementine` - Official Catholic Latin text
15. **Almeida Revista e Corrigida (1898)** - `almeida` - Classic Portuguese translation
16. **Russian Synodal Translation (1876)** - `rst` - Standard Russian Orthodox Bible

All translations include complete Old Testament (39 books) and New Testament (27 books), totaling 66 books in the Protestant canon. Some translations (KJVA, Douay-Rheims) also include the Deuterocanonical books.

## API Endpoints

### 1. Fetch Single Verse

```
GET https://bolls.life/get-verse/{translation}/{chapter}/{verse}/{book}/
```

**Parameters:**
- `translation`: Translation ID (e.g., `kjv`, `geneva`)
- `chapter`: Chapter number
- `verse`: Verse number
- `book`: Full book name (e.g., `Genesis`, `John`)

**Response:**
```json
{
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "text": "For God so loved the world..."
}
```

### 2. Fetch Complete Chapter

```
GET https://bolls.life/get-chapter/{translation}/{chapter}/{book}/
```

**Parameters:**
- `translation`: Translation ID
- `chapter`: Chapter number
- `book`: Full book name

**Response:**
```json
[
  {
    "book": "John",
    "chapter": 3,
    "verse": 1,
    "text": "There was a man of the Pharisees..."
  },
  {
    "book": "John",
    "chapter": 3,
    "verse": 2,
    "text": "The same came to Jesus by night..."
  }
  // ... more verses
]
```

### 3. Search Bible Text

```
GET https://bolls.life/search/{translation}/{query}/
```

**Parameters:**
- `translation`: Translation ID
- `query`: Search term (URL encoded)

**Response:**
```json
[
  {
    "book": "John",
    "chapter": 3,
    "verse": 16,
    "text": "For God so loved the world..."
  }
  // ... more results
]
```

## Implementation Files

### Core API Service
**File**: `/src/lib/bibleApi.ts`

Provides low-level API functions:
- `fetchVerse()` - Fetch a single verse
- `fetchChapter()` - Fetch complete chapter
- `fetchMultipleTranslations()` - Fetch same verse in multiple translations
- `searchBible()` - Search across Bible text

### React Hooks
**File**: `/src/hooks/use-bible-api.ts`

Provides React hooks for easy integration:

#### `useBibleVerse`
Fetch a single verse with loading states:

```typescript
import { useBibleVerse } from '@/hooks/use-bible-api'

const { verse, loading, error } = useBibleVerse({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3,
  verse: 16
})
```

#### `useBibleChapter`
Fetch a complete chapter with automatic caching:

```typescript
import { useBibleChapter } from '@/hooks/use-bible-api'

const { verses, loading, error } = useBibleChapter({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3
})
```

#### `useCompareVerses`
Fetch the same verse in multiple translations:

```typescript
import { useCompareVerses } from '@/hooks/use-bible-api'

const { verses, loading, error } = useCompareVerses(
  'joh',      // bookId
  3,          // chapter
  16,         // verse
  ['kjv', 'geneva', 'web']  // translations to compare
)
```

#### `useBibleSearch`
Search Bible text with debouncing:

```typescript
import { useBibleSearch } from '@/hooks/use-bible-api'

const { results, loading, error } = useBibleSearch(
  'love',     // search query
  'kjv'       // translation to search
)
```

## Book ID Mapping

The API uses full book names, but the application uses short book IDs. The mapping is handled automatically:

| Book ID | Full Name | Book ID | Full Name |
|---------|-----------|---------|-----------|
| `gen` | Genesis | `mat` | Matthew |
| `exo` | Exodus | `mar` | Mark |
| `lev` | Leviticus | `luk` | Luke |
| `num` | Numbers | `joh` | John |
| `deu` | Deuteronomy | `act` | Acts |
| `jos` | Joshua | `rom` | Romans |
| `jdg` | Judges | `1co` | 1 Corinthians |
| `rut` | Ruth | `2co` | 2 Corinthians |
| ... | ... | ... | ... |

## Caching Strategy

### Chapter Caching
Fetched chapters are automatically cached in local KV storage to:
- Minimize API calls
- Improve performance
- Enable offline functionality for previously viewed content

Cache key format: `{translationId}-{bookId}-{chapter}`

Example:
```typescript
// Cached automatically on first fetch
const { verses } = useBibleChapter({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3
})

// Second call returns cached data instantly
const { verses } = useBibleChapter({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3
}) // ← Instant from cache
```

## Usage Examples

### Simple Verse Display

```typescript
import { useBibleVerse } from '@/hooks/use-bible-api'

function VerseDisplay() {
  const { verse, loading } = useBibleVerse({
    translationId: 'kjv',
    bookId: 'joh',
    chapter: 3,
    verse: 16
  })

  if (loading) return <div>Loading...</div>
  if (!verse) return <div>Verse not found</div>

  return (
    <div>
      <div>{verse.workId.toUpperCase()} {verse.chapterNumber}:{verse.verseNumber}</div>
      <p>{verse.text}</p>
    </div>
  )
}
```

### Chapter Reader

```typescript
import { useBibleChapter } from '@/hooks/use-bible-api'

function ChapterReader() {
  const { verses, loading } = useBibleChapter({
    translationId: 'kjv',
    bookId: 'joh',
    chapter: 3
  })

  if (loading) return <div>Loading chapter...</div>

  return (
    <div>
      {verses.map((verse) => (
        <div key={verse.id}>
          <span>{verse.verseNumber}</span>
          <p>{verse.text}</p>
        </div>
      ))}
    </div>
  )
}
```

### Translation Comparison

```typescript
import { useCompareVerses } from '@/hooks/use-bible-api'

function ComparisonView() {
  const { verses, loading } = useCompareVerses(
    'joh',
    3,
    16,
    ['kjv', 'geneva', 'web']
  )

  if (loading) return <div>Loading translations...</div>

  return (
    <div>
      {verses.map((verse) => (
        <div key={verse.id}>
          <h3>{verse.translationId.toUpperCase()}</h3>
          <p>{verse.text}</p>
        </div>
      ))}
    </div>
  )
}
```

### Search Interface

```typescript
import { useState } from 'react'
import { useBibleSearch } from '@/hooks/use-bible-api'

function SearchInterface() {
  const [query, setQuery] = useState('')
  const { results, loading } = useBibleSearch(query, 'kjv')

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search the Bible..."
      />
      
      {loading && <div>Searching...</div>}
      
      <div>
        {results.map((verse) => (
          <div key={verse.id}>
            <div>{verse.workId.toUpperCase()} {verse.chapterNumber}:{verse.verseNumber}</div>
            <p>{verse.text}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Error Handling

All hooks return an `error` property for handling failures:

```typescript
const { verse, loading, error } = useBibleVerse({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3,
  verse: 16
})

if (error) {
  return <div>Error: {error}</div>
}
```

## Performance Considerations

1. **Debounced Search**: Search queries are debounced by 500ms to avoid excessive API calls
2. **Chapter Caching**: Chapters are cached in KV storage for instant repeat access
3. **Parallel Requests**: Multiple translations can be fetched in parallel for comparison
4. **Conditional Fetching**: Hooks only fetch when parameters are provided

## License Compliance

All translations accessed through this API are **Public Domain** with the following characteristics:

- ✅ No attribution required
- ✅ Free commercial use
- ✅ Free non-commercial use
- ✅ No API key required
- ✅ Unlimited access
- ✅ Full text allowed
- ✅ Offline caching allowed
- ✅ Modification allowed
- ✅ Distribution allowed

## Demo Component

A comprehensive demo component is available at `/src/components/BibleApiDemo.tsx` that demonstrates:
- Fetching individual verses
- Fetching complete chapters
- Searching Bible text
- Using different translations
- Error handling
- Loading states

Access the demo by navigating to the "API Demo" tab in the application.

## Additional Resources

- **Bolls Life Documentation**: https://bolls.life/api-documentation/
- **Bible Book Names**: Standard English book names (e.g., "Genesis", "John")
- **Translation Codes**: See `/src/lib/data.ts` for full translation list

## Support

For issues with the Bible API integration:
1. Check the browser console for error messages
2. Verify book names are spelled correctly
3. Ensure chapter and verse numbers are valid
4. Check network connectivity

For API-specific issues, visit: https://bolls.life
