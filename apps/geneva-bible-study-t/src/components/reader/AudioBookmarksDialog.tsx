import { useState, useRef } from 'react'
import { useKV } from '@github/spark/hooks'
import { BookmarkSimple, Play, Trash, NotePencil, Tag, MagnifyingGlass, SortAscending, X, Microphone, SpeakerHigh, Stop as StopIcon, TextT, Copy, Sparkle, PencilSimple } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import VoiceAnnotationRecorder from '@/components/reader/VoiceAnnotationRecorder'
import TranscriptionEditor from '@/components/social/TranscriptionEditor'
import { useAudioTranscription } from '@/hooks/use-audio-transcription'
import type { AudioBookmark } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'

interface AudioBookmarksDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onPlayBookmark: (bookmark: AudioBookmark) => void
  currentUserId: string
}

export default function AudioBookmarksDialog({
  open,
  onOpenChange,
  onPlayBookmark,
  currentUserId
}: AudioBookmarksDialogProps) {
  const [bookmarks, setBookmarks] = useKV<AudioBookmark[]>('audio-bookmarks', [])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editNote, setEditNote] = useState('')
  const [editTags, setEditTags] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'recent' | 'oldest' | 'most-played' | 'book'>('recent')
  const [recordingVoiceFor, setRecordingVoiceFor] = useState<string | null>(null)
  const [playingVoiceFor, setPlayingVoiceFor] = useState<string | null>(null)
  const [transcribingFor, setTranscribingFor] = useState<string | null>(null)
  const [editingTranscriptionFor, setEditingTranscriptionFor] = useState<AudioBookmark | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const { transcribeAudio, isTranscribing, progress } = useAudioTranscription()

  const userBookmarks = (bookmarks || []).filter(b => b.userId === currentUserId)

  const filteredBookmarks = userBookmarks.filter(bookmark => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      bookmark.bookName.toLowerCase().includes(query) ||
      bookmark.verseText.toLowerCase().includes(query) ||
      bookmark.note?.toLowerCase().includes(query) ||
      bookmark.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  })

  const sortedBookmarks = [...filteredBookmarks].sort((a, b) => {
    switch (sortBy) {
      case 'recent':
        return b.createdAt - a.createdAt
      case 'oldest':
        return a.createdAt - b.createdAt
      case 'most-played':
        return b.playCount - a.playCount
      case 'book':
        return a.bookName.localeCompare(b.bookName) || a.chapterNumber - b.chapterNumber || a.verseNumber - b.verseNumber
      default:
        return 0
    }
  })

  const handleDeleteBookmark = (bookmarkId: string) => {
    setBookmarks(current => (current || []).filter(b => b.id !== bookmarkId))
  }

  const handleStartEdit = (bookmark: AudioBookmark) => {
    setEditingId(bookmark.id)
    setEditNote(bookmark.note || '')
    setEditTags(bookmark.tags?.join(', ') || '')
  }

  const handleSaveEdit = (bookmarkId: string) => {
    setBookmarks(current => 
      (current || []).map(b => 
        b.id === bookmarkId 
          ? {
              ...b,
              note: editNote || undefined,
              tags: editTags 
                ? editTags.split(',').map(t => t.trim()).filter(t => t.length > 0)
                : undefined
            }
          : b
      )
    )
    setEditingId(null)
    setEditNote('')
    setEditTags('')
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditNote('')
    setEditTags('')
  }

  const handlePlay = (bookmark: AudioBookmark) => {
    setBookmarks(current =>
      (current || []).map(b =>
        b.id === bookmark.id
          ? {
              ...b,
              lastPlayedAt: Date.now(),
              playCount: b.playCount + 1
            }
          : b
      )
    )
    onPlayBookmark(bookmark)
    onOpenChange(false)
  }

  const handleSaveVoiceAnnotation = async (bookmarkId: string, audioBlob: Blob, duration: number) => {
    try {
      const audioUrl = URL.createObjectURL(audioBlob)
      
      setBookmarks(current =>
        (current || []).map(b =>
          b.id === bookmarkId
            ? {
                ...b,
                voiceAnnotationUrl: audioUrl,
                voiceAnnotationDuration: duration,
                voiceAnnotationCreatedAt: Date.now()
              }
            : b
        )
      )
      
      setRecordingVoiceFor(null)
      toast.success('Voice annotation saved! Click transcribe to convert to text.')
    } catch (error) {
      console.error('Error saving voice annotation:', error)
      toast.error('Failed to save voice annotation')
    }
  }

  const handlePlayVoiceAnnotation = (bookmark: AudioBookmark) => {
    if (!bookmark.voiceAnnotationUrl) return

    if (playingVoiceFor === bookmark.id) {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      setPlayingVoiceFor(null)
      return
    }

    if (audioRef.current) {
      audioRef.current.pause()
    }

    const audio = new Audio(bookmark.voiceAnnotationUrl)
    audioRef.current = audio

    audio.onended = () => {
      setPlayingVoiceFor(null)
      audioRef.current = null
    }

    audio.play()
    setPlayingVoiceFor(bookmark.id)
  }

  const handleDeleteVoiceAnnotation = (bookmarkId: string) => {
    if (playingVoiceFor === bookmarkId && audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
      setPlayingVoiceFor(null)
    }

    setBookmarks(current =>
      (current || []).map(b =>
        b.id === bookmarkId
          ? {
              ...b,
              voiceAnnotationUrl: undefined,
              voiceAnnotationDuration: undefined,
              voiceAnnotationCreatedAt: undefined,
              voiceAnnotationTranscription: undefined,
              voiceAnnotationTranscribedAt: undefined,
              voiceAnnotationOriginalTranscription: undefined,
              voiceAnnotationEditedAt: undefined,
              voiceAnnotationConfidence: undefined
            }
          : b
      )
    )
    toast.success('Voice annotation deleted')
  }

  const handleTranscribeAnnotation = async (bookmark: AudioBookmark) => {
    if (!bookmark.voiceAnnotationUrl) return

    setTranscribingFor(bookmark.id)
    
    try {
      const transcription = await transcribeAudio(bookmark.voiceAnnotationUrl)
      
      setBookmarks(current =>
        (current || []).map(b =>
          b.id === bookmark.id
            ? {
                ...b,
                voiceAnnotationTranscription: transcription,
                voiceAnnotationOriginalTranscription: transcription,
                voiceAnnotationTranscribedAt: Date.now(),
                voiceAnnotationConfidence: 0.85
              }
            : b
        )
      )
      toast.success('Transcription complete! You can edit it for accuracy.')
    } catch (error) {
      console.error('Failed to transcribe:', error)
    } finally {
      setTranscribingFor(null)
    }
  }

  const handleSaveTranscriptionEdit = (editedText: string) => {
    if (!editingTranscriptionFor) return

    setBookmarks(current =>
      (current || []).map(b =>
        b.id === editingTranscriptionFor.id
          ? {
              ...b,
              voiceAnnotationTranscription: editedText,
              voiceAnnotationEditedAt: Date.now()
            }
          : b
      )
    )
    setEditingTranscriptionFor(null)
  }

  const handleCopyTranscription = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Transcription copied to clipboard')
  }

  const handleConvertToNote = (bookmark: AudioBookmark) => {
    if (!bookmark.voiceAnnotationTranscription) return
    
    setEditingId(bookmark.id)
    setEditNote(bookmark.voiceAnnotationTranscription)
    setEditTags(bookmark.tags?.join(', ') || '')
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookmarkSimple size={24} weight="duotone" className="text-primary" />
            Audio Bookmarks
          </DialogTitle>
          <DialogDescription>
            Your saved audio moments from Bible readings
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 flex-1 overflow-hidden">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <MagnifyingGlass 
                size={18} 
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
              />
              <Input
                placeholder="Search bookmarks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger className="w-[160px]">
                <SortAscending size={18} className="mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Most Recent</SelectItem>
                <SelectItem value="oldest">Oldest First</SelectItem>
                <SelectItem value="most-played">Most Played</SelectItem>
                <SelectItem value="book">By Book</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {sortedBookmarks.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <BookmarkSimple size={48} weight="duotone" className="mx-auto mb-2 opacity-50" />
                <p className="font-medium">No bookmarks yet</p>
                <p className="text-sm">Save favorite audio moments while listening</p>
              </div>
            </div>
          ) : (
            <ScrollArea className="flex-1 pr-4">
              <div className="flex flex-col gap-3">
                {sortedBookmarks.map((bookmark) => (
                  <Card key={bookmark.id} className="p-4">
                    <div className="flex gap-3">
                      <Button
                        size="icon"
                        onClick={() => handlePlay(bookmark)}
                        className="shrink-0"
                      >
                        <Play size={20} weight="fill" />
                      </Button>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div>
                            <h4 className="font-semibold text-sm">
                              {bookmark.bookName} {bookmark.chapterNumber}:{bookmark.verseNumber}
                            </h4>
                            <p className="text-xs text-muted-foreground">
                              {bookmark.narratorName} • {bookmark.playbackRate}x speed • {bookmark.translation}
                            </p>
                          </div>
                          <div className="flex gap-1">
                            {editingId !== bookmark.id && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8"
                                  onClick={() => handleStartEdit(bookmark)}
                                >
                                  <NotePencil size={16} />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-destructive hover:text-destructive"
                                  onClick={() => handleDeleteBookmark(bookmark.id)}
                                >
                                  <Trash size={16} />
                                </Button>
                              </>
                            )}
                          </div>
                        </div>

                        <p className="text-sm text-foreground/90 mb-2 line-clamp-2">
                          "{bookmark.verseText}"
                        </p>

                        {recordingVoiceFor === bookmark.id ? (
                          <div className="mt-3">
                            <VoiceAnnotationRecorder
                              onSave={(blob, duration) => handleSaveVoiceAnnotation(bookmark.id, blob, duration)}
                              onCancel={() => setRecordingVoiceFor(null)}
                              existingAnnotationUrl={bookmark.voiceAnnotationUrl}
                            />
                          </div>
                        ) : editingId === bookmark.id ? (
                          <div className="flex flex-col gap-2 mt-3">
                            <Textarea
                              placeholder="Add a note..."
                              value={editNote}
                              onChange={(e) => setEditNote(e.target.value)}
                              className="min-h-[60px]"
                            />
                            <Input
                              placeholder="Tags (comma-separated)"
                              value={editTags}
                              onChange={(e) => setEditTags(e.target.value)}
                            />
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => handleSaveEdit(bookmark.id)}
                              >
                                Save
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={handleCancelEdit}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            {bookmark.note && (
                              <p className="text-sm text-muted-foreground italic mb-2">
                                {bookmark.note}
                              </p>
                            )}
                            {bookmark.tags && bookmark.tags.length > 0 && (
                              <div className="flex gap-1 flex-wrap mb-2">
                                {bookmark.tags.map((tag, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    <Tag size={12} className="mr-1" weight="fill" />
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                            
                            {bookmark.voiceAnnotationUrl && (
                              <Card className="p-3 mb-2 bg-accent/10 border-accent/20">
                                <div className="flex items-center justify-between gap-3 mb-2">
                                  <div className="flex items-center gap-2">
                                    <Microphone size={18} weight="fill" className="text-accent" />
                                    <div className="text-sm">
                                      <p className="font-medium">Voice Annotation</p>
                                      <p className="text-xs text-muted-foreground">
                                        {bookmark.voiceAnnotationDuration ? formatTime(bookmark.voiceAnnotationDuration) : '0:00'}
                                        {bookmark.voiceAnnotationCreatedAt && (
                                          <> • Recorded {formatDistanceToNow(bookmark.voiceAnnotationCreatedAt, { addSuffix: true })}</>
                                        )}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Button
                                      size="sm"
                                      variant={playingVoiceFor === bookmark.id ? "default" : "outline"}
                                      onClick={() => handlePlayVoiceAnnotation(bookmark)}
                                    >
                                      {playingVoiceFor === bookmark.id ? (
                                        <>
                                          <StopIcon size={16} weight="fill" className="mr-1" />
                                          Stop
                                        </>
                                      ) : (
                                        <>
                                          <SpeakerHigh size={16} weight="fill" className="mr-1" />
                                          Listen
                                        </>
                                      )}
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => handleDeleteVoiceAnnotation(bookmark.id)}
                                    >
                                      <Trash size={16} />
                                    </Button>
                                  </div>
                                </div>

                                {transcribingFor === bookmark.id && (
                                  <div className="space-y-2 mt-2 pt-2 border-t border-accent/20">
                                    <div className="flex items-center gap-2 text-sm">
                                      <Sparkle size={16} weight="fill" className="text-accent animate-pulse" />
                                      <span className="text-muted-foreground">Transcribing audio...</span>
                                    </div>
                                    <Progress value={progress} className="h-1.5" />
                                  </div>
                                )}

                                {!transcribingFor && bookmark.voiceAnnotationTranscription && (
                                  <div className="mt-2 pt-2 border-t border-accent/20">
                                    <div className="flex items-center justify-between mb-1">
                                      <div className="flex items-center gap-2">
                                        <TextT size={14} weight="bold" className="text-accent" />
                                        <span className="text-xs font-medium">Transcription</span>
                                        {bookmark.voiceAnnotationEditedAt && (
                                          <Badge variant="secondary" className="text-xs">Edited</Badge>
                                        )}
                                        {bookmark.voiceAnnotationTranscribedAt && (
                                          <span className="text-xs text-muted-foreground">
                                            • {formatDistanceToNow(bookmark.voiceAnnotationTranscribedAt, { addSuffix: true })}
                                          </span>
                                        )}
                                      </div>
                                      <div className="flex gap-1">
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          className="h-7 px-2"
                                          onClick={() => setEditingTranscriptionFor(bookmark)}
                                          title="Edit transcription"
                                        >
                                          <PencilSimple size={14} />
                                        </Button>
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          className="h-7 px-2"
                                          onClick={() => handleCopyTranscription(bookmark.voiceAnnotationTranscription!)}
                                          title="Copy to clipboard"
                                        >
                                          <Copy size={14} />
                                        </Button>
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          className="h-7 px-2"
                                          onClick={() => handleConvertToNote(bookmark)}
                                          title="Convert to text note"
                                        >
                                          <NotePencil size={14} />
                                        </Button>
                                      </div>
                                    </div>
                                    <p className="text-sm text-foreground/80 bg-background/50 rounded p-2">
                                      {bookmark.voiceAnnotationTranscription}
                                    </p>
                                  </div>
                                )}

                                {!transcribingFor && !bookmark.voiceAnnotationTranscription && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="w-full mt-2"
                                    onClick={() => handleTranscribeAnnotation(bookmark)}
                                  >
                                    <Sparkle size={16} weight="fill" className="mr-2" />
                                    Transcribe to Text
                                  </Button>
                                )}
                              </Card>
                            )}
                            
                            {!bookmark.voiceAnnotationUrl && !recordingVoiceFor && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="w-full mb-2"
                                onClick={() => setRecordingVoiceFor(bookmark.id)}
                              >
                                <Microphone size={16} weight="fill" className="mr-2" />
                                Add Voice Annotation
                              </Button>
                            )}
                          </>
                        )}

                        <Separator className="my-2" />

                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>
                            Saved {formatDistanceToNow(bookmark.createdAt, { addSuffix: true })}
                          </span>
                          <div className="flex items-center gap-3">
                            {bookmark.lastPlayedAt && (
                              <span>
                                Last played {formatDistanceToNow(bookmark.lastPlayedAt, { addSuffix: true })}
                              </span>
                            )}
                            <span>
                              Played {bookmark.playCount} {bookmark.playCount === 1 ? 'time' : 'times'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      </DialogContent>

      {editingTranscriptionFor && (
        <TranscriptionEditor
          open={!!editingTranscriptionFor}
          onOpenChange={(open) => !open && setEditingTranscriptionFor(null)}
          originalText={editingTranscriptionFor.voiceAnnotationOriginalTranscription || editingTranscriptionFor.voiceAnnotationTranscription || ''}
          currentText={editingTranscriptionFor.voiceAnnotationTranscription || ''}
          onSave={handleSaveTranscriptionEdit}
          audioUrl={editingTranscriptionFor.voiceAnnotationUrl}
          confidence={editingTranscriptionFor.voiceAnnotationConfidence}
          title="Edit Voice Annotation Transcription"
          description="Review and correct the AI-generated transcription of your voice annotation to ensure accuracy."
        />
      )}
    </Dialog>
  )
}
