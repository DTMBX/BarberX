import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import MessagesList from '@/components/social/MessagesList'
import MessageThread from '@/components/social/MessageThread'
import { ChatCircle } from '@phosphor-icons/react'
import { useIsMobile } from '@/hooks/use-mobile'
import type { UserConnection } from '@/lib/types'

interface MessagesViewProps {
  initialNavigation?: { friendId: string; verseRef?: any } | null
  onClearNavigation?: () => void
}

export default function MessagesView({ initialNavigation, onClearNavigation }: MessagesViewProps) {
  const [selectedConversation, setSelectedConversation] = useState<{
    conversationId: string
    friendId: string
    friendName: string
    friendAvatar?: string
  } | null>(null)
  const isMobile = useIsMobile()
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])

  useEffect(() => {
    if (initialNavigation) {
      const friend = friends.find(f => f.userId === initialNavigation.friendId)
      if (friend) {
        setSelectedConversation({
          conversationId: '',
          friendId: friend.userId,
          friendName: friend.userName,
          friendAvatar: friend.userAvatar
        })
      }
      onClearNavigation?.()
    }
  }, [initialNavigation, friends, onClearNavigation])

  const handleSelectConversation = (
    conversationId: string,
    friendId: string,
    friendName: string,
    friendAvatar?: string
  ) => {
    setSelectedConversation({ conversationId, friendId, friendName, friendAvatar })
  }

  const handleBack = () => {
    setSelectedConversation(null)
  }

  if (isMobile) {
    return (
      <div className="h-full">
        {selectedConversation ? (
          <MessageThread
            conversationId={selectedConversation.conversationId}
            friendId={selectedConversation.friendId}
            friendName={selectedConversation.friendName}
            friendAvatar={selectedConversation.friendAvatar}
            onBack={handleBack}
          />
        ) : (
          <MessagesList onSelectConversation={handleSelectConversation} />
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex bg-background">
      <div className="w-80 border-r">
        <MessagesList onSelectConversation={handleSelectConversation} />
      </div>
      <div className="flex-1">
        {selectedConversation ? (
          <MessageThread
            conversationId={selectedConversation.conversationId}
            friendId={selectedConversation.friendId}
            friendName={selectedConversation.friendName}
            friendAvatar={selectedConversation.friendAvatar}
            onBack={handleBack}
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <ChatCircle size={80} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Select a conversation</h3>
              <p className="text-muted-foreground max-w-sm">
                Choose a friend from the list to start messaging about verses and scripture
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
