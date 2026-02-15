// ============================================================================
// Legal Resources Hub – Comprehensive Legal Research Portal
// ============================================================================
// Central dashboard linking to all major free legal research resources:
//   - CourtListener (case law)
//   - Federal Register (exec orders, regs)
//   - Congress.gov (bills, members)
//   - Cornell LII (legal encyclopedia)
//   - Oyez (SCOTUS oral arguments)
//   - Supreme Court official website
//   - GPO GovInfo (official publications)
//   - PACER (federal court filings)
//   - Google Scholar (case law)
// ============================================================================

import { useState } from 'react'
import {
  Scales,
  Buildings,
  Scroll,
  BookOpen,
  GlobeHemisphereWest,
  ArrowSquareOut,
  Gavel,
  FilePdf,
  MagnifyingGlass,
  Stamp,
  UsersThree,
  Newspaper,
  Bank,
  Certificate,
  Megaphone,
  Key,
  Warning,
  Info,
} from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  hasCongressApiKey,
  setCongressApiKey,
  clearCongressApiKey,
  buildCongressSearchUrl,
} from '@/lib/api/congress'
import type { RouteId } from '@/lib/types'
import { cn } from '@/lib/utils'

// ── Resource Cards ───────────────────────────────────────────────────
interface LegalResource {
  id: string
  name: string
  description: string
  url: string
  icon: typeof Scales
  category: 'case-law' | 'legislation' | 'regulation' | 'reference' | 'court'
  tags: string[]
  free: boolean
  highlight?: boolean
  inApp?: RouteId
}

