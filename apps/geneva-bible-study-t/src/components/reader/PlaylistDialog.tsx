import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Plus, Trash, Play, ArrowUp, ArrowDown, X } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { toast } from 'sonner'
import type { AudioPlaylist, AudioPlaylistItem } from '@/lib/types'

interface PlaylistDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onPlaylistSelect: (playlist: AudioPlaylist) => void
  currentBookId?: string
  currentChapter?: number
}

const BIBLE_BOOKS = [
  { id: 'gen', name: 'Genesis', chapters: 50 },
  { id: 'exod', name: 'Exodus', chapters: 40 },
  { id: 'lev', name: 'Leviticus', chapters: 27 },
  { id: 'num', name: 'Numbers', chapters: 36 },
  { id: 'deut', name: 'Deuteronomy', chapters: 34 },
  { id: 'josh', name: 'Joshua', chapters: 24 },
  { id: 'judg', name: 'Judges', chapters: 21 },
  { id: 'ruth', name: 'Ruth', chapters: 4 },
  { id: '1sam', name: '1 Samuel', chapters: 31 },
  { id: '2sam', name: '2 Samuel', chapters: 24 },
  { id: '1kgs', name: '1 Kings', chapters: 22 },
  { id: '2kgs', name: '2 Kings', chapters: 25 },
  { id: 'ps', name: 'Psalms', chapters: 150 },
  { id: 'prov', name: 'Proverbs', chapters: 31 },
  { id: 'matt', name: 'Matthew', chapters: 28 },
  { id: 'mark', name: 'Mark', chapters: 16 },
  { id: 'luke', name: 'Luke', chapters: 24 },
  { id: 'john', name: 'John', chapters: 21 },
  { id: 'rom', name: 'Romans', chapters: 16 },
  { id: '1cor', name: '1 Corinthians', chapters: 16 },
  { id: 'gal', name: 'Galatians', chapters: 6 },
  { id: 'eph', name: 'Ephesians', chapters: 6 },
  { id: 'phil', name: 'Philippians', chapters: 4 },
  { id: 'col', name: 'Colossians', chapters: 4 },
  { id: 'jas', name: 'James', chapters: 5 },
  { id: 'rev', name: 'Revelation', chapters: 22 }
]

