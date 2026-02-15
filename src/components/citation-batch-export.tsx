import { useState } from 'react'
import { Section, Document, Jurisdiction } from '@/lib/types'
import {
  CitationFormat,
  ExportFormat,
  ExportOptions,
  CitationMetadata,
  generateCourtDefensibleExport,
  downloadExport,
  getDefaultExportOptions,
  formatExportAsText,
  formatExportAsMarkdown,
  formatExportAsHTML,
  formatExportAsJSON,
} from '@/lib/citation-export'
import { createAuditLog } from '@/lib/compliance'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from 'sonner'
import { FileText, Download, Package, Scales, Check } from '@phosphor-icons/react'

interface BatchExportItem {
  section: Section
  document: Document
  jurisdiction: Jurisdiction
  selected: boolean
}

interface CitationBatchExportProps {
  open: boolean
  onClose: () => void
  items: Array<{
    section: Section
    document: Document
    jurisdiction: Jurisdiction
  }>
  userId: string
}

export function CitationBatchExport({ open, onClose, items, userId }: CitationBatchExportProps) {
  const [batchItems, setBatchItems] = useState<BatchExportItem[]>(
    items.map(item => ({ ...item, selected: true }))
  )
  const [options, setOptions] = useState<ExportOptions>(getDefaultExportOptions())
  const [isExporting, setIsExporting] = useState(false)

  const selectedCount = batchItems.filter(item => item.selected).length

  const toggleItem = (index: number) => {
    setBatchItems(prev =>
      prev.map((item, i) => (i === index ? { ...item, selected: !item.selected } : item))
    )
  }

  const toggleAll = () => {
    const allSelected = batchItems.every(item => item.selected)
    setBatchItems(prev => prev.map(item => ({ ...item, selected: !allSelected })))
  }

  const handleBatchExport = async () => {
    setIsExporting(true)
    try {
      const selectedItems = batchItems.filter(item => item.selected)
      
      if (selectedItems.length === 0) {
        toast.error('No items selected for export')
        return
      }

      const exports = await Promise.all(
        selectedItems.map(async ({ section, document, jurisdiction }) => {
          const metadata: CitationMetadata = {
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
          return generateCourtDefensibleExport(metadata, options)
        })
      )

      let combinedContent = ''
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)

      switch (options.format) {
        case 'txt':
          combinedContent = exports
            .map((exp, idx) => {
              const content = formatExportAsText(exp, options)
              return `\n\n${'='.repeat(80)}\nCITATION ${idx + 1} OF ${exports.length}\n${'='.repeat(80)}\n\n${content}`
            })
            .join('\n\n')
          break
        case 'md':
          combinedContent = `# Batch Citation Export\n\n**Total Citations:** ${exports.length}\n**Exported:** ${new Date().toLocaleString()}\n\n---\n\n` +
            exports
              .map((exp, idx) => `## Citation ${idx + 1}\n\n${formatExportAsMarkdown(exp, options)}`)
              .join('\n\n---\n\n')
          break
        case 'html':
          const htmlParts = exports.map((exp, idx) => {
            const html = formatExportAsHTML(exp, options)
            const bodyContent = html.match(/<body>([\s\S]*)<\/body>/)?.[1] || ''
            return `<div class="citation-item" id="citation-${idx + 1}">
              <h2 class="citation-number">Citation ${idx + 1} of ${exports.length}</h2>
              ${bodyContent}
            </div>`
          })
          combinedContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Batch Citation Export - Civics Stack</title>
  <style>
    body { font-family: 'Georgia', serif; max-width: 900px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #333; }
    .batch-header { text-align: center; border-bottom: 3px solid #333; padding-bottom: 20px; margin-bottom: 40px; }
    .citation-item { margin: 60px 0; page-break-inside: avoid; border-top: 2px dashed #999; padding-top: 40px; }
    .citation-item:first-child { border-top: none; }
    .citation-number { color: #666; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    @media print { body { margin: 0; padding: 20px; } .citation-item { page-break-after: always; } }
  </style>
</head>
<body>
  <div class="batch-header">
    <h1>Batch Citation Export</h1>
    <p><strong>Total Citations:</strong> ${exports.length}</p>
    <p><strong>Exported:</strong> ${new Date().toLocaleString()}</p>
  </div>
  ${htmlParts.join('\n')}
</body>
</html>`
          break
        case 'json':
          combinedContent = JSON.stringify(
            {
              batchExport: true,
              totalCitations: exports.length,
              exportedDate: new Date().toISOString(),
              exportedBy: userId,
              citations: exports,
            },
            null,
            2
          )
          break
        default:
          combinedContent = exports
            .map((exp, idx) => `CITATION ${idx + 1}:\n\n${formatExportAsText(exp, options)}`)
            .join('\n\n' + '='.repeat(80) + '\n\n')
      }

      const blob = new Blob([combinedContent], {
        type: options.format === 'html' ? 'text/html' : options.format === 'json' ? 'application/json' : 'text/plain',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `batch_citations_${timestamp}.${options.format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      await createAuditLog({
        userId,
        userRole: 'reader',
        action: 'export',
        entityType: 'batch-citation',
        entityId: `batch-${timestamp}`,
        metadata: {
          format: options.format,
          citationStyle: options.citationStyle,
          itemCount: selectedItems.length,
        },
      })

      toast.success('Batch export completed', {
        description: `${selectedCount} citations exported successfully`,
      })

      onClose()
    } catch (error) {
      console.error('Batch export error:', error)
      toast.error('Failed to export citations')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            Batch Citation Export
          </DialogTitle>
          <DialogDescription>
            Export multiple citations in a single file with full verification metadata
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-6 py-4">
              <Card className="p-4 bg-accent/10 border-accent/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Scales className="w-5 h-5 text-accent" />
                    <div>
                      <p className="font-medium">Court-Defensible Standards</p>
                      <p className="text-sm text-muted-foreground">
                        {selectedCount} {selectedCount === 1 ? 'citation' : 'citations'} selected for export
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={toggleAll}>
                    {batchItems.every(item => item.selected) ? 'Deselect All' : 'Select All'}
                  </Button>
                </div>
              </Card>

              <div className="space-y-2">
                <Label className="text-base">Select Citations</Label>
                <div className="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3 bg-muted/30">
                  {batchItems.map((item, index) => (
                    <div key={index} className="flex items-start gap-3 p-2 hover:bg-accent/5 rounded">
                      <Checkbox
                        id={`item-${index}`}
                        checked={item.selected}
                        onCheckedChange={() => toggleItem(index)}
                        className="mt-1"
                      />
                      <label
                        htmlFor={`item-${index}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        <div className="font-medium">{item.section.title}</div>
                        <div className="text-muted-foreground">
                          {item.section.canonicalCitation} • {item.document.title}
                        </div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="batch-citation-style">Citation Style</Label>
                  <Select
                    value={options.citationStyle}
                    onValueChange={(value) =>
                      setOptions(prev => ({ ...prev, citationStyle: value as CitationFormat }))
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
                  <Label htmlFor="batch-format">Export Format</Label>
                  <Select
                    value={options.format}
                    onValueChange={(value) =>
                      setOptions(prev => ({ ...prev, format: value as ExportFormat }))
                    }
                  >
                    <SelectTrigger id="batch-format">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="txt">Plain Text (.txt)</SelectItem>
                      <SelectItem value="md">Markdown (.md)</SelectItem>
                      <SelectItem value="html">HTML (.html)</SelectItem>
                      <SelectItem value="json">JSON (.json)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-3">
                <Label className="text-base">Export Options</Label>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="batch-full-text" className="text-sm font-normal">
                      Include Full Text
                    </Label>
                    <Switch
                      id="batch-full-text"
                      checked={options.includeFullText}
                      onCheckedChange={(checked) =>
                        setOptions(prev => ({ ...prev, includeFullText: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="batch-metadata" className="text-sm font-normal">
                      Include Metadata
                    </Label>
                    <Switch
                      id="batch-metadata"
                      checked={options.includeMetadata}
                      onCheckedChange={(checked) =>
                        setOptions(prev => ({ ...prev, includeMetadata: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="batch-verification" className="text-sm font-normal">
                      Include Verification Chain
                    </Label>
                    <Switch
                      id="batch-verification"
                      checked={options.includeVerificationInfo}
                      onCheckedChange={(checked) =>
                        setOptions(prev => ({ ...prev, includeVerificationInfo: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="batch-disclaimers" className="text-sm font-normal">
                      Include Legal Disclaimers
                    </Label>
                    <Switch
                      id="batch-disclaimers"
                      checked={options.includeDisclaimers}
                      onCheckedChange={(checked) =>
                        setOptions(prev => ({ ...prev, includeDisclaimers: checked }))
                      }
                    />
                  </div>
                </div>
              </div>
            </div>
          </ScrollArea>
        </div>

        <Separator />

        <div className="flex items-center justify-between pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleBatchExport} disabled={isExporting || selectedCount === 0}>
            <Download className="w-4 h-4 mr-2" />
            {isExporting ? 'Exporting...' : `Export ${selectedCount} ${selectedCount === 1 ? 'Citation' : 'Citations'}`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
