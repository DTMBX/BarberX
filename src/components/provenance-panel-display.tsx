import { ProvenancePanel } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { SealCheck, Warning, Link as LinkIcon, Clock, Hash } from '@phosphor-icons/react'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'

interface ProvenancePanelDisplayProps {
  provenance: ProvenancePanel
  onExportReport?: () => void
}

export function ProvenancePanelDisplay({ provenance, onExportReport }: ProvenancePanelDisplayProps) {
  const { sourceRegistryEntry, retrievalMetadata, verificationChain, versionSnapshot } = provenance

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              {sourceRegistryEntry.isOfficialSource ? (
                <SealCheck className="text-primary" weight="fill" />
              ) : (
                <Warning className="text-amber-500" weight="fill" />
              )}
              Source Provenance
            </CardTitle>
            <CardDescription>
              Court-defensible verification and retrieval metadata
            </CardDescription>
          </div>
          {onExportReport && (
            <Button variant="outline" size="sm" onClick={onExportReport}>
              Export Report
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Source Information</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <Badge variant={sourceRegistryEntry.isOfficialSource ? "default" : "secondary"}>
                  {sourceRegistryEntry.isOfficialSource ? 'Official Source' : 'Non-official Mirror'}
                </Badge>
              </div>
              <div className="flex items-start gap-2">
                <LinkIcon className="mt-0.5 flex-shrink-0 text-muted-foreground" size={16} />
                <div className="flex-1">
                  <div className="font-medium">Official URL</div>
                  <a
                    href={sourceRegistryEntry.officialUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline break-all"
                  >
                    {sourceRegistryEntry.officialUrl}
                  </a>
                </div>
              </div>
              <div>
                <div className="font-medium">Publisher</div>
                <div className="text-muted-foreground">{sourceRegistryEntry.publisher}</div>
              </div>
              <div>
                <div className="font-medium">Retrieval Method</div>
                <div className="text-muted-foreground capitalize">{sourceRegistryEntry.retrievalMethod.replace(/-/g, ' ')}</div>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="text-sm font-medium mb-2">Verification Metadata</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <Clock className="mt-0.5 flex-shrink-0 text-muted-foreground" size={16} />
                <div className="flex-1">
                  <div className="font-medium">Retrieved At</div>
                  <div className="text-muted-foreground">
                    {new Date(retrievalMetadata.retrievedAt).toLocaleString('en-US', {
                      dateStyle: 'long',
                      timeStyle: 'long'
                    })}
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Hash className="mt-0.5 flex-shrink-0 text-muted-foreground" size={16} />
                <div className="flex-1">
                  <div className="font-medium">Checksum (SHA-256 equivalent)</div>
                  <code className="text-xs text-muted-foreground font-mono">{retrievalMetadata.checksum}</code>
                </div>
              </div>
              <div>
                <div className="font-medium">Parsing Method</div>
                <div className="text-muted-foreground capitalize">{retrievalMetadata.parsingMethod}</div>
              </div>
            </div>
          </div>

          {versionSnapshot && (
            <>
              <Separator />
              <div>
                <h4 className="text-sm font-medium mb-2">Version Information</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <div className="font-medium">Effective Start</div>
                    <div className="text-muted-foreground">
                      {new Date(versionSnapshot.effectiveStart).toLocaleDateString('en-US', {
                        dateStyle: 'long'
                      })}
                    </div>
                  </div>
                  {versionSnapshot.effectiveEnd && (
                    <div>
                      <div className="font-medium">Effective End</div>
                      <div className="text-muted-foreground">
                        {new Date(versionSnapshot.effectiveEnd).toLocaleDateString('en-US', {
                          dateStyle: 'long'
                        })}
                      </div>
                    </div>
                  )}
                  {versionSnapshot.notes && (
                    <div>
                      <div className="font-medium">Notes</div>
                      <div className="text-muted-foreground">{versionSnapshot.notes}</div>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {verificationChain.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="text-sm font-medium mb-2">Verification Chain</h4>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-3">
                    {verificationChain.map((step, index) => (
                      <div key={index} className="text-sm p-3 bg-muted/50 rounded-lg">
                        <div className="font-medium">Verification {index + 1}</div>
                        <div className="mt-2 space-y-1 text-muted-foreground">
                          <div><span className="font-medium">By:</span> {step.verifiedBy}</div>
                          <div>
                            <span className="font-medium">At:</span>{' '}
                            {new Date(step.verifiedAt).toLocaleString()}
                          </div>
                          <div><span className="font-medium">Method:</span> {step.method}</div>
                          {step.notes && (
                            <div className="mt-2 text-sm">{step.notes}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </>
          )}
        </div>

        {!sourceRegistryEntry.isOfficialSource && sourceRegistryEntry.curatorJustification && (
          <div className="p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-700 rounded-lg">
            <div className="flex gap-2">
              <Warning className="flex-shrink-0 text-amber-600 dark:text-amber-400" weight="fill" />
              <div className="text-sm">
                <div className="font-medium text-amber-900 dark:text-amber-200">Non-official Source Notice</div>
                <div className="text-amber-700 dark:text-amber-400 mt-1">
                  {sourceRegistryEntry.curatorJustification}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="text-xs text-muted-foreground italic pt-2 border-t">
          This provenance panel provides transparent documentation of source verification and retrieval
          for court-defensible citation purposes. All metadata is immutably logged and auditable.
        </div>
      </CardContent>
    </Card>
  )
}
