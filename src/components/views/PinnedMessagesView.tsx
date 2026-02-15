import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { MagnifyingGlass, PushPin, BookOpen, X, ArrowLeft } from '@phosphor-icons/react'
import type { GroupMessage, GroupDiscussion } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'

interface PinnedMessagesViewProps {
  onBack?: () => void
  onNavigateToGroup?: (groupId: string, groupName: string) => void
}

export default function PinnedMessagesView({
  onBack,
  onNavigateToGroup
}: PinnedMessagesViewProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGroup, setSelectedGroup] = useState<string>('all')
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [groups = [], setGroups] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [pinnedData, setPinnedData] = useState<Array<{
    message: GroupMessage
    group: GroupDiscussion
  }>>([])

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  useEffect(() => {
    const loadPinnedMessages = async () => {
      const allPinned: Array<{
        message: GroupMessage
        group: GroupDiscussion
      }> = []

      const filteredGroups = selectedGroup === 'all'
        ? groups.filter(g => g.memberIds.includes(currentUserId))
        : groups.filter(g => g.id === selectedGroup && g.memberIds.includes(currentUserId))

      for (const group of filteredGroups) {
        if (group.pinnedMessageIds.length > 0) {
          const messagesKey = `group-messages-${group.id}`
          const storedMessages = await window.spark.kv.get<GroupMessage[]>(messagesKey)
          const messages = storedMessages || []
          
          messages
            .filter(msg => group.pinnedMessageIds.includes(msg.id) && !msg.deletedAt)
            .forEach(msg => {
              allPinned.push({ message: msg, group })
            })
        }
      }

      setPinnedData(allPinned)
    }

    if (currentUserId) {
      loadPinnedMessages()
    }
  }, [groups, selectedGroup, currentUserId])

  const filteredMessages = pinnedData.filter(({ message, group }) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      message.content.toLowerCase().includes(query) ||
      message.fromUserName.toLowerCase().includes(query) ||
      group.name.toLowerCase().includes(query) ||
      message.verseReference?.bookName.toLowerCase().includes(query)
    )
  })

  const sortedMessages = [...filteredMessages].sort((a, b) => 
    b.message.createdAt - a.message.createdAt
  )

  const handleUnpin = (groupId: string, messageId: string) => {
    setGroups((currentGroups) =>
      (currentGroups || []).map(g =>
        g.id === groupId
          ? {
              ...g,
              pinnedMessageIds: g.pinnedMessageIds.filter(id => id !== messageId)
            }
          : g
      )
    )
    toast.success('Message unpinned')
  }

  const canManagePin = (group: GroupDiscussion) => {
    const isAdmin = group.createdBy === currentUserId
    const member = group.members.find(m => m.userId === currentUserId)
    const isModerator = member?.role === 'moderator' || member?.role === 'admin'
    return isAdmin || isModerator
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

  const userGroups = groups.filter(g => g.memberIds.includes(currentUserId))

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b bg-card p-4">
        <div className="flex items-center gap-3 mb-4">
          {onBack && (
            <Button variant="ghost" size="icon" onClick={onBack}>
              <ArrowLeft size={20} weight="bold" />
            </Button>
          )}
          <div className="flex items-center gap-2">
            <PushPin size={28} weight="fill" className="text-primary" />
            <h2 className="text-xl font-bold">Pinned Messages</h2>
          </div>
        </div>

        <div className="space-y-3">
          <div className="relative">
            <MagnifyingGlass
              size={18}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <Input
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={selectedGroup} onValueChange={setSelectedGroup}>
            <SelectTrigger>
              <SelectValue placeholder="All groups" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All groups</SelectItem>
              {userGroups.map(group => (
                <SelectItem key={group.id} value={group.id}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {sortedMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <PushPin size={80} weight="duotone" className="text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No pinned messages</h3>
            <p className="text-muted-foreground max-w-md">
              {searchQuery
                ? 'No pinned messages match your search'
                : 'Pinned messages from your group discussions will appear here'}
            </p>
          </div>
        ) : (
          <div className="space-y-3 max-w-4xl mx-auto">
            {sortedMessages.map(({ message, group }) => (
              <div
                key={`${group.id}-${message.id}`}
                className="border rounded-lg p-4 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Avatar className="h-10 w-10 flex-shrink-0">
                    <AvatarFallback className="text-sm">
                      {getInitials(message.fromUserName)}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-medium">{message.fromUserName}</span>
                      <span className="text-xs text-muted-foreground">in</span>
                      <Badge
                        variant="outline"
                        className="text-xs cursor-pointer hover:bg-primary/10"
                        onClick={() => onNavigateToGroup?.(group.id, group.name)}
                      >
                        {group.name}
                      </Badge>
                      <span className="text-xs text-muted-foreground ml-auto">
                        {formatDistanceToNow(message.createdAt, { addSuffix: true })}
                      </span>
                      {message.editedAt && (
                        <span className="text-xs text-muted-foreground italic">(edited)</span>
                      )}
                    </div>

                    {message.verseReference && (
                      <div className="flex items-center gap-2 text-sm mb-2 pb-2 border-b">
                        <BookOpen size={16} weight="fill" className="text-primary" />
                        <span className="font-medium">
                          {message.verseReference.bookName} {message.verseReference.chapterNumber}:
                          {message.verseReference.verseNumber}
                          {message.verseReference.verseEndNumber &&
                            `-${message.verseReference.verseEndNumber}`}
                        </span>
                      </div>
                    )}

                    <p className="text-sm whitespace-pre-wrap break-words mb-3">
                      {message.content}
                    </p>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onNavigateToGroup?.(group.id, group.name)}
                      >
                        View in Discussion
                      </Button>

                      {canManagePin(group) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUnpin(group.id, message.id)}
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <X size={16} weight="bold" className="mr-1" />
                          Unpin
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
