import { QualityMetrics } from '@/lib/types'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  Warning, 
  XCircle,
  ChartLineUp,
  Eye,
  TextAlignLeft,
  SealWarning
} from '@phosphor-icons/react'

interface QualityBadgeProps {
  metrics: QualityMetrics
  compact?: boolean
}

export function QualityBadge({ metrics, compact = false }: QualityBadgeProps) {
  const getQualityLevel = (score: number) => {
    if (score >= 0.85) return { label: 'Excellent', color: 'bg-[oklch(0.60_0.18_145)] text-foreground', icon: CheckCircle }
    if (score >= 0.70) return { label: 'Good', color: 'bg-[oklch(0.65_0.15_160)] text-foreground', icon: CheckCircle }
    if (score >= 0.50) return { label: 'Fair', color: 'bg-accent text-accent-foreground', icon: Warning }
    if (score >= 0.30) return { label: 'Poor', color: 'bg-[oklch(0.60_0.22_25)]/80 text-foreground', icon: Warning }
    return { label: 'Very Poor', color: 'bg-destructive text-destructive-foreground', icon: XCircle }
  }

  const quality = getQualityLevel(metrics.overallScore)
  const Icon = quality.icon

  if (compact) {
    return (
      <Badge className={quality.color}>
        <Icon size={12} weight="bold" className="mr-1" />
        Quality: {quality.label}
      </Badge>
    )
  }

  return (
    <Card className={`border-2 ${
      metrics.flaggedForReview ? 'border-accent' : 
      metrics.reprocessRecommended ? 'border-destructive' : 
      'border-border'
    }`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Icon className={quality.color.includes('destructive') ? 'text-destructive' : 
                             quality.color.includes('accent') ? 'text-accent' : 
                             'text-[oklch(0.60_0.18_145)]'} size={20} weight="duotone" />
              <span className="text-lg font-bold">{quality.label}</span>
              <Badge variant="outline" className="ml-2">
                {(metrics.overallScore * 100).toFixed(0)}%
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Overall Quality Score
            </p>
          </div>
          {metrics.flaggedForReview && (
            <Badge className="bg-accent text-accent-foreground">
              <Warning size={12} weight="bold" className="mr-1" />
              Flagged
            </Badge>
          )}
          {metrics.reprocessRecommended && (
            <Badge className="bg-destructive text-destructive-foreground">
              <SealWarning size={12} weight="bold" className="mr-1" />
              Reprocess
            </Badge>
          )}
        </div>

        <div className="space-y-3">
          <MetricBar 
            label="Text Density" 
            value={metrics.textDensity} 
            icon={TextAlignLeft}
            description="Characters per page area"
          />
          <MetricBar 
            label="OCR Confidence" 
            value={metrics.ocrConfidenceProxy} 
            icon={Eye}
            description="Estimated recognition quality"
          />
          <MetricBar 
            label="Character Accuracy" 
            value={1 - metrics.characterErrorRate} 
            icon={CheckCircle}
            description="Estimated error rate"
          />
          <MetricBar 
            label="Layout Quality" 
            value={metrics.layoutQuality} 
            icon={ChartLineUp}
            description="Structural consistency"
          />
          <MetricBar 
            label="Readability" 
            value={metrics.readabilityScore} 
            icon={TextAlignLeft}
            description="Language coherence"
          />
        </div>

        {metrics.pageNo && (
          <div className="text-xs text-muted-foreground mt-3 pt-3 border-t">
            Page-level metrics for page {metrics.pageNo}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface MetricBarProps {
  label: string
  value: number
  icon: any
  description: string
}

function MetricBar({ label, value, icon: Icon, description }: MetricBarProps) {
  const percentage = Math.round(value * 100)
  const color = value >= 0.7 ? '[oklch(0.60_0.18_145)]' : 
                value >= 0.5 ? 'accent' : 
                'destructive'

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <Icon size={14} className="text-muted-foreground" />
          <span className="text-sm font-medium">{label}</span>
        </div>
        <span className="text-sm text-muted-foreground">{percentage}%</span>
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-primary/20">
        <div 
          className={`h-full transition-all bg-${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
    </div>
  )
}
