import { useState, useMemo } from 'react'
import { Document, Section, TreatyMetadata } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  GlobeHemisphereWest,
  MagnifyingGlass,
  CheckCircle,
  Clock,
  XCircle,
  Pause,
  FileText,
  Info,
  ArrowRight,
  Warning,
} from '@phosphor-icons/react'

interface TreatiesViewProps {
  documents: Document[]
  sections: Section[]
  onSectionSelect: (section: Section) => void
}

/**
 * Treaty metadata keyed by actual document IDs from seed-data.ts.
 * Each entry uses accurate ratification/status data from U.S. Senate records.
 */
const TREATY_METADATA: Record<string, TreatyMetadata> = {
  'treaty-un-charter': {
    id: 'treaty-meta-un-charter',
    documentId: 'treaty-un-charter',
    ratificationDate: '1945-08-08',
    status: 'ratified',
    signatories: ['United States', '192 other Member States'],
    implementingLegislation: ['22 U.S.C. §§ 287–287e (United Nations Participation Act of 1945)'],
    reservations:
      'U.S. participation subject to domestic Constitutional limitations; Connally Reservation to ICJ jurisdiction',
  },
  'treaty-geneva-conventions': {
    id: 'treaty-meta-geneva',
    documentId: 'treaty-geneva-conventions',
    ratificationDate: '1955-08-02',
    status: 'ratified',
    signatories: ['United States', '196 other State Parties'],
    implementingLegislation: [
      '18 U.S.C. § 2441 (War Crimes Act of 1996)',
      '10 U.S.C. § 948a et seq. (Military Commissions Act)',
    ],
  },
  'treaty-nato': {
    id: 'treaty-meta-nato',
    documentId: 'treaty-nato',
    ratificationDate: '1949-08-24',
    status: 'ratified',
    signatories: ['United States', '31 other NATO Allies'],
    implementingLegislation: ['22 U.S.C. § 1651 (Mutual Defense Assistance Act)'],
  },
  'treaty-udhr': {
    id: 'treaty-meta-udhr',
    documentId: 'treaty-udhr',
    status: 'signed-not-ratified',
    signatories: ['United States', '192 other UN Member States'],
    reservations:
      'Note: The UDHR is a UN General Assembly resolution (A/RES/217(III)), not a binding treaty. It is widely regarded as customary international law but is not ratified as a treaty.',
  },
  'treaty-iccpr': {
    id: 'treaty-meta-iccpr',
    documentId: 'treaty-iccpr',
    ratificationDate: '1992-06-08',
    status: 'ratified',
    signatories: ['United States', '173 other State Parties'],
    reservations:
      'United States filed 5 reservations, 5 understandings, and 4 declarations upon ratification, including a declaration that Articles 1–27 are not self-executing.',
    implementingLegislation: [],
  },
  'treaty-cerd': {
    id: 'treaty-meta-cerd',
    documentId: 'treaty-cerd',
    ratificationDate: '1994-10-21',
    status: 'ratified',
    signatories: ['United States', '182 other State Parties'],
    reservations:
      'United States filed a reservation that CERD is not self-executing and a declaration preserving existing First Amendment speech protections.',
    implementingLegislation: ['42 U.S.C. § 2000d et seq. (Civil Rights Act Title VI)'],
  },
  'treaty-cat': {
    id: 'treaty-meta-cat',
    documentId: 'treaty-cat',
    ratificationDate: '1994-10-21',
    status: 'ratified',
    signatories: ['United States', '173 other State Parties'],
    reservations:
      'United States reservation limiting "cruel, inhuman, or degrading treatment" to the meaning of the Fifth, Eighth, and Fourteenth Amendments.',
    implementingLegislation: [
      '18 U.S.C. § 2340 et seq. (Federal Torture Statute)',
      '8 U.S.C. § 1231 (non-refoulement provisions)',
    ],
  },
}

