import { useState } from 'react'
import {
  House,
  Scales,
  MapPin,
  MagnifyingGlass,
  ChartBar,
  GlobeHemisphereWest,
  Books,
  GraduationCap,
  DotsThreeOutline,
  Scroll,
  Gavel,
} from '@phosphor-icons/react'
import { cn } from '@/lib/utils'
import type { RouteId } from '@/lib/types'

interface MobileNavProps {
  activeTab: RouteId
  onTabChange: (tab: RouteId) => void
}

type NavTab = { id: RouteId; label: string; icon: typeof House }

const PRIMARY_TABS: NavTab[] = [
  { id: 'home', label: 'Home', icon: House },
  { id: 'supreme-law', label: 'Supreme', icon: Scales },
  { id: 'my-jurisdiction', label: 'My State', icon: MapPin },
  { id: 'search', label: 'Search', icon: MagnifyingGlass },
]

const OVERFLOW_TABS: NavTab[] = [
  { id: 'case-law', label: 'Case Law', icon: Gavel },
  { id: 'federal-register', label: 'Fed. Register', icon: Scroll },
  { id: 'legal-resources', label: 'Resources', icon: GlobeHemisphereWest },
  { id: 'treaties', label: 'Treaties', icon: GlobeHemisphereWest },
  { id: 'citations', label: 'Citations', icon: Books },
  { id: 'learn', label: 'Learn', icon: GraduationCap },
  { id: 'analyzer', label: 'Analyze', icon: ChartBar },
]

export function MobileNav({ activeTab, onTabChange }: MobileNavProps) {
  const [overflowOpen, setOverflowOpen] = useState(false)

  // If the active tab is in overflow, promote it
  const isOverflowActive = OVERFLOW_TABS.some(t => t.id === activeTab)

  return (
    <>
      {/* Overflow drawer */}
      {overflowOpen && (
        <div className="fixed inset-0 z-40 md:hidden" onClick={() => setOverflowOpen(false)}>
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
          <nav
            className="absolute bottom-[calc(3.5rem+env(safe-area-inset-bottom))] left-2 right-2 bg-card border border-border rounded-xl p-3 grid grid-cols-4 gap-1.5 shadow-2xl"
            onClick={e => e.stopPropagation()}
            aria-label="More navigation options"
          >
            {OVERFLOW_TABS.map(tab => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    onTabChange(tab.id)
                    setOverflowOpen(false)
                  }}
                  className={cn(
                    'flex flex-col items-center justify-center gap-0.5 py-2.5 rounded-lg transition-colors',
                    isActive
                      ? 'text-primary bg-primary/10'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon size={20} weight={isActive ? 'fill' : 'regular'} />
                  <span className="text-[10px] font-medium leading-tight">{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>
      )}

      {/* Primary bottom bar */}
      <nav
        className="fixed bottom-0 left-0 right-0 bg-card/95 backdrop-blur-md border-t-2 border-accent/40 z-50 md:hidden shadow-[0_-2px_10px_rgba(0,0,0,0.08)] pb-[env(safe-area-inset-bottom)]"
        aria-label="Main navigation"
      >
        <div className="flex items-stretch h-14">
          {PRIMARY_TABS.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => {
                  onTabChange(tab.id)
                  setOverflowOpen(false)
                }}
                className={cn(
                  'flex flex-col items-center justify-center gap-0.5 flex-1 transition-colors',
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground active:text-foreground'
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon size={20} weight={isActive ? 'fill' : 'regular'} />
                <span className="text-[10px] font-medium leading-tight">{tab.label}</span>
              </button>
            )
          })}

          {/* More button */}
          <button
            onClick={() => setOverflowOpen(prev => !prev)}
            className={cn(
              'flex flex-col items-center justify-center gap-0.5 flex-1 transition-colors',
              isOverflowActive || overflowOpen
                ? 'text-primary'
                : 'text-muted-foreground active:text-foreground'
            )}
            aria-expanded={overflowOpen}
            aria-label="More navigation options"
          >
            <DotsThreeOutline size={20} weight={isOverflowActive || overflowOpen ? 'fill' : 'regular'} />
            <span className="text-[10px] font-medium leading-tight">More</span>
          </button>
        </div>
      </nav>
    </>
  )
}
