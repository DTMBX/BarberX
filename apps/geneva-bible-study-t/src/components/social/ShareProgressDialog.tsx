import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Trophy, ShareNetwork, Copy, CheckCircle } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import type { SharedProgress } from '@/lib/types'

interface ShareProgressDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  type: 'milestone' | 'plan-complete' | 'streak'
  title: string
  description: string
  planName?: string
  planId?: string
  daysCompleted?: number
  totalDays?: number
  streakDays?: number
}

export default function ShareProgressDialog({
  open,
  onOpenChange,
  type,
  title,
  description,
  planName,
  planId,
  daysCompleted,
  totalDays,
  streakDays
}: ShareProgressDialogProps) {
  const [note, setNote] = useState('')
  const [copied, setCopied] = useState(false)
  const [sharedProgress, setSharedProgress] = useKV<SharedProgress[]>('shared-progress', [])

  const handleCopyText = () => {
    const text = `🎉 ${title}\n\n${description}\n\n— Geneva Bible Study`
    navigator.clipboard.writeText(text)
    setCopied(true)
    toast.success('Progress copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleShareProgress = async () => {
    const user = await window.spark.user()
    
    const newShare: SharedProgress = {
      id: Date.now().toString(),
      userId: user?.id?.toString() || 'anonymous',
      userName: user?.login || 'Reader',
      userAvatar: user?.avatarUrl,
      type,
      title,
      description: note.trim() || description,
      planName,
      planId,
      daysCompleted,
      totalDays,
      streakDays,
      createdAt: Date.now(),
      likes: [],
      comments: []
    }

    setSharedProgress((current = []) => [newShare, ...current])
    
    toast.success('Progress shared to your feed!')
    setNote('')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Trophy size={24} weight="duotone" className="text-accent" />
            Share Achievement
          </DialogTitle>
          <DialogDescription>
            Celebrate your progress with your community
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg border-l-4 border-l-accent">
            <div className="flex items-start gap-3">
              <Trophy size={32} weight="fill" className="text-accent flex-shrink-0" />
              <div>
                <h3 className="font-bold text-lg mb-1">{title}</h3>
                <p className="text-sm text-muted-foreground">{description}</p>
                {planName && (
                  <p className="text-sm font-medium mt-2 text-primary">
                    {planName}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="progress-note">Add a personal note (optional)</Label>
            <Textarea
              id="progress-note"
              placeholder="Share what this achievement means to you..."
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
                  Copy
                </>
              )}
            </Button>
            <Button
              onClick={handleShareProgress}
              className="flex-1"
            >
              <ShareNetwork size={20} weight="duotone" className="mr-2" />
              Share
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
