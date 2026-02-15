import { useKV } from '@github/spark/hooks'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ClockCounterClockwise, User as UserIcon, Database, UsersThree, Graph } from '@phosphor-icons/react'
import { AuditEvent } from '@/lib/types'

export function AuditLogView() {
  const [auditEvents] = useKV<AuditEvent[]>('audit-events', [])
  
  const eventsList = auditEvents || []
  
  const getActionIcon = (objectType: string) => {
    switch (objectType) {
      case 'source':
        return <Database size={16} className="text-muted-foreground" />
      case 'entity':
        return <UsersThree size={16} className="text-muted-foreground" />
      case 'relationship':
        return <Graph size={16} className="text-muted-foreground" />
      default:
        return <ClockCounterClockwise size={16} className="text-muted-foreground" />
    }
  }
  
  const getActionColor = (action: string) => {
    if (action.includes('create')) return 'bg-[oklch(0.60_0.18_145)] text-white'
    if (action.includes('update') || action.includes('merge')) return 'bg-accent text-accent-foreground'
    if (action.includes('delete')) return 'bg-destructive text-destructive-foreground'
    return 'bg-secondary text-secondary-foreground'
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Audit Log</h1>
        <p className="text-muted-foreground mt-1">
          Complete audit trail of all system actions with actor tracking and change details
        </p>
      </div>
      
      <div className="space-y-2">
        {eventsList.map((event) => (
          <Card key={event.id} className="hover:border-accent/30 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/20">
                  {getActionIcon(event.objectType)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getActionColor(event.action)}>
                          {event.action}
                        </Badge>
                        <span className="text-sm text-muted-foreground capitalize">
                          {event.objectType}
                        </span>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <UserIcon size={14} className="inline mr-1" />
                        {event.actor}
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground text-right">
                      <div>{new Date(event.timestamp).toLocaleDateString()}</div>
                      <div>{new Date(event.timestamp).toLocaleTimeString()}</div>
                    </div>
                  </div>
                  
                  <div className="text-sm space-y-1">
                    <div>
                      <span className="text-muted-foreground">Object ID:</span>{' '}
                      <code className="font-mono text-xs">{event.objectId}</code>
                    </div>
                    
                    {event.ipAddress && (
                      <div>
                        <span className="text-muted-foreground">IP Address:</span>{' '}
                        <code className="font-mono text-xs">{event.ipAddress}</code>
                      </div>
                    )}
                    
                    {Object.keys(event.details).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-muted-foreground cursor-pointer hover:text-foreground">
                          View Details
                        </summary>
                        <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto">
                          {JSON.stringify(event.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {eventsList.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <ClockCounterClockwise size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Audit Events</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                All system actions including entity merges, relationship approvals, and configuration changes 
                will be logged here with complete provenance.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
