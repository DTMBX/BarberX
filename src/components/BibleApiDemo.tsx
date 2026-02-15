import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { BookOpen, MagnifyingGlass } from '@phosphor-icons/react'
import { useBibleVerse, useBibleChapter, useBibleSearch } from '@/hooks/use-bible-api'
import { useState } from 'react'
import { translations } from '@/lib/data'

export default function BibleApiDemo() {
  const [selectedTranslation, setSelectedTranslation] = useState('kjv')
  const [bookId, setBookId] = useState('joh')
  const [chapter, setChapter] = useState(3)
  const [verse, setVerse] = useState(16)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'verse' | 'chapter' | 'search'>('verse')

  const { verse: verseData, loading: verseLoading } = useBibleVerse(
    activeTab === 'verse' ? { translationId: selectedTranslation, bookId, chapter, verse } : null
  )

  const { verses: chapterData, loading: chapterLoading } = useBibleChapter(
    activeTab === 'chapter' ? { translationId: selectedTranslation, bookId, chapter } : null
  )

  const { results: searchResults, loading: searchLoading } = useBibleSearch(
    activeTab === 'search' ? searchQuery : '',
    selectedTranslation
  )

  const publicDomainTranslations = translations.filter(t => 
    t.licenseRestrictions.fullTextAllowed
  )

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
          Bible API Integration Demo
        </h1>
        <p className="text-muted-foreground">
          Demonstrating authentic Bible text from Bolls Life API - 16 Public Domain translations, Full Old & New Testament
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>API Source: Bolls Life</CardTitle>
            <CardDescription>
              Free, unlimited access to 16+ public domain Bible translations - Full Old & New Testament
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-medium">License:</span>
              <span className="text-sm text-muted-foreground">Public Domain</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Coverage:</span>
              <span className="text-sm text-muted-foreground">Complete Old & New Testament (66 books)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Attribution:</span>
              <span className="text-sm text-muted-foreground">Not Required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">API Key:</span>
              <span className="text-sm text-muted-foreground">Not Required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Endpoint:</span>
              <span className="text-sm font-mono text-muted-foreground">https://bolls.life</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Available Translations</CardTitle>
            <CardDescription>
              {publicDomainTranslations.length} public domain translations with full Old & New Testament access
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[400px] overflow-y-auto">
              <ul className="space-y-1">
                {publicDomainTranslations.map((t) => (
                  <li key={t.id} className="text-sm flex items-center gap-2">
                    <BookOpen size={16} className="text-primary" weight="duotone" />
                    <span className="font-medium">{t.shortCode}</span>
                    <span className="text-muted-foreground">- {t.name} ({t.year})</span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>API Demonstration</CardTitle>
          <CardDescription>
            Test fetching verses, chapters, and search functionality
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="flex gap-2 border-b">
              <Button
                variant={activeTab === 'verse' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('verse')}
              >
                Fetch Verse
              </Button>
              <Button
                variant={activeTab === 'chapter' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('chapter')}
              >
                Fetch Chapter
              </Button>
              <Button
                variant={activeTab === 'search' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('search')}
              >
                Search
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-2">
                <Label>Translation</Label>
                <Select value={selectedTranslation} onValueChange={setSelectedTranslation}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {publicDomainTranslations.map((t) => (
                      <SelectItem key={t.id} value={t.id}>
                        {t.shortCode}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {activeTab !== 'search' && (
                <>
                  <div className="space-y-2">
                    <Label>Book</Label>
                    <Input
                      value={bookId}
                      onChange={(e) => setBookId(e.target.value)}
                      placeholder="e.g., joh"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Chapter</Label>
                    <Input
                      type="number"
                      value={chapter}
                      onChange={(e) => setChapter(parseInt(e.target.value))}
                    />
                  </div>

                  {activeTab === 'verse' && (
                    <div className="space-y-2">
                      <Label>Verse</Label>
                      <Input
                        type="number"
                        value={verse}
                        onChange={(e) => setVerse(parseInt(e.target.value))}
                      />
                    </div>
                  )}
                </>
              )}

              {activeTab === 'search' && (
                <div className="space-y-2 md:col-span-3">
                  <Label>Search Query</Label>
                  <div className="flex gap-2">
                    <MagnifyingGlass size={20} className="mt-2" />
                    <Input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="e.g., love"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="border rounded-lg p-6 bg-muted/30 min-h-[200px]">
              {activeTab === 'verse' && (
                verseLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : verseData ? (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">
                      {verseData.workId.toUpperCase()} {verseData.chapterNumber}:{verseData.verseNumber} ({selectedTranslation.toUpperCase()})
                    </div>
                    <p className="text-lg leading-relaxed" style={{ fontFamily: 'var(--font-body)' }}>
                      {verseData.text}
                    </p>
                  </div>
                ) : (
                  <div className="text-muted-foreground">No verse data</div>
                )
              )}

              {activeTab === 'chapter' && (
                chapterLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                ) : chapterData.length > 0 ? (
                  <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    <div className="text-sm text-muted-foreground mb-4">
                      {chapterData[0].workId.toUpperCase()} {chapterData[0].chapterNumber} ({selectedTranslation.toUpperCase()}) - {chapterData.length} verses
                    </div>
                    {chapterData.map((v) => (
                      <div key={v.id} className="flex gap-3">
                        <span className="text-sm font-mono text-muted-foreground mt-1">{v.verseNumber}</span>
                        <p className="leading-relaxed" style={{ fontFamily: 'var(--font-body)' }}>
                          {v.text}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-muted-foreground">No chapter data</div>
                )
              )}

              {activeTab === 'search' && (
                searchLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    <div className="text-sm text-muted-foreground mb-4">
                      Found {searchResults.length} results for "{searchQuery}"
                    </div>
                    {searchResults.slice(0, 20).map((v) => (
                      <div key={v.id} className="border-l-2 border-accent pl-4">
                        <div className="text-sm font-medium text-muted-foreground mb-1">
                          {v.workId.toUpperCase()} {v.chapterNumber}:{v.verseNumber}
                        </div>
                        <p className="leading-relaxed" style={{ fontFamily: 'var(--font-body)' }}>
                          {v.text}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : searchQuery.length >= 3 ? (
                  <div className="text-muted-foreground">No results found</div>
                ) : (
                  <div className="text-muted-foreground">Enter at least 3 characters to search</div>
                )
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6 bg-accent/10">
        <CardHeader>
          <CardTitle>Usage in Your Code</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-sm bg-background p-4 rounded-lg overflow-x-auto">
            {`import { useBibleVerse, useBibleChapter, useBibleSearch } from '@/hooks/use-bible-api'

// Fetch a single verse
const { verse, loading } = useBibleVerse({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3,
  verse: 16
})

// Fetch a complete chapter
const { verses, loading } = useBibleChapter({
  translationId: 'kjv',
  bookId: 'joh',
  chapter: 3
})

// Search the Bible
const { results, loading } = useBibleSearch('love', 'kjv')`}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
