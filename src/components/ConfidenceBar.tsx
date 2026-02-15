import { cn } from '@/lib/utils'

interface ConfidenceBarProps {
  confidence: number
  className?: string
  showLabel?: boolean
}

export function ConfidenceBar({ confidence, className, showLabel = true }: ConfidenceBarProps) {
  const percentage = Math.round(confidence * 100)
  
  const getColor = () => {
    if (confidence >= 0.8) return 'bg-accent'
    if (confidence >= 0.6) return 'bg-[oklch(0.65_0.15_160)]'
    if (confidence >= 0.4) return 'bg-[oklch(0.65_0.10_70)]'
    return 'bg-muted-foreground/50'
  }
  
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div 
          className={cn('h-full transition-all duration-300', getColor())}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs font-mono text-muted-foreground min-w-[3ch]">
          {percentage}%
        </span>
      )}
    </div>
  )
}
