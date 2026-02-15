import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { 
  Play, 
  Gear, 
  CheckCircle, 
  XCircle,
  Lock,
  CaretRight,
  Flask
} from '@phosphor-icons/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AnalysisScript, ScriptCategory } from '@/lib/types'
import { getAllScripts, SCRIPT_DEFINITIONS } from '@/lib/scriptDefinitions'

const categoryLabels: Record<ScriptCategory, string> = {
  'pattern-scanner': 'Pattern Scanner',
  'entity-enrichment': 'Entity Enrichment',
  'timeline-builder': 'Timeline Builder',
  'similarity-linker': 'Similarity Linker',
  'relationship-engine': 'Relationship Engine',
  'summarization': 'Summarization',
  'export-generator': 'Export Generator'
}

const categoryDescriptions: Record<ScriptCategory, string> = {
  'pattern-scanner': 'Scan documents for keywords, phrases, and patterns',
  'entity-enrichment': 'Enhance entity data with aliases and variants',
  'timeline-builder': 'Extract and normalize dates into timelines',
  'similarity-linker': 'Find similar documents using embeddings',
  'relationship-engine': 'Generate evidence-backed relationships',
  'summarization': 'Create objective document summaries',
  'export-generator': 'Generate reports with citations and redaction'
}

export function AnalysisScriptsView() {
  const [scripts, setScripts] = useState<AnalysisScript[]>(getAllScripts())
  const [selectedScript, setSelectedScript] = useState<AnalysisScript | null>(null)
  const [activeCategory, setActiveCategory] = useState<ScriptCategory | 'all'>('all')

  const handleToggleScript = (scriptId: string) => {
    setScripts(current =>
      current.map(s => s.id === scriptId ? { ...s, enabled: !s.enabled } : s)
    )
  }

  const filteredScripts = activeCategory === 'all' 
    ? scripts 
    : scripts.filter(s => s.category === activeCategory)

  const categories: Array<ScriptCategory | 'all'> = [
    'all',
    'pattern-scanner',
    'entity-enrichment',
    'timeline-builder',
    'similarity-linker',
    'relationship-engine',
    'summarization',
    'export-generator'
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis Scripts</h1>
        <p className="text-muted-foreground mt-2">
          Manage modular analysis scripts that process documents and generate findings, timelines, and relationships.
        </p>
      </div>

      <Alert className="border-accent/30 bg-accent/10">
        <Flask className="text-accent" size={20} weight="duotone" />
        <AlertDescription className="text-sm">
          <strong className="font-semibold">Script Governance:</strong> All scripts are sandboxed, rate-limited, and audited. 
          Every run writes an immutable log with script version, config hash, and input/output hashes for reproducibility.
        </AlertDescription>
      </Alert>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Scripts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{scripts.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Available analysis scripts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Enabled</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[oklch(0.60_0.18_145)]">
              {scripts.filter(s => s.enabled).length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Active scripts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Auto-Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[oklch(0.70_0.15_280)]">
              {scripts.filter(s => s.executionMode === 'automatic').length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Automatic execution</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeCategory} onValueChange={(v) => setActiveCategory(v as ScriptCategory | 'all')}>
        <ScrollArea className="w-full">
          <TabsList className="inline-flex w-max">
            {categories.map(cat => (
              <TabsTrigger key={cat} value={cat}>
                {cat === 'all' ? 'All Scripts' : categoryLabels[cat]}
              </TabsTrigger>
            ))}
          </TabsList>
        </ScrollArea>

        <TabsContent value={activeCategory} className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredScripts.map((script) => (
              <Card key={script.id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{script.name}</CardTitle>
                      <CardDescription className="text-xs mt-1">
                        v{script.version} • {categoryLabels[script.category]}
                      </CardDescription>
                    </div>
                    <Switch
                      checked={script.enabled}
                      onCheckedChange={() => handleToggleScript(script.id)}
                    />
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    {script.description}
                  </p>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <Badge variant={script.executionMode === 'automatic' ? 'default' : 'outline'}>
                        {script.executionMode === 'automatic' ? 'Auto-Run' : 'Manual Only'}
                      </Badge>
                      {script.enabled ? (
                        <Badge variant="default" className="gap-1">
                          <CheckCircle size={12} weight="fill" />
                          Enabled
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="gap-1">
                          <XCircle size={12} weight="fill" />
                          Disabled
                        </Badge>
                      )}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Lock size={12} />
                        <span>Roles: {script.allowedRoles.join(', ')}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <div className="font-medium text-foreground mb-1">Triggers</div>
                      <div className="flex flex-wrap gap-1">
                        {script.triggers.map(trigger => (
                          <Badge key={trigger} variant="outline" className="text-xs">
                            {trigger}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <div className="font-medium text-foreground mb-1">Outputs</div>
                      <div className="flex flex-wrap gap-1">
                        {script.outputs.map(output => (
                          <Badge key={output} variant="outline" className="text-xs">
                            {output}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Separator className="my-4" />

                  <div className="flex gap-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" className="flex-1" onClick={() => setSelectedScript(script)}>
                          <Gear size={16} />
                          Configure
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl max-h-[80vh]">
                        <DialogHeader>
                          <DialogTitle>{script.name}</DialogTitle>
                          <DialogDescription>
                            v{script.version} • {categoryLabels[script.category]}
                          </DialogDescription>
                        </DialogHeader>
                        <ScrollArea className="max-h-[60vh]">
                          <div className="space-y-4">
                            <div>
                              <div className="text-sm font-medium mb-2">Description</div>
                              <p className="text-sm text-muted-foreground">{script.description}</p>
                            </div>

                            <Separator />

                            <div>
                              <div className="text-sm font-medium mb-2">Execution Details</div>
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <div className="text-muted-foreground">Mode</div>
                                  <div className="font-medium">{script.executionMode}</div>
                                </div>
                                <div>
                                  <div className="text-muted-foreground">Status</div>
                                  <div className="font-medium">{script.enabled ? 'Enabled' : 'Disabled'}</div>
                                </div>
                                <div>
                                  <div className="text-muted-foreground">Version</div>
                                  <div className="font-medium">{script.version}</div>
                                </div>
                                <div>
                                  <div className="text-muted-foreground">Version Hash</div>
                                  <div className="font-mono text-xs">{script.versionHash}</div>
                                </div>
                              </div>
                            </div>

                            <Separator />

                            <div>
                              <div className="text-sm font-medium mb-2">Permissions</div>
                              <div className="space-y-2">
                                <div>
                                  <div className="text-xs text-muted-foreground mb-1">Allowed Roles</div>
                                  <div className="flex flex-wrap gap-1">
                                    {script.allowedRoles.map(role => (
                                      <Badge key={role} variant="secondary">{role}</Badge>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-xs text-muted-foreground mb-1">Required Permissions</div>
                                  <div className="flex flex-wrap gap-1">
                                    {script.requiredPermissions.map(perm => (
                                      <Badge key={perm} variant="outline" className="text-xs font-mono">{perm}</Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>

                            <Separator />

                            <div>
                              <div className="text-sm font-medium mb-2">Inputs/Outputs</div>
                              <div className="space-y-2">
                                <div>
                                  <div className="text-xs text-muted-foreground mb-1">Required Inputs</div>
                                  <div className="font-mono text-xs bg-muted p-2 rounded">
                                    {script.inputs.required.join(', ')}
                                  </div>
                                </div>
                                {script.inputs.optional.length > 0 && (
                                  <div>
                                    <div className="text-xs text-muted-foreground mb-1">Optional Inputs</div>
                                    <div className="font-mono text-xs bg-muted p-2 rounded">
                                      {script.inputs.optional.join(', ')}
                                    </div>
                                  </div>
                                )}
                                <div>
                                  <div className="text-xs text-muted-foreground mb-1">Outputs</div>
                                  <div className="font-mono text-xs bg-muted p-2 rounded">
                                    {script.outputs.join(', ')}
                                  </div>
                                </div>
                              </div>
                            </div>

                            <Separator />

                            <div>
                              <div className="text-sm font-medium mb-2">Configuration</div>
                              <div className="bg-muted p-3 rounded font-mono text-xs">
                                <pre className="whitespace-pre-wrap">
                                  {JSON.stringify(script.config, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </div>
                        </ScrollArea>
                      </DialogContent>
                    </Dialog>

                    <Button size="sm" disabled={!script.enabled}>
                      <Play size={16} weight="fill" />
                      Run Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
