import { useState, useMemo } from 'react'
import { Section, Document, Jurisdiction, CompareView } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'
import { ArrowsHorizontal, Scales, Warning, Info } from '@phosphor-icons/react'
import { federalStateOverlayMappings } from '@/lib/us-constitution-full'
import { STANDARD_DISCLAIMERS } from '@/lib/content-safeguards'

interface SupremeOverlayProps {
  open: boolean
  onClose: () => void
  /** The state/territory section being viewed */
  stateSection: Section | null
  /** All sections for finding federal parallels */
  allSections: Section[]
  /** All documents for metadata */
  documents: Document[]
  /** Current jurisdiction */
  jurisdiction?: Jurisdiction
}

/**
 * Compute a simple textual similarity score between two sections
 * based on shared significant words (≥4 chars).
 */
function computeSimilarity(a: string, b: string): number {
  const wordsA = new Set(
    a.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length >= 4)
  )
  const wordsB = new Set(
    b.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length >= 4)
  )
  if (wordsA.size === 0 || wordsB.size === 0) return 0

  let shared = 0
  wordsA.forEach(w => { if (wordsB.has(w)) shared++ })
  return shared / Math.max(wordsA.size, wordsB.size)
}

/**
 * Identify key differences and similarities between two texts.
 */
function analyzeDifferences(
  federalText: string,
  stateText: string
): { similarities: string[]; differences: string[] } {
  const similarities: string[] = []
  const differences: string[] = []

  // Key constitutional concepts to check
  const concepts = [
    { term: 'due process', label: 'Due Process protection' },
    { term: 'equal protection', label: 'Equal Protection provision' },
    { term: 'free(dom|ly)?.{0,10}(speech|speak|press|expression)', label: 'Free speech/press protection' },
    { term: 'relig(ion|ious)', label: 'Religious liberty provision' },
    { term: 'bear arms|keep.{0,10}arms', label: 'Arms provision' },
    { term: 'search(es)?.{0,10}seizure', label: 'Search and seizure protection' },
    { term: 'life.{0,15}liberty.{0,15}property', label: 'Life, liberty, property protection' },
    { term: 'jury|trial', label: 'Trial/jury provision' },
    { term: 'cruel.{0,10}unusual', label: 'Punishment protection' },
    { term: 'petition', label: 'Right to petition' },
    { term: 'assemble|assembly', label: 'Right to assemble' },
    { term: 'privacy', label: 'Privacy protection' },
  ]

  const fedLower = federalText.toLowerCase()
  const stateLower = stateText.toLowerCase()

  for (const { term, label } of concepts) {
    const regex = new RegExp(term, 'i')
    const inFederal = regex.test(fedLower)
    const inState = regex.test(stateLower)

    if (inFederal && inState) {
      similarities.push(`Both texts address ${label}`)
    } else if (inFederal && !inState) {
      differences.push(`Federal text includes ${label}; state text does not explicitly address this`)
    } else if (!inFederal && inState) {
      differences.push(`State text includes ${label}; federal text does not explicitly address this in the compared section`)
    }
  }

  if (similarities.length === 0) {
    similarities.push('Both provisions address fundamental rights within their respective constitutional frameworks')
  }

  return { similarities, differences }
}

