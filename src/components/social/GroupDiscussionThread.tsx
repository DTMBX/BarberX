import { useState, useEffect, useRef } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ArrowLeft,
  PaperPlaneRight,
  DotsThreeVertical,
  UsersThree,
  Smiley,
  ThumbsUp,
  Heart,
  HandsPraying,
  Fire,
  Check,
  Info,
  SignOut,
  UserPlus,
  Bookmark,
  BookOpen,
  PushPin,
  X,
  PencilSimple,
  Trash,
  Gear,
  ShieldCheck,
  Microphone
} from '@phosphor-icons/react'
import type { GroupDiscussion, GroupMessage } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'
import GroupInfoDialog from './GroupInfoDialog'
import InviteMembersDialog from './InviteMembersDialog'
import GroupAdminSettingsDialog from './GroupAdminSettingsDialog'
import VoiceMessageComposer from './VoiceMessageComposer'
import {
  getUserRole,
  canPostMessages,
  canPinMessages,
  canUnpinMessages,
  canDeleteMessage,
  canEditMessage,
  canInviteMembers,
  canUpdateSettings,
  canReactToMessages,
} from '@/lib/permissions'

interface GroupDiscussionThreadProps {
  groupId: string
  groupName: string
  onBack?: () => void
}

const REACTION_EMOJIS = [
  { icon: ThumbsUp, key: 'thumbsup' },
  { icon: Heart, key: 'heart' },
  { icon: HandsPraying, key: 'pray' },
  { icon: Fire, key: 'fire' },
] as const

