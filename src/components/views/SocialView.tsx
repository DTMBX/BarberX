import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Users, Heart, ChatCircle, ShareNetwork, Trophy, BookOpen, CalendarCheck, UserPlus, MagnifyingGlass, Path, PaperPlaneTilt } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import type { SharedVerse, SharedProgress, UserConnection } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import FriendsList from '@/components/social/FriendsList'
import FindFriends from '@/components/social/FindFriends'
import ReadingJourneyView from '@/components/social/ReadingJourneyView'
import FriendsLeaderboard from '@/components/social/FriendsLeaderboard'
import { seedDemoFriendRequests, seedDemoFriends } from '@/lib/friend-seeding'

interface SocialViewProps {
  onNavigateToMessages?: (friendId: string, verseRef?: any) => void
}

export default function SocialView({ onNavigateToMessages }: SocialViewProps) {
  const [sharedVerses = []] = useKV<SharedVerse[]>('shared-verses', [])
  const [sharedProgress = []] = useKV<SharedProgress[]>('shared-progress', [])
  const [likedItems, setLikedItems] = useKV<string[]>('liked-items', [])
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [commentText, setCommentText] = useState<Record<string, string>>({})
  const [activeView, setActiveView] = useState<'feed' | 'friends' | 'find' | 'journey'>('feed')
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  const [initialized, setInitialized] = useState(false)

  if (!initialized) {
    seedDemoFriendRequests()
    seedDemoFriends()
    setInitialized(true)
  }

  const allShares = [...sharedVerses, ...sharedProgress].sort((a, b) => b.createdAt - a.createdAt)

  const handleViewJourney = (userId: string) => {
    setSelectedUserId(userId)
    setActiveView('journey')
  }

  const handleBackToFeed = () => {
    setActiveView('feed')
    setSelectedUserId(null)
  }

  const handleLike = async (itemId: string) => {
    const user = await window.spark.user()
    const userId = user?.id?.toString() || 'anonymous'

    setLikedItems((current = []) => {
      if (current.includes(itemId)) {
        return current.filter(id => id !== itemId)
      } else {
        return [...current, itemId]
      }
    })
  }

  const isVerse = (item: SharedVerse | SharedProgress): item is SharedVerse => {
    return 'verseText' in item
  }

  const isFriend = (userId: string): boolean => {
    return friends.some(friend => friend.userId === userId)
  }

  if (activeView === 'journey' && selectedUserId) {
    return (
      <div className="h-full bg-background">
        <ReadingJourneyView userId={selectedUserId} onBack={handleBackToFeed} />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b bg-card px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-1 flex items-center gap-2" style={{ fontFamily: 'var(--font-heading)' }}>
            <Users size={28} weight="duotone" className="text-primary" />
            Community
          </h2>
          <p className="text-muted-foreground">
            Connect with friends and share your Bible reading journey
          </p>
        </div>
      </div>

      <Tabs value={activeView} onValueChange={(value) => setActiveView(value as any)} className="flex-1 flex flex-col">
        <div className="border-b bg-card px-6 py-2">
          <TabsList className="max-w-4xl mx-auto">
            <TabsTrigger value="feed" className="gap-2">
              <ShareNetwork size={16} weight="duotone" />
              Feed
            </TabsTrigger>
            <TabsTrigger value="friends" className="gap-2">
              <Users size={16} weight="duotone" />
              Friends
            </TabsTrigger>
            <TabsTrigger value="find" className="gap-2">
              <MagnifyingGlass size={16} weight="duotone" />
              Find Friends
            </TabsTrigger>
          </TabsList>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              <TabsContent value="feed" className="mt-0 space-y-4">
                <Tabs defaultValue="all" className="w-full">
                  <TabsList className="w-full">
                    <TabsTrigger value="all" className="flex-1">All Updates</TabsTrigger>
                    <TabsTrigger value="verses" className="flex-1">Verses</TabsTrigger>
                    <TabsTrigger value="progress" className="flex-1">Progress</TabsTrigger>
                  </TabsList>

                  <div className="mt-4">
                    <TabsContent value="all" className="mt-0 space-y-4">
                      {allShares.length === 0 ? (
                        <Card className="p-12 text-center">
                          <ShareNetwork size={64} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-xl font-semibold mb-2">No shares yet</h3>
                          <p className="text-muted-foreground mb-4">
                            Share your favorite verses and reading progress to get started!
                          </p>
                        </Card>
                      ) : (
                        allShares.map((item) => (
                          <ShareCard
                            key={item.id}
                            item={item}
                            isLiked={likedItems?.includes(item.id) || false}
                            onLike={() => handleLike(item.id)}
                            commentText={commentText[item.id] || ''}
                            onCommentChange={(text) => setCommentText({ ...commentText, [item.id]: text })}
                            onViewJourney={() => handleViewJourney(item.userId)}
                            onMessage={onNavigateToMessages ? () => {
                              const verseRef = isVerse(item) ? {
                                bookName: item.bookName,
                                chapterNumber: item.chapterNumber,
                                verseNumber: item.verseNumber,
                                verseEndNumber: item.verseEndNumber,
                                verseText: item.verseText,
                                translation: item.translation
                              } : undefined
                              onNavigateToMessages(item.userId, verseRef)
                            } : undefined}
                            isFriend={isFriend(item.userId)}
                          />
                        ))
                      )}
                    </TabsContent>

                    <TabsContent value="verses" className="mt-0 space-y-4">
                      {sharedVerses.length === 0 ? (
                        <Card className="p-12 text-center">
                          <BookOpen size={64} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-xl font-semibold mb-2">No verses shared</h3>
                          <p className="text-muted-foreground">
                            Share inspiring verses from your reading
                          </p>
                        </Card>
                      ) : (
                        sharedVerses.map((verse) => (
                          <ShareCard
                            key={verse.id}
                            item={verse}
                            isLiked={likedItems?.includes(verse.id) || false}
                            onLike={() => handleLike(verse.id)}
                            commentText={commentText[verse.id] || ''}
                            onCommentChange={(text) => setCommentText({ ...commentText, [verse.id]: text })}
                            onViewJourney={() => handleViewJourney(verse.userId)}
                            onMessage={onNavigateToMessages ? () => {
                              const verseRef = {
                                bookName: verse.bookName,
                                chapterNumber: verse.chapterNumber,
                                verseNumber: verse.verseNumber,
                                verseEndNumber: verse.verseEndNumber,
                                verseText: verse.verseText,
                                translation: verse.translation
                              }
                              onNavigateToMessages(verse.userId, verseRef)
                            } : undefined}
                            isFriend={isFriend(verse.userId)}
                          />
                        ))
                      )}
                    </TabsContent>

                    <TabsContent value="progress" className="mt-0 space-y-4">
                      {sharedProgress.length === 0 ? (
                        <Card className="p-12 text-center">
                          <Trophy size={64} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-xl font-semibold mb-2">No progress shared</h3>
                          <p className="text-muted-foreground">
                            Complete reading plans and celebrate milestones
                          </p>
                        </Card>
                      ) : (
                        sharedProgress.map((progress) => (
                          <ShareCard
                            key={progress.id}
                            item={progress}
                            isLiked={likedItems?.includes(progress.id) || false}
                            onLike={() => handleLike(progress.id)}
                            commentText={commentText[progress.id] || ''}
                            onCommentChange={(text) => setCommentText({ ...commentText, [progress.id]: text })}
                            onViewJourney={() => handleViewJourney(progress.userId)}
                            onMessage={onNavigateToMessages ? () => {
                              onNavigateToMessages(progress.userId)
                            } : undefined}
                            isFriend={isFriend(progress.userId)}
                          />
                        ))
                      )}
                    </TabsContent>
                  </div>
                </Tabs>
              </TabsContent>

              <TabsContent value="friends" className="mt-0">
                <div className="space-y-6">
                  <FriendsLeaderboard onViewJourney={handleViewJourney} />
                  <FriendsList onViewJourney={handleViewJourney} />
                </div>
              </TabsContent>

              <TabsContent value="find" className="mt-0">
                <FindFriends onViewJourney={handleViewJourney} />
              </TabsContent>
            </div>
          </div>
        </ScrollArea>
      </Tabs>
    </div>
  )
}

interface ShareCardProps {
  item: SharedVerse | SharedProgress
  isLiked: boolean
  onLike: () => void
  commentText: string
  onCommentChange: (text: string) => void
  onViewJourney: () => void
  onMessage?: () => void
  isFriend?: boolean
}

function ShareCard({ item, isLiked, onLike, onViewJourney, onMessage, isFriend }: ShareCardProps) {
  const isVerse = 'verseText' in item

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <button onClick={onViewJourney} className="hover:opacity-80 transition-opacity">
            <Avatar>
              <AvatarImage src={item.userAvatar} />
              <AvatarFallback>{item.userName[0]?.toUpperCase()}</AvatarFallback>
            </Avatar>
          </button>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <button onClick={onViewJourney} className="hover:underline">
                <p className="font-semibold">{item.userName}</p>
              </button>
              {isVerse ? (
                <Badge variant="secondary" className="text-xs">
                  <BookOpen size={12} weight="duotone" className="mr-1" />
                  Verse
                </Badge>
              ) : (
                <Badge variant="secondary" className="text-xs bg-accent/20 text-accent-foreground">
                  <Trophy size={12} weight="duotone" className="mr-1" />
                  Achievement
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatDistanceToNow(item.createdAt, { addSuffix: true })}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {isVerse ? (
          <>
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-l-primary">
              <p className="text-sm font-mono text-muted-foreground mb-2">
                {item.bookName} {item.chapterNumber}:{item.verseNumber}
                {item.verseEndNumber && item.verseEndNumber !== item.verseNumber && `-${item.verseEndNumber}`}
              </p>
              <p className="text-base leading-relaxed" style={{ fontFamily: 'var(--font-body)' }}>
                "{item.verseText}"
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {item.translation.toUpperCase()}
              </p>
            </div>
            {item.note && (
              <p className="text-sm text-foreground/80 italic">
                {item.note}
              </p>
            )}
          </>
        ) : (
          <div className="p-4 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg border-l-4 border-l-accent">
            <div className="flex items-start gap-3">
              <Trophy size={28} weight="fill" className="text-accent flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-bold mb-1">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
                {item.planName && (
                  <div className="flex items-center gap-2 mt-2">
                    <CalendarCheck size={16} weight="duotone" className="text-primary" />
                    <p className="text-sm font-medium text-primary">
                      {item.planName}
                    </p>
                  </div>
                )}
                {item.daysCompleted !== undefined && item.totalDays !== undefined && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {item.daysCompleted} of {item.totalDays} days completed
                  </p>
                )}
                {item.streakDays !== undefined && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {item.streakDays} day streak! 🔥
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        <Separator />

        <div className="flex items-center gap-2">
          <Button
            variant={isLiked ? "default" : "ghost"}
            size="sm"
            onClick={onLike}
            className="gap-1"
          >
            <Heart size={16} weight={isLiked ? "fill" : "regular"} />
            <span className="text-xs">
              {item.likes.length > 0 && item.likes.length}
            </span>
          </Button>
          <Button variant="ghost" size="sm" className="gap-1">
            <ChatCircle size={16} weight="regular" />
            <span className="text-xs">
              {item.comments.length > 0 && item.comments.length}
            </span>
          </Button>
          {onMessage && isFriend && (
            <Button variant="ghost" size="sm" className="gap-1" onClick={onMessage}>
              <PaperPlaneTilt size={16} weight="regular" />
              <span className="text-xs">Message</span>
            </Button>
          )}
          <Button variant="ghost" size="sm" className="gap-1 ml-auto">
            <ShareNetwork size={16} weight="regular" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
