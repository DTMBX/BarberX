import { useKV } from '@/lib/local-storage-kv'
import { SavedCitation } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BookmarkSimple, FolderOpen, Star } from '@phosphor-icons/react'

interface CitationLibraryStatsProps {
  onNavigateToCitations: () => void
}

export function CitationLibraryStats({ onNavigateToCitations }: CitationLibraryStatsProps) {
  const [savedCitations] = useKV<SavedCitation[]>('citation-library', [])

  const totalCitations = (savedCitations || []).length
  const favoriteCitations = (savedCitations || []).filter((c) => c.isFavorite).length
  const recentCitations = (savedCitations || [])
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 3)

  if (totalCitations === 0) {
    return (
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookmarkSimple className="w-5 h-5" />
            Citation Library
          </CardTitle>
          <CardDescription>Save frequently used citations for quick access</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Your citation library is empty. When viewing a section, click "Save to Library" to add
            it here for quick reference.
          </p>
          <Button variant="outline" className="w-full" onClick={onNavigateToCitations}>
            <FolderOpen className="w-4 h-4 mr-2" />
            Open Citation Library
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookmarkSimple className="w-5 h-5" />
          Citation Library
        </CardTitle>
        <CardDescription>Quick access to saved citations</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-2xl font-bold">{totalCitations}</p>
            <p className="text-xs text-muted-foreground">Total Citations</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold flex items-center gap-1">
              {favoriteCitations}
              <Star className="w-4 h-4 text-accent" />
            </p>
            <p className="text-xs text-muted-foreground">Favorites</p>
          </div>
        </div>

        {recentCitations.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Recently Updated</p>
            <div className="space-y-2">
              {recentCitations.map((citation) => (
                <div
                  key={citation.id}
                  className="text-xs p-2 bg-muted/50 rounded border border-border"
                >
                  <p className="font-semibold line-clamp-1">{citation.title}</p>
                  <p className="text-muted-foreground font-mono text-[10px] mt-0.5">
                    {citation.canonicalCitation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        <Button className="w-full" onClick={onNavigateToCitations}>
          <FolderOpen className="w-4 h-4 mr-2" />
          Open Citation Library
        </Button>
      </CardContent>
    </Card>
  )
}
