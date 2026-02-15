import { useMemo } from 'react'
import { SavedCitation } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tag, Hash } from '@phosphor-icons/react'

interface CitationTagStatsProps {
  citations: SavedCitation[]
  onTagClick?: (tag: string) => void
  tagDefinitions?: any[]
}

export function CitationTagStats({ citations, onTagClick, tagDefinitions = [] }: CitationTagStatsProps) {
  const tagStats = useMemo(() => {
    const counts: Record<string, number> = {}
    
    citations.forEach(citation => {
      citation.tags.forEach(tag => {
        counts[tag] = (counts[tag] || 0) + 1
      })
    })

    const sorted = Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 20)

    return sorted
  }, [citations])

  const getTagColor = (tagName: string): string => {
    const tagDef = Array.isArray(tagDefinitions)
      ? tagDefinitions.find((t: any) => t.name === tagName)
      : undefined
    return tagDef?.color || '#64748B'
  }

  const maxCount = tagStats.length > 0 ? tagStats[0][1] : 1

  if (tagStats.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Hash className="w-4 h-4" />
          Most Used Tags
        </CardTitle>
        <CardDescription>
          Your top {tagStats.length} tags by frequency
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] pr-4">
          <div className="space-y-3">
            {tagStats.map(([tag, count]) => (
              <div key={tag} className="space-y-1">
                <div className="flex items-center justify-between">
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:shadow-sm transition-shadow"
                    style={{
                      borderColor: getTagColor(tag),
                      color: getTagColor(tag),
                    }}
                    onClick={() => onTagClick?.(tag)}
                  >
                    {tag}
                  </Badge>
                  <span className="text-sm text-muted-foreground font-mono">
                    {count} {count === 1 ? 'citation' : 'citations'}
                  </span>
                </div>
                <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="absolute left-0 top-0 h-full rounded-full transition-all"
                    style={{
                      width: `${(count / maxCount) * 100}%`,
                      backgroundColor: getTagColor(tag),
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
