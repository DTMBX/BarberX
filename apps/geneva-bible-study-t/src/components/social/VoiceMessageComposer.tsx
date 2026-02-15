import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  Microphone, 
  Stop, 
  Play, 
  Pause, 
  X, 
  Check, 
  PencilSimple,
  ArrowCounterClockwise,
  Waveform,
  SpinnerGap
} from '@phosphor-icons/react'
import { useVoiceToText } from '@/hooks/use-voice-to-text'
import { toast } from 'sonner'

interface VoiceMessageComposerProps {
  onSend: (text: string) => void
  onCancel: () => void
  placeholder?: string
}

export default function VoiceMessageComposer({ 
  onSend, 
  onCancel,
  placeholder = "Your transcription will appear here..."
}: VoiceMessageComposerProps) {
  const {
    isRecording,
    isProcessing,
    audioUrl,
    startRecording,
    stopRecording,
    cancelRecording,
    convertToText,
    cleanup
  } = useVoiceToText()

  const [transcribedText, setTranscribedText] = useState('')
  const [editedText, setEditedText] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [confidence, setConfidence] = useState<number | null>(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingDuration(prev => prev + 1)
      }, 1000)
    } else {
      setRecordingDuration(0)
    }
    return () => clearInterval(interval)
  }, [isRecording])

  useEffect(() => {
    if (audioUrl) {
      const audio = new Audio(audioUrl)
      audio.onended = () => setIsPlaying(false)
      setAudioElement(audio)
    }
    return () => {
      if (audioElement) {
        audioElement.pause()
        audioElement.src = ''
      }
    }
  }, [audioUrl])

  useEffect(() => {
    return () => {
      cleanup()
    }
  }, [cleanup])

  const handleStartRecording = async () => {
    try {
      await startRecording()
      setTranscribedText('')
      setEditedText('')
      setConfidence(null)
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const handleStopRecording = async () => {
    try {
      const url = await stopRecording()
      toast.info('Processing audio...')
      
      const result = await convertToText(url)
      setTranscribedText(result.text)
      setEditedText(result.text)
      setConfidence(result.confidence)
      
      toast.success('Transcription complete! You can edit the text before sending.')
    } catch (error) {
      console.error('Failed to process recording:', error)
    }
  }

  const handleCancel = () => {
    cancelRecording()
    cleanup()
    onCancel()
  }

  const handleSend = () => {
    const textToSend = isEditing ? editedText : transcribedText
    if (textToSend.trim()) {
      onSend(textToSend.trim())
      cleanup()
    } else {
      toast.error('Cannot send empty message')
    }
  }

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleRevert = () => {
    setEditedText(transcribedText)
    setIsEditing(false)
  }

  const handlePlayPause = () => {
    if (!audioElement) return

    if (isPlaying) {
      audioElement.pause()
      setIsPlaying(false)
    } else {
      audioElement.play()
      setIsPlaying(true)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <Card className="p-4 space-y-4 bg-card">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Waveform size={24} weight="duotone" className="text-primary" />
          <h3 className="font-semibold">Voice Message</h3>
        </div>
        <Button variant="ghost" size="icon" onClick={handleCancel}>
          <X size={20} />
        </Button>
      </div>

      {!isRecording && !audioUrl && (
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <Button
            size="lg"
            onClick={handleStartRecording}
            className="h-16 w-16 rounded-full"
            disabled={isProcessing}
          >
            <Microphone size={28} weight="fill" />
          </Button>
          <p className="text-sm text-muted-foreground text-center">
            Tap to start recording your message
          </p>
        </div>
      )}

      {isRecording && (
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <div className="relative">
            <Button
              size="lg"
              onClick={handleStopRecording}
              className="h-16 w-16 rounded-full bg-destructive hover:bg-destructive/90"
            >
              <Stop size={28} weight="fill" />
            </Button>
            <div className="absolute -inset-2 rounded-full border-2 border-destructive animate-pulse" />
          </div>
          <Badge variant="secondary" className="text-base px-4 py-1">
            {formatDuration(recordingDuration)}
          </Badge>
          <p className="text-sm text-muted-foreground">Recording...</p>
        </div>
      )}

      {isProcessing && (
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <SpinnerGap size={48} className="text-primary animate-spin" />
          <p className="text-sm text-muted-foreground">Transcribing audio...</p>
          <p className="text-xs text-muted-foreground">This may take a few moments</p>
        </div>
      )}

      {audioUrl && transcribedText && !isProcessing && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
            <Button
              variant="ghost"
              size="icon"
              onClick={handlePlayPause}
              className="flex-shrink-0"
            >
              {isPlaying ? <Pause size={20} weight="fill" /> : <Play size={20} weight="fill" />}
            </Button>
            <div className="flex-1">
              <Progress value={50} className="h-1" />
            </div>
          </div>

          {confidence !== null && (
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Transcription confidence:</span>
              <Badge variant={confidence > 0.8 ? 'default' : 'secondary'}>
                {Math.round(confidence * 100)}%
              </Badge>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Transcription</label>
              <div className="flex items-center gap-2">
                {isEditing && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRevert}
                    className="gap-1 text-xs"
                  >
                    <ArrowCounterClockwise size={14} />
                    Revert
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleEdit}
                  className="gap-1 text-xs"
                >
                  <PencilSimple size={14} />
                  Edit
                </Button>
              </div>
            </div>
            
            {isEditing ? (
              <Textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                placeholder={placeholder}
                className="min-h-[120px] resize-none"
                autoFocus
              />
            ) : (
              <div className="p-3 bg-muted rounded-md min-h-[120px] text-sm whitespace-pre-wrap">
                {editedText || transcribedText}
              </div>
            )}
          </div>

          {isEditing && editedText !== transcribedText && (
            <div className="text-xs text-amber-600 dark:text-amber-500 flex items-center gap-1">
              <PencilSimple size={12} />
              <span>Edited from original transcription</span>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleCancel}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSend}
              className="flex-1 gap-2"
              disabled={!editedText.trim()}
            >
              <Check size={18} weight="bold" />
              Send Message
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}
