import { useEffect, useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Share, BookmarkSimple, Copy, Check, ChatCircle, UsersThree, Heart, BookOpen, Translate } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { fetchVerse } from '@/lib/bibleApi'
import { bibleBooks } from '@/lib/data'
import type { Bookmark, Conversation, UserConnection, GroupDiscussion } from '@/lib/types'
import VerseComparisonDialog from '@/components/VerseComparisonDialog'

interface VerseOfTheDayData {
  date: string
  bookId: string
  chapter: number
  verse: number
  text: string
  translation: string
}

interface VerseOfTheDayProps {
  userProfile: any
  onNavigateToReader?: (bookId: string, chapter: number) => void
  onNavigateToMessages?: (friendId: string, verseRef: any) => void
}

const AVAILABLE_TRANSLATIONS = [
  { id: 'kjv', name: 'King James Version (KJV)' },
  { id: 'web', name: 'World English Bible (WEB)' },
  { id: 'bbe', name: 'Bible in Basic English (BBE)' },
  { id: 'ylt', name: "Young's Literal Translation (YLT)" },
  { id: 'oeb-cw', name: 'Open English Bible (OEB)' },
  { id: 'webbe', name: 'World English Bible, British Edition (WEBBE)' },
  { id: 'wmb', name: 'World Messianic Bible (WMB)' },
  { id: 'net', name: 'New English Translation (NET)' },
  { id: 'lsg', name: 'Louis Segond (LSG) - French' },
  { id: 'byz', name: 'Byzantine/Majority Text (BYZ) - Greek' },
]

