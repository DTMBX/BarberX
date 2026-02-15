import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { 
  MagnifyingGlass,
  Clock,
  Graph,
  Link,
  FileText,
  Warning,
  ChartLineUp
} from '@phosphor-icons/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ConfidenceBar } from '@/components/ConfidenceBar'
import { QualityBadge } from '@/components/QualityBadge'
import { 
  Finding, 
  TimelineEvent, 
  DocumentSimilarity,
  Relationship,
  DocumentAnalysis,
  QualityMetrics
} from '@/lib/types'

interface DocumentAnalysisPanelProps {
  documentId: string
}

function SnippetDisplay({ text }: { text: string }) {
  return (
    <div className="bg-muted/50 border rounded p-3 text-sm font-mono leading-relaxed">
      {text}
    </div>
  )
}

export function DocumentAnalysisPanel({ documentId }: DocumentAnalysisPanelProps) {
  const [findings] = useKV<Finding[]>(`findings-${documentId}`, [])
  const [timelineEvents] = useKV<TimelineEvent[]>(`timeline-${documentId}`, [])
  const [similarities] = useKV<DocumentSimilarity[]>(`similarities-${documentId}`, [])
  const [relationships] = useKV<Relationship[]>(`relationships-${documentId}`, [])
  const [qualityMetrics] = useKV<QualityMetrics>(`quality-${documentId}`, undefined)
  const [analysis] = useKV<DocumentAnalysis>(`analysis-${documentId}`, {
    documentId,
    findings: [],
    timelineEvents: [],
    similarities: [],
    graphEdges: []
  })

  const getSeverityColor = (severity: Finding['severity']) => {
    switch (severity) {
      case 'high':
        return 'text-destructive'
      case 'medium':
        return 'text-[oklch(0.70_0.15_70)]'
      case 'low':
        return 'text-[oklch(0.70_0.15_280)]'
      default:
        return 'text-muted-foreground'
    }
  }

  const getSeverityBadge = (severity: Finding['severity']) => {
    switch (severity) {
      case 'high':
        return 'destructive'
      case 'medium':
        return 'default'
      case 'low':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <div className="space-y-4">
      <Alert className="border-accent/30 bg-accent/10">
        <Warning className="text-accent" size={20} />
        <AlertDescription className="text-sm">
          <strong className="font-semibold">Analysis Disclaimer:</strong> All automated analysis outputs are probabilistic 
          and must be verified against source documents. No conclusions of guilt should be drawn from automated findings.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="findings" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="quality">
            <ChartLineUp size={16} />
            Quality
          </TabsTrigger>
          <TabsTrigger value="findings">
            <MagnifyingGlass size={16} />
            Findings ({(findings || []).length})
          </TabsTrigger>
          <TabsTrigger value="timeline">
            <Clock size={16} />
            Timeline ({(timelineEvents || []).length})
          </TabsTrigger>
          <TabsTrigger value="similar">
            <Link size={16} />
            Similar ({(similarities || []).length})
          </TabsTrigger>
          <TabsTrigger value="graph">
            <Graph size={16} />
            Edges ({(relationships || []).length})
          </TabsTrigger>
          <TabsTrigger value="summary">
            <FileText size={16} />
            Summary
          </TabsTrigger>
        </TabsList>

        <TabsContent value="quality" className="mt-4">
          {qualityMetrics ? (
            <QualityBadge metrics={qualityMetrics} />
          ) : (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <ChartLineUp size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                <p>No quality metrics available yet.</p>
                <p className="text-sm mt-1">Run quality scoring scripts to analyze document quality.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="findings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Pattern Findings</CardTitle>
              <CardDescription>
                Keyword and phrase matches detected by pattern scanner scripts
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(findings || []).length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <MagnifyingGlass size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                  <p>No findings generated yet.</p>
                  <p className="text-sm mt-1">Run pattern scanner scripts to analyze this document.</p>
                </div>
              ) : (
                <ScrollArea className="h-[500px]">
                  <div className="space-y-4">
                    {(findings || []).map((finding) => (
                      <div key={finding.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant={getSeverityBadge(finding.severity)}>
                                {finding.severity}
                              </Badge>
                              <Badge variant="outline">{finding.category}</Badge>
                              {finding.pattern && (
                                <span className="text-xs font-mono text-muted-foreground">
                                  {finding.pattern}
                                </span>
                              )}
                            </div>
                            {finding.pageNo && (
                              <div className="text-xs text-muted-foreground">
                                Page {finding.pageNo}
                              </div>
                            )}
                          </div>
                          <ConfidenceBar confidence={finding.confidence} />
                        </div>

                        <SnippetDisplay text={finding.snippet} />

                        <div className="flex items-center justify-between text-xs">
                          <div className="text-muted-foreground">
                            Review Status: <span className="font-medium">{finding.reviewStatus}</span>
                          </div>
                          <div className="text-muted-foreground">
                            {new Date(finding.createdAt).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Timeline Events</CardTitle>
              <CardDescription>
                Extracted and normalized dates with source evidence
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(timelineEvents || []).length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Clock size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                  <p>No timeline events extracted yet.</p>
                  <p className="text-sm mt-1">Run timeline builder scripts to analyze dates in this document.</p>
                </div>
              ) : (
                <ScrollArea className="h-[500px]">
                  <div className="space-y-4">
                    {(timelineEvents || [])
                      .sort((a, b) => new Date(a.normalizedDate).getTime() - new Date(b.normalizedDate).getTime())
                      .map((event) => (
                        <div key={event.id} className="border rounded-lg p-4 space-y-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="text-lg font-semibold mb-1">
                                {new Date(event.normalizedDate).toLocaleDateString('en-US', {
                                  year: 'numeric',
                                  month: 'long',
                                  day: 'numeric'
                                })}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                Raw text: "{event.rawDateText}"
                              </div>
                              {event.pageNo && (
                                <div className="text-xs text-muted-foreground mt-1">
                                  Page {event.pageNo}
                                </div>
                              )}
                            </div>
                            <ConfidenceBar confidence={event.dateConfidence} />
                          </div>

                          <div className="text-sm">{event.eventDescription}</div>

                          <SnippetDisplay text={event.snippet} />

                          <div className="text-xs text-muted-foreground">
                            {new Date(event.createdAt).toLocaleString()}
                          </div>
                        </div>
                      ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="similar" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Similar Documents</CardTitle>
              <CardDescription>
                Documents with high similarity scores based on content analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(similarities || []).length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Link size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                  <p>No similar documents found yet.</p>
                  <p className="text-sm mt-1">Run similarity linker scripts to find related documents.</p>
                </div>
              ) : (
                <ScrollArea className="h-[500px]">
                  <div className="space-y-4">
                    {(similarities || []).map((similarity) => (
                      <div key={similarity.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="font-semibold mb-1">
                              Document: {similarity.documentAId === documentId 
                                ? similarity.documentBId 
                                : similarity.documentAId}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Similarity: {(similarity.similarityScore * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>

                        {similarity.matchedConcepts.length > 0 && (
                          <div>
                            <div className="text-xs font-medium mb-2">Matched Concepts</div>
                            <div className="flex flex-wrap gap-1">
                              {similarity.matchedConcepts.map((concept, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {concept}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="text-xs text-muted-foreground">
                          {new Date(similarity.createdAt).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="graph" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Graph Edges</CardTitle>
              <CardDescription>
                Evidence-backed relationship edges involving entities in this document
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(relationships || []).length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Graph size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                  <p>No relationship edges generated yet.</p>
                  <p className="text-sm mt-1">Run relationship engine scripts to analyze entity connections.</p>
                </div>
              ) : (
                <ScrollArea className="h-[500px]">
                  <div className="space-y-4">
                    {(relationships || []).map((rel) => (
                      <div key={rel.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="font-semibold mb-1">
                              {rel.entityAId} ↔ {rel.entityBId}
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{rel.type}</Badge>
                              <Badge variant={rel.reviewStatus === 'approved' ? 'default' : 'secondary'}>
                                {rel.reviewStatus}
                              </Badge>
                            </div>
                          </div>
                          <ConfidenceBar confidence={rel.confidence} />
                        </div>

                        <div className="text-xs text-muted-foreground">
                          Evidence chunks: {rel.evidenceChunkIds.length}
                        </div>

                        {rel.reviewedBy && (
                          <div className="text-xs text-muted-foreground">
                            Reviewed by {rel.reviewedBy} on {rel.reviewedAt && new Date(rel.reviewedAt).toLocaleString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Document Summary</CardTitle>
              <CardDescription>
                Objective, non-accusatory summary for navigation purposes
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.summary ? (
                <div className="space-y-4">
                  <Alert className="border-accent/30 bg-accent/10">
                    <Warning className="text-accent" size={20} />
                    <AlertDescription className="text-xs">
                      This summary is probabilistic and generated for navigation purposes only. 
                      Always verify information against the source document.
                    </AlertDescription>
                  </Alert>

                  <div>
                    <div className="text-sm font-medium mb-2">Abstract</div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {analysis.summary.abstract}
                    </p>
                  </div>

                  <Separator />

                  {analysis.summary.topics.length > 0 && (
                    <div>
                      <div className="text-sm font-medium mb-2">Topics</div>
                      <div className="flex flex-wrap gap-2">
                        {analysis.summary.topics.map((topic, idx) => (
                          <Badge key={idx} variant="secondary">{topic}</Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysis.summary.keyEntities.length > 0 && (
                    <div>
                      <div className="text-sm font-medium mb-2">Key Entities</div>
                      <div className="flex flex-wrap gap-2">
                        {analysis.summary.keyEntities.map((entity, idx) => (
                          <Badge key={idx} variant="outline">{entity}</Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysis.summary.dateRange && (
                    <div>
                      <div className="text-sm font-medium mb-2">Date Range</div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(analysis.summary.dateRange[0]).toLocaleDateString()} — {new Date(analysis.summary.dateRange[1]).toLocaleDateString()}
                      </div>
                    </div>
                  )}

                  {analysis.summary.documentType && (
                    <div>
                      <div className="text-sm font-medium mb-2">Document Type</div>
                      <Badge>{analysis.summary.documentType}</Badge>
                    </div>
                  )}

                  {analysis.summary.keyPassages && analysis.summary.keyPassages.length > 0 && (
                    <>
                      <Separator />
                      <div>
                        <div className="text-sm font-medium mb-3">Key Passages</div>
                        <div className="space-y-3">
                          {analysis.summary.keyPassages.map((passage, idx) => (
                            <div key={idx} className="border rounded-lg p-3">
                              <div className="text-xs text-muted-foreground mb-2">
                                Page {passage.pageNo} • {passage.reason}
                              </div>
                              <SnippetDisplay text={passage.snippet} />
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
                  <p>No summary generated yet.</p>
                  <p className="text-sm mt-1">Run summarization scripts to generate document abstracts.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
