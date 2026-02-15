import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { CaretLeft, CaretRight, BookOpen, BookmarkSimple, NotePencil, Gear, ListNumbers, ShareNetwork, PaperPlaneTilt, SpeakerHigh, User, ListPlus } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { bibleBooks } from '@/lib/data'
import type { UserProfile, VerseUnit, PassageReference, AudioPlaylist, AudioBookmark } from '@/lib/types'
import { generateChapterVerses } from '@/lib/verse-generator'
import ShareDialog from '@/components/social/ShareDialog'
import ShareVerseWithFriendsDialog from '@/components/reader/ShareVerseWithFriendsDialog'
import AudioPlayerControls from '@/components/reader/AudioPlayerControls'
import NarratorSelectionDialog from '@/components/reader/NarratorSelectionDialog'
import PlaylistDialog from '@/components/reader/PlaylistDialog'
import AudioBookmarksDialog from '@/components/reader/AudioBookmarksDialog'
import { useAudioBible } from '@/hooks/use-audio-bible'
import { toast } from 'sonner'

interface ReaderViewProps {
  userProfile: UserProfile
}

export default function ReaderView({ userProfile }: ReaderViewProps) {
  const [currentBookId, setCurrentBookId] = useState('gen')
  const [currentChapter, setCurrentChapter] = useState(1)
  const [selectedVerses, setSelectedVerses] = useState<number[]>([])
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [shareFriendsDialogOpen, setShareFriendsDialogOpen] = useState(false)
  const [narratorDialogOpen, setNarratorDialogOpen] = useState(false)
  const [playlistDialogOpen, setPlaylistDialogOpen] = useState(false)
  const [bookmarksDialogOpen, setBookmarksDialogOpen] = useState(false)
  const [showAudioPlayer, setShowAudioPlayer] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [bookmarks, setBookmarks] = useKV<AudioBookmark[]>('audio-bookmarks', [])
  
  const [lastReadPosition, setLastReadPosition] = useKV<PassageReference>('last-read-position', {
    workId: 'gen',
    chapterNumber: 1,
    verseNumber: 1
  })

  useState(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  })

  const currentBook = bibleBooks.find(b => b.id === currentBookId)
  const translationId = userProfile.preferences.defaultTranslation

  const verses = generateChapterVerses(currentBookId, currentChapter, translationId)
  
  const {
    playbackState,
    currentNarrator,
    narrators,
    audioPreferences,
    currentPlaylist,
    play,
    pause,
    resume,
    stop,
    skipToVerse,
    setNarrator,
    setPlaybackRate,
    setVolume,
    setSleepTimer,
    loadPlaylist,
    advancePlaylist
  } = useAudioBible(verses, currentBookId, currentChapter)

  useEffect(() => {
    if (lastReadPosition) {
      setCurrentBookId(lastReadPosition.workId)
      setCurrentChapter(lastReadPosition.chapterNumber)
    }
  }, [])

  useEffect(() => {
    const handleNavigateToPassage = (event: Event) => {
      const customEvent = event as CustomEvent<{ bookId: string; chapter: number }>
      if (customEvent.detail) {
        setCurrentBookId(customEvent.detail.bookId)
        setCurrentChapter(customEvent.detail.chapter)
        setSelectedVerses([])
      }
    }

    const handlePlaylistAdvance = (event: Event) => {
      const customEvent = event as CustomEvent<{ bookId: string; chapter: number }>
      if (customEvent.detail) {
        setCurrentBookId(customEvent.detail.bookId)
        setCurrentChapter(customEvent.detail.chapter)
        setSelectedVerses([])
        setTimeout(() => play(), 500)
      }
    }

    window.addEventListener('navigate-to-passage', handleNavigateToPassage)
    window.addEventListener('playlist-advance', handlePlaylistAdvance)
    return () => {
      window.removeEventListener('navigate-to-passage', handleNavigateToPassage)
      window.removeEventListener('playlist-advance', handlePlaylistAdvance)
    }
  }, [play])

  useEffect(() => {
    setLastReadPosition((current) => ({
      workId: currentBookId,
      chapterNumber: currentChapter,
      verseNumber: 1
    }))
  }, [currentBookId, currentChapter, setLastReadPosition])

  const handlePrevChapter = () => {
    stop()
    if (currentChapter > 1) {
      setCurrentChapter(currentChapter - 1)
      setSelectedVerses([])
    } else {
      const currentBookIndex = bibleBooks.findIndex(b => b.id === currentBookId)
      if (currentBookIndex > 0) {
        const prevBook = bibleBooks[currentBookIndex - 1]
        setCurrentBookId(prevBook.id)
        setCurrentChapter(prevBook.chaptersCount)
        setSelectedVerses([])
      }
    }
  }

  const handleNextChapter = () => {
    stop()
    if (currentBook && currentChapter < currentBook.chaptersCount) {
      setCurrentChapter(currentChapter + 1)
      setSelectedVerses([])
      if (playbackState.currentPlaylistId) {
        advancePlaylist()
      }
    } else {
      const currentBookIndex = bibleBooks.findIndex(b => b.id === currentBookId)
      if (currentBookIndex < bibleBooks.length - 1) {
        const nextBook = bibleBooks[currentBookIndex + 1]
        setCurrentBookId(nextBook.id)
        setCurrentChapter(1)
        setSelectedVerses([])
        if (playbackState.currentPlaylistId) {
          advancePlaylist()
        }
      }
    }
  }

  const handlePlaylistSelect = (playlist: AudioPlaylist) => {
    if (playlist.items.length > 0) {
      loadPlaylist(playlist)
      const firstItem = playlist.items[0]
      setCurrentBookId(firstItem.bookId)
      setCurrentChapter(firstItem.chapter)
      setShowAudioPlayer(true)
      setTimeout(() => play(), 500)
    }
  }

  const handleVerseClick = (verseNumber: number) => {
    setSelectedVerses(prev => {
      if (prev.includes(verseNumber)) {
        return prev.filter(v => v !== verseNumber)
      }
      return [...prev, verseNumber]
    })
  }

  const handleAddBookmark = () => {
    if (!playbackState.isPlaying && !playbackState.isPaused) return
    
    const currentVerse = verses.find(v => v.verseNumber === playbackState.currentVerseNumber)
    if (!currentVerse) return

    const newBookmark: AudioBookmark = {
      id: `bookmark-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      userId: currentUserId,
      bookId: currentBookId,
      bookName: currentBook?.title || '',
      chapterNumber: currentChapter,
      verseNumber: playbackState.currentVerseNumber,
      verseText: currentVerse.text,
      translation: translationId,
      narratorId: playbackState.narratorId,
      narratorName: currentNarrator?.name || '',
      playbackRate: playbackState.playbackRate,
      createdAt: Date.now(),
      playCount: 0
    }

    setBookmarks(current => [...(current || []), newBookmark])
    toast.success('Audio moment bookmarked!', {
      description: `${currentBook?.title} ${currentChapter}:${playbackState.currentVerseNumber}`
    })
  }

  const handlePlayBookmark = (bookmark: AudioBookmark) => {
    stop()
    setCurrentBookId(bookmark.bookId)
    setCurrentChapter(bookmark.chapterNumber)
    setShowAudioPlayer(true)
    
    if (bookmark.narratorId !== playbackState.narratorId) {
      setNarrator(bookmark.narratorId)
    }
    if (bookmark.playbackRate !== playbackState.playbackRate) {
      setPlaybackRate(bookmark.playbackRate)
    }
    
    setTimeout(() => {
      play(bookmark.verseNumber)
    }, 500)
  }

  const handleBookChange = (bookId: string) => {
    stop()
    setCurrentBookId(bookId)
    setCurrentChapter(1)
    setSelectedVerses([])
  }

  const handleChapterChange = (chapter: string) => {
    stop()
    setCurrentChapter(parseInt(chapter))
    setSelectedVerses([])
  }

  const getSelectedVerseText = () => {
    if (selectedVerses.length === 0) return ''
    const sortedVerses = [...selectedVerses].sort((a, b) => a - b)
    return sortedVerses
      .map(vNum => verses.find(v => v.verseNumber === vNum)?.text || '')
      .join(' ')
  }

  return (
    <div className="h-full flex flex-col bg-background">
      <ShareDialog
        open={shareDialogOpen}
        onOpenChange={setShareDialogOpen}
        workId={currentBookId}
        chapterNumber={currentChapter}
        verseNumber={selectedVerses[0] || 1}
        verseEndNumber={selectedVerses.length > 1 ? Math.max(...selectedVerses) : undefined}
        verseText={getSelectedVerseText()}
        translation={translationId}
      />
      <ShareVerseWithFriendsDialog
        open={shareFriendsDialogOpen}
        onOpenChange={setShareFriendsDialogOpen}
        bookName={currentBook?.title || ''}
        chapterNumber={currentChapter}
        verseNumber={selectedVerses.length > 0 ? Math.min(...selectedVerses) : 1}
        verseEndNumber={selectedVerses.length > 1 ? Math.max(...selectedVerses) : undefined}
        verseText={getSelectedVerseText()}
        translation={translationId}
      />
      <NarratorSelectionDialog
        open={narratorDialogOpen}
        onOpenChange={setNarratorDialogOpen}
        narrators={narrators}
        currentNarratorId={playbackState.narratorId}
        onSelectNarrator={setNarrator}
      />
      <PlaylistDialog
        open={playlistDialogOpen}
        onOpenChange={setPlaylistDialogOpen}
        onPlaylistSelect={handlePlaylistSelect}
        currentBookId={currentBookId}
        currentChapter={currentChapter}
      />
      <AudioBookmarksDialog
        open={bookmarksDialogOpen}
        onOpenChange={setBookmarksDialogOpen}
        onPlayBookmark={handlePlayBookmark}
        currentUserId={currentUserId}
      />
      <div className="border-b border-border bg-card px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <Select value={currentBookId} onValueChange={handleBookChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {bibleBooks.map(book => (
                <SelectItem key={book.id} value={book.id}>
                  {book.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={currentChapter.toString()} onValueChange={handleChapterChange}>
            <SelectTrigger className="w-[100px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Array.from({ length: currentBook?.chaptersCount || 1 }, (_, i) => i + 1).map(ch => (
                <SelectItem key={ch} value={ch.toString()}>
                  Chapter {ch}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Badge variant="secondary" className="hidden sm:flex">
            {translationId.toUpperCase()}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button 
            variant={showAudioPlayer ? "default" : "outline"} 
            size="sm" 
            onClick={() => setShowAudioPlayer(!showAudioPlayer)}
            className="gap-2"
          >
            <SpeakerHigh size={18} weight="duotone" />
            <span className="hidden sm:inline">Audio</span>
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setNarratorDialogOpen(true)}
            className="gap-2 hidden sm:flex"
          >
            <User size={18} weight="duotone" />
            <span>Narrator</span>
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setPlaylistDialogOpen(true)}
            className="gap-2 hidden sm:flex"
          >
            <ListPlus size={18} weight="duotone" />
            <span>Playlists</span>
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setBookmarksDialogOpen(true)}
            className="gap-2 hidden sm:flex"
            title="Audio Bookmarks"
          >
            <BookmarkSimple size={18} weight="duotone" />
            <span>Bookmarks</span>
          </Button>
          {selectedVerses.length > 0 && (
            <>
              <Button 
                variant="default" 
                size="sm" 
                onClick={() => setShareFriendsDialogOpen(true)}
                className="gap-2"
              >
                <PaperPlaneTilt size={18} weight="duotone" />
                <span className="hidden sm:inline">Message Friend</span>
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShareDialogOpen(true)}>
                <ShareNetwork size={18} weight="duotone" />
              </Button>
              <Button variant="ghost" size="sm">
                <NotePencil size={18} weight="duotone" />
              </Button>
              <Button variant="ghost" size="sm">
                <BookmarkSimple size={18} weight="duotone" />
              </Button>
            </>
          )}
        </div>
      </div>

      {showAudioPlayer && (
        <div className="border-b border-border px-4 py-3 bg-background">
          <AudioPlayerControls
            playbackState={playbackState}
            currentNarrator={currentNarrator}
            narrators={narrators}
            currentPlaylist={currentPlaylist}
            onPlay={() => play()}
            onPause={pause}
            onResume={resume}
            onStop={stop}
            onNarratorChange={setNarrator}
            onPlaybackRateChange={setPlaybackRate}
            onVolumeChange={setVolume}
            onSleepTimerSet={setSleepTimer}
            onPlaylistOpen={() => setPlaylistDialogOpen(true)}
            onBookmarkOpen={() => setBookmarksDialogOpen(true)}
            onAddBookmark={handleAddBookmark}
            totalVerses={verses.length}
          />
        </div>
      )}

      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="max-w-3xl mx-auto px-6 py-8">
            <div className="mb-8">
              <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                {currentBook?.title}
              </h1>
              <div className="flex items-center gap-2">
                <Badge variant="outline">Chapter {currentChapter}</Badge>
                <Badge variant="secondary">{currentBook?.category}</Badge>
              </div>
            </div>

            <div className="space-y-4">
              {verses.map((verse) => (
                <div
                  key={verse.id}
                  className={`
                    group cursor-pointer rounded-md px-3 py-2 transition-colors relative
                    ${selectedVerses.includes(verse.verseNumber) 
                      ? 'bg-accent/20 border-l-4 border-l-accent' 
                      : playbackState.isPlaying && playbackState.currentVerseNumber === verse.verseNumber && audioPreferences?.highlightCurrentVerse
                      ? 'bg-primary/10 border-l-4 border-l-primary animate-pulse'
                      : 'hover:bg-muted/50'
                    }
                  `}
                >
                  <div className="flex gap-3">
                    <span 
                      onClick={() => handleVerseClick(verse.verseNumber)}
                      className="text-xs text-muted-foreground font-mono mt-1 select-none opacity-50 group-hover:opacity-100 transition-opacity"
                      style={{ fontFamily: 'var(--font-mono)' }}
                    >
                      {verse.verseNumber}
                    </span>
                    <p 
                      onClick={() => handleVerseClick(verse.verseNumber)}
                      className="flex-1 leading-relaxed text-foreground"
                      style={{ 
                        fontFamily: 'var(--font-body)',
                        fontSize: `${userProfile.preferences.fontSize}px`,
                        lineHeight: userProfile.preferences.lineSpacing
                      }}
                    >
                      {verse.text}
                    </p>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-start gap-1 mt-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedVerses([verse.verseNumber])
                          setShareFriendsDialogOpen(true)
                        }}
                      >
                        <PaperPlaneTilt size={16} weight="duotone" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 pt-6 border-t border-border flex items-center justify-between">
              <Button
                variant="outline"
                onClick={handlePrevChapter}
                disabled={currentBookId === bibleBooks[0]?.id && currentChapter === 1}
              >
                <CaretLeft size={20} weight="bold" className="mr-2" />
                Previous Chapter
              </Button>

              <Button
                variant="outline"
                onClick={handleNextChapter}
                disabled={
                  currentBookId === bibleBooks[bibleBooks.length - 1]?.id &&
                  currentChapter === currentBook?.chaptersCount
                }
              >
                Next Chapter
                <CaretRight size={20} weight="bold" className="ml-2" />
              </Button>
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}