const LEGAL_RESOURCES: LegalResource[] = [
  // ── Case Law ─────────────────────────────────────
  {
    id: 'courtlistener',
    name: 'CourtListener',
    description:
      'Free, open-source case law database with millions of opinions from federal and state courts. Citation network, SCOTUS opinions, oral arguments.',
    url: 'https://www.courtlistener.com',
    icon: Scales,
    category: 'case-law',
    tags: ['Case Law', 'SCOTUS', 'Citations', 'Oral Arguments'],
    free: true,
    highlight: true,
    inApp: 'case-law',
  },
  {
    id: 'google-scholar',
    name: 'Google Scholar',
    description:
      'Search case law and legal journals. Provides "Cited by" links showing how cases build on each other.',
    url: 'https://scholar.google.com',
    icon: MagnifyingGlass,
    category: 'case-law',
    tags: ['Case Law', 'Journals', 'Citation Analysis'],
    free: true,
  },
  {
    id: 'oyez',
    name: 'Oyez Project',
    description:
      'Supreme Court multimedia archive — oral argument audio, case summaries, justice voting records. Run by IIT Chicago-Kent.',
    url: 'https://www.oyez.org',
    icon: Megaphone,
    category: 'case-law',
    tags: ['SCOTUS', 'Oral Arguments', 'Audio', 'Voting Records'],
    free: true,
  },
  {
    id: 'scotus-official',
    name: 'Supreme Court of the U.S.',
    description:
      'Official website. Slip opinions, orders, case calendars, rules, and transcripts directly from the Court.',
    url: 'https://www.supremecourt.gov',
    icon: Bank,
    category: 'court',
    tags: ['SCOTUS', 'Official', 'Opinions', 'Orders'],
    free: true,
  },
  {
    id: 'caselaw-access',
    name: 'Caselaw Access Project',
    description:
      'Harvard Law School initiative — digitized nearly 6.9 million cases from 1658 to present. Complete U.S. case law record.',
    url: 'https://case.law',
    icon: BookOpen,
    category: 'case-law',
    tags: ['Historical', 'Complete', 'API Available'],
    free: true,
  },
  {
    id: 'justia',
    name: 'Justia',
    description:
      'Free case law, codes, regulations, and legal information for lawyers, business, students, and consumers.',
    url: 'https://law.justia.com',
    icon: Gavel,
    category: 'case-law',
    tags: ['Case Law', 'Statutes', 'Free Access'],
    free: true,
  },

  // ── Legislation ──────────────────────────────────
  {
    id: 'congress-gov',
    name: 'Congress.gov',
    description:
      'Official website for U.S. federal legislative information. Bills, resolutions, Congressional Record, members, committees.',
    url: 'https://www.congress.gov',
    icon: Buildings,
    category: 'legislation',
    tags: ['Bills', 'Members', 'Congressional Record', 'Official'],
    free: true,
    highlight: true,
  },
  {
    id: 'govinfo',
    name: 'GovInfo (GPO)',
    description:
      'Government Publishing Office — official, authenticated publications of all three branches of the Federal Government.',
    url: 'https://www.govinfo.gov',
    icon: FilePdf,
    category: 'legislation',
    tags: ['CFR', 'U.S. Code', 'Statutes at Large', 'Official'],
    free: true,
  },
  {
    id: 'uscode',
    name: 'U.S. Code (OLRC)',
    description:
      'Official U.S. Code classification from the Office of the Law Revision Counsel (House). Current, authoritative text.',
    url: 'https://uscode.house.gov',
    icon: BookOpen,
    category: 'legislation',
    tags: ['U.S. Code', 'Official', 'Current Law'],
    free: true,
  },

  // ── Regulations ──────────────────────────────────
  {
    id: 'federal-register',
    name: 'Federal Register',
    description:
      'Daily journal of the U.S. Government. Executive orders, rules, proposed rules, and notices from federal agencies.',
    url: 'https://www.federalregister.gov',
    icon: Scroll,
    category: 'regulation',
    tags: ['Executive Orders', 'Regulations', 'Agency Rules', 'API'],
    free: true,
    highlight: true,
    inApp: 'federal-register',
  },
  {
    id: 'ecfr',
    name: 'eCFR',
    description:
      'Electronic Code of Federal Regulations — current, unofficial compilation of all federal regulations, updated daily.',
    url: 'https://www.ecfr.gov',
    icon: Scroll,
    category: 'regulation',
    tags: ['CFR', 'Regulations', 'Current', 'Searchable'],
    free: true,
  },
  {
    id: 'regulations-gov',
    name: 'Regulations.gov',
    description:
      'Search, view, and comment on federal regulatory actions. Notice-and-comment rulemaking portal.',
    url: 'https://www.regulations.gov',
    icon: Newspaper,
    category: 'regulation',
    tags: ['Public Comment', 'Rulemaking', 'Dockets'],
    free: true,
  },

  // ── Reference ────────────────────────────────────
  {
    id: 'cornell-lii',
    name: 'Cornell LII',
    description:
      'Legal Information Institute — free, authoritative legal encyclopedia. Wex definitions, U.S. Code, CFR, Supreme Court opinions.',
    url: 'https://www.law.cornell.edu',
    icon: Certificate,
    category: 'reference',
    tags: ['Legal Encyclopedia', 'Wex', 'Definitions'],
    free: true,
    highlight: true,
  },
  {
    id: 'constitution-annotated',
    name: 'Constitution Annotated',
    description:
      'Congressional Research Service — analysis and interpretation of the U.S. Constitution with Supreme Court case annotations.',
    url: 'https://constitution.congress.gov',
    icon: BookOpen,
    category: 'reference',
    tags: ['Constitution', 'Analysis', 'CRS', 'Annotated'],
    free: true,
    highlight: true,
  },
  {
    id: 'nara-constitution',
    name: 'National Archives (NARA)',
    description:
      'Official transcription of the U.S. Constitution, Bill of Rights, and all Amendments from the National Archives.',
    url: 'https://www.archives.gov/founding-docs/constitution-transcript',
    icon: Stamp,
    category: 'reference',
    tags: ['Constitution', 'Official Text', 'Founding Documents'],
    free: true,
  },
  {
    id: 'pacer',
    name: 'PACER',
    description:
      'Public Access to Court Electronic Records — federal court filings and docket sheets. $0.10/page (fee waiver available).',
    url: 'https://pacer.uscourts.gov',
    icon: Gavel,
    category: 'court',
    tags: ['Court Filings', 'Dockets', 'Federal Courts'],
    free: false,
  },
]

