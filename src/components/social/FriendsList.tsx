import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Users, MagnifyingGlass, UserPlus, Check, X, DotsThree, Fire, BookOpen, Trophy, CalendarCheck, TrendUp } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import type { UserConnection, FriendRequest, CommunityProfile } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'

interface FriendsListProps {
  onViewJourney: (userId: string) => void
}

export default function FriendsList({ onViewJourney }: FriendsListProps) {
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [friendRequests = [], setFriendRequests] = useKV<FriendRequest[]>('friend-requests', [])
  const [searchQuery, setSearchQuery] = useState('')
  const [friendProfiles, setFriendProfiles] = useState<Map<string, CommunityProfile>>(new Map())
  const [expandedFriends, setExpandedFriends] = useState<Set<string>>(new Set())

  const pendingRequests = friendRequests.filter(req => req.status === 'pending')
  const filteredFriends = friends.filter(friend =>
    friend.userName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  useEffect(() => {
    loadFriendProfiles()
  }, [friends])

  const loadFriendProfiles = async () => {
    const profiles = new Map<string, CommunityProfile>()
    
    const mockProfiles: Record<string, CommunityProfile> = {
      'user-1': {
        userId: 'user-1',
        userName: 'Sarah Johnson',
        userAvatar: undefined,
        bio: 'Studying Scripture daily, growing in faith',
        location: 'Nashville, TN',
        denomination: 'Presbyterian',
        favoriteBooks: ['Psalms', 'Romans', 'John'],
        readingGoals: {
          chaptersPerWeek: 7,
          currentStreak: 45,
          longestStreak: 120,
          totalChaptersRead: 892,
          plansCompleted: 3
        },
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now() - 365 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now()
      },
      'user-2': {
        userId: 'user-2',
        userName: 'Michael Chen',
        userAvatar: undefined,
        bio: 'Teaching the Word, loving people',
        location: 'Austin, TX',
        denomination: 'Non-denominational',
        favoriteBooks: ['Genesis', 'Matthew', 'Ephesians'],
        readingGoals: {
          chaptersPerWeek: 14,
          currentStreak: 89,
          longestStreak: 180,
          totalChaptersRead: 1245,
          plansCompleted: 5
        },
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now() - 500 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now()
      },
      'user-3': {
        userId: 'user-3',
        userName: 'Emily Rodriguez',
        userAvatar: undefined,
        bio: 'Journey through Scripture with joy',
        location: 'Denver, CO',
        denomination: 'Catholic',
        favoriteBooks: ['Proverbs', 'Luke', 'James'],
        readingGoals: {
          chaptersPerWeek: 5,
          currentStreak: 21,
          longestStreak: 65,
          totalChaptersRead: 456,
          plansCompleted: 2
        },
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: false,
          allowFriendRequests: true
        },
        createdAt: Date.now() - 180 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now()
      },
      'user-4': {
        userId: 'user-4',
        userName: 'David Thompson',
        userAvatar: undefined,
        bio: 'Seeking wisdom in the Word every day',
        location: 'Boston, MA',
        denomination: 'Baptist',
        favoriteBooks: ['Isaiah', 'Acts', 'Revelation'],
        readingGoals: {
          chaptersPerWeek: 10,
          currentStreak: 156,
          longestStreak: 200,
          totalChaptersRead: 2103,
          plansCompleted: 8
        },
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now() - 730 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now()
      }
    }

    friends.forEach(friend => {
      if (mockProfiles[friend.userId]) {
        profiles.set(friend.userId, mockProfiles[friend.userId])
      }
    })

    setFriendProfiles(profiles)
  }

  const handleAcceptRequest = async (requestId: string) => {
    const user = await window.spark.user()
    const request = friendRequests.find(r => r.id === requestId)
    if (!request) return

    setFriendRequests((current = []) =>
      current.map(r =>
        r.id === requestId
          ? { ...r, status: 'accepted' as const, respondedAt: Date.now() }
          : r
      )
    )

    const newFriend: UserConnection = {
      userId: request.fromUserId,
      userName: request.fromUserName,
      userAvatar: request.fromUserAvatar,
      connectedAt: Date.now(),
      lastActivityAt: Date.now(),
      mutualFriends: 0
    }

    const currentFriends = await window.spark.kv.get<UserConnection[]>('user-friends') || []
    await window.spark.kv.set('user-friends', [...currentFriends, newFriend])

    toast.success(`You are now friends with ${request.fromUserName}!`)
  }

  const handleRejectRequest = async (requestId: string) => {
    setFriendRequests((current = []) =>
      current.map(r =>
        r.id === requestId
          ? { ...r, status: 'rejected' as const, respondedAt: Date.now() }
          : r
      )
    )
    toast('Friend request declined')
  }

  const handleRemoveFriend = async (userId: string) => {
    const friendsData = await window.spark.kv.get<UserConnection[]>('user-friends')
    const updatedFriends = (friendsData || []).filter(f => f.userId !== userId)
    await window.spark.kv.set('user-friends', updatedFriends)
    toast('Friend removed')
  }

  const toggleExpandFriend = (userId: string) => {
    setExpandedFriends(prev => {
      const newSet = new Set(prev)
      if (newSet.has(userId)) {
        newSet.delete(userId)
      } else {
        newSet.add(userId)
      }
      return newSet
    })
  }

  return (
    <div className="space-y-6">
      {pendingRequests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <UserPlus size={20} weight="duotone" className="text-primary" />
              Friend Requests ({pendingRequests.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingRequests.map((request) => (
              <div key={request.id} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={request.fromUserAvatar} />
                  <AvatarFallback>{request.fromUserName[0]?.toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold">{request.fromUserName}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(request.createdAt, { addSuffix: true })}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleAcceptRequest(request.id)}
                    className="gap-1"
                  >
                    <Check size={16} weight="bold" />
                    Accept
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRejectRequest(request.id)}
                  >
                    <X size={16} weight="bold" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Users size={20} weight="duotone" className="text-primary" />
            My Friends ({friends.length})
          </CardTitle>
          <div className="relative mt-3">
            <MagnifyingGlass
              size={18}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              weight="bold"
            />
            <Input
              placeholder="Search friends..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardHeader>
        <CardContent>
          {filteredFriends.length === 0 ? (
            <div className="text-center py-8">
              <Users size={48} weight="duotone" className="text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">
                {searchQuery ? 'No friends found' : 'No friends yet'}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Search for friends to connect with!
              </p>
            </div>
          ) : (
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-2">
                {filteredFriends.map((friend, index) => {
                  const profile = friendProfiles.get(friend.userId)
                  const isExpanded = expandedFriends.has(friend.userId)
                  
                  return (
                    <div key={friend.userId}>
                      {index > 0 && <Separator className="my-2" />}
                      <Collapsible
                        open={isExpanded}
                        onOpenChange={() => toggleExpandFriend(friend.userId)}
                      >
                        <div className="p-3 rounded-lg hover:bg-muted/30 transition-colors">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-12 w-12">
                              <AvatarImage src={friend.userAvatar} />
                              <AvatarFallback>{friend.userName[0]?.toUpperCase()}</AvatarFallback>
                            </Avatar>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <p className="font-semibold">{friend.userName}</p>
                                {profile?.denomination && (
                                  <Badge variant="secondary" className="text-xs">
                                    {profile.denomination}
                                  </Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-2 flex-wrap mt-1">
                                <p className="text-xs text-muted-foreground">
                                  Active {formatDistanceToNow(friend.lastActivityAt, { addSuffix: true })}
                                </p>
                                {friend.mutualFriends > 0 && (
                                  <Badge variant="secondary" className="text-xs">
                                    {friend.mutualFriends} mutual
                                  </Badge>
                                )}
                              </div>
                              {profile && (
                                <div className="flex gap-3 mt-2">
                                  <div className="flex items-center gap-1">
                                    <Fire size={14} weight="fill" className="text-orange-500" />
                                    <span className="text-xs font-semibold text-primary">
                                      {profile.readingGoals.currentStreak}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <BookOpen size={14} weight="duotone" className="text-primary" />
                                    <span className="text-xs text-muted-foreground">
                                      {profile.readingGoals.totalChaptersRead} chapters
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Trophy size={14} weight="duotone" className="text-accent" />
                                    <span className="text-xs text-muted-foreground">
                                      {profile.readingGoals.plansCompleted} plans
                                    </span>
                                  </div>
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-1">
                              <CollapsibleTrigger asChild>
                                <Button size="sm" variant="ghost" className="h-8 px-2">
                                  <TrendUp size={16} weight="bold" className="text-primary" />
                                  <span className="ml-1 text-xs">Stats</span>
                                </Button>
                              </CollapsibleTrigger>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                                    <DotsThree size={20} weight="bold" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem onClick={() => onViewJourney(friend.userId)}>
                                    View Full Journey
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    className="text-destructive"
                                    onClick={() => handleRemoveFriend(friend.userId)}
                                  >
                                    Remove Friend
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>

                          {profile && (
                            <CollapsibleContent className="mt-3">
                              <div className="p-4 bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg border space-y-4">
                                <div className="grid grid-cols-3 gap-3">
                                  <div className="text-center p-3 bg-background/50 rounded-lg">
                                    <Fire size={24} weight="fill" className="text-orange-500 mx-auto mb-1" />
                                    <p className="text-xl font-bold text-primary">
                                      {profile.readingGoals.currentStreak}
                                    </p>
                                    <p className="text-xs text-muted-foreground">Day Streak</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                      Best: {profile.readingGoals.longestStreak}
                                    </p>
                                  </div>
                                  <div className="text-center p-3 bg-background/50 rounded-lg">
                                    <BookOpen size={24} weight="duotone" className="text-primary mx-auto mb-1" />
                                    <p className="text-xl font-bold text-primary">
                                      {profile.readingGoals.totalChaptersRead}
                                    </p>
                                    <p className="text-xs text-muted-foreground">Chapters</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                      ~{profile.readingGoals.chaptersPerWeek}/week
                                    </p>
                                  </div>
                                  <div className="text-center p-3 bg-background/50 rounded-lg">
                                    <Trophy size={24} weight="duotone" className="text-accent mx-auto mb-1" />
                                    <p className="text-xl font-bold text-primary">
                                      {profile.readingGoals.plansCompleted}
                                    </p>
                                    <p className="text-xs text-muted-foreground">Plans Done</p>
                                  </div>
                                </div>

                                {profile.favoriteBooks.length > 0 && (
                                  <div>
                                    <p className="text-xs font-semibold text-muted-foreground mb-2">
                                      Favorite Books
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                      {profile.favoriteBooks.map((book) => (
                                        <Badge key={book} variant="outline" className="text-xs">
                                          {book}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="w-full gap-2"
                                  onClick={() => onViewJourney(friend.userId)}
                                >
                                  <CalendarCheck size={16} weight="duotone" />
                                  View Full Reading Journey
                                </Button>
                              </div>
                            </CollapsibleContent>
                          )}
                        </div>
                      </Collapsible>
                    </div>
                  )
                })}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
