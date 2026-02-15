import { Badge } from '@/components/ui/badge'
import { AuthorityLevel, VerificationStatus } from '@/lib/types'
import { SealCheck, Warning } from '@phosphor-icons/react'
import { cn } from '@/lib/utils'

interface AuthorityBadgeProps {
  level: AuthorityLevel
  className?: string
}

export function AuthorityBadge({ level, className }: AuthorityBadgeProps) {
  const config = {
    federal: {
      label: 'Federal',
      className: 'bg-[oklch(0.42_0.10_250)] text-white hover:bg-[oklch(0.42_0.10_250)]'
    },
    state: {
      label: 'State',
      className: 'bg-[oklch(0.55_0.08_250)] text-white hover:bg-[oklch(0.55_0.08_250)]'
    },
    territory: {
      label: 'Territory',
      className: 'bg-[oklch(0.60_0.06_250)] text-white hover:bg-[oklch(0.60_0.06_250)]'
    },
    local: {
      label: 'Local',
      className: 'bg-[oklch(0.70_0.04_250)] text-white hover:bg-[oklch(0.70_0.04_250)]'
    }
  }

  const { label, className: badgeClass } = config[level]

  return (
    <Badge className={cn(badgeClass, className)}>
      {label}
    </Badge>
  )
}

interface VerificationBadgeProps {
  status: VerificationStatus
  className?: string
}

export function VerificationBadge({ status, className }: VerificationBadgeProps) {
  const config = {
    official: {
      label: 'Official Source',
      icon: SealCheck,
      className: 'bg-[oklch(0.55_0.15_145)] text-white hover:bg-[oklch(0.55_0.15_145)]'
    },
    verified: {
      label: 'Verified',
      icon: SealCheck,
      className: 'bg-[oklch(0.65_0.12_145)] text-white hover:bg-[oklch(0.65_0.12_145)]'
    },
    unverified: {
      label: 'Unverified',
      icon: Warning,
      className: 'bg-[oklch(0.72_0.15_65)] text-[oklch(0.20_0.01_260)] hover:bg-[oklch(0.72_0.15_65)]'
    }
  }

  const { label, icon: Icon, className: badgeClass } = config[status]

  return (
    <Badge className={cn('flex items-center gap-1', badgeClass, className)}>
      <Icon size={14} weight="bold" />
      {label}
    </Badge>
  )
}
