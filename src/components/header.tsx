import { Button } from '@/components/ui/button'
import { MapPin, Gear, MagnifyingGlass, GraduationCap, Books, ChartBar, Scales, Scroll, GlobeHemisphereWest, Sun, Moon, Shield, ShieldCheck } from '@phosphor-icons/react'
import { Jurisdiction, RouteId } from '@/lib/types'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import { useTheme } from 'next-themes'

interface HeaderProps {
  selectedJurisdiction?: Jurisdiction
  jurisdictions: Jurisdiction[]
  onJurisdictionChange: (id: string) => void
  onSettingsClick: () => void
  activeRoute?: RouteId
  onNavigate?: (route: RouteId) => void
  isAdmin?: boolean
}

export function Header({
  selectedJurisdiction,
  jurisdictions,
  onJurisdictionChange,
  onSettingsClick,
  activeRoute,
  onNavigate,
  isAdmin = false,
}: HeaderProps) {
  const statesAndTerritories = jurisdictions.filter(
    j => j.type === 'state' || j.type === 'territory'
  )

  const { theme, setTheme } = useTheme()

  const desktopNavItems: { id: RouteId; label: string; icon: typeof MagnifyingGlass }[] = [
    { id: 'search', label: 'Search', icon: MagnifyingGlass },
    { id: 'case-law', label: 'Case Law', icon: Scales },
    { id: 'federal-register', label: 'Fed. Register', icon: Scroll },
    { id: 'legal-resources', label: 'Resources', icon: GlobeHemisphereWest },
    { id: 'citations', label: 'Citations', icon: Books },
    { id: 'analyzer', label: 'Analyze', icon: ChartBar },
  ]

  return (
    <header className="sticky top-0 z-40 border-b-2 border-accent/60 bg-gradient-to-r from-primary via-primary to-[oklch(0.25_0.06_250)] dark:from-[oklch(0.14_0.025_255)] dark:via-[oklch(0.16_0.025_255)] dark:to-[oklch(0.18_0.03_252)] shadow-md">
      {/* Thin flag-stripe accent bar */}
      <div className="h-[3px] bg-gradient-to-r from-destructive via-accent to-primary" />

      <div className="flex items-center gap-3 px-3 py-2 md:px-5">
        {/* Left: Logo + Nav */}
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <button
            className="flex items-center gap-2 hover:opacity-90 transition-opacity shrink-0"
            onClick={() => onNavigate?.('home')}
          >
            <Shield size={26} weight="fill" className="text-accent" />
            <div className="leading-none">
              <h1 className="text-lg md:text-xl font-bold tracking-tight font-serif text-primary-foreground">
                Civics Stack
              </h1>
              <span className="hidden md:block text-[10px] uppercase tracking-[0.2em] text-primary-foreground/60 font-sans font-medium mt-px">
                We the People
              </span>
            </div>
          </button>

          {/* Desktop nav links */}
          {onNavigate && (
            <nav className="hidden lg:flex items-center ml-2" aria-label="Quick links">
              {desktopNavItems.map(item => {
                const Icon = item.icon
                const isActive = activeRoute === item.id
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                    size="sm"
                    className={cn(
                      'gap-1 px-2.5 h-8 text-[13px] text-primary-foreground/70 hover:text-primary-foreground hover:bg-white/10 rounded-md',
                      isActive && 'text-accent font-semibold bg-white/10'
                    )}
                    onClick={() => onNavigate(item.id)}
                  >
                    <Icon size={15} weight={isActive ? 'fill' : 'regular'} />
                    {item.label}
                  </Button>
                )
              })}
            </nav>
          )}
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          <Select
            value={selectedJurisdiction?.id}
            onValueChange={onJurisdictionChange}
          >
            <SelectTrigger className="w-[120px] md:w-[180px] h-8 bg-white/10 border-white/20 text-primary-foreground text-xs md:text-sm">
              <div className="flex items-center gap-1.5 truncate">
                <MapPin size={14} className="shrink-0" />
                <SelectValue placeholder="Jurisdiction" />
              </div>
            </SelectTrigger>
            <SelectContent>
              {statesAndTerritories.map((j) => (
                <SelectItem key={j.id} value={j.id}>
                  {j.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-primary-foreground/70 hover:text-accent hover:bg-white/10"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label="Toggle dark mode"
          >
            <Sun size={18} className="block dark:hidden" />
            <Moon size={18} className="hidden dark:block" />
          </Button>

          <Button variant="ghost" size="icon" className="h-8 w-8 text-primary-foreground/70 hover:text-primary-foreground hover:bg-white/10" onClick={onSettingsClick}>
            <Gear size={18} />
          </Button>

          {isAdmin && onNavigate && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-primary-foreground/70 hover:text-accent hover:bg-white/10"
              onClick={() => onNavigate('admin-observability')}
              title="Admin Console"
            >
              <ShieldCheck size={18} weight={activeRoute === 'admin-observability' ? 'fill' : 'regular'} />
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
