import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { PencilSimple, ArrowCounterClockwise, Check, X, Waveform } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface TranscriptionEditorProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  originalText: string
  currentText: string
  onSave: (editedText: string) => void
  audioUrl?: string
  confidence?: number
  title?: string
  description?: string
}

export default function TranscriptionEditor({
  open,
  onOpenChange,
  originalText,
  currentText,
  onSave,
  audioUrl,
  confidence,
  title = "Edit Transcription",
  description = "Review and correct the AI-generated transcription to ensure accuracy."
}: TranscriptionEditorProps) {
  const [editedText, setEditedText] = useState(currentText)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

  const hasChanges = editedText !== currentText
  const isReverted = editedText === originalText

  const handleSave = () => {
    if (!editedText.trim()) {
      toast.error('Transcription cannot be empty')
      return
    }

    if (editedText === currentText) {
      toast.info('No changes to save')
      onOpenChange(false)
      return
    }

    onSave(editedText.trim())
    toast.success('Transcription updated successfully')
    onOpenChange(false)
  }

  const handleRevert = () => {
    setEditedText(originalText)
    toast.info('Reverted to original transcription')
  }

  const handleCancel = () => {
    setEditedText(currentText)
    onOpenChange(false)
  }

  const handlePlayPause = () => {
    if (!audioUrl) return

    if (!audioElement) {
      const audio = new Audio(audioUrl)
      audio.onended = () => setIsPlaying(false)
      setAudioElement(audio)
      audio.play()
      setIsPlaying(true)
    } else {
      if (isPlaying) {
        audioElement.pause()
        setIsPlaying(false)
      } else {
        audioElement.play()
        setIsPlaying(true)
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PencilSimple size={24} weight="duotone" className="text-primary" />
            {title}
          </DialogTitle>
          <DialogDescription>
            {description}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {audioUrl && (
            <div className="p-3 bg-muted rounded-md">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePlayPause}
                className="gap-2 w-full"
              >
                <Waveform size={18} weight="duotone" />
                {isPlaying ? 'Pause Audio' : 'Play Original Audio'}
              </Button>
            </div>
          )}

          {confidence !== undefined && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">AI Confidence:</span>
              <Badge variant={confidence > 0.8 ? 'default' : 'secondary'}>
                {Math.round(confidence * 100)}%
              </Badge>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Edit Transcription</label>
              {!isReverted && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRevert}
                  className="gap-1 text-xs"
                >
                  <ArrowCounterClockwise size={14} />
                  Revert to Original
                </Button>
              )}
            </div>
            
            <Textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="min-h-[200px] resize-none font-body"
              placeholder="Transcription text..."
              autoFocus
            />

            <div className="text-xs text-muted-foreground">
              {editedText.length} characters
            </div>
          </div>

          {originalText !== currentText && editedText === originalText && (
            <div className="p-3 bg-amber-50 dark:bg-amber-950/20 rounded-md border border-amber-200 dark:border-amber-800">
              <p className="text-xs text-amber-800 dark:text-amber-200">
                This will revert any previous edits back to the original AI-generated transcription.
              </p>
            </div>
          )}

          {hasChanges && editedText !== originalText && (
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-md border border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-800 dark:text-blue-200 flex items-center gap-1">
                <PencilSimple size={12} />
                You've made changes to the transcription
              </p>
            </div>
          )}

          {originalText !== currentText && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                Original AI Transcription (for reference)
              </label>
              <div className="p-3 bg-muted/50 rounded-md text-sm max-h-32 overflow-y-auto text-muted-foreground">
                {originalText}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={handleCancel}
          >
            <X size={16} className="mr-2" />
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <Check size={16} className="mr-2" />
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
