import { useState } from 'react'
import { SavedCitation, Document, Section, Jurisdiction } from '@/lib/types'
import {
  CitationFormat,
  ExportFormat,
  ExportOptions,
  generateCourtDefensibleExport,
  getDefaultExportOptions,
} from '@/lib/citation-export'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Progress } from '@/components/ui/progress'
import { Download } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface BatchCitationExportDialogProps {
  open: boolean
  onClose: () => void
  citations: SavedCitation[]
  documents: Document[]
  sections: Section[]
  jurisdictions: Jurisdiction[]
  userId: string
}

export function BatchCitationExportDialog({
  open,
  onClose,
  citations,
  documents,
  sections,
  jurisdictions,
  userId,
}: BatchCitationExportDialogProps) {
  const [options, setOptions] = useState<ExportOptions>(getDefaultExportOptions())
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)

  const handleBatchExport = async () => {
    setIsExporting(true)
    setExportProgress(0)

    try {
      const exportData: any[] = []
      const total = citations.length

      for (let i = 0; i < citations.length; i++) {
        const citation = citations[i]
        const section = sections.find((s) => s.id === citation.sectionId)
        const document = documents.find((d) => d.id === citation.documentId)
        const jurisdiction = jurisdictions.find((j) => j.id === citation.jurisdictionId)

        if (section && document && jurisdiction) {
          const metadata = {
            section,
            document,
            jurisdiction,
            retrievalDate: new Date().toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            }),
            userId,
            exportDate: new Date().toISOString(),
            verificationStatus: document.verificationStatus,
            lastVerified: document.lastChecked,
            sourceUrl: document.sourceUrl,
          }

          const courtDefensibleExport = await generateCourtDefensibleExport(metadata, options)
          exportData.push({
            ...courtDefensibleExport,
            userNotes: citation.notes,
            tags: citation.tags,
            collections: citation.collections,
            accessCount: citation.accessCount,
          })
        }

        setExportProgress(((i + 1) / total) * 100)
      }

      const fullExport = {
        exportType: 'citation-library-batch',
        exportedAt: new Date().toISOString(),
        exportedBy: userId,
        totalCitations: exportData.length,
        citationStyle: options.citationStyle,
        citations: exportData,
      }

      let content: string
      let filename: string
      let mimeType: string

      if (options.format === 'json') {
        content = JSON.stringify(fullExport, null, 2)
        filename = `citation-library-batch-${new Date().toISOString().slice(0, 10)}.json`
        mimeType = 'application/json'
      } else if (options.format === 'csv') {
        const headers = [
          'Title',
          'Citation',
          'Document',
          'Jurisdiction',
          'Authority Level',
          'Verification Status',
          'Notes',
          'Tags',
          'Access Count',
        ]
        const rows = exportData.map((item) => [
          item.metadata.sectionReference,
          item.citation,
          item.metadata.documentTitle,
          item.metadata.jurisdiction,
          item.metadata.authorityLevel,
          item.metadata.verificationStatus,
          item.userNotes || '',
          item.tags.join('; '),
          item.accessCount.toString(),
        ])
        content = [headers, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n')
        filename = `citation-library-batch-${new Date().toISOString().slice(0, 10)}.csv`
        mimeType = 'text/csv'
      } else {
        let textContent = '='.repeat(80) + '\n'
        textContent += 'CIVICS STACK - BATCH CITATION EXPORT\n'
        textContent += '='.repeat(80) + '\n\n'
        textContent += `Exported: ${new Date().toLocaleString()}\n`
        textContent += `Total Citations: ${exportData.length}\n`
        textContent += `Citation Style: ${options.citationStyle}\n`
        textContent += `Exported By: ${userId}\n\n`
        textContent += '='.repeat(80) + '\n\n'

        exportData.forEach((item, index) => {
          textContent += `[${index + 1}] ${item.metadata.sectionReference}\n`
          textContent += '-'.repeat(80) + '\n'
          textContent += `Citation: ${item.citation}\n`
          textContent += `Document: ${item.metadata.documentTitle}\n`
          textContent += `Jurisdiction: ${item.metadata.jurisdiction}\n`
          textContent += `Authority Level: ${item.metadata.authorityLevel}\n`
          textContent += `Verification: ${item.metadata.verificationStatus}\n`
          if (item.userNotes) {
            textContent += `Notes: ${item.userNotes}\n`
          }
          if (item.tags.length > 0) {
            textContent += `Tags: ${item.tags.join(', ')}\n`
          }
          textContent += `Access Count: ${item.accessCount}\n`
          if (options.includeFullText && item.fullText) {
            textContent += '\nFull Text:\n'
            textContent += item.fullText + '\n'
          }
          textContent += '\n' + '='.repeat(80) + '\n\n'
        })

        content = textContent
        filename = `citation-library-batch-${new Date().toISOString().slice(0, 10)}.txt`
        mimeType = 'text/plain'
      }

      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      toast.success('Batch export completed', {
        description: `Exported ${exportData.length} citations`,
      })

      onClose()
    } catch (error) {
      console.error('Batch export error:', error)
      toast.error('Failed to export citations')
    } finally {
      setIsExporting(false)
      setExportProgress(0)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Batch Export Citations</DialogTitle>
          <DialogDescription>
            Export {citations.length} citation{citations.length !== 1 ? 's' : ''} in one file
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="batch-citation-style">Citation Style</Label>
            <Select
              value={options.citationStyle}
              onValueChange={(value) =>
                setOptions({ ...options, citationStyle: value as CitationFormat })
              }
            >
              <SelectTrigger id="batch-citation-style">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bluebook">Bluebook</SelectItem>
                <SelectItem value="alwd">ALWD</SelectItem>
                <SelectItem value="apa">APA</SelectItem>
                <SelectItem value="mla">MLA</SelectItem>
                <SelectItem value="chicago">Chicago</SelectItem>
                <SelectItem value="plain">Plain Text</SelectItem>
                <SelectItem value="court-filing">Court Filing</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="batch-export-format">Export Format</Label>
            <Select
              value={options.format}
              onValueChange={(value) => setOptions({ ...options, format: value as ExportFormat })}
            >
              <SelectTrigger id="batch-export-format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="txt">Plain Text (.txt)</SelectItem>
                <SelectItem value="json">JSON (.json)</SelectItem>
                <SelectItem value="csv">CSV (.csv)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="batch-include-full-text" className="text-sm">
                Include Full Text
              </Label>
              <Switch
                id="batch-include-full-text"
                checked={options.includeFullText}
                onCheckedChange={(checked) => setOptions({ ...options, includeFullText: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="batch-include-metadata" className="text-sm">
                Include Metadata
              </Label>
              <Switch
                id="batch-include-metadata"
                checked={options.includeMetadata}
                onCheckedChange={(checked) => setOptions({ ...options, includeMetadata: checked })}
              />
            </div>
          </div>

          {isExporting && (
            <div className="space-y-2">
              <Label className="text-sm">Export Progress</Label>
              <Progress value={exportProgress} />
              <p className="text-xs text-muted-foreground text-center">
                {Math.round(exportProgress)}% complete
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleBatchExport} disabled={isExporting}>
            <Download className="w-4 h-4 mr-2" />
            {isExporting ? 'Exporting...' : 'Export All'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