export default function VerseOfTheDay({ userProfile, onNavigateToReader, onNavigateToMessages }: VerseOfTheDayProps) {
  const [verseData, setVerseData] = useState<VerseOfTheDayData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [bookmarks = [], setBookmarks] = useKV<Bookmark[]>('bookmarks', [])
  const [friends = []] = useKV<UserConnection[]>('friends', [])
  const [conversations = [], setConversations] = useKV<Conversation[]>('conversations', [])
  const [groups = []] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [likedVerses = [], setLikedVerses] = useKV<string[]>('liked-verses-of-day', [])
  const [selectedTranslation, setSelectedTranslation] = useState<string>(userProfile?.preferences?.defaultTranslation || 'kjv')
  const [isLoadingTranslation, setIsLoadingTranslation] = useState(false)
  const [comparisonDialogOpen, setComparisonDialogOpen] = useState(false)

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  useEffect(() => {
    loadVerseOfTheDay()
  }, [])

  useEffect(() => {
    if (verseData && selectedTranslation !== verseData.translation) {
      loadVerseInTranslation(selectedTranslation)
    }
  }, [selectedTranslation])

  const loadVerseInTranslation = async (translationId: string) => {
    if (!verseData) return
    
    setIsLoadingTranslation(true)
    try {
      const today = new Date().toISOString().split('T')[0]
      const cacheKey = `verse-of-day-${today}-${translationId}`
      
      const cachedVerse = await window.spark.kv.get<VerseOfTheDayData>(cacheKey)
      if (cachedVerse) {
        setVerseData(cachedVerse)
        setIsLoadingTranslation(false)
        return
      }

      const verseResult = await fetchVerse({
        translationId,
        bookId: verseData.bookId,
        chapter: verseData.chapter,
        verse: verseData.verse
      })

      if (verseResult) {
        const newVerseData: VerseOfTheDayData = {
          date: today,
          bookId: verseData.bookId,
          chapter: verseData.chapter,
          verse: verseData.verse,
          text: verseResult.text,
          translation: translationId
        }
        
        await window.spark.kv.set(cacheKey, newVerseData)
        setVerseData(newVerseData)
      }
    } catch (error) {
      console.error('Failed to load translation:', error)
      toast.error('Failed to load translation')
    } finally {
      setIsLoadingTranslation(false)
    }
  }

  const loadVerseOfTheDay = async () => {
    setIsLoading(true)
    try {
      const today = new Date().toISOString().split('T')[0]
      const cachedVerse = await window.spark.kv.get<VerseOfTheDayData>(`verse-of-day-${today}`)

      if (cachedVerse) {
        setVerseData(cachedVerse)
        setIsLoading(false)
        return
      }

      const translation = userProfile?.preferences?.defaultTranslation || 'kjv'
      let verseResult: { text: string } | null = null
      let selectedVerse: { bookId: string; chapter: number; verse: number } | null = null

      try {
        const response = await fetch('https://beta.ourmanna.com/api/v1/get/?format=json')
        const data = await response.json()
        
        if (data?.verse?.details?.reference) {
          const reference = data.verse.details.reference
          const match = reference.match(/^(\d?\s?[A-Za-z]+)\s+(\d+):(\d+)/)
          
          if (match) {
            const bookName = match[1].trim()
            const chapter = parseInt(match[2])
            const verse = parseInt(match[3])
            
            const bookMapping: Record<string, string> = {
              'Genesis': 'gen', 'Exodus': 'exo', 'Leviticus': 'lev', 'Numbers': 'num', 'Deuteronomy': 'deu',
              'Joshua': 'jos', 'Judges': 'jdg', 'Ruth': 'rut', '1 Samuel': '1sa', '2 Samuel': '2sa',
              '1 Kings': '1ki', '2 Kings': '2ki', '1 Chronicles': '1ch', '2 Chronicles': '2ch',
              'Ezra': 'ezr', 'Nehemiah': 'neh', 'Esther': 'est', 'Job': 'job', 'Psalms': 'psa', 'Psalm': 'psa',
              'Proverbs': 'pro', 'Ecclesiastes': 'ecc', 'Song of Solomon': 'sng', 'Isaiah': 'isa',
              'Jeremiah': 'jer', 'Lamentations': 'lam', 'Ezekiel': 'ezk', 'Daniel': 'dan', 'Hosea': 'hos',
              'Joel': 'jol', 'Amos': 'amo', 'Obadiah': 'oba', 'Jonah': 'jon', 'Micah': 'mic', 'Nahum': 'nam',
              'Habakkuk': 'hab', 'Zephaniah': 'zep', 'Haggai': 'hag', 'Zechariah': 'zec', 'Malachi': 'mal',
              'Matthew': 'mat', 'Mark': 'mrk', 'Luke': 'luk', 'John': 'jhn', 'Acts': 'act', 'Romans': 'rom',
              '1 Corinthians': '1co', '2 Corinthians': '2co', 'Galatians': 'gal', 'Ephesians': 'eph',
              'Philippians': 'php', 'Colossians': 'col', '1 Thessalonians': '1th', '2 Thessalonians': '2th',
              '1 Timothy': '1ti', '2 Timothy': '2ti', 'Titus': 'tit', 'Philemon': 'phm', 'Hebrews': 'heb',
              'James': 'jas', '1 Peter': '1pe', '2 Peter': '2pe', '1 John': '1jn', '2 John': '2jn',
              '3 John': '3jn', 'Jude': 'jud', 'Revelation': 'rev'
            }
            
            const bookId = bookMapping[bookName]
            if (bookId) {
              selectedVerse = { bookId, chapter, verse }
              verseResult = await fetchVerse({
                translationId: translation,
                bookId,
                chapter,
                verse
              })
            }
          }
        }
      } catch (apiError) {
        console.log('Daily verse API unavailable, using fallback')
      }

      if (!verseResult || !selectedVerse) {
        const dayOfYear = Math.floor((new Date().getTime() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000)
        
        const inspirationalVerses = [
          { bookId: 'jhn', chapter: 3, verse: 16 },
          { bookId: 'psa', chapter: 23, verse: 1 },
          { bookId: 'pro', chapter: 3, verse: 5 },
          { bookId: 'isa', chapter: 41, verse: 10 },
          { bookId: 'mat', chapter: 6, verse: 33 },
          { bookId: 'rom', chapter: 8, verse: 28 },
          { bookId: 'php', chapter: 4, verse: 13 },
          { bookId: 'jer', chapter: 29, verse: 11 },
          { bookId: '1co', chapter: 13, verse: 4 },
          { bookId: 'psa', chapter: 46, verse: 1 },
          { bookId: 'mat', chapter: 11, verse: 28 },
          { bookId: 'isa', chapter: 40, verse: 31 },
          { bookId: 'rom', chapter: 12, verse: 2 },
          { bookId: 'eph', chapter: 2, verse: 8 },
          { bookId: 'psa', chapter: 119, verse: 105 },
          { bookId: '2ti', chapter: 1, verse: 7 },
          { bookId: 'heb', chapter: 11, verse: 1 },
          { bookId: 'jas', chapter: 1, verse: 2 },
          { bookId: '1pe', chapter: 5, verse: 7 },
          { bookId: 'rev', chapter: 21, verse: 4 },
          { bookId: 'psa', chapter: 27, verse: 1 },
          { bookId: 'pro', chapter: 16, verse: 3 },
          { bookId: 'mat', chapter: 5, verse: 16 },
          { bookId: 'jhn', chapter: 14, verse: 6 },
          { bookId: 'gal', chapter: 5, verse: 22 },
          { bookId: 'col', chapter: 3, verse: 23 },
          { bookId: '1jn', chapter: 4, verse: 19 },
          { bookId: 'psa', chapter: 37, verse: 4 },
          { bookId: 'isa', chapter: 26, verse: 3 },
          { bookId: 'mic', chapter: 6, verse: 8 }
        ]

        selectedVerse = inspirationalVerses[dayOfYear % inspirationalVerses.length]
        verseResult = await fetchVerse({
          translationId: translation,
          bookId: selectedVerse.bookId,
          chapter: selectedVerse.chapter,
          verse: selectedVerse.verse
        })
      }

      if (!verseResult || !selectedVerse) {
        throw new Error('Failed to fetch verse')
      }

      const newVerseData: VerseOfTheDayData = {
        date: today,
        bookId: selectedVerse.bookId,
        chapter: selectedVerse.chapter,
        verse: selectedVerse.verse,
        text: verseResult.text,
        translation: translation
      }

      await window.spark.kv.set(`verse-of-day-${today}`, newVerseData)
      setVerseData(newVerseData)
    } catch (error) {
      console.error('Failed to load verse of the day:', error)
      toast.error('Failed to load verse of the day')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyVerse = () => {
    if (!verseData) return
    
    const book = bibleBooks.find(b => b.id === verseData.bookId)
    const translationName = AVAILABLE_TRANSLATIONS.find(t => t.id === verseData.translation)?.name || verseData.translation.toUpperCase()
    const text = `"${verseData.text}"\n\n${book?.title} ${verseData.chapter}:${verseData.verse} (${translationName})`
    
    navigator.clipboard.writeText(text)
    setCopied(true)
    toast.success('Verse copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleBookmark = () => {
    if (!verseData) return
    
    const book = bibleBooks.find(b => b.id === verseData.bookId)
    const newBookmark: Bookmark = {
      id: `bookmark-${Date.now()}`,
      userId: currentUserId,
      verseId: `${verseData.bookId}-${verseData.chapter}-${verseData.verse}`,
      workId: verseData.bookId,
      chapterNumber: verseData.chapter,
      verseNumber: verseData.verse,
      label: `Verse of the Day - ${new Date().toLocaleDateString()}`,
      createdAt: Date.now()
    }
    
    setBookmarks((current = []) => [newBookmark, ...current])
    toast.success('Verse bookmarked')
  }

  const handleLike = () => {
    if (!verseData) return
    const verseKey = `${verseData.date}-${verseData.bookId}-${verseData.chapter}-${verseData.verse}`
    
    setLikedVerses((current = []) => {
      if (current.includes(verseKey)) {
        toast.success('Removed from favorites')
        return current.filter(v => v !== verseKey)
      } else {
        toast.success('Added to favorites')
        return [...current, verseKey]
      }
    })
  }

  const handleShareWithFriend = (friend: UserConnection) => {
    if (!verseData) return
    
    const book = bibleBooks.find(b => b.id === verseData.bookId)
    const verseRef = {
      bookId: verseData.bookId,
      bookName: book?.title,
      chapter: verseData.chapter,
      verse: verseData.verse,
      text: verseData.text,
      translation: verseData.translation
    }

    if (onNavigateToMessages) {
      onNavigateToMessages(friend.userId, verseRef)
      setShareDialogOpen(false)
      toast.success(`Opening chat with ${friend.userName}`)
    }
  }

  const handleShareWithGroup = (group: GroupDiscussion) => {
    if (!verseData) return
    
    const book = bibleBooks.find(b => b.id === verseData.bookId)
    const translationName = AVAILABLE_TRANSLATIONS.find(t => t.id === verseData.translation)?.name || verseData.translation.toUpperCase()
    const message = `📖 Verse of the Day:\n\n"${verseData.text}"\n\n${book?.title} ${verseData.chapter}:${verseData.verse} (${translationName})`
    
    toast.success(`Shared with ${group.name}`)
    setShareDialogOpen(false)
  }

  const handleReadInContext = () => {
    if (!verseData || !onNavigateToReader) return
    onNavigateToReader(verseData.bookId, verseData.chapter)
  }

  if (isLoading) {
    return (
      <Card className="border-2 border-accent/50 shadow-xl bg-gradient-to-br from-card to-accent/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-3 text-2xl">
            <div className="p-2 rounded-lg bg-accent/20">
              <BookmarkSimple size={28} weight="duotone" className="text-accent" />
            </div>
            <div>
              <div className="text-2xl font-bold">Verse of the Day</div>
              <div className="text-sm font-normal text-muted-foreground mt-1">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3 animate-pulse">
            <div className="h-6 bg-muted rounded w-full" />
            <div className="h-6 bg-muted rounded w-5/6" />
            <div className="h-6 bg-muted rounded w-4/6" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!verseData) return null

  const book = bibleBooks.find(b => b.id === verseData.bookId)
  const verseKey = `${verseData.date}-${verseData.bookId}-${verseData.chapter}-${verseData.verse}`
  const isLiked = likedVerses.includes(verseKey)
  const currentTranslationName = AVAILABLE_TRANSLATIONS.find(t => t.id === verseData.translation)?.name || verseData.translation.toUpperCase()

  return (
    <>
      <Card className="border-2 border-accent/50 shadow-xl bg-gradient-to-br from-card to-accent/5 hover:shadow-2xl transition-all">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2 rounded-lg bg-accent/20">
                <BookmarkSimple size={28} weight="duotone" className="text-accent" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold">Verse of the Day</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLike}
              className="text-accent hover:text-accent shrink-0"
            >
              {isLiked ? (
                <Heart size={28} weight="fill" className="text-accent" />
              ) : (
                <Heart size={28} weight="duotone" />
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div 
            className="text-xl leading-relaxed cursor-pointer hover:text-accent transition-colors py-4 px-2 relative"
            style={{ fontFamily: 'var(--font-body)', lineHeight: '1.8' }}
            onClick={handleReadInContext}
          >
            {isLoadingTranslation && (
              <div className="absolute inset-0 bg-card/80 backdrop-blur-sm flex items-center justify-center rounded-md">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="h-4 w-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                  Loading translation...
                </div>
              </div>
            )}
            "{verseData.text}"
          </div>
          
          <div className="flex items-center justify-between gap-4 py-2 px-2 flex-wrap">
            <div className="text-base font-semibold text-primary">
              {book?.title} {verseData.chapter}:{verseData.verse}
            </div>
            <div className="flex items-center gap-2">
              <Translate size={18} className="text-muted-foreground" weight="duotone" />
              <Select value={selectedTranslation} onValueChange={setSelectedTranslation}>
                <SelectTrigger className="w-[200px] h-9">
                  <SelectValue placeholder="Select translation" />
                </SelectTrigger>
                <SelectContent>
                  {AVAILABLE_TRANSLATIONS.map(translation => (
                    <SelectItem key={translation.id} value={translation.id}>
                      {translation.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              size="default"
              onClick={handleCopyVerse}
              className="gap-2"
            >
              {copied ? <Check size={18} /> : <Copy size={18} />}
              {copied ? 'Copied!' : 'Copy Verse'}
            </Button>
            
            <Button
              variant="outline"
              size="default"
              onClick={handleBookmark}
              className="gap-2"
            >
              <BookmarkSimple size={18} weight="duotone" />
              Bookmark
            </Button>
            
            <Button
              variant="outline"
              size="default"
              onClick={() => setShareDialogOpen(true)}
              className="gap-2"
            >
              <Share size={18} weight="duotone" />
              Share
            </Button>

            <Button
              variant="secondary"
              size="default"
              onClick={() => setComparisonDialogOpen(true)}
              className="gap-2"
            >
              <Translate size={18} weight="duotone" />
              Compare Translations
            </Button>

            {onNavigateToReader && (
              <Button
                variant="default"
                size="default"
                onClick={handleReadInContext}
                className="gap-2 ml-auto"
              >
                <BookOpen size={18} weight="duotone" />
                Read in Context
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Share Verse of the Day</DialogTitle>
            <DialogDescription>
              Share this inspiring verse with friends or groups
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="p-3 bg-muted rounded-md text-sm" style={{ fontFamily: 'var(--font-body)' }}>
              "{verseData.text}"
              <div className="mt-2 text-xs text-muted-foreground">
                — {book?.title} {verseData.chapter}:{verseData.verse} ({currentTranslationName})
              </div>
            </div>

            {friends.length > 0 && (
              <div>
                <Label className="text-sm font-medium mb-2 block">Share with Friends</Label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {friends.map(friend => (
                    <button
                      key={friend.userId}
                      onClick={() => handleShareWithFriend(friend)}
                      className="w-full flex items-center gap-3 p-3 rounded-md hover:bg-muted transition-colors text-left"
                    >
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {friend.userName.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{friend.userName}</p>
                        <p className="text-xs text-muted-foreground">Send via message</p>
                      </div>
                      <ChatCircle size={20} className="text-muted-foreground" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {groups.filter(g => g.memberIds.includes(currentUserId)).length > 0 && (
              <div>
                <Label className="text-sm font-medium mb-2 block">Share with Groups</Label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {groups
                    .filter(g => g.memberIds.includes(currentUserId))
                    .map(group => (
                      <button
                        key={group.id}
                        onClick={() => handleShareWithGroup(group)}
                        className="w-full flex items-center gap-3 p-3 rounded-md hover:bg-muted transition-colors text-left"
                      >
                        <div className="h-10 w-10 rounded-full bg-accent/20 flex items-center justify-center">
                          <UsersThree size={20} className="text-accent" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{group.name}</p>
                          <p className="text-xs text-muted-foreground">{group.memberIds.length} members</p>
                        </div>
                      </button>
                    ))}
                </div>
              </div>
            )}

            {friends.length === 0 && groups.filter(g => g.memberIds.includes(currentUserId)).length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <UsersThree size={48} weight="duotone" className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No friends or groups to share with</p>
                <p className="text-xs">Add friends to start sharing verses</p>
              </div>
            )}

            <Separator />

            <div>
              <Label className="text-sm font-medium mb-2 block">Quick Actions</Label>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyVerse}
                  className="flex-1 gap-2"
                >
                  <Copy size={16} />
                  Copy Text
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleBookmark}
                  className="flex-1 gap-2"
                >
                  <BookmarkSimple size={16} />
                  Bookmark
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <VerseComparisonDialog
        open={comparisonDialogOpen}
        onOpenChange={setComparisonDialogOpen}
        verseData={verseData}
      />
    </>
  )
}
