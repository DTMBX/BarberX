import { CaretRight, House } from '@phosphor-icons/react'

interface BreadcrumbItem {
  label: string
  route?: string
  params?: Record<string, string>
}

interface BreadcrumbNavProps {
  items: BreadcrumbItem[]
  onNavigate: (route: string, params?: Record<string, string>) => void
}

export function BreadcrumbNav({ items, onNavigate }: BreadcrumbNavProps) {
  if (items.length === 0) return null

  return (
    <nav
      aria-label="Breadcrumb"
      className="flex items-center gap-1 text-xs text-muted-foreground py-1.5 overflow-x-auto scrollbar-none"
    >
      <button
        onClick={() => onNavigate('home')}
        className="flex items-center gap-1 hover:text-foreground transition-colors shrink-0"
        aria-label="Home"
      >
        <House size={14} />
      </button>

      {items.map((item, idx) => {
        const isLast = idx === items.length - 1

        return (
          <span key={idx} className="flex items-center gap-1 min-w-0">
            <CaretRight size={12} className="text-muted-foreground/50 shrink-0" />
            {isLast || !item.route ? (
              <span
                className={`truncate ${isLast ? 'text-foreground font-medium' : ''}`}
                aria-current={isLast ? 'page' : undefined}
              >
                {item.label}
              </span>
            ) : (
              <button
                onClick={() => onNavigate(item.route!, item.params)}
                className="hover:text-foreground transition-colors truncate"
              >
                {item.label}
              </button>
            )}
          </span>
        )
      })}
    </nav>
  )
}
