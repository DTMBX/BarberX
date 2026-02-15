import { useState, useMemo } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { MagnifyingGlass, Funnel, Warning } from '@phosphor-icons/react'
import { Section, Document, AuthorityLevel, DocumentType } from '@/lib/types'
import { AuthorityBadge } from '../authority-badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { FullTextSearchEngine } from '@/lib/search-engine'

interface SearchViewProps {
  documents: Document[]
  sections: Section[]
  onSectionSelect: (section: Section) => void
}

export function SearchView({ documents, sections, onSectionSelect }: SearchViewProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<{ section: Section; document: Document; snippet: string }[]>([])
  const [hasSearched, setHasSearched] = useState(false)
  const [filters, setFilters] = useState<{
    authorityLevels: AuthorityLevel[]
    documentTypes: DocumentType[]
  }>({
    authorityLevels: [],
    documentTypes: []
  })

  const searchEngine = useMemo(
    () => new FullTextSearchEngine(sections, documents),
    [sections, documents]
  )

  const handleSearch = () => {
    if (!query.trim()) return

    const searchResults = searchEngine.search(query, {
      authorityLevels: filters.authorityLevels.length > 0 ? filters.authorityLevels : undefined,
      documentTypes: filters.documentTypes.length > 0 ? filters.documentTypes : undefined
    }, 100)

    const resultsWithSnippets = searchResults.map(result => ({
      section: result.section,
      document: result.document,
      snippet: result.matchedText
    }))

    setResults(resultsWithSnippets)
    setHasSearched(true)
  }

  const toggleAuthorityFilter = (level: AuthorityLevel) => {
    setFilters(prev => ({
      ...prev,
      authorityLevels: prev.authorityLevels.includes(level)
        ? prev.authorityLevels.filter(l => l !== level)
        : [...prev.authorityLevels, level]
    }))
  }

  const toggleDocumentTypeFilter = (type: DocumentType) => {
    setFilters(prev => ({
      ...prev,
      documentTypes: prev.documentTypes.includes(type)
        ? prev.documentTypes.filter(t => t !== type)
        : [...prev.documentTypes, type]
    }))
  }

  const clearFilters = () => {
    setFilters({
      authorityLevels: [],
      documentTypes: []
    })
  }

  const activeFilterCount = filters.authorityLevels.length + filters.documentTypes.length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight font-serif">Search Legal Sources</h2>
        <p className="text-muted-foreground mt-1">
          Full-text search across all 50 states, territories, federal statutes, and treaties
        </p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <MagnifyingGlass
            size={20}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search for provisions, amendments, clauses, statutes..."
            className="pl-10"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="relative">
              <Funnel size={20} />
              {activeFilterCount > 0 && (
                <Badge className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs">
                  {activeFilterCount}
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Search Filters</SheetTitle>
            </SheetHeader>
            <div className="space-y-6 mt-6">
              <div className="space-y-3">
                <Label className="text-base font-semibold">Authority Level</Label>
                <div className="space-y-2">
                  {(['federal', 'state', 'territory', 'local'] as AuthorityLevel[]).map(level => (
                    <div key={level} className="flex items-center gap-2">
                      <Checkbox
                        id={`filter-${level}`}
                        checked={filters.authorityLevels.includes(level)}
                        onCheckedChange={() => toggleAuthorityFilter(level)}
                      />
                      <Label htmlFor={`filter-${level}`} className="capitalize cursor-pointer">
                        {level}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <Label className="text-base font-semibold">Document Type</Label>
                <div className="space-y-2">
                  {(['constitution', 'statute', 'treaty', 'regulation', 'ordinance'] as DocumentType[]).map(type => (
                    <div key={type} className="flex items-center gap-2">
                      <Checkbox
                        id={`filter-type-${type}`}
                        checked={filters.documentTypes.includes(type)}
                        onCheckedChange={() => toggleDocumentTypeFilter(type)}
                      />
                      <Label htmlFor={`filter-type-${type}`} className="capitalize cursor-pointer">
                        {type}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              {activeFilterCount > 0 && (
                <Button variant="outline" className="w-full" onClick={clearFilters}>
                  Clear All Filters
                </Button>
              )}
            </div>
          </SheetContent>
        </Sheet>
        <Button onClick={handleSearch}>Search</Button>
      </div>

      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {filters.authorityLevels.map(level => (
            <Badge
              key={level}
              variant="secondary"
              className="cursor-pointer capitalize"
              onClick={() => toggleAuthorityFilter(level)}
            >
              {level} ×
            </Badge>
          ))}
          {filters.documentTypes.map(type => (
            <Badge
              key={type}
              variant="secondary"
              className="cursor-pointer capitalize"
              onClick={() => toggleDocumentTypeFilter(type)}
            >
              {type} ×
            </Badge>
          ))}
        </div>
      )}

      {hasSearched && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {results.length} {results.length === 1 ? 'result' : 'results'} found
            </p>
          </div>

          {results.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">
                  No results found. Try adjusting your search terms or filters.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {results.map(({ section, document, snippet }) => (
                <Card
                  key={section.id}
                  className="cursor-pointer transition-shadow hover:shadow-md"
                  onClick={() => onSectionSelect(section)}
                >
                  <CardContent className="py-4 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold leading-tight mb-1">
                          {section.title}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {document.title}
                        </p>
                      </div>
                      <AuthorityBadge level={document.authorityLevel} />
                    </div>
                    <p className="text-sm font-serif leading-relaxed border-l-2 border-primary/30 pl-3">
                      {snippet}
                    </p>
                    <p className="text-xs text-muted-foreground font-medium">
                      {section.canonicalCitation}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {!hasSearched && (
        <Card className="bg-muted/30">
          <CardContent className="py-12 text-center space-y-2">
            <MagnifyingGlass size={48} className="mx-auto text-muted-foreground" weight="thin" />
            <p className="text-lg font-semibold">Full-Text Search</p>
            <p className="text-muted-foreground max-w-md mx-auto">
              Search across the U.S. Constitution, all 50 state constitutions, territories, 
              federal statutes, and international treaties
            </p>
          </CardContent>
        </Card>
      )}

      <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
        <Warning className="h-4 w-4 text-accent-foreground dark:text-accent" weight="fill" />
        <AlertDescription className="text-xs text-foreground/80 dark:text-foreground/70">
          <strong>Verify All Sources.</strong> Search results are drawn from curated educational databases. Source text may not reflect the most recent amendments or judicial interpretations. Always verify results against official government publications before relying on them for any purpose.
        </AlertDescription>
      </Alert>
    </div>
  )
}
