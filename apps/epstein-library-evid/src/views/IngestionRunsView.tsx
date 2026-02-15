import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { FileArrowDown, Play, Pause, CheckCircle, XCircle, Clock } from '@phosphor-icons/react'
import { IngestionRun, Source } from '@/lib/types'

export function IngestionRunsView() {
  const [runs] = useKV<IngestionRun[]>('ingestion-runs', [])
  const [sources] = useKV<Source[]>('sources', [])
  const runsList = runs || []
  const sourcesList = sources || []
  
  const getSourceName = (sourceId: string) => {
    return sourcesList.find(s => s.id === sourceId)?.name || 'Unknown Source'
  }
  
  const getStatusIcon = (status: IngestionRun['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} weight="fill" className="text-[oklch(0.60_0.18_145)]" />
      case 'failed':
        return <XCircle size={20} weight="fill" className="text-destructive" />
      case 'running':
        return <Play size={20} weight="fill" className="text-accent" />
      case 'paused':
        return <Pause size={20} weight="fill" className="text-[oklch(0.65_0.10_70)]" />
      default:
        return <Clock size={20} weight="fill" className="text-muted-foreground" />
    }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ingestion Runs</h1>
          <p className="text-muted-foreground mt-1">
            Monitor document discovery, download, and processing workflows
          </p>
        </div>
      </div>
      
      <div className="grid gap-4">
        {runsList.map((run) => {
          const progress = run.discovered > 0 
            ? Math.round((run.processed / run.discovered) * 100) 
            : 0
            
          return (
            <Card key={run.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(run.status)}
                    <div>
                      <CardTitle className="text-lg">
                        {getSourceName(run.sourceId)}
                      </CardTitle>
                      <div className="text-sm text-muted-foreground mt-1">
                        Started {new Date(run.startedAt).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <Badge variant={run.status === 'completed' ? 'default' : 'secondary'}>
                    {run.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground mb-1">Discovered</div>
                    <div className="text-2xl font-bold font-mono">{run.discovered}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Downloaded</div>
                    <div className="text-2xl font-bold font-mono">{run.downloaded}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Processed</div>
                    <div className="text-2xl font-bold font-mono">{run.processed}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Errors</div>
                    <div className="text-2xl font-bold font-mono text-destructive">{run.errors}</div>
                  </div>
                </div>
                
                {run.status === 'running' && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-mono">{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                )}
                
                {run.throttleInfo?.active && (
                  <div className="flex items-center gap-2 text-sm text-accent">
                    <Pause size={16} />
                    <span>
                      Throttled - Resuming at {new Date(run.throttleInfo.resumeAt || '').toLocaleTimeString()}
                    </span>
                  </div>
                )}
                
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" disabled>
                    View Details
                  </Button>
                  {run.status === 'failed' && (
                    <Button variant="outline" size="sm" disabled>
                      Retry
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
        
        {runsList.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <FileArrowDown size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Ingestion Runs</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Start an ingestion run from a configured source to begin downloading and processing documents.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
