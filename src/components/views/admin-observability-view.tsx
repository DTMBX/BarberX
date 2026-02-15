import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  ChartBarHorizontal,
  Pulse,
  MagnifyingGlass,
  ShieldCheck,
  GitBranch,
  ClockCounterClockwise,
  Database,
  Cube,
  Warning,
  CheckCircle,
  XCircle,
  ArrowsClockwise,
  Speedometer,
  Eye,
} from '@phosphor-icons/react'
import {
  getObservabilityMetrics,
  getMetricsHistory,
  getStructuredLogs,
  getBackgroundJobs,
  runHealthChecks,
  verifyLedgerIntegrity,
  getTamperEvidentEvents,
  getSystemDependencies,
  generateSystemBOM,
} from '@/lib/admin-api'
import {
  ObservabilityMetrics,
  MetricsHistoryPoint,
  StructuredLog,
  BackgroundJob,
  HealthCheckSuite,
  LedgerVerification,
  SystemBillOfMaterials,
} from '@/lib/admin-types'

export function AdminObservabilityView() {
  const [metrics, setMetrics] = useState<ObservabilityMetrics | null>(null)
  const [metricsHistory, setMetricsHistory] = useState<Record<string, MetricsHistoryPoint[]>>({})
  const [logs, setLogs] = useState<StructuredLog[]>([])
  const [jobs, setJobs] = useState<BackgroundJob[]>([])
  const [healthSuite, setHealthSuite] = useState<HealthCheckSuite | null>(null)
  const [ledgerVerification, setLedgerVerification] = useState<LedgerVerification | null>(null)
  const [sbom, setSbom] = useState<SystemBillOfMaterials | null>(null)
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [selectedLog, setSelectedLog] = useState<StructuredLog | null>(null)

  const loadDashboardData = async () => {
    try {
      const [metricsData, logsData, jobsData] = await Promise.all([
        getObservabilityMetrics(),
        getStructuredLogs(50),
        getBackgroundJobs(),
      ])

      setMetrics(metricsData)
      setLogs(logsData)
      setJobs(jobsData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    }
  }

  const loadHistoricalMetrics = async () => {
    try {
      const [throughput, ocrRate, parsingErrors, searchLatency] = await Promise.all([
        getMetricsHistory('throughput', 24),
        getMetricsHistory('ocrRate', 24),
        getMetricsHistory('parsingErrors', 24),
        getMetricsHistory('searchLatency', 24),
      ])

      setMetricsHistory({
        throughput,
        ocrRate,
        parsingErrors,
        searchLatency,
      })
    } catch (error) {
      console.error('Failed to load historical metrics:', error)
    }
  }

  const loadHealthChecks = async () => {
    try {
      const suite = await runHealthChecks()
      setHealthSuite(suite)
    } catch (error) {
      console.error('Failed to run health checks:', error)
    }
  }

  const loadLedgerVerification = async () => {
    try {
      const verification = await verifyLedgerIntegrity()
      setLedgerVerification(verification)
    } catch (error) {
      console.error('Failed to verify ledger:', error)
    }
  }

  const loadSBOM = async () => {
    try {
      const bomData = await generateSystemBOM()
      setSbom(bomData)
    } catch (error) {
      console.error('Failed to generate SBOM:', error)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await Promise.all([
        loadDashboardData(),
        loadHistoricalMetrics(),
        loadHealthChecks(),
        loadLedgerVerification(),
        loadSBOM(),
      ])
      setLoading(false)
    }

    init()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      loadDashboardData()
    }, 10000)

    return () => clearInterval(interval)
  }, [autoRefresh])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-serif">Admin Observability Console</h1>
          <p className="text-muted-foreground mt-1">
            Enterprise-grade monitoring, audit trails, and operational intelligence
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <ArrowsClockwise className={autoRefresh ? 'animate-spin' : ''} />
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </Button>
          <Button variant="outline" size="sm" onClick={loadDashboardData}>
            <ArrowsClockwise />
            Refresh Now
          </Button>
        </div>
      </div>

      <Tabs defaultValue="metrics" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6 lg:w-auto">
          <TabsTrigger value="metrics">
            <Speedometer className="mr-2" />
            Metrics
          </TabsTrigger>
          <TabsTrigger value="logs">
            <MagnifyingGlass className="mr-2" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="jobs">
            <Pulse className="mr-2" />
            Jobs
          </TabsTrigger>
          <TabsTrigger value="health">
            <ShieldCheck className="mr-2" />
            Health
          </TabsTrigger>
          <TabsTrigger value="ledger">
            <ClockCounterClockwise className="mr-2" />
            Ledger
          </TabsTrigger>
          <TabsTrigger value="deps">
            <Cube className="mr-2" />
            Dependencies
          </TabsTrigger>
        </TabsList>

        <TabsContent value="metrics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Ingestion Throughput</p>
                  <p className="text-3xl font-bold mt-1">
                    {metrics?.ingestion.throughput || 0}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">docs/hour</p>
                </div>
                <ChartBarHorizontal className="text-primary" size={32} />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">OCR Success Rate</p>
                  <p className="text-3xl font-bold mt-1">
                    {((metrics?.ingestion.ocrRate || 0) * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">last hour</p>
                </div>
                <CheckCircle className="text-green-600" size={32} />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Parsing Errors</p>
                  <p className="text-3xl font-bold mt-1">
                    {metrics?.ingestion.parsingErrors || 0}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">last hour</p>
                </div>
                {(metrics?.ingestion.parsingErrors || 0) > 5 ? (
                  <Warning className="text-amber-600" size={32} />
                ) : (
                  <CheckCircle className="text-green-600" size={32} />
                )}
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Queue Depth</p>
                  <p className="text-3xl font-bold mt-1">
                    {metrics?.ingestion.queueDepth || 0}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">pending items</p>
                </div>
                <Database className="text-primary" size={32} />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Search Latency</p>
                  <p className="text-3xl font-bold mt-1">
                    {(metrics?.ingestion.searchLatency || 0).toFixed(0)}ms
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">p95</p>
                </div>
                <Pulse className="text-primary" size={32} />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Similarity Job Runtime</p>
                  <p className="text-3xl font-bold mt-1">
                    {((metrics?.ingestion.similarityJobRuntime || 0) / 1000).toFixed(1)}s
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">average</p>
                </div>
                <GitBranch className="text-primary" size={32} />
              </div>
            </Card>
          </div>

          <Card className="p-6">
            <h3 className="font-semibold text-lg mb-4">Historical Metrics (24 hours)</h3>
            <div className="space-y-6">
              {Object.entries(metricsHistory).map(([metric, points]) => {
                const anomalies = points.filter(p => p.anomaly).length
                return (
                  <div key={metric}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium capitalize">
                        {metric.replace(/([A-Z])/g, ' $1').trim()}
                      </p>
                      {anomalies > 0 && (
                        <Badge variant="destructive">
                          {anomalies} anomalies detected
                        </Badge>
                      )}
                    </div>
                    <div className="h-16 flex items-end gap-0.5">
                      {points.slice(-50).map((point, i) => {
                        const max = Math.max(...points.map(p => p.value))
                        const height = (point.value / max) * 100
                        return (
                          <div
                            key={i}
                            className={`flex-1 ${
                              point.anomaly
                                ? point.severity === 'critical'
                                  ? 'bg-destructive'
                                  : 'bg-amber-500'
                                : 'bg-primary'
                            } opacity-70 hover:opacity-100 transition-opacity`}
                            style={{ height: `${height}%` }}
                            title={`${point.value.toFixed(2)} at ${new Date(
                              point.timestamp
                            ).toLocaleTimeString()}`}
                          />
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Structured Logs</h3>
              <Badge variant="outline">{logs.length} entries</Badge>
            </div>

            <ScrollArea className="h-[600px]">
              <div className="space-y-2">
                {logs.map(log => (
                  <div
                    key={log.id}
                    className="p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => setSelectedLog(log)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge
                            variant={
                              log.level === 'error' || log.level === 'critical'
                                ? 'destructive'
                                : log.level === 'warn'
                                ? 'default'
                                : 'secondary'
                            }
                          >
                            {log.level}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {log.component}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm font-mono truncate">{log.message}</p>
                        <p className="text-xs text-muted-foreground mt-1 font-mono">
                          ID: {log.correlationId}
                        </p>
                      </div>
                      <Eye size={16} className="text-muted-foreground flex-shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </Card>

          {selectedLog && (
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">Log Details</h3>
                <Button variant="ghost" size="sm" onClick={() => setSelectedLog(null)}>
                  Close
                </Button>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Correlation ID</p>
                  <p className="text-sm font-mono mt-1">{selectedLog.correlationId}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Trace Chain</p>
                  <div className="text-sm font-mono mt-1 space-y-1">
                    {selectedLog.traceChain?.map((trace, i) => (
                      <div key={i} className="pl-4 border-l-2">
                        {trace}
                      </div>
                    ))}
                  </div>
                </div>
                {selectedLog.metadata && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Metadata</p>
                    <pre className="text-xs bg-muted p-3 rounded mt-1 overflow-auto">
                      {JSON.stringify(selectedLog.metadata, null, 2)}
                    </pre>
                  </div>
                )}
                {selectedLog.stackTrace && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Stack Trace</p>
                    <pre className="text-xs bg-muted p-3 rounded mt-1 overflow-auto font-mono">
                      {selectedLog.stackTrace}
                    </pre>
                  </div>
                )}
              </div>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="jobs" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Background Jobs</h3>
              <Badge variant="outline">{jobs.length} jobs</Badge>
            </div>

            <div className="space-y-3">
              {jobs.map(job => (
                <div key={job.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {job.type}
                      </Badge>
                      <Badge
                        variant={
                          job.status === 'completed'
                            ? 'default'
                            : job.status === 'failed'
                            ? 'destructive'
                            : job.status === 'running'
                            ? 'default'
                            : 'secondary'
                        }
                      >
                        {job.status}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      Priority: {job.priority}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Created</p>
                      <p>{new Date(job.createdAt).toLocaleString()}</p>
                    </div>
                    {job.startedAt && (
                      <div>
                        <p className="text-muted-foreground">Started</p>
                        <p>{new Date(job.startedAt).toLocaleString()}</p>
                      </div>
                    )}
                    {job.completedAt && (
                      <div>
                        <p className="text-muted-foreground">Completed</p>
                        <p>{new Date(job.completedAt).toLocaleString()}</p>
                      </div>
                    )}
                    <div>
                      <p className="text-muted-foreground">Retries</p>
                      <p>
                        {job.retryCount} / {job.maxRetries}
                      </p>
                    </div>
                  </div>

                  {job.status === 'running' && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-muted-foreground">Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {job.errorStack && (
                    <Alert variant="destructive" className="mt-3">
                      <AlertDescription className="text-xs font-mono">
                        {job.errorStack}
                      </AlertDescription>
                    </Alert>
                  )}

                  {job.estimatedCost !== undefined && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Est. Cost: ${job.estimatedCost.toFixed(4)}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="health" className="space-y-4">
          {healthSuite && (
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-lg">System Health</h3>
                  <p className="text-sm text-muted-foreground">
                    Last checked: {new Date(healthSuite.ranAt).toLocaleString()}
                  </p>
                </div>
                <Badge
                  variant={
                    healthSuite.overallStatus === 'healthy'
                      ? 'default'
                      : healthSuite.overallStatus === 'degraded'
                      ? 'default'
                      : 'destructive'
                  }
                  className="text-lg px-4 py-2"
                >
                  {healthSuite.overallStatus === 'healthy' && <CheckCircle className="mr-2" />}
                  {healthSuite.overallStatus === 'degraded' && <Warning className="mr-2" />}
                  {healthSuite.overallStatus === 'critical' && <XCircle className="mr-2" />}
                  {healthSuite.overallStatus.toUpperCase()}
                </Badge>
              </div>

              <div className="space-y-3">
                {healthSuite.checks.map((check, i) => (
                  <div key={i} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {check.status === 'green' && (
                          <CheckCircle className="text-green-600" size={24} />
                        )}
                        {check.status === 'yellow' && (
                          <Warning className="text-amber-600" size={24} />
                        )}
                        {check.status === 'red' && (
                          <XCircle className="text-destructive" size={24} />
                        )}
                        <div>
                          <p className="font-medium">{check.name}</p>
                          <p className="text-sm text-muted-foreground">{check.message}</p>
                        </div>
                      </div>
                      <div className="text-right text-sm text-muted-foreground">
                        <p className="capitalize">{check.category}</p>
                        <p>{check.executionTime}ms</p>
                      </div>
                    </div>
                    {check.details && (
                      <pre className="text-xs bg-muted p-2 rounded mt-2 overflow-auto">
                        {JSON.stringify(check.details, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>

              <Separator className="my-4" />
              <p className="text-sm text-muted-foreground">
                Total execution time: {healthSuite.duration}ms
              </p>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="ledger" className="space-y-4">
          {ledgerVerification && (
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-lg">Tamper-Evident Ledger</h3>
                <Badge
                  variant={ledgerVerification.valid ? 'default' : 'destructive'}
                  className="text-lg px-4 py-2"
                >
                  {ledgerVerification.valid ? (
                    <>
                      <CheckCircle className="mr-2" />
                      VERIFIED
                    </>
                  ) : (
                    <>
                      <XCircle className="mr-2" />
                      COMPROMISED
                    </>
                  )}
                </Badge>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div>
                  <p className="text-sm text-muted-foreground">Total Events</p>
                  <p className="text-2xl font-bold">{ledgerVerification.totalEvents}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Verified</p>
                  <p className="text-2xl font-bold text-green-600">
                    {ledgerVerification.verifiedEvents}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Broken Links</p>
                  <p
                    className={`text-2xl font-bold ${
                      ledgerVerification.brokenLinks.length > 0
                        ? 'text-destructive'
                        : 'text-green-600'
                    }`}
                  >
                    {ledgerVerification.brokenLinks.length}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Verification Time</p>
                  <p className="text-2xl font-bold">{ledgerVerification.verificationTime}ms</p>
                </div>
              </div>

              {ledgerVerification.brokenLinks.length > 0 && (
                <Alert variant="destructive">
                  <AlertDescription>
                    Chain integrity compromised at events:{' '}
                    {ledgerVerification.brokenLinks.join(', ')}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                variant="outline"
                className="mt-4"
                onClick={loadLedgerVerification}
              >
                <ArrowsClockwise className="mr-2" />
                Re-verify Ledger
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="deps" className="space-y-4">
          {sbom && (
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-lg">System Bill of Materials</h3>
                  <p className="text-sm text-muted-foreground">
                    Generated: {new Date(sbom.generatedAt).toLocaleString()}
                  </p>
                </div>
                <Badge variant="outline">Version {sbom.systemVersion}</Badge>
              </div>

              <div className="space-y-3">
                {sbom.dependencies.map((dep, i) => (
                  <div key={i} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-semibold">{dep.name}</p>
                        <p className="text-sm text-muted-foreground">
                          Version {dep.version} · {dep.type}
                        </p>
                      </div>
                      {dep.vulnerabilities && dep.vulnerabilities.length > 0 ? (
                        <Badge variant="destructive">
                          {dep.vulnerabilities.length} vulnerabilities
                        </Badge>
                      ) : (
                        <Badge variant="default">
                          <CheckCircle className="mr-1" size={14} />
                          Secure
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p>Hash: {dep.hash}</p>
                      <p>Last updated: {new Date(dep.lastUpdated).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))}
              </div>

              <Separator className="my-4" />
              <div className="text-sm text-muted-foreground space-y-1">
                <p>Build Hash: {sbom.buildHash}</p>
                <p>Environment: {sbom.deploymentEnvironment}</p>
                <p>SBOM Version: {sbom.sbomVersion}</p>
              </div>

              <Button variant="outline" className="mt-4">
                Export SBOM
              </Button>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
