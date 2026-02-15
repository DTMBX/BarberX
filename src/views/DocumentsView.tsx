import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { FileText, MagnifyingGlass, FunnelSimple, Eye } from '@phosphor-icons/react'
import { Document, Source } from '@/lib/types'
import { StatusBadge } from '@/components/StatusBadge'
import { ConfidenceBar } from '@/components/ConfidenceBar'

export function DocumentsView() {
  const [documents] = useKV<Document[]>('documents', [])
  const [sources] = useKV<Source[]>('sources', [])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterSource, setFilterSource] = useState<string>('all')
  
  const documentsList = documents || []
  const sourcesList = sources || []
  
  const filteredDocuments = documentsList.filter(doc => {
    if (filterStatus !== 'all' && doc.status !== filterStatus) return false
    if (filterSource !== 'all' && doc.sourceId !== filterSource) return false
    if (searchQuery && !doc.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })
  
  const getSourceName = (sourceId: string) => {
    return sourcesList.find(s => s.id === sourceId)?.name || 'Unknown'
  }
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground mt-1">
            Browse and manage ingested documents with provenance tracking
          </p>
        </div>
        <Badge variant="secondary" className="text-lg px-3 py-1">
          {filteredDocuments.length} documents
        </Badge>
      </div>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <MagnifyingGlass 
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
                size={18} 
              />
              <Input
                placeholder="Search documents by title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[180px]">
                <FunnelSimple size={16} className="mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="downloaded">Downloaded</SelectItem>
                <SelectItem value="extracted">Extracted</SelectItem>
                <SelectItem value="ocr">OCR</SelectItem>
                <SelectItem value="indexed">Indexed</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterSource} onValueChange={setFilterSource}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {sourcesList.map(source => (
                  <SelectItem key={source.id} value={source.id}>
                    {source.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid gap-3">
        {filteredDocuments.map((doc) => (
          <Card key={doc.id} className="hover:border-accent/50 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/20">
                  <FileText size={24} className="text-accent" weight="duotone" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <h3 className="font-semibold text-lg leading-tight">{doc.title}</h3>
                    <StatusBadge status={doc.status} />
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 text-sm mb-3">
                    <div>
                      <div className="text-muted-foreground">Source</div>
                      <div>{getSourceName(doc.sourceId)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Pages</div>
                      <div className="font-mono">{doc.pageCount}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Size</div>
                      <div className="font-mono">{formatFileSize(doc.fileSize)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Downloaded</div>
                      <div className="text-xs">
                        {new Date(doc.downloadedAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 mb-3">
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground mb-1">Confidence</div>
                      <ConfidenceBar confidence={doc.confidence} />
                    </div>
                    {doc.ocrUsed && (
                      <Badge variant="secondary" className="bg-[oklch(0.70_0.15_280)] text-white">
                        OCR Used
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="gap-2" disabled>
                      <Eye size={16} />
                      View Document
                    </Button>
                    <code className="text-xs font-mono text-muted-foreground truncate flex-1">
                      {doc.sha256.substring(0, 16)}...
                    </code>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {filteredDocuments.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <FileText size={48} className="text-muted-foreground mb-4" weight="duotone" />
              <h3 className="font-semibold mb-2">No Documents Found</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                {documentsList.length === 0 
                  ? 'No documents have been ingested yet. Start an ingestion run to download and process documents.'
                  : 'No documents match your current filters. Try adjusting your search criteria.'
                }
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
