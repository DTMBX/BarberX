import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
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
import { Separator } from '@/components/ui/separator'
import { Gear, Crown, ShieldCheck, Trash, UserMinus, User } from '@phosphor-icons/react'
import type { GroupDiscussion } from '@/lib/types'
import { toast } from 'sonner'
import {
  getUserRole,
  canChangeRoles,
  canRemoveMembers,
  canDeleteGroup,
  getRoleDisplayName,
  getRoleDescription,
  canPromoteToRole,
  type GroupRole,
} from '@/lib/permissions'

interface GroupAdminSettingsDialogProps {
  group: GroupDiscussion
  open: boolean
  onOpenChange: (open: boolean) => void
  currentUserId: string
}

export default function GroupAdminSettingsDialog({
  group,
  open,
  onOpenChange,
  currentUserId
}: GroupAdminSettingsDialogProps) {
  const [groups = [], setGroups] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [settings, setSettings] = useState(group?.settings || { allowInvites: false, anyoneCanPost: true, moderationEnabled: false })
  const [confirmRemove, setConfirmRemove] = useState<{ userId: string; userName: string } | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const currentUserRole = group ? getUserRole(group, currentUserId) : 'member'
  const canChangeUserRoles = canChangeRoles(currentUserRole)
  const canRemoveUsers = canRemoveMembers(currentUserRole)
  const canDeleteGroupPermission = canDeleteGroup(currentUserRole)

  const handleSaveSettings = () => {
    setGroups((currentGroups) =>
      (currentGroups || []).map(g =>
        g.id === group.id
          ? { ...g, settings }
          : g
      )
    )
    toast.success('Settings saved')
    onOpenChange(false)
  }

  const handleChangeMemberRole = (userId: string, newRole: GroupRole) => {
    if (!canPromoteToRole(currentUserRole, newRole)) {
      toast.error('You do not have permission to assign this role')
      return
    }

    setGroups((currentGroups) =>
      (currentGroups || []).map(g =>
        g.id === group.id
          ? {
              ...g,
              members: g.members.map(m =>
                m.userId === userId ? { ...m, role: newRole } : m
              )
            }
          : g
      )
    )
    toast.success(`Member role updated to ${getRoleDisplayName(newRole)}`)
  }

  const handleRemoveMember = (userId: string) => {
    setGroups((currentGroups) =>
      (currentGroups || []).map(g =>
        g.id === group.id
          ? {
              ...g,
              memberIds: g.memberIds.filter(id => id !== userId),
              members: g.members.filter(m => m.userId !== userId)
            }
          : g
      )
    )
    toast.success('Member removed from group')
    setConfirmRemove(null)
  }

  const handleDeleteGroup = () => {
    setGroups((currentGroups) =>
      (currentGroups || []).filter(g => g.id !== group.id)
    )
    toast.success('Group deleted')
    setConfirmDelete(false)
    onOpenChange(false)
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

  const getRoleIcon = (role: GroupRole) => {
    switch (role) {
      case 'admin':
        return <Crown size={16} weight="fill" className="text-amber-500" />
      case 'moderator':
        return <ShieldCheck size={16} weight="fill" className="text-blue-500" />
      default:
        return <User size={16} weight="fill" className="text-muted-foreground" />
    }
  }

  if (!group) {
    return null
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Gear size={24} weight="fill" className="text-primary" />
              Admin Settings
            </DialogTitle>
            <DialogDescription>
              Manage group settings and members
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-6 py-2">
              <div>
                <h3 className="text-sm font-semibold mb-4">Group Permissions</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="allow-invites">Allow member invites</Label>
                      <p className="text-sm text-muted-foreground">
                        Let members invite others to join
                      </p>
                    </div>
                    <Switch
                      id="allow-invites"
                      checked={settings.allowInvites}
                      onCheckedChange={(checked) =>
                        setSettings({ ...settings, allowInvites: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="anyone-post">Anyone can post</Label>
                      <p className="text-sm text-muted-foreground">
                        All members can send messages
                      </p>
                    </div>
                    <Switch
                      id="anyone-post"
                      checked={settings.anyoneCanPost}
                      onCheckedChange={(checked) =>
                        setSettings({ ...settings, anyoneCanPost: checked })
                      }
                    />
                  </div>
                  {!settings.anyoneCanPost && (
                    <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-200">
                      <p className="text-sm text-amber-700 flex items-center gap-2">
                        <ShieldCheck size={16} weight="fill" />
                        <strong>Restricted Group:</strong> Only admins and moderators can post messages
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="moderation">Enable moderation</Label>
                      <p className="text-sm text-muted-foreground">
                        Require approval for new messages
                      </p>
                    </div>
                    <Switch
                      id="moderation"
                      checked={settings.moderationEnabled}
                      onCheckedChange={(checked) =>
                        setSettings({ ...settings, moderationEnabled: checked })
                      }
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-semibold mb-4">
                  Member Management ({group.members.length})
                </h3>
                
                <div className="mb-4 p-3 rounded-lg bg-primary/5 border border-primary/20">
                  <p className="text-sm text-muted-foreground">
                    💡 <strong>Testing Moderator Permissions:</strong> Promote a member to moderator to see 
                    their enhanced capabilities. Moderators can post in restricted groups, pin/unpin messages, 
                    delete any message, and invite members. Use the Permissions tab in Settings to test access.
                  </p>
                </div>

                <div className="space-y-2">
                  {group.members
                    .sort((a, b) => {
                      const roleOrder = { admin: 0, moderator: 1, member: 2 }
                      return roleOrder[a.role] - roleOrder[b.role]
                    })
                    .map(member => {
                      const isCurrentUser = member.userId === currentUserId
                      const isCreator = member.userId === group.createdBy

                      return (
                        <div
                          key={member.userId}
                          className="flex items-center gap-3 p-3 rounded-lg border"
                        >
                          <Avatar className="h-10 w-10">
                            <AvatarFallback>{getInitials(member.userName)}</AvatarFallback>
                          </Avatar>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="font-medium truncate">{member.userName}</p>
                              {getRoleIcon(member.role)}
                              <Badge variant="outline" className="text-xs capitalize">
                                {getRoleDisplayName(member.role)}
                              </Badge>
                              {isCreator && (
                                <Badge variant="outline" className="text-xs">Creator</Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {getRoleDescription(member.role)}
                            </p>
                          </div>

                          {!isCreator && !isCurrentUser && canChangeUserRoles && (
                            <div className="flex items-center gap-2">
                              <Select
                                value={member.role}
                                onValueChange={(value) =>
                                  handleChangeMemberRole(member.userId, value as GroupRole)
                                }
                                disabled={!canPromoteToRole(currentUserRole, member.role)}
                              >
                                <SelectTrigger className="w-32">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="member">Member</SelectItem>
                                  <SelectItem value="moderator">Moderator</SelectItem>
                                  <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                              </Select>

                              {canRemoveUsers && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => setConfirmRemove({
                                    userId: member.userId,
                                    userName: member.userName
                                  })}
                                  className="text-destructive hover:text-destructive"
                                >
                                  <UserMinus size={18} weight="bold" />
                                </Button>
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-semibold mb-3 text-destructive">Danger Zone</h3>
                {canDeleteGroupPermission ? (
                  <Button
                    variant="destructive"
                    onClick={() => setConfirmDelete(true)}
                    className="w-full gap-2"
                  >
                    <Trash size={18} weight="bold" />
                    Delete Group
                  </Button>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Only group admins can delete the group
                  </p>
                )}
              </div>
            </div>
          </ScrollArea>

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveSettings}>
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!confirmRemove} onOpenChange={() => setConfirmRemove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove member?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove {confirmRemove?.userName} from this group?
              They will no longer have access to group messages.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => confirmRemove && handleRemoveMember(confirmRemove.userId)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete group?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete "{group.name}" and all its messages.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteGroup}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete Group
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
