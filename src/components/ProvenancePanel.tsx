import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Hash, Link, Calendar, Download, FileText } from '@phosphor-icons/react'

interface ProvenancePanelProps {
  document: {
    sha256: string
    url: string
    downloadedAt: string
    fileSize: number
    mimeType: string
    runId: string
  }
}

export function ProvenancePanel({ document }: ProvenancePanelProps) {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  
  return (
    <Card className="border-accent/20">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Hash className="text-accent" weight="bold" />
          Provenance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <Hash className="text-muted-foreground mt-0.5 flex-shrink-0" size={16} />
            <div className="flex-1 min-w-0">
              <div className="text-xs text-muted-foreground mb-1">SHA-256</div>
              <code className="text-xs font-mono break-all text-foreground">
                {document.sha256}
              </code>
            </div>
          </div>
        </div>
        
        <Separator />
        
        <div className="space-y-3">
          <div className="flex items-start gap-2">
            <Link className="text-muted-foreground mt-0.5 flex-shrink-0" size={16} />
            <div className="flex-1 min-w-0">
              <div className="text-xs text-muted-foreground mb-1">Source URL</div>
              <a 
                href={document.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-accent hover:underline break-all"
              >
                {document.url}
              </a>
            </div>
          </div>
          
          <div className="flex items-start gap-2">
            <Calendar className="text-muted-foreground mt-0.5 flex-shrink-0" size={16} />
            <div className="flex-1">
              <div className="text-xs text-muted-foreground mb-1">Downloaded</div>
              <div className="text-xs font-mono">
                {new Date(document.downloadedAt).toLocaleString()}
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-2">
            <Download className="text-muted-foreground mt-0.5 flex-shrink-0" size={16} />
            <div className="flex-1">
              <div className="text-xs text-muted-foreground mb-1">File Size</div>
              <div className="text-xs font-mono">{formatBytes(document.fileSize)}</div>
            </div>
          </div>
          
          <div className="flex items-start gap-2">
            <FileText className="text-muted-foreground mt-0.5 flex-shrink-0" size={16} />
            <div className="flex-1">
              <div className="text-xs text-muted-foreground mb-1">MIME Type</div>
              <div className="text-xs font-mono">{document.mimeType}</div>
            </div>
          </div>
        </div>
        
        <Separator />
        
        <div className="text-xs text-muted-foreground">
          Run ID: <code className="font-mono">{document.runId}</code>
        </div>
      </CardContent>
    </Card>
  )
}
