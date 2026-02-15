import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Crown, ShieldCheck, User, Check, X } from '@phosphor-icons/react'
import type { Permission, GroupRole } from '@/lib/permissions'
import { getRoleDisplayName, getRoleDescription } from '@/lib/permissions'

interface PermissionsInfoDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const PERMISSION_DETAILS: Record<Permission, { label: string; description: string }> = {
  manage_group: {
    label: 'Manage Group',
    description: 'Full control over group configuration and existence',
  },
  delete_group: {
    label: 'Delete Group',
    description: 'Permanently delete the entire group',
  },
  manage_members: {
    label: 'Manage Members',
    description: 'Add, remove, and modify member permissions',
  },
  change_roles: {
    label: 'Change Roles',
    description: 'Promote or demote member roles',
  },
  remove_members: {
    label: 'Remove Members',
    description: 'Remove members from the group',
  },
  invite_members: {
    label: 'Invite Members',
    description: 'Invite new members to join the group',
  },
  update_settings: {
    label: 'Update Settings',
    description: 'Modify group settings and preferences',
  },
  pin_messages: {
    label: 'Pin Messages',
    description: 'Pin important messages to the top',
  },
  unpin_messages: {
    label: 'Unpin Messages',
    description: 'Remove pinned messages',
  },
  delete_any_message: {
    label: 'Delete Any Message',
    description: "Delete messages from any member, not just your own",
  },
  edit_any_message: {
    label: 'Edit Any Message',
    description: "Edit messages from any member (currently not implemented)",
  },
  post_messages: {
    label: 'Post Messages',
    description: 'Send messages in the group discussion',
  },
  react_to_messages: {
    label: 'React to Messages',
    description: 'Add reactions to messages',
  },
  view_messages: {
    label: 'View Messages',
    description: 'Read group messages and discussions',
  },
}

const ROLE_PERMISSIONS: Record<GroupRole, Permission[]> = {
  admin: [
    'manage_group',
    'delete_group',
    'manage_members',
    'change_roles',
    'remove_members',
    'invite_members',
    'update_settings',
    'pin_messages',
    'unpin_messages',
    'delete_any_message',
    'edit_any_message',
    'post_messages',
    'react_to_messages',
    'view_messages',
  ],
  moderator: [
    'invite_members',
    'pin_messages',
    'unpin_messages',
    'delete_any_message',
    'post_messages',
    'react_to_messages',
    'view_messages',
  ],
  member: [
    'post_messages',
    'react_to_messages',
    'view_messages',
  ],
}

export default function PermissionsInfoDialog({
  open,
  onOpenChange,
}: PermissionsInfoDialogProps) {
  const roles: GroupRole[] = ['admin', 'moderator', 'member']

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

  const allPermissions = Object.keys(PERMISSION_DETAILS) as Permission[]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Group Roles & Permissions</DialogTitle>
          <DialogDescription>
            Understand what each role can do within group discussions
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-6 py-2">
            {roles.map((role) => (
              <div key={role}>
                <div className="flex items-center gap-3 mb-4">
                  {getRoleIcon(role)}
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold">{getRoleDisplayName(role)}</h3>
                      <Badge variant="outline" className={getRoleBadgeClass(role)}>
                        {role}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {getRoleDescription(role)}
                    </p>
                  </div>
                </div>

                <div className="grid gap-2 ml-8">
                  {allPermissions.map((permission) => {
                    const hasPermission = ROLE_PERMISSIONS[role].includes(permission)
                    const details = PERMISSION_DETAILS[permission]

                    return (
                      <div
                        key={permission}
                        className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                          hasPermission
                            ? 'bg-primary/5 border-primary/20'
                            : 'bg-muted/30 border-border/50 opacity-50'
                        }`}
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          {hasPermission ? (
                            <Check size={18} weight="bold" className="text-primary" />
                          ) : (
                            <X size={18} weight="bold" className="text-muted-foreground" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm">{details.label}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {details.description}
                          </p>
                        </div>
                      </div>
                    )
                  })}
                </div>

                {role !== 'member' && <Separator className="mt-6" />}
              </div>
            ))}

            <div className="bg-muted/30 border border-border rounded-lg p-4 mt-6">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Crown size={18} weight="fill" className="text-amber-500" />
                Group Creator
              </h4>
              <p className="text-sm text-muted-foreground">
                The user who creates a group is automatically assigned the <strong>Admin</strong> role.
                Admins have full control and can promote other members to Admin or Moderator roles.
              </p>
            </div>

            <div className="bg-muted/30 border border-border rounded-lg p-4">
              <h4 className="font-semibold mb-2">Note on Group Settings</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Some permissions are affected by group settings:
              </p>
              <ul className="text-sm text-muted-foreground space-y-2 list-disc list-inside">
                <li>
                  <strong>Anyone can post (Unrestricted):</strong> When enabled, all members can post messages freely
                </li>
                <li>
                  <strong>Restricted Group:</strong> When "Anyone can post" is disabled, only Admins and Moderators can send messages. This is useful for announcement channels or moderated discussions.
                </li>
                <li>
                  <strong>Allow member invites:</strong> When disabled, only Admins can invite new members
                </li>
              </ul>
            </div>

            <div className="bg-amber-500/10 border border-amber-200 rounded-lg p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2 text-amber-700">
                <ShieldCheck size={18} weight="fill" />
                Testing Moderator Permissions
              </h4>
              <p className="text-sm text-amber-700 mb-2">
                Want to see moderator permissions in action? Here's how:
              </p>
              <ol className="text-sm text-amber-700 space-y-1 list-decimal list-inside">
                <li>Create a restricted group (disable "Anyone can post")</li>
                <li>Have an admin promote you to moderator in Admin Settings</li>
                <li>Try posting messages, pinning content, and deleting messages</li>
                <li>Use the Moderator Test Panel to verify your permissions</li>
              </ol>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
