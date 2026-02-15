import { useState } from 'react'
import { Document, Section, Jurisdiction } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  MapPin,
  MagnifyingGlass,
  Buildings,
  SealCheck,
  ArrowRight,
  Info,
  Scales,
  BookOpen,
  Warning,
} from '@phosphor-icons/react'

interface MyJurisdictionViewProps {
  jurisdiction: Jurisdiction | undefined
  documents: Document[]
  sections: Section[]
  onSectionSelect: (section: Section) => void
  onChangeJurisdiction: () => void
}

export function MyJurisdictionView({
  jurisdiction,
  documents,
  sections,
  onSectionSelect,
  onChangeJurisdiction
}: MyJurisdictionViewProps) {
  const [searchQuery, setSearchQuery] = useState('')

  if (!jurisdiction) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>No Jurisdiction Selected</CardTitle>
            <CardDescription>
              Select your state or territory to view applicable constitutional provisions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={onChangeJurisdiction} className="w-full">
              <MapPin className="mr-2" />
              Select Jurisdiction
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const stateConstitution = documents.find(d => 
    d.jurisdictionId === jurisdiction.id && 
    d.type === 'constitution' &&
    d.authorityLevel === 'state'
  )

  const territorialDoc = documents.find(d =>
    d.jurisdictionId === jurisdiction.id &&
    (d.type === 'constitution' || d.type === 'organic-act') &&
    d.authorityLevel === 'territory'
  )

  const constitutionDoc = stateConstitution || territorialDoc

  const constitutionSections = constitutionDoc
    ? sections.filter(s => s.documentId === constitutionDoc.id)
    : []

  const filteredSections = searchQuery
    ? constitutionSections.filter(s =>
        s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.number.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : constitutionSections

  const billOfRights = filteredSections.filter(s => 
    s.title.toLowerCase().includes('rights') || 
    s.number.toLowerCase().includes('bill of rights') ||
    s.title.toLowerCase().includes('declaration')
  )

  const structureArticles = filteredSections.filter(s => 
    !billOfRights.includes(s) &&
    (s.number.toLowerCase().includes('article') || s.title.toLowerCase().includes('article'))
  )

  const localAuthorityProvisions = filteredSections.filter(s =>
    s.text.toLowerCase().includes('home rule') ||
    s.text.toLowerCase().includes('local government') ||
    s.text.toLowerCase().includes('municipal') ||
    s.text.toLowerCase().includes('county') ||
    s.title.toLowerCase().includes('local')
  )

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <MapPin size={32} className="text-primary" weight="fill" />
          <div>
            <h1 className="text-3xl font-bold font-serif">{jurisdiction.name}</h1>
            <p className="text-muted-foreground">
              {jurisdiction.type === 'state' ? 'State' : 'Territory'} Constitution & Authority Framework
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={onChangeJurisdiction} className="mt-2">
          <MapPin className="mr-2" size={16} />
          Change Jurisdiction
        </Button>
      </div>

      {!constitutionDoc ? (
        <Alert>
          <Info />
          <AlertDescription>
            Constitution for {jurisdiction.name} is not yet available in the library.
            Federal law still applies to this jurisdiction.
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <Card className="bg-gradient-to-br from-primary/5 to-background border-primary/20">
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Scales className="text-primary" size={32} weight="fill" />
                </div>
                <div className="flex-1">
                  <CardTitle className="text-xl font-serif">{constitutionDoc.title}</CardTitle>
                  <CardDescription className="mt-2">
                    {constitutionDoc.description || `The fundamental governing document of ${jurisdiction.name}`}
                  </CardDescription>
                  <div className="mt-3 flex gap-2 flex-wrap">
                    <Badge variant="secondary">
                      <SealCheck className="mr-1" size={14} weight="fill" />
                      {constitutionDoc.verificationStatus === 'official' ? 'Official' : 'Verified'}
                    </Badge>
                    {constitutionDoc.effectiveDate && (
                      <Badge variant="outline" className="font-mono text-xs">
                        Effective: {new Date(constitutionDoc.effectiveDate).toLocaleDateString()}
                      </Badge>
                    )}
                    {constitutionDoc.lastChecked && (
                      <Badge variant="outline" className="text-xs">
                        Last Verified: {new Date(constitutionDoc.lastChecked).toLocaleDateString()}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>

          <div className="relative">
            <MagnifyingGlass 
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={20}
            />
            <Input
              placeholder={`Search ${jurisdiction.name} Constitution...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {localAuthorityProvisions.length > 0 && (
            <Card className="border-accent/30 bg-accent/5">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <Buildings className="text-accent-foreground" size={24} />
                  <div>
                    <CardTitle className="text-lg">Local Authority Provisions</CardTitle>
                    <CardDescription>
                      How {jurisdiction.name} delegates power to local governments
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {localAuthorityProvisions.slice(0, 3).map((section) => (
                    <Button
                      key={section.id}
                      variant="outline"
                      className="w-full justify-between h-auto py-3 px-4"
                      onClick={() => onSectionSelect(section)}
                    >
                      <div className="text-left">
                        <div className="font-medium">{section.title}</div>
                        <div className="text-xs text-muted-foreground mt-1 line-clamp-1">
                          {section.text.substring(0, 100)}...
                        </div>
                      </div>
                      <ArrowRight size={16} className="flex-shrink-0 ml-2" />
                    </Button>
                  ))}
                  {localAuthorityProvisions.length > 3 && (
                    <p className="text-sm text-muted-foreground text-center pt-2">
                      +{localAuthorityProvisions.length - 3} more provisions
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="font-serif">Bill of Rights & Protections</CardTitle>
                <CardDescription>
                  Individual rights and liberties under {jurisdiction.abbreviation} law
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2 pr-4">
                    {billOfRights.length > 0 ? (
                      billOfRights.map((section) => (
                        <Card
                          key={section.id}
                          className="cursor-pointer hover:border-primary/50 transition-colors"
                          onClick={() => onSectionSelect(section)}
                        >
                          <CardHeader className="p-4">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm line-clamp-1">{section.title}</div>
                                <code className="text-xs text-muted-foreground">{section.canonicalCitation}</code>
                              </div>
                              <ArrowRight size={16} className="flex-shrink-0 text-muted-foreground" />
                            </div>
                          </CardHeader>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <BookOpen size={32} className="mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No specific bill of rights sections identified</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="font-serif">Government Structure</CardTitle>
                <CardDescription>
                  Articles defining powers and organization
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2 pr-4">
                    {structureArticles.length > 0 ? (
                      structureArticles.map((section) => (
                        <Card
                          key={section.id}
                          className="cursor-pointer hover:border-primary/50 transition-colors"
                          onClick={() => onSectionSelect(section)}
                        >
                          <CardHeader className="p-4">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm line-clamp-1">{section.title}</div>
                                <code className="text-xs text-muted-foreground">{section.canonicalCitation}</code>
                              </div>
                              <ArrowRight size={16} className="flex-shrink-0 text-muted-foreground" />
                            </div>
                          </CardHeader>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <BookOpen size={32} className="mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No articles found</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
            <Warning className="h-4 w-4 text-accent-foreground dark:text-accent" weight="fill" />
            <AlertDescription className="text-xs text-foreground/80 dark:text-foreground/70">
              <strong>Important Data Accuracy Notice.</strong> Preambles and Art. I, § 1 (Bill of Rights) contain actual state-specific text sourced from each state's official constitution. Other sections (Religion, Speech, Due Process, Legislative, Executive, Local Government) display <em>representative constitutional language</em> typical of state constitutions, not the actual text of {jurisdiction.name}'s constitution. Always verify provisions against the official source before citing.
              {constitutionDoc?.sourceUrl && (
                <span> Official source: <a href={constitutionDoc.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline font-medium">{constitutionDoc.sourceUrl}</a></span>
              )}
            </AlertDescription>
          </Alert>

          <Alert>
            <Info />
            <AlertDescription className="text-sm">
              <strong>Hierarchy Note:</strong> The U.S. Constitution and federal law made in pursuance
              thereof supersede conflicting provisions of state constitutions and state law under the
              Supremacy Clause (U.S. Const. art. VI, cl. 2).
            </AlertDescription>
          </Alert>
        </>
      )}
    </div>
  )
}