export default function GroupDiscussionThread({
  groupId,
  groupName,
  onBack,
}: GroupDiscussionThreadProps) {
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [currentUserName, setCurrentUserName] = useState<string>('')
  const [groups = [], setGroups] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [messages = [], setMessages] = useKV<GroupMessage[]>(`group-messages-${groupId}`, [])
  const [newMessage, setNewMessage] = useState('')
  const [showVoiceComposer, setShowVoiceComposer] = useState(false)
  const [editingMessage, setEditingMessage] = useState<{ id: string; content: string } | null>(null)
  const [deletingMessage, setDeletingMessage] = useState<{ id: string; content: string } | null>(null)
  const [showReactionPicker, setShowReactionPicker] = useState<string | null>(null)
  const [showInfoDialog, setShowInfoDialog] = useState(false)
  const [showInviteDialog, setShowInviteDialog] = useState(false)
  const [showAdminSettings, setShowAdminSettings] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const group = groups.find(g => g.id === groupId)

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
      setCurrentUserName(user?.login || 'Anonymous')
    }
    fetchUser()
  }, [])

  useEffect(() => {
    if (group && currentUserId) {
      setGroups((currentGroups) =>
        (currentGroups || []).map(g =>
          g.id === groupId
            ? {
                ...g,
                unreadCount: {
                  ...g.unreadCount,
                  [currentUserId]: 0
                }
              }
            : g
        )
      )
    }
  }, [groupId, currentUserId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  const handleSendMessage = () => {
    if (!newMessage.trim() || !group) return

    if (!canPost) {
      toast.error('You do not have permission to post messages')
      return
    }

    sendGroupMessage(newMessage.trim())
  }

  const sendGroupMessage = (content: string) => {
    if (!content.trim() || !group) return

    const message: GroupMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      groupId,
      fromUserId: currentUserId,
      fromUserName: currentUserName,
      content: content.trim(),
      createdAt: Date.now(),
      reactions: {}
    }

    setMessages((currentMessages) => [...(currentMessages || []), message])

    setGroups((currentGroups) =>
      (currentGroups || []).map(g =>
        g.id === groupId
          ? {
              ...g,
              lastMessageAt: Date.now(),
              unreadCount: Object.fromEntries(
                g.memberIds
                  .filter(id => id !== currentUserId)
                  .map(id => [id, (g.unreadCount[id] || 0) + 1])
              )
            }
          : g
      )
    )

    setNewMessage('')
  }

  const handleVoiceMessageSend = (text: string) => {
    sendGroupMessage(text)
    setShowVoiceComposer(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const toggleReaction = (messageId: string, reactionKey: string) => {
    if (!canReact) {
      toast.error('You do not have permission to react to messages')
      return
    }

    setMessages((currentMessages) =>
      (currentMessages || []).map(msg => {
        if (msg.id !== messageId) return msg

        const reactions = { ...msg.reactions }
        const userList = reactions[reactionKey] || []

        if (userList.includes(currentUserId)) {
          reactions[reactionKey] = userList.filter(id => id !== currentUserId)
          if (reactions[reactionKey].length === 0) {
            delete reactions[reactionKey]
          }
        } else {
          reactions[reactionKey] = [...userList, currentUserId]
        }

        return { ...msg, reactions }
      })
    )
    setShowReactionPicker(null)
  }

  const handleLeaveGroup = () => {
    if (!group) return

    setGroups((currentGroups) =>
      (currentGroups || []).map(g => {
        if (g.id !== groupId) return g
        
        return {
          ...g,
          memberIds: g.memberIds.filter(id => id !== currentUserId),
          members: g.members.filter(m => m.userId !== currentUserId)
        }
      })
    )

    toast.success('Left the group')
    onBack?.()
  }

  const handlePinMessage = (messageId: string) => {
    if (!group) return

    const isPinned = group.pinnedMessageIds.includes(messageId)

    setGroups((currentGroups) =>
      (currentGroups || []).map(g => {
        if (g.id !== groupId) return g
        
        return {
          ...g,
          pinnedMessageIds: isPinned
            ? g.pinnedMessageIds.filter(id => id !== messageId)
            : [...g.pinnedMessageIds, messageId]
        }
      })
    )

    toast.success(isPinned ? 'Message unpinned' : 'Message pinned')
  }

  const handleEditMessage = (messageId: string, newContent: string) => {
    if (!newContent.trim()) {
      toast.error('Message cannot be empty')
      return
    }

    setMessages((currentMessages) =>
      (currentMessages || []).map(msg =>
        msg.id === messageId
          ? { ...msg, content: newContent.trim(), editedAt: Date.now() }
          : msg
      )
    )

    setEditingMessage(null)
    toast.success('Message updated')
  }

  const handleDeleteMessage = (messageId: string) => {
    setMessages((currentMessages) =>
      (currentMessages || []).map(msg =>
        msg.id === messageId
          ? { ...msg, deletedAt: Date.now(), deletedBy: currentUserId }
          : msg
      )
    )

    setGroups((currentGroups) =>
      (currentGroups || []).map(g => {
        if (g.id !== groupId) return g
        
        return {
          ...g,
          pinnedMessageIds: g.pinnedMessageIds.filter(id => id !== messageId)
        }
      })
    )

    setDeletingMessage(null)
    toast.success('Message deleted')
  }

  const getInitials = (name?: string) => {
    if (!name) return '??'
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getReactionIcon = (key: string) => {
    const emoji = REACTION_EMOJIS.find(e => e.key === key)
    return emoji ? emoji.icon : ThumbsUp
  }

  if (!group) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-muted-foreground">Group not found</p>
      </div>
    )
  }

  const userRole = getUserRole(group, currentUserId)
  const isAdmin = userRole === 'admin'
  const canPin = canPinMessages(userRole)
  const canUnpin = canUnpinMessages(userRole)
  const canPost = canPostMessages(userRole, group)
  const canInvite = canInviteMembers(userRole, group)
  const canManageSettings = canUpdateSettings(userRole)
  const canReact = canReactToMessages(userRole)

  const pinnedMessages = messages.filter(msg => group.pinnedMessageIds.includes(msg.id) && !msg.deletedAt)
  const regularMessages = messages.filter(msg => !group.pinnedMessageIds.includes(msg.id) && !msg.deletedAt)
  
  const newPinnedCount = pinnedMessages.filter(msg => {
    const lastRead = group.unreadCount[currentUserId] || 0
    return msg.createdAt > (group.lastMessageAt - lastRead)
  }).length

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b bg-card p-4">
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="icon" onClick={onBack}>
              <ArrowLeft size={20} weight="bold" />
            </Button>
          )}
          
          <Avatar className="h-10 w-10 bg-primary/10">
            <AvatarFallback className="text-primary font-semibold">
              {getInitials(group.name)}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 min-w-0">
            <h2 className="font-semibold truncate">{group.name}</h2>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <UsersThree size={14} weight="fill" />
              {group.memberIds.length} members
            </p>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <DotsThreeVertical size={20} weight="bold" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setShowInfoDialog(true)}>
                <Info size={18} weight="fill" className="mr-2" />
                Group Info
              </DropdownMenuItem>
              {canInvite && (
                <DropdownMenuItem onClick={() => setShowInviteDialog(true)}>
                  <UserPlus size={18} weight="fill" className="mr-2" />
                  Invite Members
                </DropdownMenuItem>
              )}
              {canManageSettings && (
                <DropdownMenuItem onClick={() => setShowAdminSettings(true)}>
                  <Gear size={18} weight="fill" className="mr-2" />
                  Admin Settings
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLeaveGroup}
                className="text-destructive focus:text-destructive"
              >
                <SignOut size={18} weight="fill" className="mr-2" />
                Leave Group
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {group.topic && (
          <Badge variant="outline" className="mt-3">
            {group.topic}
          </Badge>
        )}
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4 max-w-4xl mx-auto">
          {pinnedMessages.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3 text-sm font-medium text-muted-foreground">
                <PushPin size={16} weight="fill" />
                <span>Pinned Messages</span>
                {newPinnedCount > 0 && (
                  <Badge className="h-5 px-2 text-xs bg-primary">
                    {newPinnedCount} new
                  </Badge>
                )}
              </div>
              <div className="space-y-3">
                {pinnedMessages.map((message) => {
                  const canEditMsg = canEditMessage(userRole, message.fromUserId, currentUserId)
                  const canDeleteMsg = canDeleteMessage(userRole, message.fromUserId, currentUserId)

                  return (
                    <div
                      key={message.id}
                      className="relative bg-accent/30 border border-accent rounded-lg p-3"
                    >
                      <div className="flex items-start gap-3">
                        <Avatar className="h-8 w-8 flex-shrink-0">
                          <AvatarFallback className="text-xs">
                            {getInitials(message.fromUserName)}
                          </AvatarFallback>
                        </Avatar>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm font-medium">{message.fromUserName}</span>
                            <span className="text-xs text-muted-foreground">
                              {formatDistanceToNow(message.createdAt, { addSuffix: true })}
                            </span>
                            {message.editedAt && (
                              <span className="text-xs text-muted-foreground italic">(edited)</span>
                            )}
                            <PushPin size={14} weight="fill" className="text-accent ml-auto" />
                          </div>

                          {message.verseReference && (
                            <div className="flex items-center gap-2 text-sm mb-2 pb-2 border-b border-border">
                              <BookOpen size={16} weight="fill" />
                              <span className="font-medium">
                                {message.verseReference.bookName} {message.verseReference.chapterNumber}:
                                {message.verseReference.verseNumber}
                                {message.verseReference.verseEndNumber &&
                                  `-${message.verseReference.verseEndNumber}`}
                              </span>
                            </div>
                          )}

                          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>

                          {Object.keys(message.reactions).length > 0 && (
                            <div className="flex gap-1 mt-2 flex-wrap">
                              {Object.entries(message.reactions).map(([key, userIds]) => {
                                if (userIds.length === 0) return null
                                const ReactionIcon = getReactionIcon(key)
                                const hasReacted = userIds.includes(currentUserId)

                                return (
                                  <button
                                    key={key}
                                    onClick={() => toggleReaction(message.id, key)}
                                    className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs transition-colors ${
                                      hasReacted
                                        ? 'bg-primary/20 text-primary hover:bg-primary/30'
                                        : 'bg-muted hover:bg-muted/80'
                                    }`}
                                  >
                                    <ReactionIcon size={14} weight="fill" />
                                    <span>{userIds.length}</span>
                                  </button>
                                )
                              })}
                            </div>
                          )}
                        </div>

                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-7 w-7 flex-shrink-0">
                              <DotsThreeVertical size={16} weight="bold" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {canUnpin && (
                              <DropdownMenuItem onClick={() => handlePinMessage(message.id)}>
                                <X size={16} weight="bold" className="mr-2" />
                                Unpin
                              </DropdownMenuItem>
                            )}
                            {canEditMsg && (
                              <DropdownMenuItem onClick={() => setEditingMessage({ id: message.id, content: message.content })}>
                                <PencilSimple size={16} weight="bold" className="mr-2" />
                                Edit
                              </DropdownMenuItem>
                            )}
                            {canDeleteMsg && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  onClick={() => setDeletingMessage({ id: message.id, content: message.content })}
                                  className="text-destructive focus:text-destructive"
                                >
                                  <Trash size={16} weight="bold" className="mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              </>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {regularMessages.length === 0 && pinnedMessages.length === 0 ? (
            <div className="text-center py-12">
              <UsersThree size={64} weight="duotone" className="text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground mb-2">No messages yet</p>
              <p className="text-sm text-muted-foreground">
                Start the conversation by sending the first message!
              </p>
            </div>
          ) : (
            regularMessages.map((message, index) => {
              const isOwnMessage = message.fromUserId === currentUserId
              const canEditMsg = canEditMessage(userRole, message.fromUserId, currentUserId)
              const canDeleteMsg = canDeleteMessage(userRole, message.fromUserId, currentUserId)
              const showAvatar = index === 0 || regularMessages[index - 1].fromUserId !== message.fromUserId
              const isPinned = group.pinnedMessageIds.includes(message.id)
              const isEditing = editingMessage?.id === message.id

              return (
                <div
                  key={message.id}
                  className={`flex gap-3 ${isOwnMessage ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`flex-shrink-0 ${showAvatar ? '' : 'opacity-0'}`}>
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="text-xs">
                        {getInitials(message.fromUserName)}
                      </AvatarFallback>
                    </Avatar>
                  </div>

                  <div className={`flex-1 min-w-0 ${isOwnMessage ? 'flex flex-col items-end' : ''}`}>
                    {showAvatar && (
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{message.fromUserName}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(message.createdAt, { addSuffix: true })}
                        </span>
                        {message.editedAt && (
                          <span className="text-xs text-muted-foreground italic">(edited)</span>
                        )}
                      </div>
                    )}

                    <div className="group/message relative">
                      {isEditing ? (
                        <div className="space-y-2 max-w-[85%]">
                          <Textarea
                            value={editingMessage.content}
                            onChange={(e) => setEditingMessage({ ...editingMessage, content: e.target.value })}
                            className="min-h-[80px]"
                            autoFocus
                          />
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleEditMessage(message.id, editingMessage.content)}
                            >
                              <Check size={16} weight="bold" className="mr-1" />
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setEditingMessage(null)}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div
                            className={`rounded-2xl px-4 py-2 inline-block max-w-[85%] ${
                              isOwnMessage
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}
                          >
                            {message.verseReference && (
                              <div className={`flex items-center gap-2 text-sm mb-2 pb-2 border-b ${
                                isOwnMessage ? 'border-primary-foreground/20' : 'border-border'
                              }`}>
                                <BookOpen size={16} weight="fill" />
                                <span className="font-medium">
                                  {message.verseReference.bookName} {message.verseReference.chapterNumber}:
                                  {message.verseReference.verseNumber}
                                  {message.verseReference.verseEndNumber &&
                                    `-${message.verseReference.verseEndNumber}`}
                                </span>
                              </div>
                            )}
                            <p className="whitespace-pre-wrap break-words">{message.content}</p>
                          </div>

                          {Object.keys(message.reactions).length > 0 && (
                            <div className="flex gap-1 mt-1 flex-wrap">
                              {Object.entries(message.reactions).map(([key, userIds]) => {
                                if (userIds.length === 0) return null
                                const ReactionIcon = getReactionIcon(key)
                                const hasReacted = userIds.includes(currentUserId)

                                return (
                                  <button
                                    key={key}
                                    onClick={() => toggleReaction(message.id, key)}
                                    className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs transition-colors ${
                                      hasReacted
                                        ? 'bg-primary/20 text-primary hover:bg-primary/30'
                                        : 'bg-muted hover:bg-muted/80'
                                    }`}
                                  >
                                    <ReactionIcon size={14} weight="fill" />
                                    <span>{userIds.length}</span>
                                  </button>
                                )
                              })}
                            </div>
                          )}

                          <div className={`absolute top-0 opacity-0 group-hover/message:opacity-100 transition-opacity flex gap-1 ${isOwnMessage ? 'left-0 -translate-x-full -ml-2' : 'right-0 translate-x-full mr-2'}`}>
                            <DropdownMenu
                              open={showReactionPicker === message.id}
                              onOpenChange={(open) => setShowReactionPicker(open ? message.id : null)}
                            >
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-7 w-7">
                                  <Smiley size={16} weight="fill" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                {REACTION_EMOJIS.map(({ icon: Icon, key }) => (
                                  <DropdownMenuItem
                                    key={key}
                                    onClick={() => toggleReaction(message.id, key)}
                                  >
                                    <Icon size={20} weight="fill" className="mr-2" />
                                    {key.charAt(0).toUpperCase() + key.slice(1)}
                                  </DropdownMenuItem>
                                ))}
                              </DropdownMenuContent>
                            </DropdownMenu>

                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-7 w-7">
                                  <DotsThreeVertical size={16} weight="bold" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                {(canPin || (isPinned && canUnpin)) && (
                                  <DropdownMenuItem onClick={() => handlePinMessage(message.id)}>
                                    <PushPin size={16} weight={isPinned ? 'fill' : 'regular'} className="mr-2" />
                                    {isPinned ? 'Unpin' : 'Pin'}
                                  </DropdownMenuItem>
                                )}
                                {canEditMsg && (
                                  <DropdownMenuItem onClick={() => setEditingMessage({ id: message.id, content: message.content })}>
                                    <PencilSimple size={16} weight="bold" className="mr-2" />
                                    Edit
                                  </DropdownMenuItem>
                                )}
                                {canDeleteMsg && (
                                  <>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem
                                      onClick={() => setDeletingMessage({ id: message.id, content: message.content })}
                                      className="text-destructive focus:text-destructive"
                                    >
                                      <Trash size={16} weight="bold" className="mr-2" />
                                      Delete
                                    </DropdownMenuItem>
                                  </>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )
            })
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t bg-card p-4">
        {canPost ? (
          showVoiceComposer ? (
            <div className="max-w-4xl mx-auto">
              <VoiceMessageComposer
                onSend={handleVoiceMessageSend}
                onCancel={() => setShowVoiceComposer(false)}
                placeholder="Voice transcription will appear here..."
              />
            </div>
          ) : (
            <div className="flex gap-2 max-w-4xl mx-auto">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => setShowVoiceComposer(true)}
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
              <Input
                placeholder="Type a message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
                aria-label="Message input"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!newMessage.trim()}
                className="gap-2"
                aria-label="Send message"
              >
                <PaperPlaneRight size={18} weight="fill" />
                Send
              </Button>
            </div>
          )
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-200">
              <ShieldCheck size={24} weight="fill" className="text-amber-600 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-amber-700">
                  Restricted Group
                </p>
                <p className="text-xs text-amber-600">
                  Only admins and moderators can post messages in this group. 
                  {userRole === 'member' && ' Ask an admin to promote you to moderator to participate.'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <GroupInfoDialog
        group={group}
        open={showInfoDialog}
        onOpenChange={setShowInfoDialog}
        isAdmin={isAdmin}
      />

      <InviteMembersDialog
        group={group}
        open={showInviteDialog}
        onOpenChange={setShowInviteDialog}
      />

      <GroupAdminSettingsDialog
        group={group}
        open={showAdminSettings}
        onOpenChange={setShowAdminSettings}
        currentUserId={currentUserId}
      />

      <AlertDialog open={!!deletingMessage} onOpenChange={() => setDeletingMessage(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete message?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this message. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deletingMessage && handleDeleteMessage(deletingMessage.id)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