function ResourceCard({
  resource,
  onNavigate,
}: {
  resource: LegalResource
  onNavigate?: (route: RouteId) => void
}) {
  const Icon = resource.icon
  return (
    <Card
      className={cn(
        'hover:shadow-md transition-shadow h-full',
        resource.highlight && 'border-primary/30 bg-primary/[0.02]'
      )}
    >
      <CardContent className="p-4 space-y-3 flex flex-col h-full">
        <div className="flex items-start gap-3">
          <div
            className={cn(
              'flex items-center justify-center w-9 h-9 rounded-lg shrink-0',
              resource.highlight ? 'bg-primary/10' : 'bg-muted'
            )}
          >
            <Icon
              size={18}
              className={resource.highlight ? 'text-primary' : 'text-muted-foreground'}
              weight="duotone"
            />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-sm leading-tight">
                {resource.name}
              </h3>
              {resource.free ? (
                <Badge variant="outline" className="text-[10px] shrink-0 text-green-700 border-green-300">
                  Free
                </Badge>
              ) : (
                <Badge variant="outline" className="text-[10px] shrink-0">
                  Paid
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-3">
              {resource.description}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mt-auto pt-1">
          {resource.tags.slice(0, 3).map(tag => (
            <Badge key={tag} variant="secondary" className="text-[10px]">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex gap-2 pt-1">
          {resource.inApp && onNavigate && (
            <Button
              size="sm"
              className="flex-1 gap-1.5 text-xs"
              onClick={() => onNavigate(resource.inApp!)}
            >
              Open in App
            </Button>
          )}
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className={resource.inApp ? '' : 'flex-1'}
          >
            <Button
              variant={resource.inApp ? 'outline' : 'default'}
              size="sm"
              className="gap-1.5 text-xs w-full"
            >
              <ArrowSquareOut size={14} />
              {resource.inApp ? 'Website' : 'Open'}
            </Button>
          </a>
        </div>
      </CardContent>
    </Card>
  )
}

// ── API Key Setup for Congress.gov ─────────────────────────────────────
function CongressApiSetup() {
  const [key, setKey] = useState('')
  const [hasKey, setHasKey] = useState(hasCongressApiKey())

  const handleSave = () => {
    if (key.trim()) {
      setCongressApiKey(key.trim())
      setHasKey(true)
      setKey('')
    }
  }

  const handleClear = () => {
    clearCongressApiKey()
    setHasKey(false)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Key size={18} className="text-primary" />
          Congress.gov API Key
        </CardTitle>
        <CardDescription>
          Get a free API key from{' '}
          <a
            href="https://api.data.gov/signup/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            api.data.gov
          </a>{' '}
          to enable Congress.gov data integration (bills, members, committees).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {hasKey ? (
          <div className="flex items-center gap-2">
            <Badge variant="default" className="gap-1.5">
              <Key size={12} />
              API Key Configured
            </Badge>
            <Button variant="ghost" size="sm" onClick={handleClear}>
              Remove
            </Button>
          </div>
        ) : (
          <div className="flex gap-2">
            <Input
              type="password"
              placeholder="Paste your api.data.gov API key"
              value={key}
              onChange={e => setKey(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSave()}
              className="flex-1"
            />
            <Button onClick={handleSave} disabled={!key.trim()}>
              Save
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ── Main View ────────────────────────────────────────────────────────
export function LegalResourcesView({
  onNavigate,
}: {
  onNavigate?: (route: RouteId) => void
}) {
  const [search, setSearch] = useState('')
  const categories = [
    { id: 'all', label: 'All', icon: GlobeHemisphereWest },
    { id: 'case-law', label: 'Case Law', icon: Scales },
    { id: 'legislation', label: 'Legislation', icon: Buildings },
    { id: 'regulation', label: 'Regulations', icon: Scroll },
    { id: 'reference', label: 'Reference', icon: BookOpen },
    { id: 'court', label: 'Courts', icon: Gavel },
  ]
  const [activeCategory, setActiveCategory] = useState('all')

  const filtered = LEGAL_RESOURCES.filter(r => {
    const matchesCategory = activeCategory === 'all' || r.category === activeCategory
    const matchesSearch =
      !search ||
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.description.toLowerCase().includes(search.toLowerCase()) ||
      r.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-lg">
            <GlobeHemisphereWest size={24} className="text-primary" weight="duotone" />
          </div>
          <div>
            <h2 className="text-2xl font-serif font-bold">Legal Resources</h2>
            <p className="text-sm text-muted-foreground">
              Comprehensive directory of free legal research tools and databases
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {onNavigate && (
          <>
            <Card
              className="cursor-pointer hover:shadow-md transition-shadow border-primary/20"
              onClick={() => onNavigate('case-law')}
            >
              <CardContent className="flex items-center gap-3 p-4">
                <Scales size={24} className="text-primary" weight="duotone" />
                <div>
                  <p className="text-sm font-semibold">Case Law</p>
                  <p className="text-xs text-muted-foreground">Search opinions</p>
                </div>
              </CardContent>
            </Card>
            <Card
              className="cursor-pointer hover:shadow-md transition-shadow border-accent/20 dark:border-accent/15"
              onClick={() => onNavigate('federal-register')}
            >
              <CardContent className="flex items-center gap-3 p-4">
                <Scroll size={24} className="text-accent-foreground dark:text-accent" weight="duotone" />
                <div>
                  <p className="text-sm font-semibold">Fed. Register</p>
                  <p className="text-xs text-muted-foreground">EOs & rules</p>
                </div>
              </CardContent>
            </Card>
          </>
        )}
        <a href="https://www.congress.gov" target="_blank" rel="noopener noreferrer">
          <Card className="cursor-pointer hover:shadow-md transition-shadow h-full">
            <CardContent className="flex items-center gap-3 p-4">
              <Buildings size={24} className="text-primary dark:text-primary" weight="duotone" />
              <div>
                <p className="text-sm font-semibold">Congress.gov</p>
                <p className="text-xs text-muted-foreground">Bills & laws</p>
              </div>
            </CardContent>
          </Card>
        </a>
        <a href="https://constitution.congress.gov" target="_blank" rel="noopener noreferrer">
          <Card className="cursor-pointer hover:shadow-md transition-shadow h-full">
            <CardContent className="flex items-center gap-3 p-4">
              <BookOpen size={24} className="text-green-700" weight="duotone" />
              <div>
                <p className="text-sm font-semibold">Const. Annotated</p>
                <p className="text-xs text-muted-foreground">CRS analysis</p>
              </div>
            </CardContent>
          </Card>
        </a>
      </div>

      {/* Congress API Setup */}
      <CongressApiSetup />

      {/* Search + Filter */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <MagnifyingGlass
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Filter resources..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={activeCategory} onValueChange={v => setActiveCategory(v)}>
        <TabsList className="w-full justify-start overflow-x-auto flex-nowrap">
          {categories.map(cat => {
            const Icon = cat.icon
            return (
              <TabsTrigger key={cat.id} value={cat.id} className="gap-1.5 shrink-0">
                <Icon size={14} />
                {cat.label}
              </TabsTrigger>
            )
          })}
        </TabsList>
      </Tabs>

      {/* Disclaimer */}
      <Alert>
        <Info size={16} className="text-primary" />
        <AlertDescription className="text-xs text-muted-foreground">
          <strong>Educational Resource:</strong> These links are provided for legal research
          and education. External websites have their own terms of service. This platform
          does not provide legal advice.
        </AlertDescription>
      </Alert>

      {/* Resource Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(resource => (
          <ResourceCard
            key={resource.id}
            resource={resource}
            onNavigate={onNavigate}
          />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-8">
          <MagnifyingGlass size={40} className="mx-auto text-muted-foreground/40 mb-3" />
          <p className="text-muted-foreground">
            No resources match your search
          </p>
        </div>
      )}
    </div>
  )
}
