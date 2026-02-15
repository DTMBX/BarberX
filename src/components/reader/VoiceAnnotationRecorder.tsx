import { useState, useRef, useEffect } from 'react'
import { Microphone, Stop, Play, Pause, Trash, Check, X } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { toast } from 'sonner'

interface VoiceAnnotationRecorderProps {
  onSave: (audioBlob: Blob, duration: number) => void
  onCancel: () => void
  maxDuration?: number
  existingAnnotationUrl?: string
}

export default function VoiceAnnotationRecorder({
  onSave,
  onCancel,
  maxDuration = 300,
  existingAnnotationUrl
}: VoiceAnnotationRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [playbackTime, setPlaybackTime] = useState(0)
  const [hasRecording, setHasRecording] = useState(!!existingAnnotationUrl)
  const [audioUrl, setAudioUrl] = useState<string | null>(existingAnnotationUrl || null)
  const [duration, setDuration] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null)
  const playbackTimerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current)
      }
      if (playbackTimerRef.current) {
        clearInterval(playbackTimerRef.current)
      }
      if (audioUrl && !existingAnnotationUrl) {
        URL.revokeObjectURL(audioUrl)
      }
      if (audioRef.current) {
        audioRef.current.pause()
      }
    }
  }, [audioUrl, existingAnnotationUrl])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' })
        const url = URL.createObjectURL(audioBlob)
        setAudioUrl(url)
        setHasRecording(true)
        setDuration(recordingTime)
        
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1
          if (newTime >= maxDuration) {
            stopRecording()
            return maxDuration
          }
          return newTime
        })
      }, 1000)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      toast.error('Could not access microphone. Please check permissions.')
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause()
      setIsPaused(true)
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current)
      }
    }
  }

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume()
      setIsPaused(false)

      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1
          if (newTime >= maxDuration) {
            stopRecording()
            return maxDuration
          }
          return newTime
        })
      }, 1000)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && (mediaRecorderRef.current.state === 'recording' || mediaRecorderRef.current.state === 'paused')) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current)
      }
    }
  }

  const deleteRecording = () => {
    if (audioUrl && !existingAnnotationUrl) {
      URL.revokeObjectURL(audioUrl)
    }
    setAudioUrl(null)
    setHasRecording(false)
    setRecordingTime(0)
    setPlaybackTime(0)
    setDuration(0)
    audioChunksRef.current = []
    
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
  }

  const playRecording = () => {
    if (!audioUrl) return

    if (audioRef.current) {
      audioRef.current.play()
      setIsPlaying(true)

      playbackTimerRef.current = setInterval(() => {
        if (audioRef.current) {
          setPlaybackTime(Math.floor(audioRef.current.currentTime))
        }
      }, 100)
    } else {
      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.onended = () => {
        setIsPlaying(false)
        setPlaybackTime(0)
        if (playbackTimerRef.current) {
          clearInterval(playbackTimerRef.current)
        }
      }

      audio.play()
      setIsPlaying(true)

      playbackTimerRef.current = setInterval(() => {
        setPlaybackTime(Math.floor(audio.currentTime))
      }, 100)
    }
  }

  const pausePlayback = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      setIsPlaying(false)
      if (playbackTimerRef.current) {
        clearInterval(playbackTimerRef.current)
      }
    }
  }

  const handleSave = async () => {
    if (!audioUrl || !hasRecording) return

    try {
      if (existingAnnotationUrl) {
        onSave(new Blob(), duration)
      } else {
        const response = await fetch(audioUrl)
        const blob = await response.blob()
        onSave(blob, duration)
      }
    } catch (error) {
      console.error('Error saving annotation:', error)
      toast.error('Failed to save voice annotation')
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <Card className="p-4">
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold">Voice Annotation</h4>
          <span className="text-xs text-muted-foreground">
            Max {Math.floor(maxDuration / 60)} minutes
          </span>
        </div>

        {isRecording ? (
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-center gap-3">
              <div className={`w-3 h-3 rounded-full ${isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse'}`} />
              <span className="text-2xl font-mono font-semibold">
                {formatTime(recordingTime)}
              </span>
            </div>
            
            <Progress value={(recordingTime / maxDuration) * 100} className="h-2" />

            <div className="flex items-center justify-center gap-2">
              {isPaused ? (
                <Button onClick={resumeRecording} size="sm">
                  <Microphone size={18} weight="fill" className="mr-2" />
                  Resume
                </Button>
              ) : (
                <Button onClick={pauseRecording} variant="outline" size="sm">
                  <Pause size={18} weight="fill" className="mr-2" />
                  Pause
                </Button>
              )}
              <Button onClick={stopRecording} variant="destructive" size="sm">
                <Stop size={18} weight="fill" className="mr-2" />
                Stop
              </Button>
            </div>
          </div>
        ) : hasRecording ? (
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-center gap-3">
              <span className="text-xl font-mono">
                {formatTime(isPlaying ? playbackTime : 0)} / {formatTime(duration)}
              </span>
            </div>

            {isPlaying && (
              <Progress value={(playbackTime / duration) * 100} className="h-2" />
            )}

            <div className="flex items-center justify-center gap-2">
              {isPlaying ? (
                <Button onClick={pausePlayback} variant="outline" size="sm">
                  <Pause size={18} weight="fill" className="mr-2" />
                  Pause
                </Button>
              ) : (
                <Button onClick={playRecording} size="sm">
                  <Play size={18} weight="fill" className="mr-2" />
                  Play
                </Button>
              )}
              <Button onClick={deleteRecording} variant="outline" size="sm">
                <Trash size={18} className="mr-2" />
                Delete
              </Button>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button onClick={onCancel} variant="ghost" size="sm">
                <X size={18} className="mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSave} size="sm">
                <Check size={18} weight="bold" className="mr-2" />
                Save Annotation
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground text-center">
              Record a personal reflection about this audio moment
            </p>
            <Button onClick={startRecording} className="w-full">
              <Microphone size={20} weight="fill" className="mr-2" />
              Start Recording
            </Button>
            <Button onClick={onCancel} variant="ghost" size="sm">
              Cancel
            </Button>
          </div>
        )}
      </div>
    </Card>
  )
}
