import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Globe, Users, Lock, Crown, ShieldCheck, User, Info } from '@phosphor-icons/react'
import type { GroupDiscussion } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'
import PermissionsInfoDialog from './PermissionsInfoDialog'

interface GroupInfoDialogProps {
  group: GroupDiscussion
  open: boolean
  onOpenChange: (open: boolean) => void
  isAdmin: boolean
}

export default function GroupInfoDialog({
  group,
  open,
  onOpenChange,
  isAdmin
}: GroupInfoDialogProps) {
  const [showPermissions, setShowPermissions] = useState(false)

  const getInitials = (name?: string) => {
    if (!name) return '??'
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getPrivacyIcon = (privacy: GroupDiscussion['privacy']) => {
    switch (privacy) {
      case 'public':
        return <Globe size={18} weight="fill" className="text-primary" />
      case 'friends-only':
        return <Users size={18} weight="fill" className="text-primary" />
      case 'invite-only':
        return <Lock size={18} weight="fill" className="text-primary" />
    }
  }

  const getRoleIcon = (role: 'admin' | 'moderator' | 'member') => {
    switch (role) {
      case 'admin':
        return <Crown size={16} weight="fill" className="text-amber-500" />
      case 'moderator':
        return <ShieldCheck size={16} weight="fill" className="text-blue-500" />
      case 'member':
        return <User size={16} weight="fill" className="text-muted-foreground" />
    }
  }

  const getRoleBadge = (role: 'admin' | 'moderator' | 'member') => {
    const colors = {
      admin: 'bg-amber-500/10 text-amber-700 border-amber-200',
      moderator: 'bg-blue-500/10 text-blue-700 border-blue-200',
      member: ''
    }
    return role !== 'member' ? colors[role] : ''
  }

  if (!group) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Group Information</DialogTitle>
          <DialogDescription>
            Details about this group discussion
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-6 py-2">
            <div className="flex items-start gap-4">
              <Avatar className="h-16 w-16 bg-primary/10">
                <AvatarFallback className="text-2xl text-primary font-bold">
                  {getInitials(group.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-1">{group.name}</h3>
                {group.description && (
                  <p className="text-muted-foreground mb-2">{group.description}</p>
                )}
                <div className="flex items-center gap-2 text-sm">
                  {getPrivacyIcon(group.privacy)}
                  <span className="capitalize">{group.privacy.replace('-', ' ')}</span>
                </div>
              </div>
            </div>

            {group.topic && (
              <div>
                <h4 className="text-sm font-medium mb-2">Topic</h4>
                <Badge variant="outline" className="text-sm">
                  {group.topic}
                </Badge>
              </div>
            )}

            <div>
              <h4 className="text-sm font-medium mb-2">Created By</h4>
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                  <AvatarFallback>{getInitials(group.createdByName)}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{group.createdByName}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDistanceToNow(group.createdAt, { addSuffix: true })}
                  </p>
                </div>
              </div>
            </div>

            <Separator />

            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium">
                  Members ({group.members.length})
                </h4>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPermissions(true)}
                  className="gap-2 text-primary"
                >
                  <Info size={16} weight="fill" />
                  Role Permissions Guide
                </Button>
              </div>
              <div className="space-y-2">
                {group.members
                  .sort((a, b) => {
                    const roleOrder = { admin: 0, moderator: 1, member: 2 }
                    return roleOrder[a.role] - roleOrder[b.role]
                  })
                  .map(member => (
                    <div
                      key={member.userId}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50"
                    >
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>{getInitials(member.userName)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium truncate">{member.userName}</p>
                          {getRoleIcon(member.role)}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Joined {formatDistanceToNow(member.joinedAt, { addSuffix: true })}
                        </p>
                      </div>
                      {member.role !== 'member' && (
                        <Badge variant="outline" className={getRoleBadge(member.role)}>
                          {member.role}
                        </Badge>
                      )}
                    </div>
                  ))}
              </div>
            </div>

            {group.relatedPassage && (
              <>
                <Separator />
                <div>
                  <h4 className="text-sm font-medium mb-2">Related Passage</h4>
                  <p className="text-sm text-muted-foreground">
                    {group.relatedPassage.bookName} {group.relatedPassage.chapterNumber}
                    {group.relatedPassage.verseNumber && `:${group.relatedPassage.verseNumber}`}
                  </p>
                </div>
              </>
            )}

            <Separator />

            <div>
              <h4 className="text-sm font-medium mb-3">Group Settings</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-muted-foreground">Allow member invites</span>
                  <Badge variant={group.settings.allowInvites ? 'default' : 'outline'}>
                    {group.settings.allowInvites ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-muted-foreground">Anyone can post</span>
                  <Badge variant={group.settings.anyoneCanPost ? 'default' : 'outline'}>
                    {group.settings.anyoneCanPost ? 'Yes' : 'No'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-muted-foreground">Moderation</span>
                  <Badge variant={group.settings.moderationEnabled ? 'default' : 'outline'}>
                    {group.settings.moderationEnabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>

      <PermissionsInfoDialog
        open={showPermissions}
        onOpenChange={setShowPermissions}
      />
    </Dialog>
  )
}
