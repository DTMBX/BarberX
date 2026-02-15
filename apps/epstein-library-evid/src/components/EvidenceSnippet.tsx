import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText } from '@phosphor-icons/react'
import { cn } from '@/lib/utils'

interface EvidenceSnippetProps {
  snippet: string
  highlight: string
  confidence: number
  documentTitle: string
  pageNo: number
  onViewDocument: () => void
  className?: string
}

export function EvidenceSnippet({
  snippet,
  highlight,
  confidence,
  documentTitle,
  pageNo,
  onViewDocument,
  className
}: EvidenceSnippetProps) {
  const highlightText = (text: string, term: string) => {
    if (!term) return text
    
    const parts = text.split(new RegExp(`(${term})`, 'gi'))
    return parts.map((part, i) => 
      part.toLowerCase() === term.toLowerCase() 
        ? <mark key={i} className="bg-accent/30 text-accent-foreground font-medium">{part}</mark>
        : part
    )
  }
  
  return (
    <Card className={cn('border-l-4 border-l-accent/50', className)}>
      <CardContent className="p-4 space-y-3">
        <div className="text-sm leading-relaxed text-foreground">
          {highlightText(snippet, highlight)}
        </div>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <span className="font-mono">
              Confidence: {Math.round(confidence * 100)}%
            </span>
            <span>•</span>
            <span>Page {pageNo}</span>
          </div>
          
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onViewDocument}
            className="h-7 text-xs"
          >
            <FileText size={14} className="mr-1" />
            View Document
          </Button>
        </div>
        
        <div className="text-xs text-muted-foreground truncate">
          {documentTitle}
        </div>
      </CardContent>
    </Card>
  )
}
