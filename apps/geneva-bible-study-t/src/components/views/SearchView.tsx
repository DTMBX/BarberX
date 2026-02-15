import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { MagnifyingGlass, Funnel } from '@phosphor-icons/react'
import { sampleVerses, translations, bibleBooks } from '@/lib/data'

export default function SearchView() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTranslation, setSelectedTranslation] = useState('all')
  const [searchResults, setSearchResults] = useState<typeof sampleVerses>([])
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = () => {
    if (!searchQuery.trim()) return

    const results = sampleVerses.filter(verse => {
      const matchesQuery = verse.text.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesTranslation = selectedTranslation === 'all' || verse.translationId === selectedTranslation
      return matchesQuery && matchesTranslation
    })

    setSearchResults(results)
    setHasSearched(true)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 text-foreground flex items-center gap-3" style={{ fontFamily: 'var(--font-heading)' }}>
          <MagnifyingGlass size={32} weight="duotone" className="text-primary" />
          Search Scripture
        </h2>
        <p className="text-muted-foreground">
          Search across all translations and biblical texts
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search Query</CardTitle>
          <CardDescription>Enter words or phrases to find in the biblical texts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3 mb-4">
            <div className="flex-1">
              <Input
                placeholder="e.g., 'God so loved the world'"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyPress}
                className="text-lg"
              />
            </div>
            <Button onClick={handleSearch} size="lg">
              <MagnifyingGlass size={20} weight="duotone" className="mr-2" />
              Search
            </Button>
          </div>

          <div className="flex gap-3 items-center">
            <Funnel size={20} weight="duotone" className="text-muted-foreground" />
            <span className="text-sm font-medium">Translation:</span>
            <Select value={selectedTranslation} onValueChange={setSelectedTranslation}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Translations</SelectItem>
                {translations.map(trans => (
                  <SelectItem key={trans.id} value={trans.id}>
                    {trans.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {hasSearched && (
          <div className="flex items-center justify-between mb-4">
            <p className="text-muted-foreground">
              Found {searchResults.length} {searchResults.length === 1 ? 'result' : 'results'}
              {searchQuery && ` for "${searchQuery}"`}
            </p>
            {searchResults.length > 0 && (
              <Button variant="ghost" size="sm" onClick={() => { setSearchQuery(''); setSearchResults([]); setHasSearched(false) }}>
                Clear
              </Button>
            )}
          </div>
        )}

        {searchResults.map(verse => {
          const book = bibleBooks.find(b => b.id === verse.workId)
          const translation = translations.find(t => t.id === verse.translationId)

          const highlightText = (text: string) => {
            if (!searchQuery.trim()) return text
            const regex = new RegExp(`(${searchQuery})`, 'gi')
            const parts = text.split(regex)
            return parts.map((part, index) =>
              regex.test(part) ? (
                <mark key={index} className="bg-accent/30 font-semibold">
                  {part}
                </mark>
              ) : (
                part
              )
            )
          }

          return (
            <Card key={verse.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">
                      {book?.title} {verse.chapterNumber}:{verse.verseNumber}
                    </CardTitle>
                    <CardDescription className="flex gap-2 mt-1">
                      <Badge variant="secondary" className="text-xs">
                        {translation?.shortCode}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {book?.category}
                      </Badge>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p
                  className="text-base leading-relaxed"
                  style={{
                    fontFamily: 'var(--font-body)',
                    lineHeight: '1.75'
                  }}
                >
                  {highlightText(verse.text)}
                </p>
              </CardContent>
            </Card>
          )
        })}

        {hasSearched && searchResults.length === 0 && (
          <Card>
            <CardContent className="pt-6 text-center">
              <MagnifyingGlass size={48} weight="duotone" className="mx-auto mb-3 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground mb-2">No results found</p>
              <p className="text-sm text-muted-foreground">
                Try different search terms or select a different translation filter
              </p>
            </CardContent>
          </Card>
        )}

        {!hasSearched && (
          <Card className="bg-secondary/30">
            <CardContent className="pt-6">
              <h3 className="font-semibold mb-3">Search Tips:</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Search for words or phrases across all biblical texts</li>
                <li>• Use quotes for exact phrase matching: "in the beginning"</li>
                <li>• Filter by translation to compare how different Bibles translate key terms</li>
                <li>• Results show the verse context with your search terms highlighted</li>
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
