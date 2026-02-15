import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { User, Buildings, MapPin, Calendar, Hash } from '@phosphor-icons/react'
import { Entity, EntityType, Mention, Document } from '@/lib/types'
import { ConfidenceBar } from '@/components/ConfidenceBar'

export function EntitiesView() {
  const [entities] = useKV<Entity[]>('entities', [])
  const [mentions] = useKV<Mention[]>('mentions', [])
  const [documents] = useKV<Document[]>('documents', [])
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  
  const entitiesList = entities || []
  const mentionsList = mentions || []
  const documentsList = documents || []
  
  const filteredEntities = entitiesList.filter(entity => {
    if (filterType !== 'all' && entity.type !== filterType) return false
    if (filterStatus !== 'all' && entity.disambiguationStatus !== filterStatus) return false
    return true
  })
  
  const getEntityIcon = (type: EntityType) => {
    switch (type) {
      case 'person':
        return <User size={20} weight="duotone" />
      case 'organization':
        return <Buildings size={20} weight="duotone" />
      case 'location':
        return <MapPin size={20} weight="duotone" />
      case 'date':
        return <Calendar size={20} weight="duotone" />
      case 'identifier':
        return <Hash size={20} weight="duotone" />
    }
  }
  
  const getMentionsForEntity = (entityId: string) => {
    return mentionsList.filter(m => m.entityId === entityId)
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Entities</h1>
          <p className="text-muted-foreground mt-1">
            Extracted entities with disambiguation controls and mention tracking
          </p>
        </div>
        <Badge variant="secondary" className="text-lg px-3 py-1">
          {filteredEntities.length} entities
        </Badge>
      </div>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="person">People</SelectItem>
                <SelectItem value="organization">Organizations</SelectItem>
                <SelectItem value="location">Locations</SelectItem>
                <SelectItem value="date">Dates</SelectItem>
                <SelectItem value="identifier">Identifiers</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="auto">Auto-extracted</SelectItem>
                <SelectItem value="needs-review">Needs Review</SelectItem>
                <SelectItem value="reviewed">Reviewed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid gap-3">
        {filteredEntities.map((entity) => {
          const entityMentions = getMentionsForEntity(entity.id)
          
          return (
            <Card key={entity.id} className="hover:border-accent/50 transition-colors">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/20 text-accent">
                      {getEntityIcon(entity.type)}
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-xl">{entity.canonicalName}</CardTitle>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="secondary" className="capitalize">
                          {entity.type}
                        </Badge>
                        <Badge 
                          variant={entity.disambiguationStatus === 'reviewed' ? 'default' : 'secondary'}
                          className={entity.disambiguationStatus === 'reviewed' ? 'bg-accent text-accent-foreground' : ''}
                        >
                          {entity.disambiguationStatus}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {entityMentions.length} mentions
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {entity.aliases.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Aliases</div>
                    <div className="flex flex-wrap gap-2">
                      {entity.aliases.map((alias, i) => (
                        <Badge key={i} variant="outline">
                          {alias}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Confidence</div>
                  <ConfidenceBar confidence={entity.confidence} />
                </div>
                
                {entity.notes && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Notes</div>
                    <div className="text-sm">{entity.notes}</div>
                  </div>
                )}
                
                <div className="flex items-center gap-2 pt-2">
                  <Button variant="outline" size="sm" disabled>
                    View Mentions
                  </Button>
                  {entity.disambiguationStatus === 'needs-review' && (
                    <Button size="sm" disabled>
                      Review & Merge
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
        
        {filteredEntities.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <User size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Entities Found</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                {entitiesList.length === 0 
                  ? 'No entities have been extracted yet. Process documents to extract people, organizations, and other entities.'
                  : 'No entities match your current filters. Try adjusting your criteria.'
                }
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
