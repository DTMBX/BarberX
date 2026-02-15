import type { GroupDiscussion } from './types'

export type GroupRole = 'admin' | 'moderator' | 'member'

export type Permission =
  | 'manage_group'
  | 'delete_group'
  | 'manage_members'
  | 'change_roles'
  | 'remove_members'
  | 'invite_members'
  | 'update_settings'
  | 'pin_messages'
  | 'unpin_messages'
  | 'delete_any_message'
  | 'edit_any_message'
  | 'post_messages'
  | 'react_to_messages'
  | 'view_messages'

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

export function hasPermission(
  role: GroupRole | undefined,
  permission: Permission,
  group?: GroupDiscussion
): boolean {
  if (!role) return false

  if (group && !group.settings.anyoneCanPost && permission === 'post_messages') {
    return role === 'admin' || role === 'moderator'
  }

  const permissions = ROLE_PERMISSIONS[role]
  return permissions.includes(permission)
}

export function canManageGroup(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'manage_group')
}

export function canDeleteGroup(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'delete_group')
}

export function canManageMembers(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'manage_members')
}

export function canChangeRoles(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'change_roles')
}

export function canRemoveMembers(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'remove_members')
}

export function canInviteMembers(
  role: GroupRole | undefined,
  group?: GroupDiscussion
): boolean {
  if (!group) return hasPermission(role, 'invite_members')
  
  if (!group.settings.allowInvites) {
    return role === 'admin'
  }
  
  return hasPermission(role, 'invite_members')
}

export function canUpdateSettings(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'update_settings')
}

export function canPinMessages(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'pin_messages')
}

export function canUnpinMessages(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'unpin_messages')
}

export function canDeleteAnyMessage(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'delete_any_message')
}

export function canEditAnyMessage(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'edit_any_message')
}

export function canPostMessages(
  role: GroupRole | undefined,
  group?: GroupDiscussion
): boolean {
  return hasPermission(role, 'post_messages', group)
}

export function canReactToMessages(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'react_to_messages')
}

export function canViewMessages(role: GroupRole | undefined): boolean {
  return hasPermission(role, 'view_messages')
}

export function canDeleteMessage(
  role: GroupRole | undefined,
  messageUserId: string,
  currentUserId: string
): boolean {
  if (messageUserId === currentUserId) return true
  
  return canDeleteAnyMessage(role)
}

export function canEditMessage(
  role: GroupRole | undefined,
  messageUserId: string,
  currentUserId: string
): boolean {
  if (messageUserId === currentUserId) return true
  
  return canEditAnyMessage(role)
}

export function getUserRole(
  group: GroupDiscussion | undefined,
  userId: string
): GroupRole | undefined {
  if (!group) return undefined
  
  const member = group.members.find(m => m.userId === userId)
  return member?.role
}

export function getRoleDisplayName(role: GroupRole): string {
  const displayNames: Record<GroupRole, string> = {
    admin: 'Admin',
    moderator: 'Moderator',
    member: 'Member',
  }
  return displayNames[role]
}

export function getRoleDescription(role: GroupRole): string {
  const descriptions: Record<GroupRole, string> = {
    admin: 'Full control over group settings, members, and content',
    moderator: 'Can moderate content, pin messages, delete messages, and invite members',
    member: 'Can participate in discussions and react to messages',
  }
  return descriptions[role]
}

export function getPermissionsByRole(role: GroupRole): Permission[] {
  return ROLE_PERMISSIONS[role]
}

export function getAllPermissions(): Permission[] {
  return [
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
  ]
}

export function getPermissionLabel(permission: Permission): string {
  const labels: Record<Permission, string> = {
    manage_group: 'Manage Group',
    delete_group: 'Delete Group',
    manage_members: 'Manage Members',
    change_roles: 'Change Roles',
    remove_members: 'Remove Members',
    invite_members: 'Invite Members',
    update_settings: 'Update Settings',
    pin_messages: 'Pin Messages',
    unpin_messages: 'Unpin Messages',
    delete_any_message: 'Delete Any Message',
    edit_any_message: 'Edit Any Message',
    post_messages: 'Post Messages',
    react_to_messages: 'React to Messages',
    view_messages: 'View Messages',
  }
  return labels[permission]
}

export function canPromoteToRole(
  currentUserRole: GroupRole | undefined,
  targetRole: GroupRole
): boolean {
  if (!canChangeRoles(currentUserRole)) return false
  
  if (currentUserRole === 'admin') return true
  
  return false
}