export default function PlaylistDialog({ 
  open, 
  onOpenChange, 
  onPlaylistSelect,
  currentBookId,
  currentChapter
}: PlaylistDialogProps) {
  const [playlists, setPlaylists] = useKV<AudioPlaylist[]>('audio-playlists', [])
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [newPlaylist, setNewPlaylist] = useState<Partial<AudioPlaylist>>({
    name: '',
    description: '',
    items: []
  })

  const handleCreatePlaylist = () => {
    if (!newPlaylist.name || !newPlaylist.items || newPlaylist.items.length === 0) {
      toast.error('Please provide a name and at least one chapter')
      return
    }

    const playlist: AudioPlaylist = {
      id: Date.now().toString(),
      name: newPlaylist.name,
      description: newPlaylist.description || '',
      items: newPlaylist.items,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    setPlaylists(current => [...(current || []), playlist])
    setNewPlaylist({ name: '', description: '', items: [] })
    setIsCreating(false)
    toast.success('Playlist created!')
  }

  const handleDeletePlaylist = (id: string) => {
    setPlaylists(current => (current || []).filter(p => p.id !== id))
    toast.success('Playlist deleted')
  }

  const handlePlayPlaylist = (playlist: AudioPlaylist) => {
    onPlaylistSelect(playlist)
    onOpenChange(false)
    toast.success(`Playing ${playlist.name}`)
  }

  const handleAddItem = () => {
    if (!currentBookId || !currentChapter) {
      toast.error('Please select a book and chapter')
      return
    }

    const book = BIBLE_BOOKS.find(b => b.id === currentBookId)
    if (!book) return

    const newItem: AudioPlaylistItem = {
      bookId: currentBookId,
      bookName: book.name,
      chapter: currentChapter,
      translationId: 'geneva'
    }

    setNewPlaylist(prev => ({
      ...prev,
      items: [...(prev.items || []), newItem]
    }))
  }

  const handleRemoveItem = (index: number) => {
    setNewPlaylist(prev => ({
      ...prev,
      items: (prev.items || []).filter((_, i) => i !== index)
    }))
  }

  const handleMoveItem = (index: number, direction: 'up' | 'down') => {
    const items = [...(newPlaylist.items || [])]
    const newIndex = direction === 'up' ? index - 1 : index + 1
    
    if (newIndex < 0 || newIndex >= items.length) return
    
    const temp = items[index]
    items[index] = items[newIndex]
    items[newIndex] = temp
    
    setNewPlaylist(prev => ({ ...prev, items }))
  }

  const handleQuickCreate = (type: 'gospel' | 'epistles' | 'psalms') => {
    const items: AudioPlaylistItem[] = []
    
    if (type === 'gospel') {
      const gospels = BIBLE_BOOKS.filter(b => ['matt', 'mark', 'luke', 'john'].includes(b.id))
      gospels.forEach(book => {
        for (let i = 1; i <= book.chapters; i++) {
          items.push({
            bookId: book.id,
            bookName: book.name,
            chapter: i,
            translationId: 'geneva'
          })
        }
      })
      setNewPlaylist({
        name: 'Complete Gospels',
        description: 'Matthew, Mark, Luke, and John in order',
        items
      })
    } else if (type === 'epistles') {
      const epistles = BIBLE_BOOKS.filter(b => 
        ['rom', '1cor', 'gal', 'eph', 'phil', 'col', 'jas'].includes(b.id)
      )
      epistles.forEach(book => {
        for (let i = 1; i <= book.chapters; i++) {
          items.push({
            bookId: book.id,
            bookName: book.name,
            chapter: i,
            translationId: 'geneva'
          })
        }
      })
      setNewPlaylist({
        name: 'Essential Epistles',
        description: 'Key letters from the Apostles',
        items
      })
    } else if (type === 'psalms') {
      const psalms = BIBLE_BOOKS.find(b => b.id === 'ps')!
      for (let i = 1; i <= 150; i++) {
        items.push({
          bookId: 'ps',
          bookName: 'Psalms',
          chapter: i,
          translationId: 'geneva'
        })
      }
      setNewPlaylist({
        name: 'Complete Psalms',
        description: 'All 150 Psalms',
        items
      })
    }
    
    setIsCreating(true)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Audio Playlists</DialogTitle>
        </DialogHeader>

        <ScrollArea className="h-[60vh]">
          <div className="space-y-4 pr-4">
            {!isCreating && (
              <>
                <div className="flex gap-2">
                  <Button onClick={() => setIsCreating(true)} className="flex-1">
                    <Plus size={20} weight="bold" className="mr-2" />
                    Create Custom Playlist
                  </Button>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h4 className="text-sm font-semibold">Quick Playlists</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <Button variant="outline" onClick={() => handleQuickCreate('gospel')}>
                      Four Gospels
                    </Button>
                    <Button variant="outline" onClick={() => handleQuickCreate('epistles')}>
                      Key Epistles
                    </Button>
                    <Button variant="outline" onClick={() => handleQuickCreate('psalms')}>
                      All Psalms
                    </Button>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h4 className="text-sm font-semibold">Your Playlists</h4>
                  {(!playlists || playlists.length === 0) ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No playlists yet. Create one to get started!
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {playlists.map(playlist => (
                        <Card key={playlist.id} className="p-4">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h3 className="font-semibold">{playlist.name}</h3>
                              {playlist.description && (
                                <p className="text-sm text-muted-foreground">{playlist.description}</p>
                              )}
                              <Badge variant="secondary" className="mt-2">
                                {playlist.items.length} chapter{playlist.items.length !== 1 ? 's' : ''}
                              </Badge>
                            </div>
                            <div className="flex gap-2">
                              <Button 
                                size="sm" 
                                onClick={() => handlePlayPlaylist(playlist)}
                              >
                                <Play size={16} weight="fill" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => handleDeletePlaylist(playlist.id)}
                              >
                                <Trash size={16} />
                              </Button>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}

            {isCreating && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Create New Playlist</h3>
                  <Button variant="ghost" size="sm" onClick={() => {
                    setIsCreating(false)
                    setNewPlaylist({ name: '', description: '', items: [] })
                  }}>
                    <X size={20} />
                  </Button>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="playlist-name">Playlist Name</Label>
                    <Input
                      id="playlist-name"
                      value={newPlaylist.name}
                      onChange={(e) => setNewPlaylist(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="My Favorite Chapters"
                    />
                  </div>

                  <div>
                    <Label htmlFor="playlist-description">Description (optional)</Label>
                    <Textarea
                      id="playlist-description"
                      value={newPlaylist.description}
                      onChange={(e) => setNewPlaylist(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="A collection of..."
                      rows={2}
                    />
                  </div>

                  <Separator />

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>Chapters</Label>
                      {currentBookId && currentChapter && (
                        <Button size="sm" variant="outline" onClick={handleAddItem}>
                          <Plus size={16} className="mr-1" />
                          Add Current Chapter
                        </Button>
                      )}
                    </div>

                    {(!newPlaylist.items || newPlaylist.items.length === 0) ? (
                      <p className="text-sm text-muted-foreground text-center py-4 border border-dashed rounded">
                        No chapters added yet
                      </p>
                    ) : (
                      <div className="space-y-2 max-h-[300px] overflow-y-auto">
                        {newPlaylist.items.map((item, index) => (
                          <Card key={index} className="p-3">
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex-1">
                                <span className="font-medium">{item.bookName}</span>
                                <span className="text-muted-foreground ml-2">Chapter {item.chapter}</span>
                              </div>
                              <div className="flex gap-1">
                                <Button 
                                  size="sm" 
                                  variant="ghost"
                                  onClick={() => handleMoveItem(index, 'up')}
                                  disabled={index === 0}
                                >
                                  <ArrowUp size={16} />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="ghost"
                                  onClick={() => handleMoveItem(index, 'down')}
                                  disabled={index === newPlaylist.items!.length - 1}
                                >
                                  <ArrowDown size={16} />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="ghost"
                                  onClick={() => handleRemoveItem(index)}
                                >
                                  <Trash size={16} />
                                </Button>
                              </div>
                            </div>
                          </Card>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button 
                      onClick={handleCreatePlaylist}
                      className="flex-1"
                      disabled={!newPlaylist.name || !newPlaylist.items || newPlaylist.items.length === 0}
                    >
                      Create Playlist
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => {
                        setIsCreating(false)
                        setNewPlaylist({ name: '', description: '', items: [] })
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
