// ============================================================================
// Case Law Search View – Powered by CourtListener (Free Law Project)
// ============================================================================
// Full-text search across millions of court opinions. SCOTUS, federal
// circuit courts, state supreme courts. Citation count, deep links,
// and constitutional relevance indicators.
// ============================================================================

import { useState, useMemo } from 'react'
import {
  MagnifyingGlass,
  Scales,
  ArrowSquareOut,
  Gavel,
  CalendarBlank,
  Hash,
  CaretDown,
  Spinner,
  Warning,
  BookOpen,
  ArrowUp,
  ArrowDown,
} from '@phosphor-icons/react'
import { useCaseLawSearch, useCourts } from '@/lib/legal-api-hooks'
import { courtListenerUrl } from '@/lib/api/court-listener'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import type { SearchResult } from '@/lib/api/court-listener'
import { format, parseISO } from 'date-fns'

// ── Suggested Searches (constitutional topics) ────────────────────────
const SUGGESTED_SEARCHES = [
  { label: 'Due Process', query: 'due process fourteenth amendment' },
  { label: 'Free Speech', query: 'first amendment free speech' },
  { label: 'Equal Protection', query: 'equal protection clause' },
  { label: 'Second Amendment', query: 'right to bear arms second amendment' },
  { label: 'Commerce Clause', query: 'commerce clause interstate' },
  { label: 'Separation of Powers', query: 'separation of powers executive legislative' },
  { label: 'Fourth Amendment', query: 'unreasonable search seizure fourth amendment' },
  { label: 'Supremacy Clause', query: 'supremacy clause preemption federal' },
]

const COURT_OPTIONS = [
  { value: '', label: 'All Courts' },
  { value: 'scotus', label: 'U.S. Supreme Court' },
  { value: 'ca1', label: '1st Circuit' },
  { value: 'ca2', label: '2nd Circuit' },
  { value: 'ca3', label: '3rd Circuit' },
  { value: 'ca4', label: '4th Circuit' },
  { value: 'ca5', label: '5th Circuit' },
  { value: 'ca6', label: '6th Circuit' },
  { value: 'ca7', label: '7th Circuit' },
  { value: 'ca8', label: '8th Circuit' },
  { value: 'ca9', label: '9th Circuit' },
  { value: 'ca10', label: '10th Circuit' },
  { value: 'ca11', label: '11th Circuit' },
  { value: 'cadc', label: 'D.C. Circuit' },
  { value: 'cafc', label: 'Federal Circuit' },
]

const ORDER_OPTIONS = [
  { value: 'score desc', label: 'Relevance' },
  { value: 'dateFiled desc', label: 'Newest First' },
  { value: 'dateFiled asc', label: 'Oldest First' },
  { value: 'citeCount desc', label: 'Most Cited' },
]