export function TreatiesView({ documents, sections, onSectionSelect }: TreatiesViewProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<
    'all' | 'ratified' | 'pending' | 'terminated' | 'signed-not-ratified'
  >('all')

  const treatyDocs = useMemo(
    () => documents.filter(d => d.type === 'treaty'),
    [documents]
  )

  const filteredTreaties = useMemo(() => {
    const q = searchQuery.toLowerCase()
    return treatyDocs.filter(treaty => {
      const meta = TREATY_METADATA[treaty.id]
      const matchesSearch = q
        ? treaty.title.toLowerCase().includes(q) ||
          treaty.description?.toLowerCase().includes(q) ||
          meta?.implementingLegislation?.some(l => l.toLowerCase().includes(q))
        : true
      const matchesStatus =
        statusFilter === 'all' || meta?.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [treatyDocs, searchQuery, statusFilter])

  const statusCounts = useMemo(() => {
    const counts = { ratified: 0, pending: 0, terminated: 0, 'signed-not-ratified': 0, unknown: 0 }
    treatyDocs.forEach(d => {
      const meta = TREATY_METADATA[d.id]
      if (meta) {
        counts[meta.status as keyof typeof counts] =
          (counts[meta.status as keyof typeof counts] || 0) + 1
      } else {
        counts.unknown++
      }
    })
    return counts
  }, [treatyDocs])

  const statusIcon = (status?: TreatyMetadata['status']) => {
    switch (status) {
      case 'ratified':
        return <CheckCircle weight="fill" className="text-green-600" size={16} />
      case 'pending':
        return <Clock weight="fill" className="text-accent-foreground dark:text-accent" size={16} />
      case 'terminated':
        return <XCircle weight="fill" className="text-red-600" size={16} />
      case 'suspended':
        return <Pause weight="fill" className="text-gray-600" size={16} />
      case 'signed-not-ratified':
        return <Clock weight="fill" className="text-orange-500" size={16} />
      default:
        return <FileText weight="fill" className="text-muted-foreground" size={16} />
    }
  }

  const statusBadge = (status?: TreatyMetadata['status']) => {
    const variants: Record<string, string> = {
      ratified: 'default',
      pending: 'secondary',
      terminated: 'destructive',
      suspended: 'outline',
      'signed-not-ratified': 'secondary',
    }
    const labels: Record<string, string> = {
      ratified: 'Ratified',
      pending: 'Pending',
      terminated: 'Terminated',
      suspended: 'Suspended',
      'signed-not-ratified': 'Signed — Not Ratified',
    }
    return (
      <Badge variant={(variants[status || 'pending'] || 'outline') as any}>
        {labels[status || ''] || 'Unknown'}
      </Badge>
    )
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-1">
          <GlobeHemisphereWest size={28} className="text-primary shrink-0" weight="fill" />
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold font-serif">
              Treaties &amp; International Agreements
            </h1>
            <p className="text-sm text-muted-foreground">
              U.S. treaty obligations and international law framework
            </p>
          </div>
        </div>
      </div>

      {/* Constitutional framework alert */}
      <Alert className="border-primary/30 bg-primary/5">
        <Info className="h-4 w-4" />
        <AlertDescription className="text-xs sm:text-sm">
          <strong>Constitutional Framework:</strong> The President makes treaties with the advice and
          consent of the Senate (two-thirds vote required). U.S. Const. art. II, § 2, cl. 2. Valid
          treaties are part of the "supreme Law of the Land" under the Supremacy Clause (art. VI,
          cl. 2) but remain subject to Constitutional limitations.
        </AlertDescription>
      </Alert>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card>
          <CardHeader className="pb-2 pt-3 px-3">
            <CardDescription className="text-[10px] sm:text-xs">Total</CardDescription>
            <CardTitle className="text-2xl font-bold">{treatyDocs.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 pt-3 px-3">
            <CardDescription className="text-[10px] sm:text-xs flex items-center gap-1">
              <CheckCircle size={12} weight="fill" className="text-green-600" />
              Ratified
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-green-600">
              {statusCounts.ratified}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 pt-3 px-3">
            <CardDescription className="text-[10px] sm:text-xs flex items-center gap-1">
              <Clock size={12} weight="fill" className="text-orange-500" />
              Signed Only
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-orange-500">
              {statusCounts['signed-not-ratified'] + statusCounts.pending}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 pt-3 px-3">
            <CardDescription className="text-[10px] sm:text-xs flex items-center gap-1">
              <XCircle size={12} weight="fill" className="text-red-600" />
              Terminated
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-red-600">
              {statusCounts.terminated}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Search + Filter */}
      <div className="space-y-2">
        <div className="relative">
          <MagnifyingGlass
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            size={18}
          />
          <Input
            placeholder="Search treaties, implementing legislation…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <Tabs
          value={statusFilter}
          onValueChange={v => setStatusFilter(v as any)}
          className="w-full"
        >
          <TabsList className="grid w-full grid-cols-3 sm:grid-cols-4">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="ratified">Ratified</TabsTrigger>
            <TabsTrigger value="signed-not-ratified" className="hidden sm:inline-flex">
              Signed
            </TabsTrigger>
            <TabsTrigger value="terminated">Terminated</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Treaty list */}
      <div className="space-y-3">
        {filteredTreaties.length === 0 ? (
          <Card className="py-12">
            <CardContent className="text-center text-muted-foreground">
              <GlobeHemisphereWest size={40} className="mx-auto mb-3 opacity-50" />
              <p className="font-medium">No treaties found</p>
              <p className="text-sm mt-1">Try adjusting your search or filters</p>
            </CardContent>
          </Card>
        ) : (
          filteredTreaties.map(treaty => {
            const meta = TREATY_METADATA[treaty.id]
            const treatySections = sections.filter(s => s.documentId === treaty.id)

            return (
              <Card
                key={treaty.id}
                className="hover:border-primary/40 transition-colors"
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        {statusIcon(meta?.status)}
                        {statusBadge(meta?.status)}
                      </div>

                      <div>
                        <CardTitle className="text-base sm:text-lg font-serif">
                          {treaty.title}
                        </CardTitle>
                        <CardDescription className="mt-0.5 text-xs sm:text-sm">
                          {treaty.description || 'International agreement'}
                        </CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3 pt-0">
                  {/* Metadata grid */}
                  {meta && (
                    <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                      {meta.ratificationDate && (
                        <div>
                          <dt className="font-semibold text-foreground">U.S. Ratified</dt>
                          <dd className="text-muted-foreground">
                            {new Date(meta.ratificationDate).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            })}
                          </dd>
                        </div>
                      )}
                      {meta.signatories && (
                        <div>
                          <dt className="font-semibold text-foreground">Parties</dt>
                          <dd className="text-muted-foreground">
                            {meta.signatories.join('; ')}
                          </dd>
                        </div>
                      )}
                      {meta.implementingLegislation &&
                        meta.implementingLegislation.length > 0 && (
                          <div className="sm:col-span-2">
                            <dt className="font-semibold text-foreground">
                              Implementing Legislation
                            </dt>
                            <dd className="text-muted-foreground font-mono">
                              {meta.implementingLegislation.join('; ')}
                            </dd>
                          </div>
                        )}
                    </dl>
                  )}

                  {/* Reservations */}
                  {meta?.reservations && (
                    <div className="p-2 bg-accent/5 dark:bg-accent/10 border border-accent/20 dark:border-accent/15 rounded text-xs">
                      <span className="font-semibold text-foreground/90 dark:text-foreground/80">Reservations / Notes: </span>
                      <span className="text-foreground/80 dark:text-foreground/70">{meta.reservations}</span>
                    </div>
                  )}

                  {/* Sections */}
                  {treatySections.length > 0 && (
                    <div className="flex gap-2 flex-wrap pt-1">
                      {treatySections.slice(0, 4).map(section => (
                        <Button
                          key={section.id}
                          variant="outline"
                          size="sm"
                          className="h-auto py-1.5 text-xs gap-1"
                          onClick={() => onSectionSelect(section)}
                        >
                          {section.title}
                          <ArrowRight size={12} />
                        </Button>
                      ))}
                      {treatySections.length > 4 && (
                        <Badge variant="secondary" className="text-[10px]">
                          +{treatySections.length - 4} more
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })
        )}
      </div>

      {/* Disclaimer */}
      <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
        <Warning className="h-4 w-4 text-accent-foreground dark:text-accent" weight="fill" />
        <AlertDescription className="text-xs text-foreground/80 dark:text-foreground/70">
          <strong>Educational Use Only.</strong> This module distinguishes between (a) treaty text,
          (b) ratification/status metadata, and (c) implementing legislation. Treaty status and
          reservation data is sourced from the U.S. State Department Treaty Affairs office and the
          U.N. Treaty Collection. The UDHR is listed here for reference but is technically a General
          Assembly resolution, not a binding treaty. The interaction between treaties and
          federal/state law depends on judicial interpretation and is not asserted here. Always
          verify current treaty status through official government sources.
        </AlertDescription>
      </Alert>
    </div>
  )
}
