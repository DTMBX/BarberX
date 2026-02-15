import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MagnifyingGlass, Quotes } from '@phosphor-icons/react'
import { SearchResult, Document } from '@/lib/types'
import { EvidenceSnippet } from '@/components/EvidenceSnippet'

interface SearchViewProps {
  initialQuery?: string
}

export function SearchView({ initialQuery = '' }: SearchViewProps) {
  const [query, setQuery] = useState(initialQuery)
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('keyword')
  const [results] = useKV<SearchResult[]>('search-results', [])
  const [documents] = useKV<Document[]>('documents', [])
  
  const resultsList = results || []
  const documentsList = documents || []
  
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery)
    }
  }, [initialQuery])
  
  const getDocument = (docId: string) => {
    return documentsList.find(d => d.id === docId)
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Search</h1>
        <p className="text-muted-foreground mt-1">
          Keyword and semantic search across indexed documents with evidence highlighting
        </p>
      </div>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <MagnifyingGlass 
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
                size={20} 
              />
              <Input
                placeholder="Search documents, entities, or content..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-11 text-base h-12"
              />
            </div>
            <Button size="lg" className="gap-2" disabled>
              <MagnifyingGlass size={20} weight="bold" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>
      
      <Tabs value={searchMode} onValueChange={(v) => setSearchMode(v as 'keyword' | 'semantic')}>
        <TabsList>
          <TabsTrigger value="keyword" className="gap-2">
            <Quotes size={16} />
            Keyword Search
          </TabsTrigger>
          <TabsTrigger value="semantic" className="gap-2">
            <MagnifyingGlass size={16} />
            Semantic Search
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value={searchMode} className="mt-6 space-y-4">
          {resultsList.length > 0 ? (
            <>
              <div className="text-sm text-muted-foreground mb-4">
                Found {resultsList.length} results
              </div>
              
              {resultsList.map((result) => {
                const doc = getDocument(result.documentId)
                if (!doc) return null
                
                return (
                  <EvidenceSnippet
                    key={result.documentId}
                    snippet={result.snippet}
                    highlight={query}
                    confidence={result.confidence}
                    documentTitle={result.title}
                    pageNo={result.pageNo}
                    onViewDocument={() => {}}
                  />
                )
              })}
            </>
          ) : (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <MagnifyingGlass size={64} className="text-muted-foreground mb-4" weight="duotone" />
                <h3 className="font-semibold mb-2 text-xl">No Search Results</h3>
                <p className="text-sm text-muted-foreground max-w-md">
                  {query 
                    ? 'No results found for your query. Try different keywords or switch to semantic search.'
                    : 'Enter a search query to find relevant documents, entities, and content.'
                  }
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
