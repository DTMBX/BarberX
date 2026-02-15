import { useState } from 'react'
import { Play, Stop, User, UserCircle } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { AudioNarrator } from '@/lib/types'

interface NarratorSelectionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  narrators: AudioNarrator[]
  currentNarratorId: string
  onSelectNarrator: (narratorId: string) => void
}

export default function NarratorSelectionDialog({
  open,
  onOpenChange,
  narrators,
  currentNarratorId,
  onSelectNarrator
}: NarratorSelectionDialogProps) {
  const [previewingId, setPreviewingId] = useState<string | null>(null)

  const handlePreview = (narrator: AudioNarrator) => {
    if (previewingId === narrator.id) {
      window.speechSynthesis.cancel()
      setPreviewingId(null)
      return
    }

    window.speechSynthesis.cancel()
    
    if (narrator.voice) {
      const utterance = new SpeechSynthesisUtterance(narrator.previewText)
      utterance.voice = narrator.voice
      utterance.rate = 1.0
      utterance.volume = 0.8
      utterance.onend = () => setPreviewingId(null)
      utterance.onerror = () => setPreviewingId(null)
      
      setPreviewingId(narrator.id)
      window.speechSynthesis.speak(utterance)
    }
  }

  const handleSelect = (narratorId: string) => {
    window.speechSynthesis.cancel()
    setPreviewingId(null)
    onSelectNarrator(narratorId)
    onOpenChange(false)
  }

  const handleClose = () => {
    window.speechSynthesis.cancel()
    setPreviewingId(null)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User size={24} weight="duotone" className="text-primary" />
            Choose Your Narrator
          </DialogTitle>
          <DialogDescription>
            Select a narrator and preview their voice reading Scripture
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[500px] pr-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {narrators.map((narrator) => (
              <Card
                key={narrator.id}
                className={`p-4 cursor-pointer transition-all ${
                  narrator.id === currentNarratorId
                    ? 'border-primary bg-primary/5'
                    : 'hover:border-accent'
                }`}
                onClick={() => handleSelect(narrator.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <UserCircle
                      size={32}
                      weight="duotone"
                      className={narrator.gender === 'male' ? 'text-blue-500' : 'text-pink-500'}
                    />
                    <div>
                      <h4 className="font-semibold">{narrator.name}</h4>
                      <div className="flex gap-1 mt-1">
                        <Badge variant="outline" className="text-[10px] px-1 py-0">
                          {narrator.gender}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] px-1 py-0">
                          {narrator.accent}
                        </Badge>
                        {narrator.quality === 'premium' && (
                          <Badge variant="secondary" className="text-[10px] px-1 py-0">
                            Premium
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  {narrator.id === currentNarratorId && (
                    <Badge className="bg-primary">Active</Badge>
                  )}
                </div>

                <p className="text-sm text-muted-foreground mb-3">
                  {narrator.description}
                </p>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePreview(narrator)
                    }}
                  >
                    {previewingId === narrator.id ? (
                      <>
                        <Stop size={16} weight="fill" className="mr-2" />
                        Stop
                      </>
                    ) : (
                      <>
                        <Play size={16} weight="fill" className="mr-2" />
                        Preview
                      </>
                    )}
                  </Button>
                  <Button
                    variant={narrator.id === currentNarratorId ? "default" : "secondary"}
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSelect(narrator.id)
                    }}
                  >
                    {narrator.id === currentNarratorId ? 'Selected' : 'Select'}
                  </Button>
                </div>

                {previewingId === narrator.id && (
                  <div className="mt-3 p-2 bg-accent/10 rounded text-xs italic border border-accent/30">
                    "{narrator.previewText}"
                  </div>
                )}
              </Card>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
