import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Info, 
  Quotes, 
  CheckCircle,
  FileText
} from '@phosphor-icons/react'
import { RelationshipExplainer as RelationshipExplainerType, Relationship } from '@/lib/types'
import { ConfidenceBar } from '@/components/ConfidenceBar'

interface RelationshipExplainerProps {
  relationship: Relationship
  explainer?: RelationshipExplainerType
}

export function RelationshipExplainer({ relationship, explainer }: RelationshipExplainerProps) {
  if (!explainer) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground">
          <Info size={48} className="mx-auto mb-4 opacity-50" weight="duotone" />
          <p>No explainer available for this relationship.</p>
          <p className="text-sm mt-1">Run relationship explainer scripts to generate explanations.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center gap-2">
              <Info size={20} weight="duotone" />
              Relationship Explanation
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {explainer.computationMethod}
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <ConfidenceBar confidence={explainer.confidence} />
            {explainer.neutralLanguageVerified && (
              <Badge variant="outline" className="bg-[oklch(0.60_0.18_145)]/10">
                <CheckCircle size={12} className="mr-1" />
                Neutral Language
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert className="border-accent/30 bg-accent/10">
          <Quotes className="text-accent" size={20} />
          <AlertDescription className="text-sm">
            {explainer.explanation}
          </AlertDescription>
        </Alert>

        {explainer.evidenceSnippets.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-3 flex items-center gap-2">
              <FileText size={16} />
              Evidence Snippets ({explainer.evidenceSnippets.length})
            </div>
            <ScrollArea className="max-h-[400px]">
              <div className="space-y-3">
                {explainer.evidenceSnippets.map((snippet, idx) => (
                  <Card key={idx} className="border">
                    <CardContent className="p-3">
                      <div className="text-xs text-muted-foreground mb-2 flex items-center justify-between">
                        <span className="font-mono">
                          Document: {snippet.documentId.slice(0, 8)}
                          {snippet.pageNo && ` • Page ${snippet.pageNo}`}
                        </span>
                        <span className="font-mono">
                          Chunk: {snippet.chunkId.slice(0, 8)}
                        </span>
                      </div>
                      
                      <div className="text-sm bg-muted/50 border rounded p-3 font-mono leading-relaxed">
                        {snippet.snippet.split(new RegExp(`(${snippet.highlightedTerms.join('|')})`, 'gi')).map((part, i) => {
                          const isHighlighted = snippet.highlightedTerms.some(
                            term => part.toLowerCase() === term.toLowerCase()
                          )
                          return isHighlighted ? (
                            <mark key={i} className="bg-accent/30 text-accent-foreground font-semibold">
                              {part}
                            </mark>
                          ) : (
                            <span key={i}>{part}</span>
                          )
                        })}
                      </div>

                      {snippet.highlightedTerms.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {snippet.highlightedTerms.map((term, termIdx) => (
                            <Badge key={termIdx} variant="secondary" className="text-xs">
                              {term}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        <div className="pt-3 border-t text-xs text-muted-foreground">
          <p>
            This explanation is generated automatically from document analysis. 
            All relationships are evidence-backed and use neutral, non-accusatory language only.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
