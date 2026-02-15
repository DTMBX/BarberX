import type { FriendRequest, UserConnection } from './types'

export async function seedDemoFriendRequests() {
  const existingRequests = await window.spark.kv.get<FriendRequest[]>('friend-requests')
  
  if (!existingRequests || existingRequests.length === 0) {
    const demoRequests: FriendRequest[] = [
      {
        id: `req-${Date.now()}-1`,
        fromUserId: 'user-1',
        fromUserName: 'Sarah Johnson',
        fromUserAvatar: undefined,
        toUserId: 'current-user',
        status: 'pending',
        createdAt: Date.now() - 2 * 60 * 60 * 1000
      },
      {
        id: `req-${Date.now()}-2`,
        fromUserId: 'user-2',
        fromUserName: 'Michael Chen',
        fromUserAvatar: undefined,
        toUserId: 'current-user',
        status: 'pending',
        createdAt: Date.now() - 24 * 60 * 60 * 1000
      }
    ]
    
    await window.spark.kv.set('friend-requests', demoRequests)
  }
}

export async function seedDemoFriends() {
  const existingFriends = await window.spark.kv.get<UserConnection[]>('user-friends')
  
  if (!existingFriends || existingFriends.length === 0) {
    const demoFriends: UserConnection[] = [
      {
        userId: 'user-3',
        userName: 'Emily Rodriguez',
        userAvatar: undefined,
        connectedAt: Date.now() - 30 * 24 * 60 * 60 * 1000,
        lastActivityAt: Date.now() - 6 * 60 * 60 * 1000,
        mutualFriends: 2
      },
      {
        userId: 'user-4',
        userName: 'David Thompson',
        userAvatar: undefined,
        connectedAt: Date.now() - 60 * 24 * 60 * 60 * 1000,
        lastActivityAt: Date.now() - 3 * 60 * 60 * 1000,
        mutualFriends: 1
      }
    ]
    
    await window.spark.kv.set('user-friends', demoFriends)
  }
}
