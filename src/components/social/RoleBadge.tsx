import { Badge } from '@/components/ui/badge'
import { Crown, ShieldCheck, User } from '@phosphor-icons/react'
import type { GroupRole } from '@/lib/permissions'

interface RoleBadgeProps {
  role: GroupRole
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
}

export default function RoleBadge({ role, size = 'md', showIcon = true }: RoleBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs h-5 px-1.5',
    md: 'text-xs h-6 px-2',
    lg: 'text-sm h-7 px-3',
  }

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16,
  }

  const getRoleConfig = (role: GroupRole) => {
    switch (role) {
      case 'admin':
        return {
          icon: Crown,
          label: 'Admin',
          className: 'bg-amber-500/10 text-amber-700 border-amber-300 hover:bg-amber-500/20',
        }
      case 'moderator':
        return {
          icon: ShieldCheck,
          label: 'Moderator',
          className: 'bg-blue-500/10 text-blue-700 border-blue-300 hover:bg-blue-500/20',
        }
      case 'member':
        return {
          icon: User,
          label: 'Member',
          className: 'bg-muted text-muted-foreground border-border hover:bg-muted/80',
        }
    }
  }

  const config = getRoleConfig(role)
  const Icon = config.icon

  return (
    <Badge
      variant="outline"
      className={`${sizeClasses[size]} ${config.className} flex items-center gap-1 font-medium`}
    >
      {showIcon && <Icon size={iconSizes[size]} weight="fill" />}
      {config.label}
    </Badge>
  )
}
