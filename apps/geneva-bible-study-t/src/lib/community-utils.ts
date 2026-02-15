import type { UserActivity, CommunityProfile } from './types'

export async function trackUserActivity(
  type: UserActivity['type'],
  data: UserActivity['data'],
  visibility: UserActivity['visibility'] = 'friends'
): Promise<void> {
  const user = await window.spark.user()
  
  const activity: UserActivity = {
    id: `activity-${Date.now()}`,
    userId: user?.id?.toString() || 'anonymous',
    userName: user?.login || 'Reader',
    userAvatar: user?.avatarUrl,
    type,
    timestamp: Date.now(),
    data,
    visibility
  }

  const activities = await window.spark.kv.get<UserActivity[]>('user-activities') || []
  await window.spark.kv.set('user-activities', [activity, ...activities.slice(0, 99)])

  await updateReadingGoals(type, data)
}

async function updateReadingGoals(type: UserActivity['type'], data: UserActivity['data']): Promise<void> {
  const profile = await window.spark.kv.get<CommunityProfile>('community-profile')
  if (!profile) return

  const updatedProfile = { ...profile }

  if (type === 'chapter-read') {
    updatedProfile.readingGoals.totalChaptersRead += 1
  }

  if (type === 'plan-completed') {
    updatedProfile.readingGoals.plansCompleted += 1
  }

  if (type === 'streak-milestone' && data.streakDays) {
    updatedProfile.readingGoals.currentStreak = data.streakDays
    if (data.streakDays > updatedProfile.readingGoals.longestStreak) {
      updatedProfile.readingGoals.longestStreak = data.streakDays
    }
  }

  updatedProfile.updatedAt = Date.now()
  await window.spark.kv.set('community-profile', updatedProfile)
}

export async function calculateStreak(): Promise<number> {
  const activities = await window.spark.kv.get<UserActivity[]>('user-activities') || []
  const readActivities = activities.filter(
    a => a.type === 'chapter-read' || a.type === 'verse-shared'
  )

  if (readActivities.length === 0) return 0

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayTime = today.getTime()

  let streak = 0
  let currentDay = todayTime

  const dayHasActivity = (dayTimestamp: number): boolean => {
    const dayStart = dayTimestamp
    const dayEnd = dayTimestamp + 24 * 60 * 60 * 1000

    return readActivities.some(
      activity => activity.timestamp >= dayStart && activity.timestamp < dayEnd
    )
  }

  while (dayHasActivity(currentDay)) {
    streak++
    currentDay -= 24 * 60 * 60 * 1000
  }

  return streak
}

export async function updateCurrentStreak(): Promise<void> {
  const streak = await calculateStreak()
  const profile = await window.spark.kv.get<CommunityProfile>('community-profile')
  
  if (!profile) return

  if (streak !== profile.readingGoals.currentStreak) {
    const updatedProfile = {
      ...profile,
      readingGoals: {
        ...profile.readingGoals,
        currentStreak: streak,
        longestStreak: Math.max(streak, profile.readingGoals.longestStreak)
      },
      updatedAt: Date.now()
    }
    await window.spark.kv.set('community-profile', updatedProfile)

    if (streak > 0 && (streak % 7 === 0 || streak % 30 === 0 || streak % 100 === 0)) {
      await trackUserActivity('streak-milestone', { streakDays: streak }, 'friends')
    }
  }
}

export async function getFriendsActivityFeed(): Promise<UserActivity[]> {
  const friends = await window.spark.kv.get<any[]>('user-friends') || []
  const friendIds = friends.map(f => f.userId)
  
  const allActivities = await window.spark.kv.get<UserActivity[]>('user-activities') || []
  
  return allActivities
    .filter(activity => 
      (friendIds.includes(activity.userId) || activity.visibility === 'public') &&
      activity.visibility !== 'private'
    )
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 50)
}
