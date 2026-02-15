import { useState, useEffect, useRef } from 'react'
import { useKV } from '@github/spark/hooks'
import { ArrowLeft, PaperPlaneTilt, BookOpen, X, Sparkle, Microphone } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import type { Message, Conversation } from '@/lib/types'
import { format, formatDistanceToNow } from 'date-fns'
import VoiceMessageComposer from './VoiceMessageComposer'

interface MessageThreadProps {
  conversationId: string
  friendId: string
  friendName: string
  friendAvatar?: string
  onBack: () => void
}

export default function MessageThread({
  conversationId: initialConversationId,
  friendId,
  friendName,
  friendAvatar,
  onBack
}: MessageThreadProps) {
  const [conversations, setConversations] = useKV<Conversation[]>('conversations', [])
  const [messages, setMessages] = useKV<Message[]>('messages', [])
  const [messageText, setMessageText] = useState('')
  const [showVoiceComposer, setShowVoiceComposer] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [currentUserName, setCurrentUserName] = useState<string>('')
  const [conversationId, setConversationId] = useState(initialConversationId)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
      setCurrentUserName(user?.login || 'Anonymous')
    }
    fetchUser()
  }, [])

  useEffect(() => {
    if (conversationId) {
      markMessagesAsRead()
    }
  }, [conversationId, messages])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const markMessagesAsRead = () => {
    if (!conversationId || !currentUserId || !messages) return

    const updatedMessages = messages.map(msg => {
      if (msg.conversationId === conversationId && msg.toUserId === currentUserId && !msg.readAt) {
        return { ...msg, readAt: Date.now() }
      }
      return msg
    })

    if (JSON.stringify(updatedMessages) !== JSON.stringify(messages)) {
      setMessages(updatedMessages)
    }

    setConversations((currentConversations = []) => {
      return currentConversations.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            unreadCount: {
              ...conv.unreadCount,
              [currentUserId]: 0
            }
          }
        }
        return conv
      })
    })
  }

  const threadMessages = (messages || [])
    .filter(msg => msg.conversationId === conversationId)
    .sort((a, b) => a.createdAt - b.createdAt)

  const handleSendMessage = async () => {
    if (!messageText.trim() || !currentUserId) return

    sendMessage(messageText.trim())
  }

  const sendMessage = (content: string) => {
    if (!content.trim() || !currentUserId) return

    const newMessage: Message = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      conversationId: conversationId || `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      fromUserId: currentUserId,
      toUserId: friendId,
      content: content.trim(),
      createdAt: Date.now()
    }

    if (!conversationId) {
      const newConversation: Conversation = {
        id: newMessage.conversationId,
        participantIds: [currentUserId, friendId],
        participants: [
          {
            userId: currentUserId,
            userName: currentUserName,
          },
          {
            userId: friendId,
            userName: friendName,
            userAvatar: friendAvatar
          }
        ],
        lastMessage: newMessage,
        lastMessageAt: newMessage.createdAt,
        unreadCount: {
          [currentUserId]: 0,
          [friendId]: 1
        },
        createdAt: newMessage.createdAt
      }

      setConversations((current = []) => [...current, newConversation])
      setConversationId(newConversation.id)
    } else {
      setConversations((current = []) => {
        return current.map(conv => {
          if (conv.id === conversationId) {
            return {
              ...conv,
              lastMessage: newMessage,
              lastMessageAt: newMessage.createdAt,
              unreadCount: {
                ...conv.unreadCount,
                [friendId]: (conv.unreadCount[friendId] || 0) + 1
              }
            }
          }
          return conv
        })
      })
    }

    setMessages((current = []) => [...current, newMessage])
    setMessageText('')
  }

  const handleVoiceMessageSend = (text: string) => {
    sendMessage(text)
    setShowVoiceComposer(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const groupMessagesByDate = (messages: Message[]) => {
    const groups: { date: string; messages: Message[] }[] = []
    let currentDate = ''
    let currentGroup: Message[] = []

    messages.forEach((msg) => {
      const msgDate = format(msg.createdAt, 'yyyy-MM-dd')
      if (msgDate !== currentDate) {
        if (currentGroup.length > 0) {
          groups.push({ date: currentDate, messages: currentGroup })
        }
        currentDate = msgDate
        currentGroup = [msg]
      } else {
        currentGroup.push(msg)
      }
    })

    if (currentGroup.length > 0) {
      groups.push({ date: currentDate, messages: currentGroup })
    }

    return groups
  }

  const messageGroups = groupMessagesByDate(threadMessages)

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="p-4 border-b bg-card flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft size={20} />
        </Button>
        <Avatar className="h-10 w-10">
          <AvatarImage src={friendAvatar} />
          <AvatarFallback>{friendName[0]?.toUpperCase()}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <h3 className="font-semibold">{friendName}</h3>
          <p className="text-xs text-muted-foreground">Friend</p>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="max-w-3xl mx-auto space-y-6">
          {messageGroups.length === 0 ? (
            <div className="text-center py-12">
              <ChatBubbleIcon className="text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Start the conversation</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Share a verse, discuss scripture, or just say hello to {friendName}!
              </p>
            </div>
          ) : (
            messageGroups.map((group) => (
              <div key={group.date} className="space-y-3">
                <div className="flex items-center justify-center">
                  <Badge variant="secondary" className="text-xs">
                    {formatDateLabel(group.date)}
                  </Badge>
                </div>
                {group.messages.map((message, index) => {
                  const isOwn = message.fromUserId === currentUserId
                  const showAvatar = index === 0 || group.messages[index - 1].fromUserId !== message.fromUserId

                  return (
                    <div
                      key={message.id}
                      className={`flex gap-2 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      <div className={`w-8 ${showAvatar ? '' : 'invisible'}`}>
                        {!isOwn && (
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={friendAvatar} />
                            <AvatarFallback>{friendName[0]?.toUpperCase()}</AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                      <div className={`flex-1 max-w-[70%] ${isOwn ? 'flex flex-col items-end' : ''}`}>
                        <Card className={`p-3 ${isOwn ? 'bg-primary text-primary-foreground' : 'bg-card'}`}>
                          {message.verseReference && (
                            <div className={`mb-2 pb-2 border-b ${isOwn ? 'border-primary-foreground/20' : 'border-border'}`}>
                              <div className="flex items-center gap-2 mb-1">
                                <BookOpen size={14} weight="duotone" />
                                <p className="text-xs font-semibold">
                                  {message.verseReference.bookName} {message.verseReference.chapterNumber}:
                                  {message.verseReference.verseNumber}
                                  {message.verseReference.verseEndNumber && message.verseReference.verseEndNumber !== message.verseReference.verseNumber && 
                                    `-${message.verseReference.verseEndNumber}`}
                                </p>
                              </div>
                              {message.verseReference.verseText && (
                                <p className={`text-sm italic ${isOwn ? 'opacity-90' : 'text-muted-foreground'}`}>
                                  "{message.verseReference.verseText}"
                                </p>
                              )}
                              {message.verseReference.translation && (
                                <p className={`text-xs mt-1 ${isOwn ? 'opacity-75' : 'text-muted-foreground'}`}>
                                  {message.verseReference.translation.toUpperCase()}
                                </p>
                              )}
                            </div>
                          )}
                          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                          {message.editedAt && (
                            <p className={`text-xs mt-1 ${isOwn ? 'opacity-75' : 'text-muted-foreground'}`}>
                              (edited)
                            </p>
                          )}
                        </Card>
                        <p className="text-xs text-muted-foreground mt-1 px-1">
                          {format(message.createdAt, 'h:mm a')}
                          {isOwn && message.readAt && ' • Read'}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="p-4 border-t bg-card">
        <div className="max-w-3xl mx-auto">
          {showVoiceComposer ? (
            <VoiceMessageComposer
              onSend={handleVoiceMessageSend}
              onCancel={() => setShowVoiceComposer(false)}
              placeholder="Voice transcription will appear here..."
            />
          ) : (
            <>
              <div className="flex gap-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => setShowVoiceComposer(true)}
                        className="h-[60px] w-[60px] flex-shrink-0"
                        aria-label="Send voice message"
                      >
                        <Microphone size={20} weight="duotone" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Send voice message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <Textarea
                  placeholder={`Message ${friendName}...`}
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="min-h-[60px] max-h-[120px] resize-none"
                  rows={2}
                  aria-label="Message input"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!messageText.trim()}
                  size="icon"
                  className="h-[60px] w-[60px] flex-shrink-0"
                  aria-label="Send message"
                >
                  <PaperPlaneTilt size={20} weight="fill" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Press Enter to send, Shift+Enter for new line • Click mic for voice message
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function ChatBubbleIcon({ className }: { className?: string }) {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}

function formatDateLabel(dateStr: string): string {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (format(date, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')) {
    return 'Today'
  } else if (format(date, 'yyyy-MM-dd') === format(yesterday, 'yyyy-MM-dd')) {
    return 'Yesterday'
  } else {
    return format(date, 'MMMM d, yyyy')
  }
}
