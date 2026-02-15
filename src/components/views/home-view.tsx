import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { MagnifyingGlass, BookmarkSimple, ClockCounterClockwise, Books, ChartBar, Warning, Scales, Scroll, GlobeHemisphereWest, ArrowSquareOut, Shield, Star } from '@phosphor-icons/react'
import { Bookmark, Jurisdiction } from '@/lib/types'
import { CitationLibraryStats } from '@/components/citation-library-stats'
import { useState } from 'react'

interface HomeViewProps {
  selectedJurisdiction?: Jurisdiction
  recentBookmarks: Bookmark[]
  onSearch: (query: string) => void
  onNavigateToLibrary: () => void
  onNavigateToAnalyzer: () => void
  onNavigateToBookmark: (bookmark: Bookmark) => void
  onNavigateToCitations: () => void
  onNavigateToCaseLaw?: () => void
  onNavigateToFederalRegister?: () => void
  onNavigateToResources?: () => void
}

export function HomeView({
  selectedJurisdiction,
  recentBookmarks,
  onSearch,
  onNavigateToLibrary,
  onNavigateToAnalyzer,
  onNavigateToBookmark,
  onNavigateToCitations,
  onNavigateToCaseLaw,
  onNavigateToFederalRegister,
  onNavigateToResources,
}: HomeViewProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = () => {
    if (searchQuery.trim()) {
      onSearch(searchQuery)
    }
  }

  return (
    <div className="space-y-6">
      {/* ── Hero Section ───────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-xl bg-gradient-to-br from-primary via-primary to-[oklch(0.35_0.07_250)] dark:from-[oklch(0.14_0.025_255)] dark:via-[oklch(0.18_0.03_252)] dark:to-[oklch(0.22_0.04_250)] px-5 py-8 md:px-8 md:py-12 shadow-lg">
        {/* Decorative stars */}
        <div className="absolute top-4 right-6 flex gap-1.5 opacity-20">
          <Star size={14} weight="fill" className="text-accent" />
          <Star size={10} weight="fill" className="text-accent" />
          <Star size={14} weight="fill" className="text-accent" />
        </div>
        <div className="absolute bottom-4 left-6 flex gap-1.5 opacity-15">
          <Star size={10} weight="fill" className="text-primary-foreground" />
          <Star size={14} weight="fill" className="text-primary-foreground" />
          <Star size={10} weight="fill" className="text-primary-foreground" />
        </div>
        <div className="relative z-10 max-w-2xl">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={24} weight="fill" className="text-accent" />
            <span className="text-xs uppercase tracking-[0.2em] font-semibold text-accent">
              Constitutional Research Platform
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight font-serif text-primary-foreground leading-tight">
            Understand the
            <span className="block text-accent">Hierarchy of Law</span>
          </h2>
          <p className="text-primary-foreground/70 mt-2 text-sm md:text-base max-w-lg leading-relaxed">
            Explore every layer of American law — from the U.S. Constitution to local ordinances — with primary sources and live legal data.
          </p>

          <div className="flex gap-2 mt-5">
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlass
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <Input
                placeholder="Search amendments, statutes, case law..."
                className="pl-9 h-9 bg-white/95 dark:bg-white/10 border-white/30 text-foreground dark:text-primary-foreground placeholder:text-muted-foreground text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch} size="sm" className="h-9 bg-accent text-accent-foreground hover:bg-accent/90 font-semibold shadow-sm px-5">
              Search
            </Button>
          </div>
        </div>
      </section>

      {selectedJurisdiction && (
        <Card className="bg-gradient-to-r from-primary/5 to-accent/5 border-primary/20 dark:from-primary/10 dark:to-accent/10 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-serif">Your Jurisdiction</CardTitle>
            <CardDescription>
              Currently viewing laws for {selectedJurisdiction.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={onNavigateToLibrary} className="w-full bg-primary hover:bg-primary/90">
              <Books size={18} />
              View My Legal Stack
            </Button>
          </CardContent>
        </Card>
      )}

      {/* ── Stats strip ────────────────────────────────────────────── */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card className="border-l-4 border-l-primary shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="p-4 pb-2">
            <CardDescription className="text-[10px] uppercase tracking-wider font-semibold text-primary/70 dark:text-primary/80">Database Size</CardDescription>
            <CardTitle className="text-2xl font-bold font-serif text-primary dark:text-primary">50+ States</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 pt-0">
            <p className="text-xs text-muted-foreground leading-relaxed">
              All 50 state constitutions plus 6 territories
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-destructive shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="p-4 pb-2">
            <CardDescription className="text-[10px] uppercase tracking-wider font-semibold text-destructive/70 dark:text-destructive/80">Federal Sources</CardDescription>
            <CardTitle className="text-2xl font-bold font-serif">Statutes & Treaties</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 pt-0">
            <p className="text-xs text-muted-foreground leading-relaxed">
              U.S. Code, federal laws, and international treaties
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-accent shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="p-4 pb-2">
            <CardDescription className="text-[10px] uppercase tracking-wider font-semibold text-accent-foreground/70 dark:text-accent/80">Full-Text Search</CardDescription>
            <CardTitle className="text-2xl font-bold font-serif">Advanced</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 pt-0">
            <p className="text-xs text-muted-foreground leading-relaxed">
              Search across all documents with filters
            </p>
          </CardContent>
        </Card>
      </section>

      {/* ── Core Features ─────────────────────────────────────────── */}
      <section className="grid sm:grid-cols-2 gap-3">
        <Card className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 group border-primary/10" onClick={onNavigateToLibrary}>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-primary/10 dark:bg-primary/20 group-hover:bg-primary/15 transition-colors">
                <Books size={24} className="text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg font-serif">Constitutional Library</CardTitle>
                <CardDescription>
                  Browse U.S. Constitution, state documents, and federal statutes
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>

        <Card className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 group border-accent/10" onClick={onNavigateToAnalyzer}>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-accent/10 dark:bg-accent/20 group-hover:bg-accent/15 transition-colors">
                <ChartBar size={24} className="text-accent-foreground dark:text-accent" />
              </div>
              <div>
                <CardTitle className="text-lg font-serif">Conflict Analyzer</CardTitle>
                <CardDescription>
                  Learn to evaluate legal conflicts and preemption
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>
      </section>

      {/* ── Live Legal Data APIs ────────────────────────────────── */}
      <section className="space-y-2.5">
        <h3 className="text-base font-semibold font-serif flex items-center gap-2">
          <Scales size={18} className="text-primary dark:text-accent" weight="duotone" />
          Live Legal Data
          <span className="ml-1 text-[9px] uppercase tracking-wider bg-destructive/10 text-destructive dark:bg-destructive/20 dark:text-destructive px-1.5 py-0.5 rounded-full font-sans font-semibold">Live</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {onNavigateToCaseLaw && (
            <Card className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 group border-primary/20 dark:border-primary/30" onClick={onNavigateToCaseLaw}>
              <CardContent className="flex items-center gap-3 p-4">
                <div className="p-2 rounded-lg bg-primary/10 dark:bg-primary/20 group-hover:bg-primary/15 transition-colors">
                  <Scales size={22} className="text-primary dark:text-primary" weight="duotone" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Case Law Search</p>
                  <p className="text-xs text-muted-foreground">CourtListener — millions of opinions</p>
                </div>
              </CardContent>
            </Card>
          )}
          {onNavigateToFederalRegister && (
            <Card className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 group border-accent/20 dark:border-accent/30" onClick={onNavigateToFederalRegister}>
              <CardContent className="flex items-center gap-3 p-4">
                <div className="p-2 rounded-lg bg-accent/10 dark:bg-accent/20 group-hover:bg-accent/15 transition-colors">
                  <Scroll size={22} className="text-accent-foreground dark:text-accent" weight="duotone" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Federal Register</p>
                  <p className="text-xs text-muted-foreground">Executive orders, rules & regs</p>
                </div>
              </CardContent>
            </Card>
          )}
          {onNavigateToResources && (
            <Card className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 group border-primary/10 dark:border-primary/20" onClick={onNavigateToResources}>
              <CardContent className="flex items-center gap-3 p-4">
                <div className="p-2 rounded-lg bg-primary/5 dark:bg-primary/15 group-hover:bg-primary/10 transition-colors">
                  <GlobeHemisphereWest size={22} className="text-primary dark:text-primary" weight="duotone" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Legal Resources</p>
                  <p className="text-xs text-muted-foreground">16+ free research databases</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
        <Warning className="h-4 w-4 text-accent-foreground dark:text-accent" weight="fill" />
        <AlertDescription className="text-xs text-foreground/80 dark:text-foreground/70">
          <strong>Educational Resource Only.</strong> This platform provides access to constitutional and statutory text for educational purposes. It does not constitute legal advice, create an attorney-client relationship, or substitute for consultation with a licensed attorney. All source text should be independently verified against official government publications.
        </AlertDescription>
      </Alert>

      <CitationLibraryStats onNavigateToCitations={onNavigateToCitations} />

      {recentBookmarks.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <ClockCounterClockwise size={20} className="text-muted-foreground" />
            <h3 className="font-semibold">Recent Bookmarks</h3>
          </div>
          <div className="space-y-2">
            {recentBookmarks.slice(0, 5).map((bookmark) => (
              <Card
                key={bookmark.id}
                className="cursor-pointer transition-shadow hover:shadow-sm"
                onClick={() => onNavigateToBookmark(bookmark)}
              >
                <CardContent className="flex items-center gap-3 py-3">
                  <BookmarkSimple size={18} className="text-primary" weight="fill" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {bookmark.note || 'Bookmarked section'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(bookmark.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
