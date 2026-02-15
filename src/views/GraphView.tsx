import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Graph, ArrowsOutSimple, ArrowsInSimple, Export } from '@phosphor-icons/react'
import { Entity, Relationship } from '@/lib/types'
import { ConfidenceBar } from '@/components/ConfidenceBar'

export function GraphView() {
  const [entities] = useKV<Entity[]>('entities', [])
  const [relationships] = useKV<Relationship[]>('relationships', [])
  const [minConfidence, setMinConfidence] = useState<string>('0.5')
  const [filterType, setFilterType] = useState<string>('all')
  
  const entitiesList = entities || []
  const relationshipsList = relationships || []
  
  const filteredRelationships = relationshipsList.filter(rel => {
    if (rel.confidence < parseFloat(minConfidence)) return false
    if (filterType !== 'all' && rel.type !== filterType) return false
    return true
  })
  
  const getEntityName = (entityId: string) => {
    return entitiesList.find(e => e.id === entityId)?.canonicalName || 'Unknown'
  }
  
  const relationshipTypeLabels: Record<string, string> = {
    'co-occurs': 'Co-occurs With',
    'referenced-in': 'Referenced In',
    'associated-with': 'Associated With',
    'same-as': 'Same As'
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Relationship Graph</h1>
          <p className="text-muted-foreground mt-1">
            Evidence-backed entity relationships with explainable connections
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled className="gap-2">
            <Export size={16} />
            Export Graph
          </Button>
        </div>
      </div>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Select value={minConfidence} onValueChange={setMinConfidence}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">All Confidence</SelectItem>
                <SelectItem value="0.5">50%+ Confidence</SelectItem>
                <SelectItem value="0.7">70%+ Confidence</SelectItem>
                <SelectItem value="0.8">80%+ Confidence</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[220px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Relationship Types</SelectItem>
                <SelectItem value="co-occurs">Co-occurs With</SelectItem>
                <SelectItem value="referenced-in">Referenced In</SelectItem>
                <SelectItem value="associated-with">Associated With</SelectItem>
                <SelectItem value="same-as">Same As (Reviewed)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-24 text-center">
          <Graph size={64} className="text-muted-foreground mb-4" weight="duotone" />
          <h3 className="font-semibold mb-2 text-xl">Graph Visualization</h3>
          <p className="text-sm text-muted-foreground max-w-md mb-4">
            Interactive graph visualization would render here showing entity nodes and relationship edges.
            Each edge would be clickable to view supporting evidence snippets.
          </p>
          <div className="text-xs text-muted-foreground">
            {entitiesList.length} entities • {filteredRelationships.length} relationships
          </div>
        </CardContent>
      </Card>
      
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Relationships</h2>
        
        {filteredRelationships.length > 0 ? (
          filteredRelationships.map((rel) => (
            <Card key={rel.id} className="hover:border-accent/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="font-semibold">{getEntityName(rel.entityAId)}</div>
                      <ArrowsOutSimple size={16} className="text-muted-foreground" />
                      <Badge variant="secondary">
                        {relationshipTypeLabels[rel.type] || rel.type}
                      </Badge>
                      <ArrowsInSimple size={16} className="text-muted-foreground" />
                      <div className="font-semibold">{getEntityName(rel.entityBId)}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Confidence</div>
                      <ConfidenceBar confidence={rel.confidence} />
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm">
                      <div className="text-muted-foreground">
                        {rel.evidenceChunkIds.length} evidence snippets
                      </div>
                      {rel.reviewStatus === 'approved' && (
                        <Badge className="bg-accent text-accent-foreground">
                          Reviewed & Approved
                        </Badge>
                      )}
                      {rel.reviewStatus === 'needs-review' && (
                        <Badge variant="secondary">
                          Needs Review
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" disabled>
                        View Evidence
                      </Button>
                      {rel.reviewStatus === 'needs-review' && (
                        <Button size="sm" disabled>
                          Review
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <Graph size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Relationships Found</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                {relationshipsList.length === 0 
                  ? 'No relationships have been extracted yet. Process documents with entity extraction enabled.'
                  : 'No relationships match your current filters. Try adjusting the confidence threshold or relationship type.'
                }
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
