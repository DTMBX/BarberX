import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ShieldCheck,
  Crown,
  User,
  Check,
  X,
  PushPin,
  Trash,
  UserPlus,
  Gear,
  ChatCircle,
} from '@phosphor-icons/react'
import type { GroupDiscussion } from '@/lib/types'
import type { GroupRole, Permission } from '@/lib/permissions'
import {
  getUserRole,
  getRoleDisplayName,
  getPermissionsByRole,
  getPermissionLabel,
  getAllPermissions,
} from '@/lib/permissions'
import { toast } from 'sonner'

export default function ModeratorTestPanel() {
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [groups = []] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [selectedGroupId, setSelectedGroupId] = useState<string>('')

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  }, [])

  const selectedGroup = groups.find(g => g.id === selectedGroupId)
  const currentUserRole = selectedGroup ? getUserRole(selectedGroup, currentUserId) : undefined
  const userPermissions = currentUserRole ? getPermissionsByRole(currentUserRole) : []
  const allPermissions = getAllPermissions()

  const userGroups = groups.filter(g => g.memberIds.includes(currentUserId))

  const getRoleIcon = (role: GroupRole) => {
    switch (role) {
      case 'admin':
        return <Crown size={20} weight="fill" className="text-amber-500" />
      case 'moderator':
        return <ShieldCheck size={20} weight="fill" className="text-blue-500" />
      case 'member':
        return <User size={20} weight="fill" className="text-muted-foreground" />
    }
  }

  const getRoleBadgeClass = (role: GroupRole) => {
    switch (role) {
      case 'admin':
        return 'bg-amber-500/10 text-amber-700 border-amber-200'
      case 'moderator':
        return 'bg-blue-500/10 text-blue-700 border-blue-200'
      case 'member':
        return 'bg-muted text-muted-foreground border-border'
    }
  }

  const getPermissionIcon = (permission: Permission) => {
    switch (permission) {
      case 'pin_messages':
      case 'unpin_messages':
        return <PushPin size={16} />
      case 'delete_any_message':
        return <Trash size={16} />
      case 'invite_members':
        return <UserPlus size={16} />
      case 'post_messages':
        return <ChatCircle size={16} />
      case 'update_settings':
      case 'manage_group':
        return <Gear size={16} />
      default:
        return <Check size={16} />
    }
  }

  const handleTestPermission = (permission: Permission) => {
    if (userPermissions.includes(permission)) {
      toast.success(`✓ You have permission: ${getPermissionLabel(permission)}`, {
        description: `As a ${getRoleDisplayName(currentUserRole!)}, this action is allowed.`
      })
    } else {
      toast.error(`✗ Permission denied: ${getPermissionLabel(permission)}`, {
        description: `Your role (${getRoleDisplayName(currentUserRole!)}) cannot perform this action.`
      })
    }
  }

  if (userGroups.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck size={24} weight="fill" className="text-primary" />
            Moderator Test Panel
          </CardTitle>
          <CardDescription>
            Test and understand role-based permissions in your groups
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <User size={48} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              You need to be a member of at least one group to test permissions.
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Create a group or get invited to one first!
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck size={24} weight="fill" className="text-primary" />
          Moderator Test Panel
        </CardTitle>
        <CardDescription>
          Test and understand role-based permissions in your groups
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-medium">Select a Group</label>
          <Select value={selectedGroupId} onValueChange={setSelectedGroupId}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a group to test..." />
            </SelectTrigger>
            <SelectContent>
              {userGroups.map(group => {
                const role = getUserRole(group, currentUserId)
                return (
                  <SelectItem key={group.id} value={group.id}>
                    <div className="flex items-center gap-2">
                      <span>{group.name}</span>
                      {role && (
                        <Badge variant="outline" className="ml-2">
                          {getRoleDisplayName(role)}
                        </Badge>
                      )}
                    </div>
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        {selectedGroup && currentUserRole && (
          <>
            <Separator />

            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 rounded-lg border bg-muted/30">
                <div className="flex items-center gap-3">
                  {getRoleIcon(currentUserRole)}
                  <div>
                    <p className="font-semibold">Your Role</p>
                    <p className="text-sm text-muted-foreground">
                      in {selectedGroup.name}
                    </p>
                  </div>
                </div>
                <Badge variant="outline" className={getRoleBadgeClass(currentUserRole)}>
                  {getRoleDisplayName(currentUserRole)}
                </Badge>
              </div>

              <div className="p-4 rounded-lg border bg-primary/5">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <Check size={18} weight="bold" className="text-primary" />
                  Group Settings
                </h4>
                <div className="space-y-1 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Anyone can post:</span>
                    <Badge variant={selectedGroup.settings.anyoneCanPost ? 'default' : 'outline'}>
                      {selectedGroup.settings.anyoneCanPost ? 'Yes' : 'No (Restricted)'}
                    </Badge>
                  </div>
                  {!selectedGroup.settings.anyoneCanPost && (
                    <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                      <ShieldCheck size={14} weight="fill" />
                      Only admins and moderators can post messages
                    </p>
                  )}
                </div>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <h4 className="font-semibold">Your Permissions</h4>
              <p className="text-sm text-muted-foreground">
                Click any permission to test if you have access
              </p>
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-2">
                  {allPermissions.map((permission) => {
                    const hasPermission = userPermissions.includes(permission)
                    const isRestrictedBySettings =
                      permission === 'post_messages' &&
                      !selectedGroup.settings.anyoneCanPost &&
                      currentUserRole === 'member'

                    return (
                      <Button
                        key={permission}
                        variant="outline"
                        className={`w-full justify-start gap-3 h-auto py-3 ${
                          hasPermission && !isRestrictedBySettings
                            ? 'border-primary/30 bg-primary/5 hover:bg-primary/10'
                            : 'opacity-60 hover:opacity-80'
                        }`}
                        onClick={() => handleTestPermission(permission)}
                      >
                        <div className="flex-shrink-0">
                          {hasPermission && !isRestrictedBySettings ? (
                            <div className="p-1 rounded-full bg-primary/20">
                              <Check size={16} weight="bold" className="text-primary" />
                            </div>
                          ) : (
                            <div className="p-1 rounded-full bg-muted">
                              <X size={16} weight="bold" className="text-muted-foreground" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 text-left">
                          <div className="flex items-center gap-2">
                            {getPermissionIcon(permission)}
                            <span className="font-medium text-sm">
                              {getPermissionLabel(permission)}
                            </span>
                          </div>
                          {isRestrictedBySettings && (
                            <p className="text-xs text-amber-600 mt-1">
                              Restricted by group settings
                            </p>
                          )}
                        </div>
                      </Button>
                    )
                  })}
                </div>
              </ScrollArea>
            </div>

            <div className="p-4 rounded-lg border bg-muted/30">
              <p className="text-sm text-muted-foreground">
                💡 <strong>Tip:</strong> To test moderator permissions, ask a group admin to promote you to the 
                moderator role in the Admin Settings. Moderators can pin messages, delete any message, 
                and post in restricted groups.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
