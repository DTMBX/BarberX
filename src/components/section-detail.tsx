import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Section, Document, Jurisdiction } from '@/lib/types'
import { AuthorityBadge, VerificationBadge } from './authority-badge'
import { SourceVerificationDisplay } from './source-verification-display'
import { DisclaimerBanner } from './disclaimer-banner'
import { CitationExportDialog } from './citation-export-dialog'
import { AddToCitationLibraryDialog } from './add-to-citation-library-dialog'
import { BookmarkSimple, Copy, ShareNetwork, Check, FileText, FolderOpen } from '@phosphor-icons/react'
import { useState } from 'react'
import { toast } from 'sonner'
import { generateCourtDefensibleCitation } from '@/lib/compliance'

interface SectionDetailProps {
  section: Section | null
  document?: Document
  jurisdiction?: Jurisdiction
  userId?: string
  open: boolean
  onClose: () => void
  onBookmark?: () => void
}

export function SectionDetail({ section, document, jurisdiction, userId, open, onClose, onBookmark }: SectionDetailProps) {
  const [copied, setCopied] = useState(false)
  const [showVerificationDetail, setShowVerificationDetail] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showAddToLibrary, setShowAddToLibrary] = useState(false)

  if (!section || !document) return null

  const handleCopy = async () => {
    const text = `${section.title}\n${section.canonicalCitation}\n\n${section.text}\n\nSource: ${document.title}`
    await navigator.clipboard.writeText(text)
    setCopied(true)
    toast.success('Text copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleGenerateCitation = async () => {
    const citation = generateCourtDefensibleCitation(
      document.title,
      section.number,
      section.canonicalCitation,
      document.sourceUrl || 'Source URL not available',
      document.lastChecked || new Date().toISOString()
    )
    await navigator.clipboard.writeText(citation)
    toast.success('Court-defensible citation copied to clipboard')
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: section.title,
          text: `${section.canonicalCitation}: ${section.text.slice(0, 200)}...`
        })
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          handleCopy()
        }
      }
    } else {
      handleCopy()
    }
  }

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-2xl">
        <SheetHeader className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-start justify-between gap-2">
              <SheetTitle className="text-xl leading-tight pr-8">
                {section.title}
              </SheetTitle>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <AuthorityBadge level={document.authorityLevel} />
              <VerificationBadge status={document.verificationStatus} />
            </div>
          </div>
          
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">
              {document.title}
            </p>
            <p className="text-sm font-bold">
              {section.canonicalCitation}
            </p>
          </div>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-280px)] mt-6 pr-4">
          <div className="space-y-6">
            <DisclaimerBanner variant="verify-sources" showIcon={true} />

            <div className="font-serif text-base leading-relaxed whitespace-pre-line">
              {section.text}
            </div>

            <SourceVerificationDisplay
              verificationStatus={document.verificationStatus}
              sourceUrl={document.sourceUrl}
              lastChecked={document.lastChecked}
              canonicalCitation={section.canonicalCitation}
              documentTitle={document.title}
              onGenerateCitation={handleGenerateCitation}
            />
          </div>
        </ScrollArea>

        <div className="absolute bottom-0 left-0 right-0 p-6 border-t bg-background">
          <div className="flex gap-2 mb-2">
            <Button 
              onClick={() => setShowExportDialog(true)} 
              variant="default" 
              className="flex-1"
            >
              <FileText size={18} className="mr-2" />
              Export Citation
            </Button>
            <Button 
              onClick={() => setShowAddToLibrary(true)} 
              variant="secondary" 
              className="flex-1"
            >
              <FolderOpen size={18} className="mr-2" />
              Save to Library
            </Button>
          </div>
          <div className="flex gap-2">
            {onBookmark && (
              <Button onClick={onBookmark} variant="outline" className="flex-1">
                <BookmarkSimple size={18} />
                Bookmark
              </Button>
            )}
            <Button onClick={handleCopy} variant="outline">
              {copied ? <Check size={18} /> : <Copy size={18} />}
            </Button>
            <Button onClick={handleShare} variant="outline">
              <ShareNetwork size={18} />
            </Button>
          </div>
        </div>
      </SheetContent>

      <CitationExportDialog
        open={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        section={section}
        document={document}
        jurisdiction={jurisdiction || null}
        userId={userId || 'anonymous'}
      />

      {section && document && (
        <AddToCitationLibraryDialog
          open={showAddToLibrary}
          onClose={() => setShowAddToLibrary(false)}
          section={section}
          document={document}
          jurisdiction={jurisdiction || { id: 'us-federal', name: 'United States (Federal)', type: 'federal' as const, abbreviation: 'US' }}
        />
      )}
    </Sheet>
  )
}
