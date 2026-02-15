import { Button } from '@/components/ui/button'
import { FileArrowDown } from '@phosphor-icons/react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Section, Document, Jurisdiction } from '@/lib/types'
import {
  CitationFormat,
  CitationMetadata,
  generateCitation,
  generateCourtDefensibleExport,
  downloadExport,
  getDefaultExportOptions,
} from '@/lib/citation-export'
import { toast } from 'sonner'

interface QuickExportButtonProps {
  section: Section
  document: Document
  jurisdiction: Jurisdiction
  userId: string
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

export function QuickExportButton({
  section,
  document,
  jurisdiction,
  userId,
  variant = 'outline',
  size = 'sm',
}: QuickExportButtonProps) {
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

  const handleQuickExport = async (format: CitationFormat) => {
    try {
      const options = getDefaultExportOptions()
      options.citationStyle = format
      
      const exportData = await generateCourtDefensibleExport(metadata, options)
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
      const filename = `citation_${section.id}_${format}_${timestamp}.${options.format}`
      
      await downloadExport(exportData, options, filename)
      
      toast.success(`Citation exported as ${format.toUpperCase()}`)
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export citation')
    }
  }

  const handleCopyCitation = async (format: CitationFormat) => {
    try {
      const citation = generateCitation(metadata, format)
      await navigator.clipboard.writeText(citation)
      toast.success(`${format.toUpperCase()} citation copied to clipboard`)
    } catch (error) {
      toast.error('Failed to copy citation')
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size}>
          <FileArrowDown className="w-4 h-4 mr-2" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Quick Export</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Copy to Clipboard
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => handleCopyCitation('bluebook')}>
          Copy as Bluebook
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleCopyCitation('alwd')}>
          Copy as ALWD
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleCopyCitation('apa')}>
          Copy as APA
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleCopyCitation('plain')}>
          Copy as Plain Text
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Download File
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => handleQuickExport('bluebook')}>
          Download Bluebook Citation
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleQuickExport('court-filing')}>
          Download Court Filing Format
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
