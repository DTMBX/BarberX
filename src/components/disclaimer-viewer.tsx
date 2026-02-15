import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Warning, DownloadSimple, Printer, FileText, Info } from '@phosphor-icons/react'
import { LEGAL_DISCLAIMERS, DisclaimerType } from '@/lib/compliance'
import {
  generateDisclaimerDocument,
  downloadDisclaimer,
  printDisclaimer,
  copyToClipboard,
  getAllDisclaimerTypes,
} from '@/lib/disclaimer-export'
import { toast } from 'sonner'

interface DisclaimerViewerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  userId?: string
}

/** Safe wrapper — avoids crash when window.spark is missing */
async function safeGetUser() {
  try {
    return await window.spark?.user?.()
  } catch {
    return null
  }
}

export function DisclaimerViewer({ open, onOpenChange, userId }: DisclaimerViewerProps) {
  const allDisclaimerTypes = getAllDisclaimerTypes()

  const handleExport = async (format: 'html' | 'markdown' | 'text') => {
    try {
      const user = await safeGetUser()
      const content = generateDisclaimerDocument(allDisclaimerTypes, {
        format,
        includeMetadata: true,
        includeTimestamp: true,
        userId,
        userName: user?.login,
      })
      downloadDisclaimer(content, format)
      toast.success(`Disclaimers exported as ${format.toUpperCase()}`)
    } catch (error) {
      toast.error('Failed to export disclaimers')
      console.error('Export error:', error)
    }
  }

  const handlePrint = async () => {
    try {
      const user = await safeGetUser()
      const content = generateDisclaimerDocument(allDisclaimerTypes, {
        format: 'html',
        includeMetadata: true,
        includeTimestamp: true,
        userId,
        userName: user?.login,
      })
      printDisclaimer(content)
    } catch (error) {
      toast.error('Failed to print disclaimers')
      console.error('Print error:', error)
    }
  }

  const handleCopyText = async () => {
    try {
      const user = await safeGetUser()
      const content = generateDisclaimerDocument(allDisclaimerTypes, {
        format: 'text',
        includeMetadata: true,
        includeTimestamp: true,
        userId,
        userName: user?.login,
      })
      await copyToClipboard(content)
      toast.success('Disclaimers copied to clipboard')
    } catch (error) {
      toast.error('Failed to copy to clipboard')
      console.error('Copy error:', error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl w-[95vw] flex flex-col p-0" style={{ maxHeight: 'min(90vh, 800px)' }}>
        <DialogHeader className="px-5 pt-5 pb-4 border-b shrink-0">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-destructive/10 dark:bg-destructive/20 rounded-lg shrink-0">
                <Warning className="w-5 h-5 text-destructive dark:text-destructive" weight="fill" />
              </div>
              <div>
                <DialogTitle className="text-lg sm:text-xl font-serif">Legal Disclaimers</DialogTitle>
                <DialogDescription className="text-sm mt-0.5">
                  Review and export all legal disclaimers
                </DialogDescription>
              </div>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <Button variant="ghost" size="sm" onClick={() => handleExport('text')} title="Download as text" className="h-8 w-8 p-0">
                <DownloadSimple className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handlePrint} title="Print" className="h-8 w-8 p-0">
                <Printer className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handleCopyText} title="Copy to clipboard" className="h-8 w-8 p-0">
                <FileText className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-hidden px-5 py-4 min-h-0">
          <Tabs defaultValue="all" className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-3 mb-3 shrink-0">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="required">Required</TabsTrigger>
              <TabsTrigger value="info">About</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="flex-1 overflow-hidden mt-0 min-h-0">
              <ScrollArea className="h-full">
                <div className="space-y-3 pb-4 pr-3">
                  {allDisclaimerTypes.map(type => {
                    const d = LEGAL_DISCLAIMERS[type]
                    return (
                      <Card key={type} className="border">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base font-serif flex items-center gap-2 flex-wrap">
                            {d.title}
                            {d.required && (
                              <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                                Required
                              </Badge>
                            )}
                          </CardTitle>
                          <CardDescription className="flex flex-wrap gap-3 text-xs">
                            <span>ID: {d.id}</span>
                            <span>v{d.version}</span>
                            <span>Effective: {d.effectiveDate}</span>
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="bg-accent/5 dark:bg-accent/10 border border-accent/20 dark:border-accent/15 rounded-md p-3">
                            <p className="text-sm leading-relaxed whitespace-pre-line text-foreground/90 dark:text-foreground/80">
                              {d.content}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="required" className="flex-1 overflow-hidden mt-0 min-h-0">
              <ScrollArea className="h-full">
                <div className="space-y-3 pb-4 pr-3">
                  {allDisclaimerTypes
                    .filter(type => LEGAL_DISCLAIMERS[type].required)
                    .map(type => {
                      const d = LEGAL_DISCLAIMERS[type]
                      return (
                        <Card key={type} className="border border-destructive/20 dark:border-destructive/15">
                          <CardHeader className="pb-2">
                            <CardTitle className="text-base font-serif flex items-center gap-2 flex-wrap">
                              {d.title}
                              <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                                Required
                              </Badge>
                            </CardTitle>
                            <CardDescription className="flex flex-wrap gap-3 text-xs">
                              <span>ID: {d.id}</span>
                              <span>v{d.version}</span>
                              <span>Effective: {d.effectiveDate}</span>
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="bg-accent/5 dark:bg-accent/10 border border-accent/20 dark:border-accent/15 rounded-md p-3">
                              <p className="text-sm leading-relaxed whitespace-pre-line text-foreground/90 dark:text-foreground/80">
                                {d.content}
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      )
                    })}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="info" className="flex-1 overflow-hidden mt-0 min-h-0">
              <ScrollArea className="h-full">
                <div className="space-y-4 pb-4 pr-3">
                  <Card className="border-primary/20 bg-primary/5 dark:bg-primary/10">
                    <CardHeader className="pb-2">
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Info className="w-4 h-4 text-primary" />
                        About These Disclaimers
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm text-primary dark:text-foreground">
                      <p>
                        These legal disclaimers are designed to ensure court-defensible compliance and
                        transparency. They define the boundaries of how this educational platform should be
                        used and understood.
                      </p>
                      <p>
                        <strong>Court-Defensible Documentation:</strong> All disclaimers include version
                        numbers, effective dates, and unique identifiers for precise citation and audit trail
                        purposes.
                      </p>
                      <p>
                        <strong>Export Options:</strong> You can export disclaimers in multiple formats
                        (HTML, Markdown, Plain Text) using the toolbar icons above.
                      </p>
                      <p>
                        <strong>Required vs Optional:</strong> Disclaimers marked as "Required" must be
                        acknowledged before using the application.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </div>

        <div className="px-5 py-3 border-t shrink-0 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => handleExport('html')} className="gap-1.5 text-xs">
              <DownloadSimple className="w-3.5 h-3.5" />
              HTML
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport('markdown')} className="gap-1.5 text-xs">
              <DownloadSimple className="w-3.5 h-3.5" />
              Markdown
            </Button>
          </div>
          <Button onClick={() => onOpenChange(false)} size="sm">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
