import { useState, useMemo } from 'react'
import { Document, Section } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  BookOpen,
  MagnifyingGlass,
  Scales,
  GlobeHemisphereWest,
  SealCheck,
  BookBookmark,
  ArrowRight,
  Info,
  Warning,
} from '@phosphor-icons/react'
import { AuthorityBadge, VerificationBadge } from '@/components/authority-badge'

interface SupremeLawViewProps {
  documents: Document[]
  sections: Section[]
  onSectionSelect: (section: Section) => void
  onNavigateToTreaties?: () => void
}

/**
 * Determine whether a U.S. Constitution section is an article (not an amendment).
 * Matches: 'Preamble', 'I', 'I.2', 'II', 'VII', etc.
 * Excludes: 'Amend. I', 'Amend. XIV', etc.
 */
function isArticleSection(s: Section): boolean {
  if (s.documentId !== 'us-constitution') return false
  return !s.number.startsWith('Amend.')
}

/** Determine whether a U.S. Constitution section is an amendment */
function isAmendmentSection(s: Section): boolean {
  if (s.documentId !== 'us-constitution') return false
  return s.number.startsWith('Amend.')
}

export function SupremeLawView({
  documents,
  sections,
  onSectionSelect,
  onNavigateToTreaties,
}: SupremeLawViewProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const usConstitution = documents.find(d => d.id === 'us-constitution')

  const articles = useMemo(
    () => sections.filter(isArticleSection),
    [sections]
  )

  const amendments = useMemo(
    () => sections.filter(isAmendmentSection),
    [sections]
  )

  const keyFederalDocs = useMemo(
    () =>
      documents.filter(
        d =>
          d.authorityLevel === 'federal' &&
          (d.type === 'statute' || d.type === 'treaty') &&
          d.id !== 'us-constitution'
      ),
    [documents]
  )

  const q = searchQuery.toLowerCase()

  const filteredArticles = q
    ? articles.filter(
        a =>
          a.title.toLowerCase().includes(q) ||
          a.text.toLowerCase().includes(q) ||
          a.canonicalCitation.toLowerCase().includes(q)
      )
    : articles

  const filteredAmendments = q
    ? amendments.filter(
        a =>
          a.title.toLowerCase().includes(q) ||
          a.text.toLowerCase().includes(q) ||
          a.canonicalCitation.toLowerCase().includes(q)
      )
    : amendments

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-serif mb-1">
          Supreme Law of the Land
        </h1>
        <p className="text-sm text-muted-foreground">
          U.S. Constitution, Amendments, and Federal Authority Sources
        </p>
      </div>

      {/* Supremacy Clause card */}
      <Card className="bg-gradient-to-br from-primary/5 to-background border-primary/20">
        <CardHeader className="pb-3">
          <div className="flex items-start gap-3">
            <div className="p-2.5 bg-primary/10 rounded-lg shrink-0">
              <Scales className="text-primary" size={28} weight="fill" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg sm:text-xl font-serif">The Supremacy Clause</CardTitle>
              <CardDescription className="mt-1.5 text-sm leading-relaxed italic">
                "This Constitution, and the Laws of the United States which shall be made in
                Pursuance thereof; and all Treaties made, or which shall be made, under the
                Authority of the United States, shall be the supreme Law of the Land…"
              </CardDescription>
              <Badge variant="secondary" className="mt-2 font-mono text-xs">
                U.S. Const. art. VI, cl. 2
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Disclaimer */}
      <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
        <Warning className="h-4 w-4 text-accent-foreground dark:text-accent" weight="fill" />
        <AlertDescription className="text-xs text-foreground/80 dark:text-foreground/70">
          <strong>Educational Use Only.</strong> This is not legal advice. All text is sourced from
          official NARA transcripts. Always verify against official government publications before
          reliance. See{' '}
          <a
            href="https://www.archives.gov/founding-docs/constitution-transcript"
            target="_blank"
            rel="noopener noreferrer"
            className="underline font-medium"
          >
            NARA
          </a>{' '}
          for the authoritative source.
        </AlertDescription>
      </Alert>

      {/* Search */}
      <div className="relative">
        <MagnifyingGlass
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          size={18}
        />
        <Input
          placeholder="Search Constitution text, citations…"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="constitution" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="constitution">
            Articles
            <Badge variant="secondary" className="ml-1.5 text-[10px] px-1.5 hidden sm:inline-flex">
              {filteredArticles.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="amendments">
            Amendments
            <Badge variant="secondary" className="ml-1.5 text-[10px] px-1.5 hidden sm:inline-flex">
              {filteredAmendments.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="federal">Federal</TabsTrigger>
        </TabsList>

        {/* ── Articles Tab ────────────────────────────────────────── */}
        <TabsContent value="constitution" className="space-y-4 mt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg sm:text-xl font-semibold font-serif">
                Articles of the Constitution
              </h2>
              <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
                The foundational structure of U.S. government — 7 Articles
              </p>
            </div>
            <div className="flex items-center gap-1.5">
              <VerificationBadge status="official" />
            </div>
          </div>

          <div className="grid gap-2">
            {filteredArticles.map(article => (
              <Card
                key={article.id}
                className="cursor-pointer hover:border-primary/50 transition-colors group"
                onClick={() => onSectionSelect(article)}
              >
                <CardHeader className="py-3 px-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-sm sm:text-base font-serif">
                        {article.title}
                      </CardTitle>
                      <CardDescription className="mt-0.5 line-clamp-2 text-xs sm:text-sm">
                        {article.text.substring(0, 160)}…
                      </CardDescription>
                    </div>
                    <ArrowRight
                      className="shrink-0 text-muted-foreground opacity-60 group-hover:opacity-100 transition-opacity mt-0.5"
                      size={16}
                    />
                  </div>
                  <code className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded mt-1.5 inline-block">
                    {article.canonicalCitation}
                  </code>
                </CardHeader>
              </Card>
            ))}
          </div>

          {filteredArticles.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <BookOpen size={40} className="mx-auto mb-3 opacity-50" />
              <p className="text-sm">No articles match your search.</p>
            </div>
          )}
        </TabsContent>

        {/* ── Amendments Tab ─────────────────────────────────────── */}
        <TabsContent value="amendments" className="space-y-4 mt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg sm:text-xl font-semibold font-serif">
                Constitutional Amendments
              </h2>
              <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
                27 Amendments protecting rights and refining governance (1791–1992)
              </p>
            </div>
            <div className="flex items-center gap-1.5">
              <VerificationBadge status="official" />
            </div>
          </div>

          <div className="grid gap-2">
            {filteredAmendments.map(amendment => (
              <Card
                key={amendment.id}
                className="cursor-pointer hover:border-primary/50 transition-colors group"
                onClick={() => onSectionSelect(amendment)}
              >
                <CardHeader className="py-3 px-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-sm sm:text-base font-serif">
                        {amendment.title}
                      </CardTitle>
                      <CardDescription className="mt-0.5 line-clamp-2 text-xs sm:text-sm">
                        {amendment.text.substring(0, 160)}…
                      </CardDescription>
                    </div>
                    <ArrowRight
                      className="shrink-0 text-muted-foreground opacity-60 group-hover:opacity-100 transition-opacity mt-0.5"
                      size={16}
                    />
                  </div>
                  <code className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded mt-1.5 inline-block">
                    {amendment.canonicalCitation}
                  </code>
                </CardHeader>
              </Card>
            ))}
          </div>

          {filteredAmendments.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <BookOpen size={40} className="mx-auto mb-3 opacity-50" />
              <p className="text-sm">No amendments match your search.</p>
            </div>
          )}
        </TabsContent>

        {/* ── Federal Authority Tab ───────────────────────────────── */}
        <TabsContent value="federal" className="space-y-4 mt-6">
          <div>
            <h2 className="text-lg sm:text-xl font-semibold font-serif">
              Federal Authority Sources
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
              Key federal statutes and treaties under U.S. authority
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {/* Federal Statutes */}
            <Card className="border-primary/20">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded shrink-0">
                    <BookBookmark className="text-primary" size={22} />
                  </div>
                  <div>
                    <CardTitle className="text-base">Federal Statutes</CardTitle>
                    <CardDescription className="text-xs">U.S. Code provisions</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {keyFederalDocs
                  .filter(d => d.type === 'statute')
                  .map(doc => (
                    <Button
                      key={doc.id}
                      variant="outline"
                      size="sm"
                      className="w-full justify-between text-left h-auto py-2"
                      onClick={() => {
                        const sec = sections.find(s => s.documentId === doc.id)
                        if (sec) onSectionSelect(sec)
                      }}
                    >
                      <span className="truncate text-xs">{doc.title}</span>
                      <ArrowRight size={14} className="shrink-0 ml-1" />
                    </Button>
                  ))}
              </CardContent>
            </Card>

            {/* Treaties */}
            <Card className="border-primary/20">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded shrink-0">
                    <GlobeHemisphereWest className="text-primary" size={22} />
                  </div>
                  <div>
                    <CardTitle className="text-base">Treaties</CardTitle>
                    <CardDescription className="text-xs">International agreements</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {keyFederalDocs
                  .filter(d => d.type === 'treaty')
                  .slice(0, 5)
                  .map(doc => (
                    <Button
                      key={doc.id}
                      variant="outline"
                      size="sm"
                      className="w-full justify-between text-left h-auto py-2"
                      onClick={() => {
                        const sec = sections.find(s => s.documentId === doc.id)
                        if (sec) onSectionSelect(sec)
                      }}
                    >
                      <span className="truncate text-xs">{doc.title}</span>
                      <ArrowRight size={14} className="shrink-0 ml-1" />
                    </Button>
                  ))}
                {onNavigateToTreaties && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-primary text-xs"
                    onClick={onNavigateToTreaties}
                  >
                    View Treaty Index
                    <ArrowRight className="ml-1" size={14} />
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Explanatory card */}
          <Card className="bg-muted/30">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Understanding Federal Authority</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p>
                Under the Supremacy Clause (Art. VI, cl. 2), federal law — consisting of the
                Constitution, federal statutes enacted pursuant to it, and treaties — preempts
                conflicting state or local law.
              </p>
              <p>
                Federal authority is limited to powers enumerated in the Constitution (Art. I, § 8)
                and those necessary and proper to execute those powers (Necessary and Proper Clause).
              </p>
              <p className="italic text-accent-foreground dark:text-accent">
                Note: Under the "last-in-time" rule, treaties and federal statutes are co-equal in
                authority. A later statute can supersede an earlier treaty provision, and vice versa.
                The hierarchy shown here orders treaties above statutes for presentational clarity only.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
