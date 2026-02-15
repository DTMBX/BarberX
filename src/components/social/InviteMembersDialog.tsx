import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { MagnifyingGlass } from '@phosphor-icons/react'
import type { GroupDiscussion, UserConnection } from '@/lib/types'
import { toast } from 'sonner'

interface InviteMembersDialogProps {
  group: GroupDiscussion
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function InviteMembersDialog({
  group,
  open,
  onOpenChange
}: InviteMembersDialogProps) {
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [groups = [], setGroups] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedMembers, setSelectedMembers] = useState<string[]>([])

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  const availableFriends = friends.filter(
    friend => !group?.memberIds?.includes(friend.userId)
  ).filter(
    friend =>
      searchQuery === '' ||
      friend.userName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleInvite = () => {
    if (selectedMembers.length === 0) {
      toast.error('Please select at least one friend to invite')
      return
    }

    setGroups((currentGroups) =>
      (currentGroups || []).map(g => {
        if (g.id !== group.id) return g

        const newMembers = selectedMembers.map(memberId => {
          const friend = friends.find(f => f.userId === memberId)
          return {
            userId: memberId,
            userName: friend?.userName || 'Unknown',
            userAvatar: friend?.userAvatar,
            role: 'member' as const,
            joinedAt: Date.now()
          }
        })

        return {
          ...g,
          memberIds: [...g.memberIds, ...selectedMembers],
          members: [...g.members, ...newMembers]
        }
      })
    )

    toast.success(`Invited ${selectedMembers.length} ${selectedMembers.length === 1 ? 'member' : 'members'}`)
    
    setSelectedMembers([])
    setSearchQuery('')
    onOpenChange(false)
  }

  const toggleMember = (userId: string) => {
    setSelectedMembers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    )
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

  if (!group) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Invite Members</DialogTitle>
          <DialogDescription>
            Invite your friends to join "{group.name}"
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 flex-1 min-h-0">
          <div className="relative">
            <MagnifyingGlass
              size={18}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <Input
              placeholder="Search friends..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {availableFriends.length} friends available
            </p>
            {selectedMembers.length > 0 && (
              <Badge variant="outline">
                {selectedMembers.length} selected
              </Badge>
            )}
          </div>

          <ScrollArea className="flex-1 -mx-6 px-6">
            {availableFriends.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                {searchQuery
                  ? 'No friends found matching your search'
                  : 'All your friends are already in this group!'}
              </p>
            ) : (
              <div className="space-y-2">
                {availableFriends.map(friend => (
                  <div
                    key={friend.userId}
                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <Checkbox
                      id={`invite-${friend.userId}`}
                      checked={selectedMembers.includes(friend.userId)}
                      onCheckedChange={() => toggleMember(friend.userId)}
                    />
                    <label
                      htmlFor={`invite-${friend.userId}`}
                      className="flex items-center gap-3 flex-1 cursor-pointer"
                    >
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>{getInitials(friend.userName)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{friend.userName}</p>
                        <p className="text-xs text-muted-foreground">
                          Friend since {new Date(friend.connectedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleInvite}
            disabled={selectedMembers.length === 0}
          >
            Invite {selectedMembers.length > 0 && `(${selectedMembers.length})`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
