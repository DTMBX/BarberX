import { Badge } from '@/components/ui/badge'
import { Document } from '@/lib/types'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: Document['status']
  className?: string
}

const statusConfig = {
  downloaded: {
    label: 'Downloaded',
    className: 'bg-[oklch(0.60_0.15_210)] text-white'
  },
  extracting: {
    label: 'Extracting',
    className: 'bg-[oklch(0.65_0.10_70)] text-[oklch(0.15_0.01_250)]'
  },
  extracted: {
    label: 'Extracted',
    className: 'bg-[oklch(0.65_0.15_160)] text-white'
  },
  ocr: {
    label: 'OCR',
    className: 'bg-[oklch(0.70_0.15_280)] text-white'
  },
  indexed: {
    label: 'Indexed',
    className: 'bg-[oklch(0.60_0.18_145)] text-white'
  },
  error: {
    label: 'Error',
    className: 'bg-destructive text-destructive-foreground'
  }
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <Badge className={cn(config.className, 'font-medium', className)}>
      {config.label}
    </Badge>
  )
}
