import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { ShareNetwork, Copy, Image as ImageIcon, CheckCircle, X } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { toast } from 'sonner'
import type { SharedVerse, ImageCardTemplate } from '@/lib/types'
import { bibleBooks } from '@/lib/data'
import VerseImageCard from './VerseImageCard'

interface ShareDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  workId: string
  chapterNumber: number
  verseNumber: number
  verseEndNumber?: number
  verseText: string
  translation: string
}

export default function ShareDialog({
  open,
  onOpenChange,
  workId,
  chapterNumber,
  verseNumber,
  verseEndNumber,
  verseText,
  translation
}: ShareDialogProps) {
  const [note, setNote] = useState('')
  const [template, setTemplate] = useState<ImageCardTemplate>('classic')
  const [copied, setCopied] = useState(false)
  const [sharedVerses, setSharedVerses] = useKV<SharedVerse[]>('shared-verses', [])

  const book = bibleBooks.find(b => b.id === workId)
  const reference = verseEndNumber && verseEndNumber !== verseNumber
    ? `${book?.title} ${chapterNumber}:${verseNumber}-${verseEndNumber}`
    : `${book?.title} ${chapterNumber}:${verseNumber}`

  const handleCopyText = () => {
    const formattedText = `"${verseText}"\n\n— ${reference} (${translation.toUpperCase()})`
    navigator.clipboard.writeText(formattedText)
    setCopied(true)
    toast.success('Verse copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleShareVerse = async (withImage: boolean) => {
    const user = await window.spark.user()
    
    const newShare: SharedVerse = {
      id: Date.now().toString(),
      userId: user?.id?.toString() || 'anonymous',
      userName: user?.login || 'Reader',
      userAvatar: user?.avatarUrl,
      verseId: `${workId}-${chapterNumber}-${verseNumber}`,
      workId,
      bookName: book?.title || '',
      chapterNumber,
      verseNumber,
      verseEndNumber,
      verseText,
      translation,
      note: note.trim() || undefined,
      imageTemplate: withImage ? template : undefined,
      createdAt: Date.now(),
      likes: [],
      comments: []
    }

    setSharedVerses((current = []) => [newShare, ...current])
    
    toast.success('Verse shared to your feed!')
    setNote('')
    onOpenChange(false)
  }

  const handleDownloadImage = () => {
    const canvas = document.getElementById('verse-card-canvas') as HTMLCanvasElement
    if (canvas) {
      const link = document.createElement('a')
      link.download = `${reference.replace(/\s+/g, '_')}.png`
      link.href = canvas.toDataURL()
      link.click()
      toast.success('Image downloaded!')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShareNetwork size={24} weight="duotone" className="text-primary" />
            Share Verse
          </DialogTitle>
          <DialogDescription>
            Share this verse with your community or save as an image
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="text" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="text">Text Share</TabsTrigger>
            <TabsTrigger value="image">Image Card</TabsTrigger>
          </TabsList>

          <TabsContent value="text" className="space-y-4">
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm font-mono text-muted-foreground mb-2">{reference}</p>
              <p className="text-lg leading-relaxed" style={{ fontFamily: 'var(--font-body)' }}>
                "{verseText}"
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="note">Add a note (optional)</Label>
              <Textarea
                id="note"
                placeholder="Share your thoughts about this verse..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleCopyText}
                variant="secondary"
                className="flex-1"
              >
                {copied ? (
                  <>
                    <CheckCircle size={20} weight="duotone" className="mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={20} weight="duotone" className="mr-2" />
                    Copy Text
                  </>
                )}
              </Button>
              <Button
                onClick={() => handleShareVerse(false)}
                className="flex-1"
              >
                <ShareNetwork size={20} weight="duotone" className="mr-2" />
                Share to Feed
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="image" className="space-y-4">
            <div className="space-y-3">
              <Label>Choose Design Template</Label>
              <RadioGroup value={template} onValueChange={(value) => setTemplate(value as ImageCardTemplate)}>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:border-primary transition-colors">
                    <RadioGroupItem value="classic" id="classic" />
                    <Label htmlFor="classic" className="cursor-pointer flex-1">
                      <span className="font-semibold">Classic</span>
                      <p className="text-xs text-muted-foreground">Timeless & elegant</p>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:border-primary transition-colors">
                    <RadioGroupItem value="modern" id="modern" />
                    <Label htmlFor="modern" className="cursor-pointer flex-1">
                      <span className="font-semibold">Modern</span>
                      <p className="text-xs text-muted-foreground">Clean & bold</p>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:border-primary transition-colors">
                    <RadioGroupItem value="minimalist" id="minimalist" />
                    <Label htmlFor="minimalist" className="cursor-pointer flex-1">
                      <span className="font-semibold">Minimalist</span>
                      <p className="text-xs text-muted-foreground">Simple & focused</p>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:border-primary transition-colors">
                    <RadioGroupItem value="illuminated" id="illuminated" />
                    <Label htmlFor="illuminated" className="cursor-pointer flex-1">
                      <span className="font-semibold">Illuminated</span>
                      <p className="text-xs text-muted-foreground">Ornate & decorative</p>
                    </Label>
                  </div>
                </div>
              </RadioGroup>
            </div>

            <div className="border rounded-lg p-4 bg-muted/30">
              <VerseImageCard
                verseText={verseText}
                reference={reference}
                translation={translation}
                template={template}
              />
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleDownloadImage}
                variant="secondary"
                className="flex-1"
              >
                <ImageIcon size={20} weight="duotone" className="mr-2" />
                Download Image
              </Button>
              <Button
                onClick={() => handleShareVerse(true)}
                className="flex-1"
              >
                <ShareNetwork size={20} weight="duotone" className="mr-2" />
                Share with Image
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
