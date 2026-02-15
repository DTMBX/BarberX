import { Warning, Scales, SealCheck } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { DownloadSimple } from '@phosphor-icons/react'

interface DisclaimerBannerProps {
  variant?: 'legal-advice' | 'verify-sources' | 'court-use' | 'educational'
  showIcon?: boolean
  dismissible?: boolean
  onDismiss?: () => void
  showExport?: boolean
  onExport?: () => void
}

const CONFIGS = {
  'legal-advice': {
    icon: Warning,
    iconColor: 'text-destructive dark:text-destructive',
    bg: 'bg-destructive/5 dark:bg-destructive/10 border-destructive/30 dark:border-destructive/20',
    titleColor: 'text-destructive dark:text-destructive',
    textColor: 'text-foreground/80 dark:text-foreground/70',
    title: 'Not Legal Advice',
    description:
      'This is an educational tool only. It does NOT constitute legal advice and does NOT create an attorney-client relationship. For legal advice specific to your situation, consult a licensed attorney.',
  },
  'verify-sources': {
    icon: SealCheck,
    iconColor: 'text-primary dark:text-primary',
    bg: 'bg-primary/5 dark:bg-primary/10 border-primary/30 dark:border-primary/20',
    titleColor: 'text-primary dark:text-primary',
    textColor: 'text-foreground/80 dark:text-foreground/70',
    title: 'Always Verify Sources',
    description:
      'While we maintain strict verification standards, you are responsible for confirming all information through official government sources before relying on it.',
  },
  'court-use': {
    icon: Scales,
    iconColor: 'text-primary dark:text-primary',
    bg: 'bg-primary/5 dark:bg-primary/10 border-primary/25 dark:border-primary/15',
    titleColor: 'text-primary dark:text-primary',
    textColor: 'text-foreground/80 dark:text-foreground/70',
    title: 'For Court Filings',
    description:
      'Always cite directly to official government publications when preparing court documents. This educational platform is not admissible as legal authority. Consult the Bluebook or your jurisdiction citation rules.',
  },
  educational: {
    icon: Warning,
    iconColor: 'text-accent-foreground dark:text-accent',
    bg: 'bg-accent/5 dark:bg-accent/10 border-accent/25 dark:border-accent/15',
    titleColor: 'text-accent-foreground dark:text-accent',
    textColor: 'text-foreground/80 dark:text-foreground/70',
    title: 'Educational Purpose Only',
    description:
      'This application provides educational information to help you understand legal hierarchies and civic processes. It is designed to promote informed, lawful civic engagement.',
  },
} as const

export function DisclaimerBanner({
  variant = 'legal-advice',
  showIcon = true,
  dismissible = false,
  onDismiss,
  showExport = false,
  onExport,
}: DisclaimerBannerProps) {
  const config = CONFIGS[variant]
  const Icon = config.icon

  return (
    <div
      role="alert"
      className={`${config.bg} border rounded-lg px-4 py-3 flex items-start gap-3`}
    >
      {showIcon && (
        <Icon className={`h-5 w-5 ${config.iconColor} shrink-0 mt-0.5`} weight="fill" />
      )}
      <div className="flex-1 min-w-0">
        <p className={`font-semibold text-sm ${config.titleColor}`}>{config.title}</p>
        <p className={`text-xs sm:text-sm leading-relaxed mt-1 ${config.textColor}`}>
          {config.description}
        </p>
      </div>
      {(showExport || dismissible) && (
        <div className="flex items-center gap-1 shrink-0">
          {showExport && onExport && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onExport}
              className="h-7 px-2 text-xs gap-1"
            >
              <DownloadSimple className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Export</span>
            </Button>
          )}
          {dismissible && onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-7 px-2 text-xs"
            >
              Dismiss
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
