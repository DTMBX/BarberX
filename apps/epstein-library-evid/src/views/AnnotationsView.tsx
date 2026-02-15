import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Notepad, 
  Plus, 
  Quotes,
  Lightbulb,
  Question,
  CheckSquare,
  MagnifyingGlass,
  Warning,
  Link as LinkIcon
} from '@phosphor-icons/react'
import { Annotation, AnnotationType, Document } from '@/lib/types'
import { format } from 'date-fns'

export function AnnotationsView() {
  const [annotations, setAnnotations] = useKV<Annotation[]>('annotations', [])
  const [documents] = useKV<Document[]>('documents', [])
  const [selectedType, setSelectedType] = useState<AnnotationType | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newAnnotation, setNewAnnotation] = useState<Partial<Annotation>>({
    type: 'evidence-quote',
    content: '',
    citations: [],
    tags: []
  })

  const items = annotations || []
  const docList = documents || []

  const annotationTypes: Array<{ type: AnnotationType; label: string; icon: any; color: string; description: string }> = [
    { 
      type: 'evidence-quote', 
      label: 'Evidence Quote', 
      icon: Quotes, 
      color: 'text-[oklch(0.60_0.18_145)]',
      description: 'Direct quotes from source documents with mandatory citations'
    },
    { 
      type: 'interpretation', 
      label: 'Interpretation', 
      icon: Lightbulb, 
      color: 'text-accent',
      description: 'Your analysis or reading of the evidence'
    },
    { 
      type: 'hypothesis', 
      label: 'Hypothesis', 
      icon: Question, 
      color: 'text-[oklch(0.70_0.15_280)]',
      description: 'Possible explanations requiring further investigation'
    },
    { 
      type: 'to-verify', 
      label: 'To Verify', 
      icon: CheckSquare, 
      color: 'text-[oklch(0.65_0.15_160)]',
      description: 'Claims that need verification against source documents'
    }
  ]

  const filteredAnnotations = items.filter(ann => {
    if (selectedType !== 'all' && ann.type !== selectedType) return false
    if (searchQuery && !ann.content.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const getTypeConfig = (type: AnnotationType) => {
    return annotationTypes.find(t => t.type === type)!
  }

  const validateAnnotation = (ann: Partial<Annotation>): string[] => {
    const errors: string[] = []
    if (!ann.content || ann.content.trim().length === 0) {
      errors.push('Content is required')
    }
    if (ann.type === 'evidence-quote' && (!ann.citations || ann.citations.length === 0)) {
      errors.push('Evidence quotes must have at least one citation')
    }
    if (ann.type === 'evidence-quote') {
      const hasRequiredCitation = ann.citations?.some(c => c.required)
      if (!hasRequiredCitation) {
        errors.push('At least one citation must be marked as required for evidence quotes')
      }
    }
    return errors
  }

  const handleCreate = () => {
    const errors = validateAnnotation(newAnnotation)
    if (errors.length > 0) {
      alert(errors.join('\n'))
      return
    }

    const annotation: Annotation = {
      id: `ann-${Date.now()}`,
      documentId: newAnnotation.documentId || '',
      chunkId: newAnnotation.chunkId || `chunk-${Date.now()}`,
      type: newAnnotation.type as AnnotationType,
      content: newAnnotation.content!,
      citations: newAnnotation.citations || [],
      createdBy: 'CurrentUser',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: newAnnotation.tags || [],
      linkedAnnotations: []
    }

    setAnnotations(current => [...(current || []), annotation])
    setIsCreateDialogOpen(false)
    setNewAnnotation({
      type: 'evidence-quote',
      content: '',
      citations: [],
      tags: []
    })
  }

  const getDocumentTitle = (docId: string) => {
    return docList.find(d => d.id === docId)?.title || 'Unknown Document'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Annotations</h1>
          <p className="text-muted-foreground mt-1">
            Claims vs Evidence guardrail - keep teams honest and prevent narrative drift
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus size={18} weight="bold" className="mr-2" />
              New Annotation
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Annotation</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <Alert className="border-accent/30 bg-accent/10">
                <Warning className="text-accent" size={20} />
                <AlertDescription className="text-sm">
                  <strong>Evidence Quotes</strong> require mandatory citations. 
                  Interpretations and Hypotheses should reference supporting evidence.
                  This keeps analysis traceable and prevents unsupported claims.
                </AlertDescription>
              </Alert>

              <div>
                <label className="text-sm font-medium mb-2 block">Annotation Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {annotationTypes.map(({ type, label, icon: Icon, color, description }) => (
                    <Card 
                      key={type}
                      className={`cursor-pointer transition-all ${
                        newAnnotation.type === type ? 'border-accent bg-accent/5' : 'hover:border-accent/50'
                      }`}
                      onClick={() => setNewAnnotation({ ...newAnnotation, type })}
                    >
                      <CardContent className="p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Icon className={color} size={18} weight="duotone" />
                          <span className="text-sm font-medium">{label}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">{description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Content</label>
                <Textarea
                  placeholder={
                    newAnnotation.type === 'evidence-quote' 
                      ? 'Enter the exact quote from the source document...'
                      : newAnnotation.type === 'interpretation'
                      ? 'Enter your interpretation or analysis...'
                      : newAnnotation.type === 'hypothesis'
                      ? 'Describe the hypothesis to investigate...'
                      : 'Enter what needs to be verified...'
                  }
                  value={newAnnotation.content}
                  onChange={(e) => setNewAnnotation({ ...newAnnotation, content: e.target.value })}
                  rows={4}
                  className="resize-none"
                />
              </div>

              {newAnnotation.type === 'evidence-quote' && (
                <Alert className="border-[oklch(0.60_0.18_145)]/30 bg-[oklch(0.60_0.18_145)]/10">
                  <Quotes size={20} className="text-[oklch(0.60_0.18_145)]" />
                  <AlertDescription className="text-sm">
                    Evidence quotes <strong>require at least one citation</strong> marked as required.
                    This ensures all factual claims are traceable to source documents.
                  </AlertDescription>
                </Alert>
              )}

              <div>
                <label className="text-sm font-medium mb-2 block">Tags (comma-separated)</label>
                <Input
                  placeholder="financial, communication, timeline..."
                  value={newAnnotation.tags?.join(', ')}
                  onChange={(e) => setNewAnnotation({ 
                    ...newAnnotation, 
                    tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                  })}
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate}>
                  Create Annotation
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {annotationTypes.map(({ type, label, icon: Icon, color }) => {
          const count = items.filter(a => a.type === type).length
          return (
            <Card 
              key={type} 
              className={`cursor-pointer hover:border-accent/50 transition-colors ${
                selectedType === type ? 'border-accent' : ''
              }`}
              onClick={() => setSelectedType(selectedType === type ? 'all' : type)}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Icon className={color} size={18} weight="duotone" />
                  {label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{count}</div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Annotations</CardTitle>
            <div className="flex-1 max-w-sm ml-4">
              <div className="relative">
                <MagnifyingGlass 
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
                  size={16} 
                />
                <Input
                  placeholder="Search annotations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredAnnotations.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Notepad size={48} className="mx-auto mb-4 opacity-50" />
              <p>No annotations yet. Create your first annotation to start tracking evidence.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredAnnotations.map(ann => {
                const typeConfig = getTypeConfig(ann.type)
                const Icon = typeConfig.icon
                return (
                  <Card key={ann.id} className="border-l-4" style={{
                    borderLeftColor: typeConfig.color.replace('text-', '')
                  }}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <Icon className={typeConfig.color} size={20} weight="duotone" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline">{typeConfig.label}</Badge>
                            {ann.tags.map(tag => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          
                          <p className="text-sm mb-3 leading-relaxed">{ann.content}</p>
                          
                          {ann.citations.length > 0 && (
                            <div className="bg-muted/50 p-3 rounded space-y-2 mb-3">
                              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <LinkIcon size={12} />
                                Citations ({ann.citations.length})
                              </div>
                              {ann.citations.map((citation, idx) => (
                                <div key={idx} className="text-xs bg-background p-2 rounded">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-mono text-muted-foreground">
                                      {citation.documentId.slice(0, 8)}
                                    </span>
                                    {citation.required && (
                                      <Badge className="text-[10px] h-4 px-1 bg-[oklch(0.60_0.18_145)]">
                                        Required
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-muted-foreground italic">"{citation.snippet}"</p>
                                  {citation.pageNo && (
                                    <span className="text-muted-foreground">Page {citation.pageNo}</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                          
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>{ann.createdBy}</span>
                            <span>{format(new Date(ann.createdAt), 'MMM d, yyyy h:mm a')}</span>
                            {ann.linkedAnnotations.length > 0 && (
                              <span className="flex items-center gap-1">
                                <LinkIcon size={12} />
                                {ann.linkedAnnotations.length} linked
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
