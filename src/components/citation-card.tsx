import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ShareNetwork, Check, Copy } from '@phosphor-icons/react'
import { AuthorityBadge } from './authority-badge'
import { AuthorityLevel } from '@/lib/types'
import { useState } from 'react'
import { toast } from 'sonner'

interface CitationCardProps {
  title: string
  citation: string
  snippet: string
  authorityLevel: AuthorityLevel
  sourceUrl?: string
  onNavigate?: () => void
}

export function CitationCard({
  title,
  citation,
  snippet,
  authorityLevel,
  sourceUrl,
  onNavigate
}: CitationCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    const text = `${title}\n${citation}\n\n"${snippet}"\n${sourceUrl || ''}`
    await navigator.clipboard.writeText(text)
    setCopied(true)
    toast.success('Citation copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text: `${citation}: ${snippet}`,
          url: sourceUrl
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
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg leading-tight">{title}</CardTitle>
          <AuthorityBadge level={authorityLevel} />
        </div>
        <p className="text-sm text-muted-foreground font-medium">{citation}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm font-serif leading-relaxed italic border-l-2 border-primary pl-4">
          {snippet}
        </p>
        <div className="flex gap-2">
          {onNavigate && (
            <Button variant="default" size="sm" onClick={onNavigate} className="flex-1">
              View in Context
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </Button>
          <Button variant="outline" size="sm" onClick={handleShare}>
            <ShareNetwork size={16} />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
