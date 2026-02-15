import { useState, useEffect } from 'react'
import { Section, Document, Jurisdiction } from '@/lib/types'
import {
  CitationFormat,
  ExportFormat,
  ExportOptions,
  CitationMetadata,
  generateCitation,
  generateCourtDefensibleExport,
  downloadExport,
  getDefaultExportOptions,
} from '@/lib/citation-export'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { toast } from 'sonner'
import {
  FileText,
  Download,
  Copy,
  ShareNetwork,
  Scales,
  ShieldCheck,
  Clock,
  Warning,
} from '@phosphor-icons/react'

interface CitationExportDialogProps {
  open: boolean
  onClose: () => void
  section: Section | null
  document: Document | null
  jurisdiction: Jurisdiction | null
  userId: string
}

export function CitationExportDialog({
  open,
  onClose,
  section,
  document,
  jurisdiction,
  userId,
}: CitationExportDialogProps) {
  const [options, setOptions] = useState<ExportOptions>(getDefaultExportOptions())
  const [previewCitation, setPreviewCitation] = useState<string>('')
  const [isExporting, setIsExporting] = useState(false)

  const metadata: CitationMetadata | null = section && document && jurisdiction ? {
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
  } : null

  const updatePreview = (newOptions: ExportOptions) => {
    if (!metadata) return
    const citation = generateCitation(metadata, newOptions.citationStyle)
    setPreviewCitation(citation)
    setOptions(newOptions)
  }

  const handleCitationStyleChange = (style: CitationFormat) => {
    updatePreview({ ...options, citationStyle: style })
  }

  const handleFormatChange = (format: ExportFormat) => {
    updatePreview({ ...options, format })
  }

  const handleCopyCitation = async () => {
    if (!metadata) return
    try {
      const citation = generateCitation(metadata, options.citationStyle)
      await navigator.clipboard.writeText(citation)
      toast.success('Citation copied to clipboard')
    } catch (error) {
      toast.error('Failed to copy citation')
    }
  }

  const handleExport = async () => {
    if (!metadata || !section) return
    setIsExporting(true)
    try {
      const exportData = await generateCourtDefensibleExport(metadata, options)
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
      const filename = `citation_${section.id}_${timestamp}.${options.format}`
      
      await downloadExport(exportData, options, filename)
      
      toast.success('Citation exported successfully', {
        description: `File: ${filename}`,
      })
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export citation')
    } finally {
      setIsExporting(false)
    }
  }

  const handleShare = async () => {
    if (!metadata || !section) return
    const citation = generateCitation(metadata, options.citationStyle)
    const shareData = {
      title: `Citation: ${section.title}`,
      text: citation,
    }

    if (navigator.share) {
      try {
        await navigator.share(shareData)
        toast.success('Citation shared')
      } catch (error) {
        if ((error as Error).name !== 'AbortError') {
          toast.error('Failed to share citation')
        }
      }
    } else {
      handleCopyCitation()
    }
  }

  useEffect(() => {
    if (metadata) {
      updatePreview(options)
    }
  }, [options.citationStyle, section, document, jurisdiction])

  if (!section || !document || !jurisdiction) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Scales className="w-5 h-5" />
            Export Court-Defensible Citation
          </DialogTitle>
          <DialogDescription>
            Generate properly formatted legal citations with verification metadata and audit trails
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-6 py-4">
              <div className="bg-muted/50 p-4 rounded-lg border border-border">
                <div className="flex items-start gap-3">
                  <Warning className="w-5 h-5 text-accent mt-0.5 flex-shrink-0" />
                  <div className="space-y-1 text-sm">
                    <p className="font-medium">Important: Court Filing Notice</p>
                    <p className="text-muted-foreground">
                      For court filings, cite directly to official government publications, not educational platforms.
                      Use this export as a research aid to locate official sources.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Verification Status:</span>
                  <Badge variant={document.verificationStatus === 'official' ? 'default' : 'secondary'}>
                    {document.verificationStatus}
                  </Badge>
                  {document.lastChecked && (
                    <>
                      <Clock className="w-4 h-4 ml-2" />
                      <span>Last verified: {new Date(document.lastChecked).toLocaleDateString()}</span>
                    </>
                  )}
                </div>

                <Separator />

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="citation-style">Citation Style</Label>
                    <Select
                      value={options.citationStyle}
                      onValueChange={(value) => handleCitationStyleChange(value as CitationFormat)}
                    >
                      <SelectTrigger id="citation-style">
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
                        <SelectItem value="bibtex">BibTeX</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="export-format">Export Format</Label>
                    <Select
                      value={options.format}
                      onValueChange={(value) => handleFormatChange(value as ExportFormat)}
                    >
                      <SelectTrigger id="export-format">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="txt">Plain Text (.txt)</SelectItem>
                        <SelectItem value="md">Markdown (.md)</SelectItem>
                        <SelectItem value="html">HTML (.html)</SelectItem>
                        <SelectItem value="json">JSON (.json)</SelectItem>
                        <SelectItem value="csv">CSV (.csv)</SelectItem>
                        <SelectItem value="bibtex">BibTeX (.bib)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Card className="p-4 bg-card">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-sm font-medium">Citation Preview</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCopyCitation}
                      className="h-8"
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Copy
                    </Button>
                  </div>
                  <div className="bg-muted/30 p-3 rounded border border-border font-mono text-sm whitespace-pre-wrap break-words">
                    {previewCitation || 'Generating preview...'}
                  </div>
                </Card>

                <Separator />

                <div className="space-y-3">
                  <Label className="text-base">Export Options</Label>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="include-full-text" className="text-sm font-normal">
                          Include Full Text
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Include the complete text of the section
                        </p>
                      </div>
                      <Switch
                        id="include-full-text"
                        checked={options.includeFullText}
                        onCheckedChange={(checked) =>
                          setOptions({ ...options, includeFullText: checked })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="include-metadata" className="text-sm font-normal">
                          Include Metadata
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Document details, jurisdiction, verification status
                        </p>
                      </div>
                      <Switch
                        id="include-metadata"
                        checked={options.includeMetadata}
                        onCheckedChange={(checked) =>
                          setOptions({ ...options, includeMetadata: checked })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="include-verification" className="text-sm font-normal">
                          Include Verification Chain
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Complete verification and audit trail information
                        </p>
                      </div>
                      <Switch
                        id="include-verification"
                        checked={options.includeVerificationInfo}
                        onCheckedChange={(checked) =>
                          setOptions({ ...options, includeVerificationInfo: checked })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="include-audit" className="text-sm font-normal">
                          Include Audit Trail ID
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Unique identifier for this export in audit logs
                        </p>
                      </div>
                      <Switch
                        id="include-audit"
                        checked={options.includeAuditTrail}
                        onCheckedChange={(checked) =>
                          setOptions({ ...options, includeAuditTrail: checked })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="include-disclaimers" className="text-sm font-normal">
                          Include Legal Disclaimers
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Required disclaimers and notices
                        </p>
                      </div>
                      <Switch
                        id="include-disclaimers"
                        checked={options.includeDisclaimers}
                        onCheckedChange={(checked) =>
                          setOptions({ ...options, includeDisclaimers: checked })
                        }
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-accent/10 p-4 rounded-lg border border-accent/20">
                  <div className="flex items-start gap-2">
                    <FileText className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                    <div className="space-y-1 text-sm">
                      <p className="font-medium">Court Defensibility Standards</p>
                      <ul className="text-muted-foreground space-y-1 list-disc list-inside">
                        <li>All citations traceable to primary sources</li>
                        <li>Verification status clearly indicated</li>
                        <li>Immutable audit trail generated for each export</li>
                        <li>Timestamps recorded for all access</li>
                        <li>Legal disclaimers included as required</li>
                      </ul>
                    </div>
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
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleShare}>
              <ShareNetwork className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button onClick={handleExport} disabled={isExporting}>
              <Download className="w-4 h-4 mr-2" />
              {isExporting ? 'Exporting...' : 'Export Citation'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
