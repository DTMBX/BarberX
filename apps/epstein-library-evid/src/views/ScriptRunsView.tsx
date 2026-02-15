import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { 
  Play, 
  Stop, 
  CheckCircle, 
  XCircle, 
  Clock,
  ArrowClockwise,
  Gear,
  Warning,
  CaretRight
} from '@phosphor-icons/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { AnalysisScript, ScriptRun } from '@/lib/types'
import { getAllScripts } from '@/lib/scriptDefinitions'
import { scriptRunner } from '@/lib/scriptRunner'
import { formatDuration } from '@/lib/utils'

export function ScriptRunsView() {
  const [scripts] = useState<AnalysisScript[]>(getAllScripts())
  const [scriptRuns, setScriptRuns] = useKV<ScriptRun[]>('script-runs', [])
  const [selectedRun, setSelectedRun] = useState<ScriptRun | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const getScriptById = (scriptId: string) => {
    return scripts.find(s => s.id === scriptId)
  }

  const getStatusIcon = (status: ScriptRun['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-[oklch(0.60_0.18_145)]" size={20} weight="fill" />
      case 'failed':
        return <XCircle className="text-destructive" size={20} weight="fill" />
      case 'running':
        return <Clock className="text-[oklch(0.70_0.15_280)] animate-pulse" size={20} weight="fill" />
      case 'cancelled':
        return <Stop className="text-muted-foreground" size={20} weight="fill" />
      default:
        return <Clock className="text-muted-foreground" size={20} />
    }
  }

  const getStatusBadgeVariant = (status: ScriptRun['status']) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'failed':
        return 'destructive'
      case 'running':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const filteredRuns = (scriptRuns || []).filter(run => {
    if (activeTab === 'all') return true
    if (activeTab === 'running') return run.status === 'running'
    if (activeTab === 'completed') return run.status === 'completed'
    if (activeTab === 'failed') return run.status === 'failed'
    return true
  })

  const handleReplayRun = async (run: ScriptRun) => {
    console.log('Replaying run:', run.id)
  }

  const handleCancelRun = (runId: string) => {
    if (scriptRunner.cancelScriptRun(runId)) {
      setScriptRuns(current => 
        (current || []).map(r => r.id === runId ? { ...r, status: 'cancelled' as const } : r)
      )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis Script Runs</h1>
        <p className="text-muted-foreground mt-2">
          Monitor and manage analysis script executions with full audit trails and replay controls.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{(scriptRuns || []).length}</div>
            <p className="text-xs text-muted-foreground mt-1">All-time script executions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Running Now</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[oklch(0.70_0.15_280)]">
              {(scriptRuns || []).filter(r => r.status === 'running').length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Active script executions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[oklch(0.60_0.18_145)]">
              {(scriptRuns || []).length > 0 
                ? `${(((scriptRuns || []).filter(r => r.status === 'completed').length / (scriptRuns || []).length) * 100).toFixed(0)}%`
                : '—'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Successful completions</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All Runs</TabsTrigger>
          <TabsTrigger value="running">Running</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="failed">Failed</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          {filteredRuns.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Gear size={48} className="text-muted-foreground mb-4" weight="duotone" />
                <p className="text-muted-foreground text-center">
                  No script runs found.
                  <br />
                  Scripts will execute automatically after ingestion stages or can be triggered manually.
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Status</TableHead>
                      <TableHead>Script</TableHead>
                      <TableHead>Started</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Documents</TableHead>
                      <TableHead>Findings</TableHead>
                      <TableHead>Errors</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRuns.map((run) => {
                      const script = getScriptById(run.scriptId)
                      const duration = run.endedAt 
                        ? new Date(run.endedAt).getTime() - new Date(run.startedAt).getTime()
                        : Date.now() - new Date(run.startedAt).getTime()

                      return (
                        <TableRow key={run.id} className="cursor-pointer hover:bg-muted/50">
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getStatusIcon(run.status)}
                              <Badge variant={getStatusBadgeVariant(run.status)}>
                                {run.status}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{script?.name || run.scriptId}</div>
                              <div className="text-xs text-muted-foreground">v{run.scriptVersion}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {new Date(run.startedAt).toLocaleString()}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm font-mono">
                              {formatDuration(duration)}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">{run.documentsProcessed}</div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm font-semibold">{run.findingsGenerated}</div>
                          </TableCell>
                          <TableCell>
                            {run.errors.length > 0 && (
                              <div className="flex items-center gap-1 text-destructive">
                                <Warning size={16} weight="fill" />
                                <span className="text-sm">{run.errors.length}</span>
                              </div>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button 
                                    variant="ghost" 
                                    size="sm"
                                    onClick={() => setSelectedRun(run)}
                                  >
                                    <CaretRight size={16} />
                                    Details
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-3xl max-h-[80vh]">
                                  <DialogHeader>
                                    <DialogTitle>Script Run Details</DialogTitle>
                                    <DialogDescription>
                                      {script?.name} • Run ID: {run.id}
                                    </DialogDescription>
                                  </DialogHeader>
                                  <ScrollArea className="max-h-[60vh]">
                                    <div className="space-y-4">
                                      <div className="grid grid-cols-2 gap-4">
                                        <div>
                                          <div className="text-sm font-medium mb-1">Status</div>
                                          <Badge variant={getStatusBadgeVariant(run.status)}>
                                            {run.status}
                                          </Badge>
                                        </div>
                                        <div>
                                          <div className="text-sm font-medium mb-1">Version</div>
                                          <div className="text-sm text-muted-foreground">
                                            {run.scriptVersion}
                                          </div>
                                        </div>
                                        <div>
                                          <div className="text-sm font-medium mb-1">Started At</div>
                                          <div className="text-sm text-muted-foreground">
                                            {new Date(run.startedAt).toLocaleString()}
                                          </div>
                                        </div>
                                        <div>
                                          <div className="text-sm font-medium mb-1">Duration</div>
                                          <div className="text-sm text-muted-foreground font-mono">
                                            {formatDuration(duration)}
                                          </div>
                                        </div>
                                      </div>

                                      <Separator />

                                      <div>
                                        <div className="text-sm font-medium mb-2">Metrics</div>
                                        <div className="grid grid-cols-3 gap-4 text-sm">
                                          <div>
                                            <div className="text-muted-foreground">Documents</div>
                                            <div className="font-semibold">{run.documentsProcessed}</div>
                                          </div>
                                          <div>
                                            <div className="text-muted-foreground">Findings</div>
                                            <div className="font-semibold">{run.findingsGenerated}</div>
                                          </div>
                                          <div>
                                            <div className="text-muted-foreground">Avg Time/Doc</div>
                                            <div className="font-semibold font-mono">
                                              {run.metrics.avgTimePerDocument 
                                                ? formatDuration(run.metrics.avgTimePerDocument)
                                                : '—'}
                                            </div>
                                          </div>
                                        </div>
                                      </div>

                                      {run.errors.length > 0 && (
                                        <>
                                          <Separator />
                                          <div>
                                            <div className="text-sm font-medium mb-2 flex items-center gap-2">
                                              <Warning size={16} className="text-destructive" weight="fill" />
                                              Errors ({run.errors.length})
                                            </div>
                                            <div className="space-y-2">
                                              {run.errors.map((error, idx) => (
                                                <Alert key={idx} variant="destructive">
                                                  <AlertDescription className="text-xs">
                                                    <div className="font-semibold mb-1">{error.message}</div>
                                                    {error.documentId && (
                                                      <div className="text-muted-foreground">
                                                        Document: {error.documentId}
                                                      </div>
                                                    )}
                                                    <div className="text-muted-foreground">
                                                      {new Date(error.timestamp).toLocaleString()}
                                                    </div>
                                                  </AlertDescription>
                                                </Alert>
                                              ))}
                                            </div>
                                          </div>
                                        </>
                                      )}

                                      <Separator />

                                      <div>
                                        <div className="text-sm font-medium mb-2">Configuration Hash</div>
                                        <div className="font-mono text-xs text-muted-foreground bg-muted p-2 rounded">
                                          {run.configHash}
                                        </div>
                                      </div>

                                      <div>
                                        <div className="text-sm font-medium mb-2">Input Hashes</div>
                                        <div className="font-mono text-xs text-muted-foreground bg-muted p-2 rounded space-y-1">
                                          {Object.entries(run.inputHashes).map(([key, hash]) => (
                                            <div key={key}>
                                              <span className="text-foreground">{key}:</span> {hash}
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    </div>
                                  </ScrollArea>
                                </DialogContent>
                              </Dialog>

                              {run.status === 'running' ? (
                                <Button 
                                  variant="destructive" 
                                  size="sm"
                                  onClick={() => handleCancelRun(run.id)}
                                >
                                  <Stop size={16} />
                                  Cancel
                                </Button>
                              ) : run.canReplay && (
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={() => handleReplayRun(run)}
                                >
                                  <ArrowClockwise size={16} />
                                  Replay
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
