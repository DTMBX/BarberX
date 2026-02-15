import { useEffect, useState } from 'react'
import { useKV } from '@github/spark/hooks'
import {
  BookOpen,
  CalendarCheck,
  Fire,
  Trophy,
  Heart,
  ChatCircle,
  ChartLine,
  BookBookmark
} from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import type { ReadingJourney, CommunityProfile, UserActivity } from '@/lib/types'
import { formatDistanceToNow, format } from 'date-fns'

interface ReadingJourneyViewProps {
  userId: string
  onBack: () => void
}

export default function ReadingJourneyView({ userId, onBack }: ReadingJourneyViewProps) {
  const [journey, setJourney] = useState<ReadingJourney | null>(null)
  const [profile, setProfile] = useState<CommunityProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadJourneyData()
  }, [userId])

  const loadJourneyData = async () => {
    setLoading(true)

    setTimeout(() => {
      const mockProfile: CommunityProfile = {
        userId,
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
      }

      const mockJourney: ReadingJourney = {
        userId,
        currentBook: 'Romans',
        currentChapter: 8,
        activeReadingPlans: [
          {
            planId: 'plan-1',
            planName: 'New Testament in 90 Days',
            progress: 62,
            currentDay: 56,
            totalDays: 90
          },
          {
            planId: 'plan-2',
            planName: 'Book of Psalms',
            progress: 38,
            currentDay: 57,
            totalDays: 150
          }
        ],
        recentVerses: [
          {
            verseId: 'rom-8-28',
            bookName: 'Romans',
            reference: 'Romans 8:28',
            timestamp: Date.now() - 2 * 60 * 60 * 1000
          },
          {
            verseId: 'john-3-16',
            bookName: 'John',
            reference: 'John 3:16',
            timestamp: Date.now() - 24 * 60 * 60 * 1000
          },
          {
            verseId: 'psalm-23-1',
            bookName: 'Psalms',
            reference: 'Psalm 23:1',
            timestamp: Date.now() - 2 * 24 * 60 * 60 * 1000
          }
        ],
        recentActivity: [
          {
            id: 'act-1',
            userId,
            userName: 'Sarah Johnson',
            type: 'chapter-read',
            timestamp: Date.now() - 2 * 60 * 60 * 1000,
            data: { bookName: 'Romans', chapterNumber: 8 },
            visibility: 'friends'
          },
          {
            id: 'act-2',
            userId,
            userName: 'Sarah Johnson',
            type: 'verse-shared',
            timestamp: Date.now() - 24 * 60 * 60 * 1000,
            data: { bookName: 'John', chapterNumber: 3, verseNumber: 16 },
            visibility: 'friends'
          },
          {
            id: 'act-3',
            userId,
            userName: 'Sarah Johnson',
            type: 'streak-milestone',
            timestamp: Date.now() - 3 * 24 * 60 * 60 * 1000,
            data: { streakDays: 45 },
            visibility: 'friends'
          }
        ],
        milestones: [
          {
            id: 'mile-1',
            type: 'streak',
            title: '45 Day Reading Streak',
            achievedAt: Date.now() - 3 * 24 * 60 * 60 * 1000,
            value: 45
          },
          {
            id: 'mile-2',
            type: 'chapters',
            title: '500 Chapters Read',
            achievedAt: Date.now() - 30 * 24 * 60 * 60 * 1000,
            value: 500
          },
          {
            id: 'mile-3',
            type: 'plan-complete',
            title: 'Completed Gospel Journey',
            achievedAt: Date.now() - 60 * 24 * 60 * 60 * 1000,
            value: 1
          }
        ]
      }

      setProfile(mockProfile)
      setJourney(mockJourney)
      setLoading(false)
    }, 500)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <BookOpen size={48} weight="duotone" className="text-primary animate-pulse mx-auto mb-3" />
          <p className="text-muted-foreground">Loading journey...</p>
        </div>
      </div>
    )
  }

  if (!profile || !journey) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-muted-foreground">Journey not found</p>
          <Button onClick={onBack} className="mt-4">Go Back</Button>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        <div>
          <Button variant="ghost" onClick={onBack} className="mb-4">
            ← Back to Community
          </Button>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-4">
              <Avatar className="h-20 w-20">
                <AvatarImage src={profile.userAvatar} />
                <AvatarFallback className="text-2xl">{profile.userName[0]?.toUpperCase()}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-2xl font-bold">{profile.userName}</h2>
                  {profile.denomination && (
                    <Badge variant="secondary">{profile.denomination}</Badge>
                  )}
                </div>
                {profile.location && (
                  <p className="text-sm text-muted-foreground mb-2">{profile.location}</p>
                )}
                {profile.bio && (
                  <p className="text-sm">{profile.bio}</p>
                )}
                <div className="flex flex-wrap gap-2 mt-3">
                  {profile.favoriteBooks.map((book) => (
                    <Badge key={book} variant="outline" className="text-xs">
                      <BookBookmark size={12} weight="duotone" className="mr-1" />
                      {book}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6 text-center">
              <Fire size={32} weight="fill" className="text-orange-500 mx-auto mb-2" />
              <p className="text-3xl font-bold text-primary">{profile.readingGoals.currentStreak}</p>
              <p className="text-sm text-muted-foreground">Day Streak</p>
              <p className="text-xs text-muted-foreground mt-1">
                Best: {profile.readingGoals.longestStreak}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <BookOpen size={32} weight="duotone" className="text-primary mx-auto mb-2" />
              <p className="text-3xl font-bold text-primary">{profile.readingGoals.totalChaptersRead}</p>
              <p className="text-sm text-muted-foreground">Chapters Read</p>
              <p className="text-xs text-muted-foreground mt-1">
                ~{profile.readingGoals.chaptersPerWeek}/week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <Trophy size={32} weight="duotone" className="text-accent mx-auto mb-2" />
              <p className="text-3xl font-bold text-primary">{profile.readingGoals.plansCompleted}</p>
              <p className="text-sm text-muted-foreground">Plans Done</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <ChartLine size={32} weight="duotone" className="text-primary mx-auto mb-2" />
              <p className="text-3xl font-bold text-primary">{journey.activeReadingPlans.length}</p>
              <p className="text-sm text-muted-foreground">Active Plans</p>
            </CardContent>
          </Card>
        </div>

        {journey.currentBook && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen size={20} weight="duotone" className="text-primary" />
                Currently Reading
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-primary/10 rounded-lg">
                <p className="text-2xl font-bold">{journey.currentBook}</p>
                <p className="text-muted-foreground">Chapter {journey.currentChapter}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {journey.activeReadingPlans.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CalendarCheck size={20} weight="duotone" className="text-primary" />
                Active Reading Plans
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {journey.activeReadingPlans.map((plan) => (
                <div key={plan.planId} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{plan.planName}</p>
                      <p className="text-xs text-muted-foreground">
                        Day {plan.currentDay} of {plan.totalDays}
                      </p>
                    </div>
                    <Badge variant="secondary">{plan.progress}%</Badge>
                  </div>
                  <Progress value={plan.progress} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {journey.milestones.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy size={20} weight="duotone" className="text-primary" />
                Recent Milestones
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {journey.milestones.map((milestone, index) => (
                <div key={milestone.id}>
                  {index > 0 && <Separator className="my-3" />}
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent/20 rounded-lg">
                      {milestone.type === 'streak' && <Fire size={24} weight="fill" className="text-orange-500" />}
                      {milestone.type === 'chapters' && <BookOpen size={24} weight="duotone" className="text-primary" />}
                      {milestone.type === 'plan-complete' && <Trophy size={24} weight="fill" className="text-accent" />}
                      {milestone.type === 'year-complete' && <CalendarCheck size={24} weight="fill" className="text-primary" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">{milestone.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {format(milestone.achievedAt, 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookBookmark size={20} weight="duotone" className="text-primary" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {journey.recentActivity.map((activity, index) => (
              <div key={activity.id}>
                {index > 0 && <Separator className="my-3" />}
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {activity.type === 'chapter-read' && <BookOpen size={20} weight="duotone" className="text-primary" />}
                    {activity.type === 'verse-shared' && <Heart size={20} weight="fill" className="text-red-500" />}
                    {activity.type === 'streak-milestone' && <Fire size={20} weight="fill" className="text-orange-500" />}
                    {activity.type === 'milestone-achieved' && <Trophy size={20} weight="fill" className="text-accent" />}
                    {activity.type === 'plan-completed' && <CalendarCheck size={20} weight="fill" className="text-primary" />}
                    {activity.type === 'note-created' && <ChatCircle size={20} weight="duotone" className="text-primary" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">
                      {activity.type === 'chapter-read' && `Read ${activity.data.bookName} ${activity.data.chapterNumber}`}
                      {activity.type === 'verse-shared' && `Shared ${activity.data.bookName} ${activity.data.chapterNumber}:${activity.data.verseNumber}`}
                      {activity.type === 'streak-milestone' && `Reached ${activity.data.streakDays} day streak!`}
                      {activity.type === 'milestone-achieved' && `Achieved a milestone`}
                      {activity.type === 'plan-completed' && `Completed ${activity.data.planName}`}
                      {activity.type === 'note-created' && `Created a study note`}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </ScrollArea>
  )
}
