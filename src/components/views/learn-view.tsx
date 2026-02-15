import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { Section, Document } from '@/lib/types'
import { learningTopics } from '@/lib/seed-data'
import { BookOpen, ArrowRight } from '@phosphor-icons/react'

interface LearnViewProps {
  sections: Section[]
  documents: Document[]
  onSectionSelect: (section: Section) => void
}

export function LearnView({ sections, documents, onSectionSelect }: LearnViewProps) {
  const handleRelatedSectionClick = (sectionId: string) => {
    const section = sections.find(s => s.id === sectionId)
    if (section) {
      onSectionSelect(section)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Learn About Law</h2>
        <p className="text-muted-foreground mt-1">
          Understand constitutional principles and legal hierarchy
        </p>
      </div>

      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Educational Framework</CardTitle>
          <CardDescription>
            These modules explain core concepts of U.S. constitutional law and federalism. 
            All information is for educational purposes and linked to primary sources.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Constitutional Framework</h3>
        
        <Accordion type="single" collapsible className="space-y-3">
          {learningTopics.map((topic) => (
            <AccordionItem key={topic.id} value={topic.id} className="border rounded-lg px-6">
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3">
                  <BookOpen size={20} className="text-primary" />
                  <span className="font-semibold text-left">{topic.title}</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4 pt-4">
                <div className="prose prose-sm max-w-none font-serif leading-relaxed whitespace-pre-line">
                  {topic.content}
                </div>
                
                {topic.relatedSections.length > 0 && (
                  <div className="space-y-2 pt-4 border-t">
                    <h4 className="font-semibold text-sm">Related Primary Sources:</h4>
                    <div className="space-y-1">
                      {topic.relatedSections.map(sectionId => {
                        const section = sections.find(s => s.id === sectionId)
                        if (!section) return null
                        return (
                          <Button
                            key={sectionId}
                            variant="ghost"
                            size="sm"
                            className="w-full justify-between h-auto py-2"
                            onClick={() => handleRelatedSectionClick(sectionId)}
                          >
                            <span className="text-left">
                              {section.title}
                              <span className="block text-xs text-muted-foreground">
                                {section.canonicalCitation}
                              </span>
                            </span>
                            <ArrowRight size={14} className="flex-shrink-0" />
                          </Button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Visual Hierarchy of U.S. Law</CardTitle>
          <CardDescription>
            Understanding the order of legal authority (highest to lowest)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { level: 1, title: 'U.S. Constitution', description: 'Supreme law of the land' },
              { level: 2, title: 'Federal Statutes & Treaties', description: 'Laws passed by Congress and ratified treaties' },
              { level: 3, title: 'Federal Regulations', description: 'Rules created by federal agencies' },
              { level: 4, title: 'State Constitutions', description: 'Each state\'s fundamental governing document' },
              { level: 5, title: 'State Statutes', description: 'Laws passed by state legislatures' },
              { level: 6, title: 'State Regulations', description: 'Rules created by state agencies' },
              { level: 7, title: 'Local Ordinances', description: 'Laws passed by county and municipal governments' }
            ].map((item) => (
              <div
                key={item.level}
                className="flex items-start gap-4 p-4 rounded-lg border bg-card"
                style={{ marginLeft: `${(item.level - 1) * 12}px` }}
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                  {item.level}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold">{item.title}</h4>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 p-4 rounded-lg bg-accent/10 border border-accent/20">
            <p className="text-sm">
              <strong>Key Principle:</strong> When laws conflict, the higher authority prevails, 
              subject to constitutional limits on government power and the reserved powers of states (Tenth Amendment).
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Lawful Civic Engagement</CardTitle>
          <CardDescription>
            How to participate in the democratic process through proper channels
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold mb-1">Public Comment</h4>
              <p className="text-sm text-muted-foreground">
                Attend public meetings, submit written comments during rulemaking periods, 
                and participate in official hearing processes.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold mb-1">Public Records Requests</h4>
              <p className="text-sm text-muted-foreground">
                Use Freedom of Information Act (FOIA) or state equivalents to access 
                government documents and understand decision-making processes.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold mb-1">Electoral Process</h4>
              <p className="text-sm text-muted-foreground">
                Register to vote, research candidates and ballot measures, participate in 
                elections, and hold elected officials accountable.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold mb-1">Legal Counsel</h4>
              <p className="text-sm text-muted-foreground">
                Consult with licensed attorneys for legal advice, representation in disputes, 
                and guidance on navigating administrative and judicial processes.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold mb-1">Community Organizing</h4>
              <p className="text-sm text-muted-foreground">
                Join or form civic groups, educate community members, and collectively 
                advocate for policy changes through lawful, peaceful means.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