export function SupremeOverlay({
  open,
  onClose,
  stateSection,
  allSections,
  documents,
  jurisdiction,
}: SupremeOverlayProps) {
  const [selectedFederalId, setSelectedFederalId] = useState<string>('')

  // Find relevant federal sections for comparison
  const federalSections = useMemo(
    () => allSections.filter(s => s.documentId === 'us-constitution'),
    [allSections]
  )

  // Auto-suggest federal sections based on topic mapping
  const suggestedMappings = useMemo(() => {
    if (!stateSection) return []
    return federalStateOverlayMappings.filter(m => {
      // Match by looking at state section title containing the topic
      return stateSection.title
        .toLowerCase()
        .includes(m.stateTopicMatch.toLowerCase())
    })
  }, [stateSection])

  const selectedFederal = federalSections.find(s => s.id === selectedFederalId) || null

  // Auto-select first suggestion if no manual selection
  const effectiveFederal =
    selectedFederal ||
    (suggestedMappings.length > 0
      ? federalSections.find(s => s.id === suggestedMappings[0].federalSectionId) || null
      : null)

  const comparison = useMemo(() => {
    if (!stateSection || !effectiveFederal) return null
    const { similarities, differences } = analyzeDifferences(
      effectiveFederal.text,
      stateSection.text
    )
    const similarity = computeSimilarity(effectiveFederal.text, stateSection.text)

    return {
      similarities,
      differences,
      similarityScore: Math.round(similarity * 100),
    }
  }, [stateSection, effectiveFederal])

  if (!stateSection) return null

  return (
    <Sheet open={open} onOpenChange={v => !v && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-2xl p-0">
        <SheetHeader className="p-6 pb-4 border-b">
          <SheetTitle className="flex items-center gap-2">
            <ArrowsHorizontal size={20} weight="bold" />
            Supreme Overlay – Side-by-Side Comparison
          </SheetTitle>
          <SheetDescription>
            Compare a state provision with the relevant U.S. Constitutional provision.
            This is an educational comparison, not legal analysis.
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)]">
          <div className="p-6 space-y-6">
            {/* Disclaimer Banner */}
            <div className="flex items-start gap-2 p-3 rounded-md bg-accent/5 border border-accent/20 text-foreground/80 text-xs dark:bg-accent/10 dark:border-accent/15 dark:text-foreground/70">
              <Warning size={16} className="shrink-0 mt-0.5" />
              <p>{STANDARD_DISCLAIMERS.comparisonDisclaimer}</p>
            </div>

            {/* Federal Section Selector */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Federal Constitutional Provision</label>
              <Select
                value={selectedFederalId || effectiveFederal?.id || ''}
                onValueChange={setSelectedFederalId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a federal provision to compare..." />
                </SelectTrigger>
                <SelectContent>
                  {suggestedMappings.length > 0 && (
                    <>
                      <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                        Suggested Matches
                      </div>
                      {suggestedMappings.map(m => {
                        const sec = federalSections.find(s => s.id === m.federalSectionId)
                        if (!sec) return null
                        return (
                          <SelectItem key={`suggested-${sec.id}`} value={sec.id}>
                            ★ {sec.title}
                          </SelectItem>
                        )
                      })}
                      <Separator className="my-1" />
                    </>
                  )}
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    All Provisions
                  </div>
                  {federalSections.map(sec => (
                    <SelectItem key={sec.id} value={sec.id}>
                      {sec.number} – {sec.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Side-by-Side Panels */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Federal Panel */}
              <Card className={effectiveFederal ? '' : 'opacity-50'}>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Badge className="bg-primary/15 text-primary dark:bg-primary/25 dark:text-primary">
                      Federal
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      Highest Authority
                    </Badge>
                  </div>
                  <CardTitle className="text-sm mt-2">
                    {effectiveFederal?.title || 'Select a provision above'}
                  </CardTitle>
                  {effectiveFederal && (
                    <p className="text-xs text-muted-foreground font-mono">
                      {effectiveFederal.canonicalCitation}
                    </p>
                  )}
                </CardHeader>
                <CardContent>
                  {effectiveFederal ? (
                    <div className="text-sm leading-relaxed whitespace-pre-line font-serif">
                      {effectiveFederal.text}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">
                      Choose a federal provision to begin comparison.
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* State Panel */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Badge className="bg-accent/15 text-accent-foreground dark:bg-accent/25 dark:text-accent">
                      {jurisdiction?.abbreviation || 'State'}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      Subject to Supremacy Clause
                    </Badge>
                  </div>
                  <CardTitle className="text-sm mt-2">{stateSection.title}</CardTitle>
                  <p className="text-xs text-muted-foreground font-mono">
                    {stateSection.canonicalCitation}
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="text-sm leading-relaxed whitespace-pre-line font-serif">
                    {stateSection.text}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Comparison Summary */}
            {comparison && effectiveFederal && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Info size={16} />
                    Comparison Summary (Educational Only)
                  </CardTitle>
                  <p className="text-xs text-muted-foreground">
                    Textual similarity: {comparison.similarityScore}% shared key terms
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comparison.similarities.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide mb-1">
                        Shared Themes
                      </h4>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {comparison.similarities.map((s, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-green-500 shrink-0">●</span>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {comparison.differences.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-orange-700 dark:text-orange-400 uppercase tracking-wide mb-1">
                        Notable Differences
                      </h4>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {comparison.differences.map((d, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-orange-500 shrink-0">●</span>
                            {d}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Mapping notes from curated data */}
                  {suggestedMappings
                    .filter(m => m.federalSectionId === effectiveFederal.id)
                    .map(m => (
                      <div key={m.federalSectionId} className="text-xs text-muted-foreground border-t pt-3">
                        <span className="font-medium">Curator Note:</span> {m.comparisonNotes}
                      </div>
                    ))}
                </CardContent>
              </Card>
            )}

            {/* Source Attribution */}
            <div className="text-xs text-muted-foreground space-y-1 border-t pt-4">
              <p><strong>Federal Source:</strong> National Archives (archives.gov)</p>
              {jurisdiction && (
                <p>
                  <strong>State Source:</strong> Official {jurisdiction.name} legislature website
                </p>
              )}
              <p className="italic mt-2">
                {STANDARD_DISCLAIMERS.notLegalAdvice}
              </p>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}
