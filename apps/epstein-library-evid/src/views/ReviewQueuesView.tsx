import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Queue, 
  CheckCircle, 
  Clock, 
  Warning, 
  User,
  CalendarBlank,
  ChatCenteredDots,
  ArrowRight,
  Flag
} from '@phosphor-icons/react'
import { ReviewQueueItem, ReviewQueueType, ReviewQueueStatus } from '@/lib/types'
import { format } from 'date-fns'

export function ReviewQueuesView() {
  const [queueItems, setQueueItems] = useKV<ReviewQueueItem[]>('review-queue-items', [])
  const [selectedQueue, setSelectedQueue] = useState<ReviewQueueType | 'all'>('all')
  const [filterStatus, setFilterStatus] = useState<ReviewQueueStatus | 'all'>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')

  const items = queueItems || []

  const queueTypes: Array<{ type: ReviewQueueType; label: string; color: string }> = [
    { type: 'low-ocr-quality', label: 'Low OCR Quality', color: 'text-[oklch(0.70_0.15_280)]' },
    { type: 'ambiguous-entities', label: 'Ambiguous Entities', color: 'text-[oklch(0.65_0.15_160)]' },
    { type: 'relationship-proposals', label: 'Relationship Proposals', color: 'text-accent' },
    { type: 'sensitive-content-flags', label: 'Sensitive Content', color: 'text-destructive' },
    { type: 'export-requests', label: 'Export Requests', color: 'text-[oklch(0.60_0.15_210)]' },
    { type: 'translation-review', label: 'Translation Review', color: 'text-[oklch(0.75_0.15_70)]' },
    { type: 'structured-extraction-review', label: 'Structured Extraction', color: 'text-[oklch(0.60_0.18_145)]' }
  ]

  const filteredItems = items.filter(item => {
    if (selectedQueue !== 'all' && item.queueType !== selectedQueue) return false
    if (filterStatus !== 'all' && item.status !== filterStatus) return false
    if (filterPriority !== 'all' && item.priority !== filterPriority) return false
    return true
  })

  const getQueueStats = (type: ReviewQueueType) => {
    const typeItems = items.filter(i => i.queueType === type)
    return {
      total: typeItems.length,
      pending: typeItems.filter(i => i.status === 'pending').length,
      inProgress: typeItems.filter(i => i.status === 'in-progress').length,
      urgent: typeItems.filter(i => i.priority === 'urgent').length
    }
  }

  const handleAssign = (itemId: string, assignee: string) => {
    setQueueItems(current =>
      (current || []).map(item =>
        item.id === itemId
          ? { ...item, assignedTo: assignee, status: 'in-progress' as ReviewQueueStatus }
          : item
      )
    )
  }

  const handleComplete = (itemId: string, notes: string) => {
    setQueueItems(current =>
      (current || []).map(item =>
        item.id === itemId
          ? { 
              ...item, 
              status: 'completed' as ReviewQueueStatus, 
              completedAt: new Date().toISOString(),
              reviewNotes: notes
            }
          : item
      )
    )
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-destructive text-destructive-foreground'
      case 'high': return 'bg-accent text-accent-foreground'
      case 'medium': return 'bg-[oklch(0.65_0.15_160)] text-foreground'
      case 'low': return 'bg-muted text-muted-foreground'
      default: return 'bg-secondary text-secondary-foreground'
    }
  }

  const getStatusIcon = (status: ReviewQueueStatus) => {
    switch (status) {
      case 'pending': return <Clock size={16} />
      case 'in-progress': return <ArrowRight size={16} />
      case 'completed': return <CheckCircle size={16} />
      case 'escalated': return <Warning size={16} />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Review Queues</h1>
          <p className="text-muted-foreground mt-1">
            Manage review tasks with assignments, due dates, and accountability
          </p>
        </div>
        <Badge variant="secondary" className="text-lg px-3 py-1">
          {items.filter(i => i.status !== 'completed').length} active items
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {queueTypes.slice(0, 4).map(({ type, label, color }) => {
          const stats = getQueueStats(type)
          return (
            <Card key={type} className="cursor-pointer hover:border-accent/50 transition-colors"
              onClick={() => setSelectedQueue(type)}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Queue className={color} size={18} weight="duotone" />
                  {label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-xs text-muted-foreground mt-1 flex gap-3">
                  <span>{stats.pending} pending</span>
                  {stats.urgent > 0 && (
                    <span className="text-destructive font-semibold">
                      {stats.urgent} urgent
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Queue Items</CardTitle>
            <div className="flex items-center gap-2">
              <Select value={selectedQueue} onValueChange={(v) => setSelectedQueue(v as ReviewQueueType | 'all')}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Queue Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Queues</SelectItem>
                  {queueTypes.map(({ type, label }) => (
                    <SelectItem key={type} value={type}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={filterStatus} onValueChange={(v) => setFilterStatus(v as ReviewQueueStatus | 'all')}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="in-progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="escalated">Escalated</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterPriority} onValueChange={setFilterPriority}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priorities</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredItems.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Queue size={48} className="mx-auto mb-4 opacity-50" />
              <p>No items in queue matching current filters</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredItems.map(item => (
                <Card key={item.id} className="border-l-4" style={{
                  borderLeftColor: item.priority === 'urgent' ? 'oklch(0.60 0.22 25)' : 
                                   item.priority === 'high' ? 'oklch(0.75 0.15 70)' : 
                                   'oklch(0.25 0.03 250)'
                }}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getPriorityColor(item.priority)}>
                            {item.priority}
                          </Badge>
                          <Badge variant="outline" className="flex items-center gap-1">
                            {getStatusIcon(item.status)}
                            {item.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {queueTypes.find(q => q.type === item.queueType)?.label}
                          </span>
                        </div>

                        <div className="text-sm font-medium mb-1">
                          {item.objectType} #{item.objectId.slice(0, 8)}
                        </div>

                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          {item.assignedTo && (
                            <span className="flex items-center gap-1">
                              <User size={14} />
                              {item.assignedTo}
                            </span>
                          )}
                          {item.dueDate && (
                            <span className="flex items-center gap-1">
                              <CalendarBlank size={14} />
                              Due {format(new Date(item.dueDate), 'MMM d')}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Clock size={14} />
                            {format(new Date(item.createdAt), 'MMM d, h:mm a')}
                          </span>
                        </div>

                        {item.reviewNotes && (
                          <div className="mt-2 text-xs bg-muted p-2 rounded flex items-start gap-2">
                            <ChatCenteredDots size={14} className="mt-0.5 flex-shrink-0" />
                            <span>{item.reviewNotes}</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        {item.status === 'pending' && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleAssign(item.id, 'CurrentUser')}
                          >
                            Assign to Me
                          </Button>
                        )}
                        {item.status === 'in-progress' && (
                          <Button 
                            size="sm"
                            onClick={() => handleComplete(item.id, 'Review completed')}
                          >
                            <CheckCircle size={16} className="mr-1" />
                            Complete
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
