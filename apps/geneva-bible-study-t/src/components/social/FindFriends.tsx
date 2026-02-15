import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { MagnifyingGlass, UserPlus, Users, CheckCircle } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import type { CommunityProfile, FriendRequest, UserConnection } from '@/lib/types'
import { toast } from 'sonner'

interface FindFriendsProps {
  onViewJourney: (userId: string) => void
}

export default function FindFriends({ onViewJourney }: FindFriendsProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<CommunityProfile[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [friendRequests = [], setFriendRequests] = useKV<FriendRequest[]>('friend-requests', [])
  const [sentRequests, setSentRequests] = useState<string[]>([])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)

    setTimeout(async () => {
      const user = await window.spark.user()
      const currentUserId = user?.id?.toString() || 'anonymous'

      const mockProfiles: CommunityProfile[] = [
        {
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
        {
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
        {
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
        {
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
      ]

      const filtered = mockProfiles.filter(
        profile =>
          profile.userId !== currentUserId &&
          (profile.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
            profile.location?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            profile.denomination?.toLowerCase().includes(searchQuery.toLowerCase()))
      )

      setSearchResults(filtered)
      setIsSearching(false)
    }, 500)
  }

  const handleSendRequest = async (targetProfile: CommunityProfile) => {
    const user = await window.spark.user()

    const newRequest: FriendRequest = {
      id: `req-${Date.now()}`,
      fromUserId: user?.id?.toString() || 'anonymous',
      fromUserName: user?.login || 'Reader',
      fromUserAvatar: user?.avatarUrl,
      toUserId: targetProfile.userId,
      status: 'pending',
      createdAt: Date.now()
    }

    setFriendRequests((current = []) => [...current, newRequest])
    setSentRequests((current) => [...current, targetProfile.userId])
    toast.success(`Friend request sent to ${targetProfile.userName}`)
  }

  const isFriend = (userId: string) => friends.some(f => f.userId === userId)
  const hasPendingRequest = (userId: string) => 
    sentRequests.includes(userId) ||
    friendRequests.some(r => r.toUserId === userId && r.status === 'pending')

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <MagnifyingGlass size={20} weight="duotone" className="text-primary" />
            Find Friends
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Connect with other believers on their Bible reading journey
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search by name, location, or denomination..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={isSearching}>
              Search
            </Button>
          </div>

          {searchResults.length > 0 && (
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-3">
                {searchResults.map((profile, index) => (
                  <div key={profile.userId}>
                    {index > 0 && <Separator className="my-3" />}
                    <div className="p-4 bg-muted/30 rounded-lg space-y-3">
                      <div className="flex items-start gap-3">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={profile.userAvatar} />
                          <AvatarFallback>{profile.userName[0]?.toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <p className="font-semibold text-lg">{profile.userName}</p>
                            {profile.denomination && (
                              <Badge variant="secondary" className="text-xs">
                                {profile.denomination}
                              </Badge>
                            )}
                          </div>
                          {profile.location && (
                            <p className="text-sm text-muted-foreground">{profile.location}</p>
                          )}
                          {profile.bio && (
                            <p className="text-sm mt-2">{profile.bio}</p>
                          )}
                        </div>
                        <div>
                          {isFriend(profile.userId) ? (
                            <Button size="sm" variant="secondary" disabled className="gap-1">
                              <CheckCircle size={16} weight="fill" />
                              Friends
                            </Button>
                          ) : hasPendingRequest(profile.userId) ? (
                            <Button size="sm" variant="secondary" disabled>
                              Request Sent
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleSendRequest(profile)}
                              className="gap-1"
                            >
                              <UserPlus size={16} weight="bold" />
                              Add Friend
                            </Button>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {profile.favoriteBooks.slice(0, 3).map((book) => (
                          <Badge key={book} variant="outline" className="text-xs">
                            {book}
                          </Badge>
                        ))}
                      </div>

                      {profile.privacy.showReadingProgress && (
                        <div className="grid grid-cols-3 gap-3 pt-3 border-t">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-primary">
                              {profile.readingGoals.currentStreak}
                            </p>
                            <p className="text-xs text-muted-foreground">Day Streak</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-primary">
                              {profile.readingGoals.totalChaptersRead}
                            </p>
                            <p className="text-xs text-muted-foreground">Chapters Read</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-primary">
                              {profile.readingGoals.plansCompleted}
                            </p>
                            <p className="text-xs text-muted-foreground">Plans Done</p>
                          </div>
                        </div>
                      )}

                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => onViewJourney(profile.userId)}
                      >
                        View Reading Journey
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}

          {searchResults.length === 0 && searchQuery && !isSearching && (
            <div className="text-center py-8">
              <Users size={48} weight="duotone" className="text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">No users found. Try a different search.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
