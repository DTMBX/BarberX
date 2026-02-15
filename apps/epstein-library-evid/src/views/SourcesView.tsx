import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { useEngine } from '@/hooks/use-engine'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, Database, Play } from '@phosphor-icons/react'
import { Source } from '@/lib/types'
import { SetupGuide } from '@/components/SetupGuide'

export function SourcesView() {
  const { mode } = useEngine()
  const [sources] = useKV<Source[]>('sources', [])
  const [showConnectionDialog, setShowConnectionDialog] = useState(false)
  const sourcesList = sources || []
  
  return (
    <div className="space-y-6">
      {mode === 'demo' && (
        <SetupGuide onConnect={() => setShowConnectionDialog(true)} />
      )}
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sources</h1>
          <p className="text-muted-foreground mt-1">
            Configure document sources with crawl rules and ingestion policies
          </p>
        </div>
        <Button disabled className="gap-2">
          <Plus size={20} weight="bold" />
          Add Source
        </Button>
      </div>
      
      <div className="grid gap-4">
        {sourcesList.map((source) => (
          <Card key={source.id} className="hover:border-accent/50 transition-colors">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-primary/20">
                    <Database size={24} className="text-accent" weight="duotone" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">{source.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {source.description}
                    </CardDescription>
                  </div>
                </div>
                <Badge 
                  variant={source.status === 'active' ? 'default' : 'secondary'}
                  className={source.status === 'active' ? 'bg-accent text-accent-foreground' : ''}
                >
                  {source.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground mb-1">Base URL</div>
                  <code className="text-xs font-mono break-all">{source.baseUrl}</code>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Last Run</div>
                  <div className="text-xs">
                    {source.lastRunAt 
                      ? new Date(source.lastRunAt).toLocaleString()
                      : 'Never'
                    }
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 pt-2">
                <Button size="sm" className="gap-2" disabled>
                  <Play size={16} weight="fill" />
                  Start Ingestion
                </Button>
                <Button variant="outline" size="sm" disabled>
                  Configure
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {sourcesList.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <Database size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Sources Configured</h3>
              <p className="text-sm text-muted-foreground mb-4 max-w-md">
                Add a document source to begin ingesting and analyzing public records.
                Each source includes crawl rules, rate limits, and provenance tracking.
              </p>
              <Button disabled className="gap-2">
                <Plus size={20} />
                Add Your First Source
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
