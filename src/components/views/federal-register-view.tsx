// ============================================================================
// Federal Register View – Executive Orders, Rules & Regulations
// https://www.federalregister.gov/
// ============================================================================
// Free, no auth required. Browse the daily journal of the U.S. Government:
//   - Executive Orders (all Presidents)
//   - Final Rules & Regulations
//   - Proposed Rules (notice-and-comment)
//   - Agency Notices
// ============================================================================

import { useState, useMemo, useCallback } from 'react'
import {
  MagnifyingGlass,
  Scroll,
  ArrowSquareOut,
  CalendarBlank,
  Buildings,
  FileText,
  Spinner,
  Warning,
  Funnel,
  Stamp,
  Newspaper,
} from '@phosphor-icons/react'
import {
  useFederalRegisterSearch,
  useExecutiveOrders,
  useRecentRules,
} from '@/lib/legal-api-hooks'
import { FR_DOC_TYPE_LABELS, type FRDocument, type FRDocumentType } from '@/lib/api/federal-register'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { format, parseISO } from 'date-fns'

// ── Document Card ────────────────────────────────────────────────────
function FRDocumentCard({ doc }: { doc: FRDocument }) {
  const formattedDate = useMemo(() => {
    if (!doc.publication_date) return null
    try {
      return format(parseISO(doc.publication_date), 'MMM d, yyyy')
    } catch {
      return doc.publication_date
    }
  }, [doc.publication_date])

  const typeLabel = doc.type
    ? FR_DOC_TYPE_LABELS[doc.type as FRDocumentType] || doc.type
    : 'Document'

  const typeBadgeVariant = useMemo(() => {
    switch (doc.type) {
      case 'Presidential Document': return 'default' as const
      case 'Rule': return 'default' as const
      case 'Proposed Rule': return 'secondary' as const
      case 'Notice': return 'outline' as const
      default: return 'outline' as const
    }
  }, [doc.type])

  const agencies = doc.agencies?.map(a => a.name || a.raw_name).filter(Boolean) || []

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4 space-y-3">
        {/* Title + link */}
        <div className="flex items-start justify-between gap-3">
          <a
            href={doc.html_url || `https://www.federalregister.gov/d/${doc.document_number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-base font-semibold text-primary hover:underline flex-1 leading-snug"
          >
            {doc.title}
          </a>
          <a
            href={doc.html_url || `https://www.federalregister.gov/d/${doc.document_number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary shrink-0 mt-0.5"
            aria-label="View on Federal Register"
          >
            <ArrowSquareOut size={18} />
          </a>
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <Badge variant={typeBadgeVariant} className="text-xs">
            {doc.executive_order_number
              ? `E.O. ${doc.executive_order_number}`
              : typeLabel}
          </Badge>
          {formattedDate && (
            <span className="flex items-center gap-1">
              <CalendarBlank size={14} />
              {formattedDate}
            </span>
          )}
          {doc.citation && (
            <span className="flex items-center gap-1 font-mono text-xs">
              <FileText size={14} />
              {doc.citation}
            </span>
          )}
          {doc.start_page && doc.end_page && (
            <span className="text-xs">
              pp. {doc.start_page.toLocaleString()}–{doc.end_page.toLocaleString()}
            </span>
          )}
        </div>

        {/* Agencies */}
        {agencies.length > 0 && (
          <div className="flex items-center gap-1.5 text-sm">
            <Buildings size={14} className="text-muted-foreground shrink-0" />
            <span className="text-muted-foreground">
              {agencies.slice(0, 3).join(' · ')}
              {agencies.length > 3 && ` +${agencies.length - 3}`}
            </span>
          </div>
        )}

        {/* Abstract */}
        {doc.abstract && (
          <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
            {doc.abstract}
          </p>
        )}

        {/* Action links */}
        <div className="flex gap-2 pt-1">
          {doc.pdf_url && (
            <a
              href={doc.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                <FileText size={14} />
                PDF
              </Button>
            </a>
          )}
          {doc.comment_url && (
            <a
              href={doc.comment_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                <Newspaper size={14} />
                Comment
              </Button>
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// ── Stat Card for summary ────────────────────────────────────────────
function StatCard({
  icon: Icon,
  label,
  value,
  onClick,
}: {
  icon: typeof Scroll
  label: string
  value: string | number
  onClick?: () => void
}) {
  return (
    <Card
      className={onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}
      onClick={onClick}
    >
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-lg">
          <Icon size={20} className="text-primary" weight="duotone" />
        </div>
        <div>
          <p className="text-2xl font-bold tabular-nums">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Main View ────────────────────────────────────────────────────────
export function FederalRegisterView() {
  const [activeTab, setActiveTab] = useState<string>('executive-orders')
  const [searchQuery, setSearchQuery] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState('')

  const {
    data: eoData,
    isLoading: eoLoading,
    error: eoError,
  } = useExecutiveOrders({ per_page: 20 })

  const {
    data: rulesData,
    isLoading: rulesLoading,
    error: rulesError,
  } = useRecentRules({ per_page: 20, significant_only: true })

  const {
    data: searchData,
    isLoading: searchLoading,
    error: searchError,
    isFetching: searchFetching,
  } = useFederalRegisterSearch(
    submittedQuery,
    { per_page: 20, order: 'newest' },
    submittedQuery.length >= 2
  )

  const handleSearch = useCallback((q?: string) => {
    const sq = q ?? searchQuery
    if (sq.trim().length >= 2) {
      setSubmittedQuery(sq.trim())
      setActiveTab('search-results')
    }
  }, [searchQuery])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-accent/10 dark:bg-accent/20 rounded-lg">
            <Scroll size={24} className="text-accent-foreground dark:text-accent" weight="duotone" />
          </div>
          <div>
            <h2 className="text-2xl font-serif font-bold">Federal Register</h2>
            <p className="text-sm text-muted-foreground">
              Official journal of the U.S. Government —{' '}
              <a
                href="https://www.federalregister.gov"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                federalregister.gov
              </a>
            </p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <MagnifyingGlass
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search executive orders, rules, regulations..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            className="pl-10"
          />
        </div>
        <Button onClick={() => handleSearch()} disabled={searchQuery.trim().length < 2}>
          {searchFetching ? <Spinner size={18} className="animate-spin" /> : 'Search'}
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          icon={Stamp}
          label="Executive Orders"
          value={eoData?.count ?? '—'}
          onClick={() => setActiveTab('executive-orders')}
        />
        <StatCard
          icon={Scroll}
          label="Significant Rules"
          value={rulesData?.count ?? '—'}
          onClick={() => setActiveTab('regulations')}
        />
        <StatCard
          icon={FileText}
          label="Document Types"
          value="4"
        />
        <StatCard
          icon={Buildings}
          label="Federal Agencies"
          value="400+"
        />
      </div>

      {/* Disclaimer */}
      <Alert>
        <Warning size={16} className="text-accent-foreground dark:text-accent" />
        <AlertDescription className="text-xs text-muted-foreground">
          <strong>Official Source:</strong> Data from the Federal Register API
          (federalregister.gov). The Federal Register is the official daily publication
          for rules, proposed rules, executive orders, and other documents from U.S. federal
          agencies. Always verify via the official GPO publication.
        </AlertDescription>
      </Alert>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={v => setActiveTab(v)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="executive-orders" className="gap-1.5">
            <Stamp size={14} />
            <span className="hidden sm:inline">Executive</span> Orders
          </TabsTrigger>
          <TabsTrigger value="regulations" className="gap-1.5">
            <Scroll size={14} />
            <span className="hidden sm:inline">Rules &</span> Regs
          </TabsTrigger>
          <TabsTrigger value="search-results" className="gap-1.5">
            <MagnifyingGlass size={14} />
            Search
          </TabsTrigger>
        </TabsList>

        {/* Executive Orders Tab */}
        <TabsContent value="executive-orders" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Recent Executive Orders</h3>
            <a
              href="https://www.federalregister.gov/presidential-documents/executive-orders"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View all <ArrowSquareOut size={14} />
            </a>
          </div>

          {eoLoading && (
            <div className="flex items-center justify-center py-12">
              <Spinner size={32} className="animate-spin text-primary" />
            </div>
          )}

          {eoError && (
            <Alert variant="destructive">
              <Warning size={16} />
              <AlertDescription>
                {eoError instanceof Error ? eoError.message : 'Failed to load executive orders'}
              </AlertDescription>
            </Alert>
          )}

          {eoData && (
            <div className="space-y-3">
              {eoData.results.map(doc => (
                <FRDocumentCard key={doc.document_number} doc={doc} />
              ))}
              {eoData.results.length === 0 && (
                <p className="text-center py-8 text-muted-foreground">
                  No executive orders found
                </p>
              )}
            </div>
          )}
        </TabsContent>

        {/* Regulations Tab */}
        <TabsContent value="regulations" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Significant Rules & Regulations</h3>
            <a
              href="https://www.federalregister.gov/documents/search?conditions%5Bsignificant%5D=1&conditions%5Btype%5D%5B%5D=RULE"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View all <ArrowSquareOut size={14} />
            </a>
          </div>

          {rulesLoading && (
            <div className="flex items-center justify-center py-12">
              <Spinner size={32} className="animate-spin text-primary" />
            </div>
          )}

          {rulesError && (
            <Alert variant="destructive">
              <Warning size={16} />
              <AlertDescription>
                {rulesError instanceof Error ? rulesError.message : 'Failed to load rules'}
              </AlertDescription>
            </Alert>
          )}

          {rulesData && (
            <div className="space-y-3">
              {rulesData.results.map(doc => (
                <FRDocumentCard key={doc.document_number} doc={doc} />
              ))}
              {rulesData.results.length === 0 && (
                <p className="text-center py-8 text-muted-foreground">
                  No significant rules found
                </p>
              )}
            </div>
          )}
        </TabsContent>

        {/* Search Results Tab */}
        <TabsContent value="search-results" className="space-y-4 mt-4">
          {!submittedQuery && (
            <div className="text-center py-12">
              <MagnifyingGlass size={40} className="mx-auto text-muted-foreground/40 mb-3" />
              <p className="text-muted-foreground">
                Search the Federal Register above to see results here
              </p>
            </div>
          )}

          {searchLoading && (
            <div className="flex items-center justify-center py-12">
              <Spinner size={32} className="animate-spin text-primary" />
            </div>
          )}

          {searchError && (
            <Alert variant="destructive">
              <Warning size={16} />
              <AlertDescription>
                {searchError instanceof Error ? searchError.message : 'Search failed'}
              </AlertDescription>
            </Alert>
          )}

          {searchData && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  {searchData.count.toLocaleString()} results for "{submittedQuery}"
                </p>
                <a
                  href={`https://www.federalregister.gov/documents/search?conditions%5Bterm%5D=${encodeURIComponent(submittedQuery)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline flex items-center gap-1"
                >
                  View on FR <ArrowSquareOut size={14} />
                </a>
              </div>
              <Separator />
              <div className="space-y-3">
                {searchData.results.map(doc => (
                  <FRDocumentCard key={doc.document_number} doc={doc} />
                ))}
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
