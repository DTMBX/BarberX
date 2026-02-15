import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Trophy, Fire, BookOpen, CalendarCheck, TrendUp, Medal } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { UserConnection, CommunityProfile } from '@/lib/types'

interface FriendsLeaderboardProps {
  onViewJourney: (userId: string) => void
}

interface LeaderboardEntry {
  userId: string
  userName: string
  userAvatar?: string
  value: number
  rank: number
}

export default function FriendsLeaderboard({ onViewJourney }: FriendsLeaderboardProps) {
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [friendProfiles, setFriendProfiles] = useState<Map<string, CommunityProfile>>(new Map())
  const [currentUser, setCurrentUser] = useState<{ id: string; login: string; avatarUrl?: string } | null>(null)

  useEffect(() => {
    loadData()
  }, [friends])

  const loadData = async () => {
    const user = await window.spark.user()
    setCurrentUser({
      id: user?.id?.toString() || 'anonymous',
      login: user?.login || 'You',
      avatarUrl: user?.avatarUrl
    })

    const profiles = new Map<string, CommunityProfile>()
    
    const mockProfiles: Record<string, CommunityProfile> = {
      'user-1': {
        userId: 'user-1',
        userName: 'Sarah Johnson',
        userAvatar: undefined,
        readingGoals: {
          chaptersPerWeek: 7,
          currentStreak: 45,
          longestStreak: 120,
          totalChaptersRead: 892,
          plansCompleted: 3
        },
        favoriteBooks: [],
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now(),
        updatedAt: Date.now()
      },
      'user-2': {
        userId: 'user-2',
        userName: 'Michael Chen',
        userAvatar: undefined,
        readingGoals: {
          chaptersPerWeek: 14,
          currentStreak: 89,
          longestStreak: 180,
          totalChaptersRead: 1245,
          plansCompleted: 5
        },
        favoriteBooks: [],
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now(),
        updatedAt: Date.now()
      },
      'user-3': {
        userId: 'user-3',
        userName: 'Emily Rodriguez',
        userAvatar: undefined,
        readingGoals: {
          chaptersPerWeek: 5,
          currentStreak: 21,
          longestStreak: 65,
          totalChaptersRead: 456,
          plansCompleted: 2
        },
        favoriteBooks: [],
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: false,
          allowFriendRequests: true
        },
        createdAt: Date.now(),
        updatedAt: Date.now()
      },
      'user-4': {
        userId: 'user-4',
        userName: 'David Thompson',
        userAvatar: undefined,
        readingGoals: {
          chaptersPerWeek: 10,
          currentStreak: 156,
          longestStreak: 200,
          totalChaptersRead: 2103,
          plansCompleted: 8
        },
        favoriteBooks: [],
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now(),
        updatedAt: Date.now()
      }
    }

    friends.forEach(friend => {
      if (mockProfiles[friend.userId]) {
        profiles.set(friend.userId, mockProfiles[friend.userId])
      }
    })

    const currentUserProfile: CommunityProfile = {
      userId: user?.id?.toString() || 'anonymous',
      userName: user?.login || 'You',
      userAvatar: user?.avatarUrl,
      readingGoals: {
        chaptersPerWeek: 8,
        currentStreak: 32,
        longestStreak: 75,
        totalChaptersRead: 567,
        plansCompleted: 2
      },
      favoriteBooks: [],
      privacy: {
        profileVisible: true,
        showReadingProgress: true,
        showFriendsList: true,
        allowFriendRequests: true
      },
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    profiles.set(currentUserProfile.userId, currentUserProfile)

    setFriendProfiles(profiles)
  }

  const createLeaderboard = (metric: 'currentStreak' | 'totalChaptersRead' | 'plansCompleted' | 'longestStreak'): LeaderboardEntry[] => {
    const entries: LeaderboardEntry[] = []
    
    friendProfiles.forEach((profile) => {
      entries.push({
        userId: profile.userId,
        userName: profile.userName,
        userAvatar: profile.userAvatar,
        value: profile.readingGoals[metric],
        rank: 0
      })
    })

    entries.sort((a, b) => b.value - a.value)
    entries.forEach((entry, index) => {
      entry.rank = index + 1
    })

    return entries
  }

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Medal size={24} weight="fill" className="text-yellow-500" />
    if (rank === 2) return <Medal size={24} weight="fill" className="text-gray-400" />
    if (rank === 3) return <Medal size={24} weight="fill" className="text-amber-600" />
    return <span className="text-sm font-bold text-muted-foreground w-6 text-center">#{rank}</span>
  }

  const streakLeaderboard = createLeaderboard('currentStreak')
  const chaptersLeaderboard = createLeaderboard('totalChaptersRead')
  const plansLeaderboard = createLeaderboard('plansCompleted')
  const bestStreakLeaderboard = createLeaderboard('longestStreak')

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Trophy size={20} weight="duotone" className="text-primary" />
          Friends Leaderboard
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          See how you compare with your friends
        </p>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="streak" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="streak" className="text-xs">
              <Fire size={14} weight="fill" className="mr-1" />
              Streak
            </TabsTrigger>
            <TabsTrigger value="chapters" className="text-xs">
              <BookOpen size={14} weight="duotone" className="mr-1" />
              Chapters
            </TabsTrigger>
            <TabsTrigger value="plans" className="text-xs">
              <CalendarCheck size={14} weight="duotone" className="mr-1" />
              Plans
            </TabsTrigger>
            <TabsTrigger value="best" className="text-xs">
              <TrendUp size={14} weight="bold" className="mr-1" />
              Best
            </TabsTrigger>
          </TabsList>

          <TabsContent value="streak" className="mt-4">
            <ScrollArea className="h-[400px]">
              <LeaderboardList
                entries={streakLeaderboard}
                getRankIcon={getRankIcon}
                formatValue={(val) => `${val} days`}
                currentUserId={currentUser?.id}
                onViewJourney={onViewJourney}
              />
            </ScrollArea>
          </TabsContent>

          <TabsContent value="chapters" className="mt-4">
            <ScrollArea className="h-[400px]">
              <LeaderboardList
                entries={chaptersLeaderboard}
                getRankIcon={getRankIcon}
                formatValue={(val) => `${val} chapters`}
                currentUserId={currentUser?.id}
                onViewJourney={onViewJourney}
              />
            </ScrollArea>
          </TabsContent>

          <TabsContent value="plans" className="mt-4">
            <ScrollArea className="h-[400px]">
              <LeaderboardList
                entries={plansLeaderboard}
                getRankIcon={getRankIcon}
                formatValue={(val) => `${val} completed`}
                currentUserId={currentUser?.id}
                onViewJourney={onViewJourney}
              />
            </ScrollArea>
          </TabsContent>

          <TabsContent value="best" className="mt-4">
            <ScrollArea className="h-[400px]">
              <LeaderboardList
                entries={bestStreakLeaderboard}
                getRankIcon={getRankIcon}
                formatValue={(val) => `${val} days`}
                currentUserId={currentUser?.id}
                onViewJourney={onViewJourney}
              />
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

