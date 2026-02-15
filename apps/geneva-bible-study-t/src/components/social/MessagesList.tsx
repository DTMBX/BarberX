import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { ChatCircle, MagnifyingGlass, PaperPlaneTilt } from '@phosphor-icons/react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import type { Conversation, UserConnection } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'

interface MessagesListProps {
  onSelectConversation: (conversationId: string, friendId: string, friendName: string, friendAvatar?: string) => void
}

export default function MessagesList({ onSelectConversation }: MessagesListProps) {
  const [conversations = []] = useKV<Conversation[]>('conversations', [])
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  const sortedConversations = [...conversations].sort(
    (a, b) => b.lastMessageAt - a.lastMessageAt
  )

  const filteredConversations = sortedConversations.filter((conv) => {
    const otherParticipant = conv.participants.find(p => p.userId !== currentUserId)
    return otherParticipant?.userName.toLowerCase().includes(searchQuery.toLowerCase())
  })

  const friendsWithoutConversation = friends.filter(friend => {
    return !conversations.some(conv =>
      conv.participantIds.includes(friend.userId) && conv.participantIds.includes(currentUserId)
    )
  })

  return (
    <div className="h-full flex flex-col bg-card">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold mb-3 flex items-center gap-2" style={{ fontFamily: 'var(--font-heading)' }}>
          <ChatCircle size={24} weight="duotone" className="text-primary" />
          Messages
        </h2>
        <div className="relative">
          <MagnifyingGlass size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {filteredConversations.length === 0 && searchQuery === '' && friendsWithoutConversation.length === 0 ? (
            <div className="p-8 text-center">
              <ChatCircle size={64} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No messages yet</h3>
              <p className="text-sm text-muted-foreground">
                Start a conversation with a friend to discuss verses and share insights
              </p>
            </div>
          ) : filteredConversations.length === 0 && searchQuery !== '' ? (
            <div className="p-8 text-center">
              <p className="text-sm text-muted-foreground">
                No conversations match "{searchQuery}"
              </p>
            </div>
          ) : (
            <>
              {filteredConversations.map((conversation) => {
                const otherParticipant = conversation.participants.find(p => p.userId !== currentUserId)
                if (!otherParticipant) return null

                const unreadCount = conversation.unreadCount[currentUserId] || 0

                return (
                  <button
                    key={conversation.id}
                    onClick={() => onSelectConversation(
                      conversation.id,
                      otherParticipant.userId,
                      otherParticipant.userName,
                      otherParticipant.userAvatar
                    )}
                    className="w-full p-3 hover:bg-muted rounded-lg transition-colors text-left relative"
                  >
                    <div className="flex items-start gap-3">
                      <div className="relative">
                        <Avatar>
                          <AvatarImage src={otherParticipant.userAvatar} />
                          <AvatarFallback>{otherParticipant.userName[0]?.toUpperCase()}</AvatarFallback>
                        </Avatar>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <p className={`font-semibold ${unreadCount > 0 ? 'text-foreground' : 'text-foreground/80'}`}>
                            {otherParticipant.userName}
                          </p>
                          {conversation.lastMessage && (
                            <p className="text-xs text-muted-foreground">
                              {formatDistanceToNow(conversation.lastMessage.createdAt, { addSuffix: false })}
                            </p>
                          )}
                        </div>
                        {conversation.lastMessage && (
                          <div className="flex items-center gap-2">
                            <p className={`text-sm truncate ${unreadCount > 0 ? 'font-medium text-foreground' : 'text-muted-foreground'}`}>
                              {conversation.lastMessage.fromUserId === currentUserId ? 'You: ' : ''}
                              {conversation.lastMessage.verseReference
                                ? `📖 ${conversation.lastMessage.verseReference.bookName} ${conversation.lastMessage.verseReference.chapterNumber}:${conversation.lastMessage.verseReference.verseNumber}`
                                : conversation.lastMessage.content
                              }
                            </p>
                          </div>
                        )}
                      </div>
                      {unreadCount > 0 && (
                        <Badge className="h-6 min-w-[24px] flex items-center justify-center bg-primary">
                          {unreadCount}
                        </Badge>
                      )}
                    </div>
                  </button>
                )
              })}

              {friendsWithoutConversation.length > 0 && (
                <>
                  {filteredConversations.length > 0 && (
                    <div className="px-3 py-2 mt-4">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Start New Conversation
                      </p>
                    </div>
                  )}
                  {friendsWithoutConversation.map((friend) => (
                    <button
                      key={friend.userId}
                      onClick={() => onSelectConversation(
                        '',
                        friend.userId,
                        friend.userName,
                        friend.userAvatar
                      )}
                      className="w-full p-3 hover:bg-muted rounded-lg transition-colors text-left"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={friend.userAvatar} />
                          <AvatarFallback>{friend.userName[0]?.toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-semibold">{friend.userName}</p>
                          <p className="text-xs text-muted-foreground">
                            Start a conversation
                          </p>
                        </div>
                        <PaperPlaneTilt size={18} className="text-muted-foreground" />
                      </div>
                    </button>
                  ))}
                </>
              )}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
