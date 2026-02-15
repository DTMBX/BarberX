import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Plus, UsersThree, MagnifyingGlass, Lock, Users, Globe, PushPin, ShieldCheck } from '@phosphor-icons/react'
import type { GroupDiscussion } from '@/lib/types'
import CreateGroupDialog from './CreateGroupDialog'
import { formatDistanceToNow } from 'date-fns'

interface GroupDiscussionsListProps {
  onSelectGroup: (groupId: string, groupName: string) => void
}

export default function GroupDiscussionsList({ onSelectGroup }: GroupDiscussionsListProps) {
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [groups = []] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [searchQuery, setSearchQuery] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  const userGroups = groups
    .filter(group => group.memberIds.includes(currentUserId))
    .filter(group =>
      searchQuery === '' ||
      group.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      group.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => b.lastMessageAt - a.lastMessageAt)

  const getUnreadCount = (group: GroupDiscussion) => {
    return group.unreadCount[currentUserId] || 0
  }

  const getPrivacyIcon = (privacy: GroupDiscussion['privacy']) => {
    switch (privacy) {
      case 'public':
        return <Globe size={14} weight="fill" className="text-muted-foreground" />
      case 'friends-only':
        return <Users size={14} weight="fill" className="text-muted-foreground" />
      case 'invite-only':
        return <Lock size={14} weight="fill" className="text-muted-foreground" />
    }
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

  return (
    <div className="h-full flex flex-col bg-card">
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Group Discussions</h2>
          <Button
            size="sm"
            onClick={() => setIsCreateDialogOpen(true)}
            className="gap-2"
          >
            <Plus size={16} weight="bold" />
            New Group
          </Button>
        </div>
        
        <div className="relative">
          <MagnifyingGlass
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search groups..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {userGroups.length === 0 ? (
            <div className="p-8 text-center">
              <UsersThree size={64} weight="duotone" className="text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground mb-4">
                {searchQuery
                  ? 'No groups found matching your search'
                  : 'No group discussions yet'}
              </p>
              {!searchQuery && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="gap-2"
                >
                  <Plus size={16} weight="bold" />
                  Create Your First Group
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-1">
              {userGroups.map(group => {
                const unreadCount = getUnreadCount(group)
                const isUnread = unreadCount > 0
                const hasPinnedMessages = group.pinnedMessageIds.length > 0

                return (
                  <button
                    key={group.id}
                    onClick={() => onSelectGroup(group.id, group.name)}
                    className="w-full p-3 rounded-lg hover:bg-muted/50 transition-colors text-left group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="relative">
                        <Avatar className="h-12 w-12 bg-primary/10">
                          <AvatarFallback className="text-primary font-semibold">
                            {getInitials(group.name)}
                          </AvatarFallback>
                        </Avatar>
                        {isUnread && (
                          <div className="absolute -top-1 -right-1 h-5 w-5 bg-primary rounded-full flex items-center justify-center">
                            <span className="text-[10px] font-bold text-primary-foreground">
                              {unreadCount > 9 ? '9+' : unreadCount}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <h3 className={`font-semibold truncate ${isUnread ? 'text-foreground' : 'text-foreground/80'}`}>
                            {group.name}
                          </h3>
                          {getPrivacyIcon(group.privacy)}
                          {hasPinnedMessages && (
                            <PushPin size={14} weight="fill" className="text-accent ml-auto" />
                          )}
                        </div>
                        
                        <p className="text-sm text-muted-foreground line-clamp-1 mb-1">
                          {group.description || 'No description'}
                        </p>

                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <UsersThree size={14} weight="fill" />
                            <span>{group.memberIds.length}</span>
                          </div>
                          {group.lastMessageAt && (
                            <>
                              <span>•</span>
                              <span>
                                {formatDistanceToNow(group.lastMessageAt, { addSuffix: true })}
                              </span>
                            </>
                          )}
                          {hasPinnedMessages && (
                            <>
                              <span>•</span>
                              <div className="flex items-center gap-1">
                                <PushPin size={12} weight="fill" />
                                <span>{group.pinnedMessageIds.length}</span>
                              </div>
                            </>
                          )}
                        </div>

                        {group.topic && (
                          <Badge variant="outline" className="mt-2 text-xs">
                            {group.topic}
                          </Badge>
                        )}
                        {!group.settings.anyoneCanPost && (
                          <Badge variant="outline" className="mt-2 text-xs bg-amber-500/10 text-amber-700 border-amber-200">
                            <ShieldCheck size={12} weight="fill" className="mr-1" />
                            Restricted
                          </Badge>
                        )}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </ScrollArea>

      <CreateGroupDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />
    </div>
  )
}