// ── Result Card ──────────────────────────────────────────────────────
function CaseResultCard({ result }: { result: SearchResult }) {
  const caseName = result.caseName || result.case_name || 'Untitled Case'
  const dateFiled = result.dateFiled || result.date_filed
  const docketNumber = result.docketNumber || result.docket_number
  const court = result.court || result.court_id || ''
  const courtCitation = result.court_citation_string || ''
  const citeCount = result.citeCount ?? result.citation_count ?? 0
  const citations = result.citation || []
  const status = result.status || result.precedential_status

  const formattedDate = useMemo(() => {
    if (!dateFiled) return null
    try {
      return format(parseISO(dateFiled), 'MMM d, yyyy')
    } catch {
      return dateFiled
    }
  }, [dateFiled])

  const statusColor = useMemo(() => {
    if (!status) return 'secondary'
    const s = status.toLowerCase()
    if (s.includes('published') || s.includes('precedential')) return 'default'
    if (s.includes('unpublished') || s.includes('non-precedential')) return 'secondary'
    return 'outline'
  }, [status])

  return (
    <Card className="hover:shadow-md transition-shadow group">
      <CardContent className="p-4 space-y-3">
        {/* Case name + link */}
        <div className="flex items-start justify-between gap-3">
          <a
            href={courtListenerUrl(result.absolute_url)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-base font-semibold text-primary hover:underline flex-1 leading-snug"
          >
            {caseName}
          </a>
          <a
            href={courtListenerUrl(result.absolute_url)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary shrink-0 mt-0.5"
            aria-label="View on CourtListener"
          >
            <ArrowSquareOut size={18} />
          </a>
        </div>

        {/* Metadata row */}
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          {courtCitation && (
            <span className="flex items-center gap-1">
              <Gavel size={14} />
              {courtCitation}
            </span>
          )}
          {!courtCitation && court && (
            <span className="flex items-center gap-1">
              <Gavel size={14} />
              {court.toUpperCase()}
            </span>
          )}
          {formattedDate && (
            <span className="flex items-center gap-1">
              <CalendarBlank size={14} />
              {formattedDate}
            </span>
          )}
          {docketNumber && (
            <span className="flex items-center gap-1">
              <Hash size={14} />
              {docketNumber}
            </span>
          )}
          {citeCount > 0 && (
            <Badge variant="secondary" className="text-xs">
              <BookOpen size={12} className="mr-1" />
              Cited {citeCount.toLocaleString()}×
            </Badge>
          )}
          {status && (
            <Badge variant={statusColor as 'default' | 'secondary' | 'outline'} className="text-xs capitalize">
              {status}
            </Badge>
          )}
        </div>

        {/* Citations */}
        {citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {citations.slice(0, 4).map((cite, i) => (
              <Badge key={i} variant="outline" className="text-xs font-mono">
                {cite}
              </Badge>
            ))}
            {citations.length > 4 && (
              <Badge variant="outline" className="text-xs">
                +{citations.length - 4} more
              </Badge>
            )}
          </div>
        )}

        {/* Snippet */}
        {result.snippet && (
          <p
            className="text-sm text-muted-foreground line-clamp-3 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: result.snippet }}
          />
        )}
      </CardContent>
    </Card>
  )
}

// ── Main View ────────────────────────────────────────────────────────
export function CaseLawSearchView() {
  const [query, setQuery] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState('')
  const [court, setCourt] = useState('')
  const [orderBy, setOrderBy] = useState('score desc')
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [filedAfter, setFiledAfter] = useState('')
  const [filedBefore, setFiledBefore] = useState('')

  const { data, isLoading, error, isFetching } = useCaseLawSearch(
    submittedQuery,
    {
      court: court || undefined,
      order_by: orderBy,
      filed_after: filedAfter || undefined,
      filed_before: filedBefore || undefined,
    },
    submittedQuery.length >= 2
  )

  const handleSearch = (q?: string) => {
    const searchQuery = q ?? query
    if (searchQuery.trim().length >= 2) {
      setSubmittedQuery(searchQuery.trim())
    }
  }

  const resultCount = typeof data?.count === 'number' ? data.count : data?.results?.length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-lg">
            <Scales size={24} className="text-primary" weight="duotone" />
          </div>
          <div>
            <h2 className="text-2xl font-serif font-bold">Case Law Search</h2>
            <p className="text-sm text-muted-foreground">
              Search millions of court opinions via{' '}
              <a
                href="https://www.courtlistener.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                CourtListener
              </a>{' '}
              (Free Law Project)
            </p>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <MagnifyingGlass
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search case law... e.g. 'due process fourteenth amendment'"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            className="pl-10"
          />
        </div>
        <Button onClick={() => handleSearch()} disabled={query.trim().length < 2}>
          {isFetching ? <Spinner size={18} className="animate-spin" /> : 'Search'}
        </Button>
      </div>

      {/* Quick Filters */}
      <div className="flex flex-wrap gap-2">
        <Select value={court} onValueChange={setCourt}>
          <SelectTrigger className="w-[180px]">
            <Gavel size={14} className="mr-1.5" />
            <SelectValue placeholder="All Courts" />
          </SelectTrigger>
          <SelectContent>
            {COURT_OPTIONS.map(c => (
              <SelectItem key={c.value} value={c.value || '_all'}>
                {c.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={orderBy} onValueChange={setOrderBy}>
          <SelectTrigger className="w-[160px]">
            {orderBy.includes('asc') ? (
              <ArrowUp size={14} className="mr-1.5" />
            ) : (
              <ArrowDown size={14} className="mr-1.5" />
            )}
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ORDER_OPTIONS.map(o => (
              <SelectItem key={o.value} value={o.value}>
                {o.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Collapsible open={filtersOpen} onOpenChange={setFiltersOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="outline" size="sm" className="gap-1.5">
              <CaretDown
                size={14}
                className={cn('transition-transform', filtersOpen && 'rotate-180')}
              />
              Date Range
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2 flex gap-2 items-center">
            <Input
              type="date"
              placeholder="Filed after"
              value={filedAfter}
              onChange={e => setFiledAfter(e.target.value)}
              className="w-[160px]"
            />
            <span className="text-muted-foreground text-sm">to</span>
            <Input
              type="date"
              placeholder="Filed before"
              value={filedBefore}
              onChange={e => setFiledBefore(e.target.value)}
              className="w-[160px]"
            />
          </CollapsibleContent>
        </Collapsible>
      </div>

      {/* Suggested Searches */}
      {!submittedQuery && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Constitutional Topics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_SEARCHES.map(s => (
                <Button
                  key={s.label}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setQuery(s.query)
                    handleSearch(s.query)
                  }}
                  className="text-sm"
                >
                  {s.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <Alert>
        <Warning size={16} className="text-accent-foreground dark:text-accent" />
        <AlertDescription className="text-xs text-muted-foreground">
          <strong>Data Source:</strong> CourtListener by Free Law Project — public domain legal
          data. Results are for educational/research purposes and do not constitute legal
          advice. Always verify cases via official court records.
        </AlertDescription>
      </Alert>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-3">
            <Spinner size={32} className="animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Searching court opinions...
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Alert variant="destructive">
          <Warning size={16} />
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to search case law'}
            <br />
            <span className="text-xs mt-1 block">
              You can also search directly on{' '}
              <a
                href={`https://www.courtlistener.com/?q=${encodeURIComponent(submittedQuery)}&type=o`}
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                CourtListener.com
              </a>
            </span>
          </AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {data && !isLoading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {resultCount !== undefined
                ? `${resultCount.toLocaleString()} results`
                : `${data.results.length} results shown`}
            </p>
            <a
              href={`https://www.courtlistener.com/?q=${encodeURIComponent(submittedQuery)}&type=o`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View on CourtListener
              <ArrowSquareOut size={14} />
            </a>
          </div>

          <Separator />

          <div className="space-y-3">
            {data.results.map((result, i) => (
              <CaseResultCard key={result.id ?? i} result={result} />
            ))}
          </div>

          {data.results.length === 0 && (
            <div className="text-center py-8">
              <MagnifyingGlass size={40} className="mx-auto text-muted-foreground/40 mb-3" />
              <p className="text-muted-foreground">
                No cases found for "{submittedQuery}"
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Try broader search terms or different court filters
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
