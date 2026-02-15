import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ClockCounterClockwise, FunnelSimple, Download, User } from '@phosphor-icons/react'
import { AuditLogEntry, AuditAction, getAuditLogs } from '@/lib/compliance'

interface AuditLogViewerProps {
  isAdmin?: boolean
}

export function AuditLogViewer({ isAdmin = false }: AuditLogViewerProps) {
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<AuditLogEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filterUserId, setFilterUserId] = useState('')
  const [filterAction, setFilterAction] = useState<AuditAction | 'all'>('all')
  const [filterEntityType, setFilterEntityType] = useState('all')

  useEffect(() => {
    loadLogs()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [logs, filterUserId, filterAction, filterEntityType])

  const loadLogs = async () => {
    setIsLoading(true)
    try {
      const allLogs = await getAuditLogs()
      setLogs(allLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp)))
    } catch (error) {
      console.error('Error loading audit logs:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...logs]

    if (filterUserId) {
      filtered = filtered.filter((log) =>
        log.userId.toLowerCase().includes(filterUserId.toLowerCase())
      )
    }

    if (filterAction !== 'all') {
      filtered = filtered.filter((log) => log.action === filterAction)
    }

    if (filterEntityType !== 'all') {
      filtered = filtered.filter((log) => log.entityType === filterEntityType)
    }

    setFilteredLogs(filtered)
  }

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User ID', 'Role', 'Action', 'Entity Type', 'Entity ID', 'IP Address'].join(
        ','
      ),
      ...filteredLogs.map((log) =>
        [
          log.timestamp,
          log.userId,
          log.userRole,
          log.action,
          log.entityType,
          log.entityId,
          log.ipAddress || 'N/A',
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-logs-${new Date().toISOString()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getActionBadgeColor = (action: AuditAction) => {
    switch (action) {
      case 'create':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-700'
      case 'update':
        return 'bg-primary/10 text-primary border-primary/20 dark:bg-primary/15 dark:border-primary/30'
      case 'delete':
        return 'bg-destructive/10 text-destructive border-destructive/20 dark:bg-destructive/15 dark:border-destructive/30'
      case 'approve':
        return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700'
      case 'reject':
        return 'bg-destructive/10 text-destructive border-destructive/20 dark:bg-destructive/15 dark:border-destructive/30'
      case 'verify':
        return 'bg-accent/10 text-accent-foreground dark:text-accent border-accent/20 dark:bg-accent/15 dark:border-accent/30'
      case 'flag':
        return 'bg-destructive/10 text-destructive border-destructive/20 dark:bg-destructive/15 dark:border-destructive/30'
      default:
        return 'bg-muted text-muted-foreground border-border'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const entityTypes = Array.from(new Set(logs.map((log) => log.entityType)))

  if (!isAdmin) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access Denied</CardTitle>
          <CardDescription>
            You do not have permission to view audit logs. Administrator access required.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-lg">
                <ClockCounterClockwise className="w-6 h-6 text-primary" weight="fill" />
              </div>
              <div>
                <CardTitle className="text-2xl font-serif">Audit Log</CardTitle>
                <CardDescription className="text-base mt-1">
                  Immutable record of all system actions for court-defensible compliance
                </CardDescription>
              </div>
            </div>
            <Button onClick={exportLogs} variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-primary/5 dark:bg-primary/10 border border-primary/20 dark:border-primary/30 rounded-lg p-4 mb-6">
            <p className="text-sm font-semibold text-primary dark:text-foreground mb-2">
              🔒 Court-Defensible Audit Trail
            </p>
            <p className="text-sm text-primary/80 dark:text-foreground/70 leading-relaxed">
              All actions are logged with timestamps, user identification, and full change history.
              This audit trail is immutable and can be used to demonstrate compliance and
              accountability in legal proceedings. Retention period: 7 years minimum.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="space-y-2">
              <Label htmlFor="filter-user">Filter by User ID</Label>
              <Input
                id="filter-user"
                placeholder="Enter user ID..."
                value={filterUserId}
                onChange={(e) => setFilterUserId(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="filter-action">Filter by Action</Label>
              <Select value={filterAction} onValueChange={(v) => setFilterAction(v as AuditAction | 'all')}>
                <SelectTrigger id="filter-action">
                  <SelectValue placeholder="All actions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All actions</SelectItem>
                  <SelectItem value="create">Create</SelectItem>
                  <SelectItem value="update">Update</SelectItem>
                  <SelectItem value="delete">Delete</SelectItem>
                  <SelectItem value="approve">Approve</SelectItem>
                  <SelectItem value="reject">Reject</SelectItem>
                  <SelectItem value="verify">Verify</SelectItem>
                  <SelectItem value="view">View</SelectItem>
                  <SelectItem value="export">Export</SelectItem>
                  <SelectItem value="submit">Submit</SelectItem>
                  <SelectItem value="flag">Flag</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="filter-entity">Filter by Entity Type</Label>
              <Select value={filterEntityType} onValueChange={setFilterEntityType}>
                <SelectTrigger id="filter-entity">
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All types</SelectItem>
                  {entityTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator className="mb-6" />

          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              Showing {filteredLogs.length} of {logs.length} entries
            </p>
            <Button onClick={loadLogs} variant="ghost" size="sm">
              Refresh
            </Button>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <p className="text-muted-foreground">Loading audit logs...</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <p className="text-muted-foreground">No audit logs found</p>
            </div>
          ) : (
            <ScrollArea className="h-[600px] rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Entity Type</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>IP Address</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-xs">
                        {formatTimestamp(log.timestamp)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-sm font-medium">{log.userId}</p>
                            <p className="text-xs text-muted-foreground">{log.userRole}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`${getActionBadgeColor(log.action)} border font-semibold`}
                        >
                          {log.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{log.entityType}</TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {log.entityId}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {log.ipAddress || 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
