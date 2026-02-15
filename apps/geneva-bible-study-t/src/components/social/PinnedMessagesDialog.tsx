import { useState, useMemo } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { MagnifyingGlass, PushPin, BookOpen, X } from '@phosphor-icons/react'
import type { GroupMessage, GroupDiscussion } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'

interface PinnedMessagesDialogProps {
  groups: GroupDiscussion[]
  allMessages: Record<string, GroupMessage[]>
  open: boolean
  onOpenChange: (open: boolean) => void
  onNavigateToMessage: (groupId: string, messageId: string) => void
  onUnpinMessage?: (groupId: string, messageId: string) => void
  canManagePins: Record<string, boolean>
}

export default function PinnedMessagesDialog({
  groups,
  allMessages,
  open,
  onOpenChange,
  onNavigateToMessage,
  onUnpinMessage,
  canManagePins
}: PinnedMessagesDialogProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGroup, setSelectedGroup] = useState<string>('all')

  const pinnedMessages = useMemo(() => {
    const messages: Array<{
      message: GroupMessage
      group: GroupDiscussion
    }> = []

    const filteredGroups = selectedGroup === 'all'
      ? groups
      : groups.filter(g => g.id === selectedGroup)

    filteredGroups.forEach(group => {
      const groupMessages = allMessages[group.id] || []
      groupMessages
        .filter(msg => group.pinnedMessageIds.includes(msg.id) && !msg.deletedAt)
        .forEach(msg => {
          messages.push({ message: msg, group })
        })
    })

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return messages.filter(({ message, group }) => 
        message.content.toLowerCase().includes(query) ||
        message.fromUserName.toLowerCase().includes(query) ||
        group.name.toLowerCase().includes(query) ||
        message.verseReference?.bookName.toLowerCase().includes(query)
      )
    }

    return messages
  }, [groups, allMessages, selectedGroup, searchQuery])

  const sortedMessages = [...pinnedMessages].sort((a, b) => 
    b.message.createdAt - a.message.createdAt
  )

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PushPin size={24} weight="fill" className="text-primary" />
            Pinned Messages
          </DialogTitle>
          <DialogDescription>
            Search and view all pinned messages across your groups
          </DialogDescription>
        </DialogHeader>

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
              {groups.map(group => (
                <SelectItem key={group.id} value={group.id}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <ScrollArea className="flex-1 pr-4 -mr-4">
          {sortedMessages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <PushPin size={64} weight="duotone" className="text-muted-foreground mb-3" />
              <p className="text-muted-foreground">
                {searchQuery
                  ? 'No pinned messages match your search'
                  : 'No pinned messages yet'}
              </p>
            </div>
          ) : (
            <div className="space-y-3 py-2">
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
                        <Badge variant="outline" className="text-xs">
                          {group.name}
                        </Badge>
                        <span className="text-xs text-muted-foreground ml-auto">
                          {formatDistanceToNow(message.createdAt, { addSuffix: true })}
                        </span>
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
                          onClick={() => {
                            onNavigateToMessage(group.id, message.id)
                            onOpenChange(false)
                          }}
                        >
                          View in Discussion
                        </Button>

                        {canManagePins[group.id] && onUnpinMessage && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onUnpinMessage(group.id, message.id)}
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
      </DialogContent>
    </Dialog>
  )
}
