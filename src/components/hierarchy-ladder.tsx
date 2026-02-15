import { HIERARCHY_LADDER_RUNGS, buildHierarchyTree } from '@/lib/hierarchy'
import { Document, Section, AuthorityLevel } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import {
  Scales,
  FileText,
  Globe,
  Bank,
  MapPin,
  CaretRight,
  Shield,
} from '@phosphor-icons/react'

interface HierarchyLadderProps {
  documents: Document[]
  sections: Section[]
  selectedJurisdictionId?: string
  activeDocumentId?: string
  onNavigate: (route: string, params?: Record<string, string>) => void
}

const LEVEL_ICONS: Record<number, React.ReactNode> = {
  1: <Shield size={18} weight="fill" />,
  2: <FileText size={18} />,
  3: <Globe size={18} />,
  4: <Bank size={18} />,
  5: <FileText size={18} />,
  6: <Scales size={18} weight="fill" />,
  7: <FileText size={18} />,
  8: <FileText size={18} />,
  9: <MapPin size={18} />,
}

const LEVEL_COLORS: Record<AuthorityLevel, string> = {
  federal: 'bg-primary/15 text-primary dark:bg-primary/25 dark:text-primary',
  state: 'bg-accent/15 text-accent-foreground dark:bg-accent/25 dark:text-accent',
  territory: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
  local: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
}

export function HierarchyLadder({
  documents,
  sections,
  selectedJurisdictionId,
  activeDocumentId,
  onNavigate,
}: HierarchyLadderProps) {
  const tree = buildHierarchyTree(documents, sections, selectedJurisdictionId)

  return (
    <aside
      className="hidden md:flex flex-col w-64 lg:w-72 border-r border-border bg-sidebar text-sidebar-foreground shrink-0"
      role="navigation"
      aria-label="Authority Hierarchy"
    >
      <div className="px-4 py-3 border-b border-sidebar-border">
        <h2 className="text-xs font-semibold tracking-widest uppercase text-primary dark:text-sidebar-primary">
          Authority Hierarchy
        </h2>
        <p className="text-[11px] text-muted-foreground dark:text-sidebar-foreground/60 mt-0.5">
          Highest → Lowest authority
        </p>
      </div>

      <ScrollArea className="flex-1">
        <nav className="py-2" aria-label="Hierarchy ladder">
          {HIERARCHY_LADDER_RUNGS.map((rung, idx) => {
            const node = tree.find(n => n.level === rung.level)
            const sectionCount = node?.sectionCount ?? 0
            const isActive = node?.documentId === activeDocumentId

            // Route mapping
            let route = 'supreme-law'
            const params: Record<string, string> = {}
            if (rung.level <= 5) {
              route = rung.documentType === 'treaty' ? 'treaties' : 'supreme-law'
            } else if (rung.level <= 8) {
              route = 'my-jurisdiction'
            } else {
              route = 'local'
            }

            return (
              <div key={rung.level}>
                <button
                  onClick={() => onNavigate(route, params)}
                  className={cn(
                    'w-full flex items-center gap-2.5 px-3 py-2 text-left text-sm transition-colors hover:bg-sidebar-accent group',
                    isActive && 'bg-sidebar-accent border-l-2 border-sidebar-primary'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <span
                    className={cn(
                      'flex items-center justify-center w-7 h-7 rounded-md shrink-0',
                      LEVEL_COLORS[rung.authorityLevel]
                    )}
                  >
                    {LEVEL_ICONS[rung.level]}
                  </span>

                  <div className="min-w-0 flex-1">
                    <div className="font-medium truncate leading-tight text-[13px]">
                      {rung.label}
                    </div>
                    <div className="text-[11px] text-muted-foreground leading-tight">
                      Level {rung.level}
                      {sectionCount > 0 && ` · ${sectionCount}`}
                    </div>
                  </div>

                  <CaretRight
                    size={12}
                    className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                  />
                </button>

                {/* Connecting line between rungs */}
                {idx < HIERARCHY_LADDER_RUNGS.length - 1 && (
                  <div className="ml-[22px]">
                    <div className="w-px h-1.5 bg-sidebar-border" />
                  </div>
                )}
              </div>
            )
          })}
        </nav>
      </ScrollArea>

      {/* Legend */}
      <div className="px-3 py-2.5 border-t border-sidebar-border text-[11px] text-muted-foreground dark:text-sidebar-foreground/60 flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-sm bg-primary/30 dark:bg-primary/40" />
          Federal
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-sm bg-accent/40 dark:bg-accent/50" />
          State
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-sm bg-emerald-200 dark:bg-emerald-800" />
          Local
        </div>
      </div>
    </aside>
  )
}
