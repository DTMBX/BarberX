import { Play, Pause, Stop, SpeakerHigh, CaretRight, CaretLeft, Moon, Timer, ListPlus, BookmarkSimple } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useState, useEffect } from 'react'
import type { AudioNarrator, AudioPlaybackState, AudioPlaylist } from '@/lib/types'

interface AudioPlayerControlsProps {
  playbackState: AudioPlaybackState
  currentNarrator: AudioNarrator | undefined
  narrators: AudioNarrator[]
  currentPlaylist?: AudioPlaylist | null
  onPlay: () => void
  onPause: () => void
  onResume: () => void
  onStop: () => void
  onNarratorChange: (narratorId: string) => void
  onPlaybackRateChange: (rate: number) => void
  onVolumeChange: (volume: number) => void
  onSleepTimerSet: (minutes: number | null) => void
  onPlaylistOpen?: () => void
  onBookmarkOpen?: () => void
  onAddBookmark?: () => void
  totalVerses: number
}

export default function AudioPlayerControls({
  playbackState,
  currentNarrator,
  narrators,
  currentPlaylist,
  onPlay,
  onPause,
  onResume,
  onStop,
  onNarratorChange,
  onPlaybackRateChange,
  onVolumeChange,
  onSleepTimerSet,
  onPlaylistOpen,
  onBookmarkOpen,
  onAddBookmark,
  totalVerses
}: AudioPlayerControlsProps) {
  const [timeRemaining, setTimeRemaining] = useState<string>('')

  useEffect(() => {
    if (!playbackState.sleepTimerEndTime) {
      setTimeRemaining('')
      return
    }

    const interval = setInterval(() => {
      const remaining = playbackState.sleepTimerEndTime! - Date.now()
      if (remaining <= 0) {
        setTimeRemaining('')
        return
      }

      const minutes = Math.floor(remaining / 60000)
      const seconds = Math.floor((remaining % 60000) / 1000)
      setTimeRemaining(`${minutes}:${seconds.toString().padStart(2, '0')}`)
    }, 1000)

    return () => clearInterval(interval)
  }, [playbackState.sleepTimerEndTime])

  const handlePlayPause = () => {
    if (playbackState.isPlaying) {
      onPause()
    } else if (playbackState.isPaused) {
      onResume()
    } else {
      onPlay()
    }
  }

  const sleepTimerOptions = [
    { label: 'Off', value: null },
    { label: '5 min', value: 5 },
    { label: '10 min', value: 10 },
    { label: '15 min', value: 15 },
    { label: '30 min', value: 30 },
    { label: '45 min', value: 45 },
    { label: '60 min', value: 60 },
    { label: '90 min', value: 90 }
  ]

  return (
    <Card className="p-4 bg-card border-primary/20">
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SpeakerHigh size={24} weight="duotone" className="text-primary" />
            <div className="flex flex-col">
              <h3 className="font-semibold text-sm">Audio Bible</h3>
              {playbackState.isPlaying && playbackState.currentVerseNumber > 0 && (
                <span className="text-xs text-muted-foreground">
                  Verse {playbackState.currentVerseNumber} of {totalVerses}
                </span>
              )}
              {currentPlaylist && playbackState.playlistPosition !== undefined && (
                <span className="text-xs text-accent font-medium">
                  Playlist: {currentPlaylist.name} ({playbackState.playlistPosition + 1}/{currentPlaylist.items.length})
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {currentNarrator && (
              <Badge variant="secondary" className="text-xs">
                {currentNarrator.name}
              </Badge>
            )}
            {timeRemaining && (
              <Badge variant="default" className="text-xs gap-1">
                <Moon size={12} weight="fill" />
                {timeRemaining}
              </Badge>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={playbackState.isPlaying || playbackState.isPaused ? "default" : "default"}
            size="icon"
            onClick={handlePlayPause}
            className="h-12 w-12"
          >
            {playbackState.isPlaying ? (
              <Pause size={24} weight="fill" />
            ) : (
              <Play size={24} weight="fill" />
            )}
          </Button>

          <Button
            variant="outline"
            size="icon"
            onClick={onStop}
            disabled={!playbackState.isPlaying && !playbackState.isPaused}
          >
            <Stop size={20} weight="fill" />
          </Button>

          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant={playbackState.sleepTimerEndTime ? "default" : "outline"}
                size="icon"
                title="Sleep Timer"
              >
                <Timer size={20} weight={playbackState.sleepTimerEndTime ? "fill" : "regular"} />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-48">
              <div className="flex flex-col gap-2">
                <h4 className="font-semibold text-sm mb-2">Sleep Timer</h4>
                {sleepTimerOptions.map((option) => (
                  <Button
                    key={option.label}
                    variant={playbackState.sleepTimerMinutes === option.value ? "default" : "ghost"}
                    size="sm"
                    onClick={() => onSleepTimerSet(option.value)}
                    className="justify-start"
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </PopoverContent>
          </Popover>

          {onPlaylistOpen && (
            <Button
              variant="outline"
              size="icon"
              onClick={onPlaylistOpen}
              title="Playlists"
            >
              <ListPlus size={20} weight="duotone" />
            </Button>
          )}

          {onAddBookmark && (
            <Button
              variant="outline"
              size="icon"
              onClick={onAddBookmark}
              title="Bookmark Current Moment"
              disabled={!playbackState.isPlaying && !playbackState.isPaused}
            >
              <BookmarkSimple size={20} weight="duotone" />
            </Button>
          )}

          {onBookmarkOpen && (
            <Button
              variant="outline"
              size="icon"
              onClick={onBookmarkOpen}
              title="View Bookmarks"
            >
              <BookmarkSimple size={20} weight="fill" />
            </Button>
          )}

          <Separator orientation="vertical" className="h-10 mx-2" />

          <div className="flex-1 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground min-w-[60px]">Narrator:</span>
              <Select
                value={playbackState.narratorId}
                onValueChange={onNarratorChange}
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {narrators.map((narrator) => (
                    <SelectItem key={narrator.id} value={narrator.id}>
                      <div className="flex items-center gap-2">
                        <span>{narrator.name}</span>
                        <Badge variant="outline" className="text-[10px] px-1 py-0">
                          {narrator.accent}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground min-w-[60px]">Speed:</span>
              <div className="flex-1 flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <Button
                    variant={playbackState.playbackRate === 0.75 ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPlaybackRateChange(0.75)}
                    className="flex-1 h-7 text-xs"
                  >
                    Slow
                  </Button>
                  <Button
                    variant={playbackState.playbackRate === 1.0 ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPlaybackRateChange(1.0)}
                    className="flex-1 h-7 text-xs"
                  >
                    Normal
                  </Button>
                  <Button
                    variant={playbackState.playbackRate === 1.5 ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPlaybackRateChange(1.5)}
                    className="flex-1 h-7 text-xs"
                  >
                    Fast
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  <Slider
                    value={[playbackState.playbackRate]}
                    onValueChange={([value]) => onPlaybackRateChange(value)}
                    min={0.5}
                    max={2.0}
                    step={0.1}
                    className="flex-1"
                  />
                  <span className="text-xs text-muted-foreground min-w-[40px] text-right">
                    {playbackState.playbackRate.toFixed(1)}x
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <SpeakerHigh size={16} className="text-muted-foreground min-w-[60px]" />
              <div className="flex-1 flex items-center gap-2">
                <Slider
                  value={[playbackState.volume * 100]}
                  onValueChange={([value]) => onVolumeChange(value / 100)}
                  min={0}
                  max={100}
                  step={5}
                  className="flex-1"
                />
                <span className="text-xs text-muted-foreground min-w-[40px] text-right">
                  {Math.round(playbackState.volume * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {currentNarrator && (
          <div className="text-xs text-muted-foreground pt-2 border-t border-border">
            {currentNarrator.description}
            {playbackState.sleepTimerEndTime && (
              <span className="ml-2 text-primary">• Audio will stop in {timeRemaining}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