interface LeaderboardListProps {
  entries: LeaderboardEntry[]
  getRankIcon: (rank: number) => React.ReactNode
  formatValue: (value: number) => string
  currentUserId?: string
  onViewJourney: (userId: string) => void
}

function LeaderboardList({ entries, getRankIcon, formatValue, currentUserId, onViewJourney }: LeaderboardListProps) {
  return (
    <div className="space-y-2">
      {entries.map((entry) => {
        const isCurrentUser = entry.userId === currentUserId
        
        return (
          <button
            key={entry.userId}
            onClick={() => !isCurrentUser && onViewJourney(entry.userId)}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
              isCurrentUser
                ? 'bg-primary/10 border-2 border-primary/30'
                : 'hover:bg-muted/50'
            }`}
          >
            <div className="flex items-center justify-center w-8">
              {getRankIcon(entry.rank)}
            </div>
            <Avatar className="h-10 w-10">
              <AvatarImage src={entry.userAvatar} />
              <AvatarFallback>{entry.userName[0]?.toUpperCase()}</AvatarFallback>
            </Avatar>
            <div className="flex-1 text-left">
              <div className="flex items-center gap-2">
                <p className={`font-semibold ${isCurrentUser ? 'text-primary' : ''}`}>
                  {entry.userName}
                </p>
                {isCurrentUser && (
                  <Badge variant="secondary" className="text-xs">You</Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{formatValue(entry.value)}</p>
            </div>
            {entry.rank === 1 && (
              <Trophy size={20} weight="fill" className="text-yellow-500" />
            )}
          </button>
        )
      })}
    </div>
  )
}
