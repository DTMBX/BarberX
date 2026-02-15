import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Section, Document, AnalyzerSession, AnalyzerReport } from '@/lib/types'
import { Warning, CheckCircle, ArrowRight, ArrowLeft, Scales } from '@phosphor-icons/react'
import { CitationCard } from '../citation-card'
import { DisclaimerBanner } from '../disclaimer-banner'
import { createAuditLog } from '@/lib/compliance'

interface AnalyzerViewProps {
  documents: Document[]
  sections: Section[]
  onSectionSelect: (section: Section) => void
}

export function AnalyzerView({ documents, sections, onSectionSelect }: AnalyzerViewProps) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [report, setReport] = useState<AnalyzerReport | null>(null)

  const questions = [
    {
      id: 'authority-levels',
      title: 'What authority levels are involved?',
      description: 'Select the primary authority levels you want to compare',
      type: 'radio' as const,
      options: [
        { value: 'federal-state', label: 'Federal law vs. State law' },
        { value: 'state-local', label: 'State law vs. Local ordinance' },
        { value: 'federal-local', label: 'Federal law vs. Local ordinance' },
        { value: 'constitutional-statutory', label: 'Constitutional provision vs. Statute' }
      ]
    },
    {
      id: 'subject-matter',
      title: 'What is the subject matter?',
      description: 'Briefly describe the area of law or policy involved',
      type: 'textarea' as const,
      placeholder: 'Example: Minimum wage requirements, environmental regulations, free speech protections...'
    },
    {
      id: 'conflict-type',
      title: 'What type of potential conflict exists?',
      description: 'How do these laws or provisions relate to each other?',
      type: 'radio' as const,
      options: [
        { value: 'direct-conflict', label: 'Direct conflict (cannot comply with both)' },
        { value: 'more-restrictive', label: 'One law is more restrictive than the other' },
        { value: 'additional-requirements', label: 'One law adds requirements not in the other' },
        { value: 'procedural-difference', label: 'Different procedures for the same outcome' },
        { value: 'not-sure', label: 'Not sure / Need guidance' }
      ]
    },
    {
      id: 'specific-provisions',
      title: 'Describe the specific provisions',
      description: 'What are the relevant legal provisions you\'re comparing?',
      type: 'textarea' as const,
      placeholder: 'Provide citations, quotes, or descriptions of the specific laws or constitutional provisions involved...'
    }
  ]

  const handleAnswer = (questionId: string, value: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleNext = () => {
    if (step < questions.length - 1) {
      setStep(step + 1)
    } else {
      generateReport()
    }
  }

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1)
    }
  }

  const generateReport = async () => {
    const relevantSections = sections.filter(s => 
      s.canonicalCitation.includes('U.S. Const. art. VI') ||
      s.canonicalCitation.includes('amend. X') ||
      s.canonicalCitation.includes('amend. XIV')
    )

    const newReport: AnalyzerReport = {
      relevantProvisions: relevantSections.slice(0, 3).map(section => {
        const doc = documents.find(d => d.id === section.documentId)!
        return {
          sectionId: section.id,
          citation: section.canonicalCitation,
          snippet: section.text.slice(0, 200) + '...',
          authorityLevel: doc.authorityLevel
        }
      }),
      preemptionCategories: getPreemptionCategories(answers),
      keyQuestions: getKeyQuestions(answers),
      nextSteps: [
        'Review the full text of relevant constitutional provisions and statutes',
        'Check official government sources for the most current version of laws',
        'Attend public meetings where these issues are discussed',
        'Submit public comments through official channels',
        'Consult with a licensed attorney for legal advice specific to your situation',
        'File a public records request to obtain relevant documents',
        'Contact your elected representatives to express your views'
      ],
      disclaimer: 'THIS ANALYSIS IS FOR EDUCATIONAL PURPOSES ONLY AND DOES NOT CONSTITUTE LEGAL ADVICE. The information provided helps you understand legal concepts and identify relevant sources, but should not be relied upon for legal decisions. No attorney-client relationship is created. Consult a qualified attorney for advice about your specific situation. This tool does not render legal judgments or predict court outcomes.'
    }

    setReport(newReport)
    setStep(questions.length)

    let userId = 'anonymous'
    try {
      const user = await window.spark.user()
      userId = user?.login || String(user?.id || '') || 'anonymous'
    } catch { /* Spark auth unavailable */ }
    
    try {
      await createAuditLog({
        userId,
        userRole: 'reader',
        action: 'create',
        entityType: 'analyzer-report',
        entityId: `report-${Date.now()}`,
        metadata: { 
          answers,
          timestamp: new Date().toISOString()
        },
      })
    } catch { /* Audit log write failed — non-blocking */ }
  }

  const getPreemptionCategories = (answers: Record<string, string>) => {
    const categories: string[] = []
    
    categories.push('Supremacy Clause Analysis (U.S. Const. art. VI, cl. 2)')
    
    if (answers['conflict-type'] === 'direct-conflict') {
      categories.push('Conflict Preemption - Laws cannot be complied with simultaneously')
    }
    
    if (answers['authority-levels']?.includes('federal')) {
      categories.push('Federal Preemption - Express or Implied')
      categories.push('Commerce Clause Considerations (U.S. Const. art. I, § 8)')
    }
    
    categories.push('Tenth Amendment Reserved Powers')
    
    return categories
  }

  const getKeyQuestions = (answers: Record<string, string>) => {
    return [
      'Does the higher authority (federal or state) explicitly state that it preempts lower laws?',
      'Is the regulatory field so comprehensively covered by higher law that no room remains for lower law?',
      'Would following the lower law obstruct or conflict with the objectives of the higher law?',
      'Does the Constitution grant specific authority to the level of government in question?',
      'Are there any savings clauses or explicit allowances for state/local regulation?',
      'Have courts ruled on similar conflicts in this subject area?'
    ]
  }

  const currentQuestion = questions[step]
  const progress = ((step + 1) / (questions.length + 1)) * 100

  if (report) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight font-serif">Issue-Spotting Report</h2>
          <p className="text-muted-foreground mt-1">
            Educational analysis of potential legal conflicts
          </p>
        </div>

        <DisclaimerBanner variant="legal-advice" showIcon={true} />

        <Alert className="border-2 border-destructive/50 bg-destructive/5 dark:bg-destructive/10">
          <Scales className="h-6 w-6 text-destructive" weight="fill" />
          <AlertTitle className="text-lg font-bold text-destructive">
            Critical: Not Legal Advice - Educational Tool Only
          </AlertTitle>
          <AlertDescription className="text-sm text-destructive/90 dark:text-destructive/80 leading-relaxed mt-2">
            {report.disclaimer}
          </AlertDescription>
        </Alert>

        <Card className="border-2 border-primary/20 bg-primary/5 dark:bg-primary/10">
          <CardHeader>
            <CardTitle className="text-xl font-serif">Court-Defensible Usage Guidelines</CardTitle>
            <CardDescription className="text-base">
              How to use this educational report responsibly
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="space-y-2">
              <p className="font-semibold">✓ Appropriate Uses:</p>
              <ul className="list-disc list-inside space-y-1 ml-4 text-muted-foreground">
                <li>Understanding legal concepts and hierarchies</li>
                <li>Identifying relevant constitutional provisions to research further</li>
                <li>Preparing questions for consultation with an attorney</li>
                <li>Educational exploration of federalism and preemption</li>
              </ul>
            </div>
            <div className="space-y-2">
              <p className="font-semibold">✗ Inappropriate Uses:</p>
              <ul className="list-disc list-inside space-y-1 ml-4 text-muted-foreground">
                <li>Making legal decisions without consulting an attorney</li>
                <li>Citing this report in court filings or legal proceedings</li>
                <li>Relying on this analysis as a legal opinion or verdict</li>
                <li>Assuming this represents how a court would rule</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Relevant Constitutional Provisions</CardTitle>
            <CardDescription>
              Key foundational sources for this type of analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.relevantProvisions.map(provision => {
              const section = sections.find(s => s.id === provision.sectionId)!
              const doc = documents.find(d => d.id === section.documentId)!
              return (
                <CitationCard
                  key={provision.sectionId}
                  title={section.title}
                  citation={provision.citation}
                  snippet={provision.snippet}
                  authorityLevel={provision.authorityLevel}
                  onNavigate={() => onSectionSelect(section)}
                />
              )
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preemption Categories to Consider</CardTitle>
            <CardDescription>
              Legal frameworks that may apply to this situation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {report.preemptionCategories.map((category, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle size={20} className="text-primary flex-shrink-0 mt-0.5" />
                  <span>{category}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Key Questions for Analysis</CardTitle>
            <CardDescription>
              Important factors to investigate further
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {report.keyQuestions.map((question, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-primary font-bold flex-shrink-0">Q{idx + 1}.</span>
                  <span>{question}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Lawful Next Steps</CardTitle>
            <CardDescription>
              How to engage through proper civic channels
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {report.nextSteps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-muted-foreground flex-shrink-0">{idx + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Button
          onClick={() => {
            setStep(0)
            setAnswers({})
            setReport(null)
          }}
          variant="outline"
          className="w-full"
        >
          Start New Analysis
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Conflict Analyzer</h2>
        <p className="text-muted-foreground mt-1">
          Learn to identify and evaluate potential legal conflicts
        </p>
      </div>

      <Alert>
        <Warning size={20} />
        <AlertTitle>Educational Tool</AlertTitle>
        <AlertDescription>
          This analyzer helps you understand legal concepts and identify relevant sources. 
          It does not provide legal advice or definitive answers. Consult an attorney for guidance on your specific situation.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-muted-foreground">
                Question {step + 1} of {questions.length}
              </CardTitle>
              <span className="text-sm font-medium">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} />
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">{currentQuestion.title}</h3>
            <p className="text-sm text-muted-foreground">{currentQuestion.description}</p>
          </div>

          {currentQuestion.type === 'radio' && (
            <RadioGroup
              value={answers[currentQuestion.id] || ''}
              onValueChange={(value) => handleAnswer(currentQuestion.id, value)}
            >
              <div className="space-y-3">
                {currentQuestion.options?.map(option => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={option.value} />
                    <Label htmlFor={option.value} className="cursor-pointer flex-1">
                      {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          )}

          {currentQuestion.type === 'textarea' && (
            <Textarea
              value={answers[currentQuestion.id] || ''}
              onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
              placeholder={currentQuestion.placeholder}
              rows={6}
            />
          )}

          <div className="flex gap-2 pt-4">
            {step > 0 && (
              <Button variant="outline" onClick={handleBack}>
                <ArrowLeft size={16} />
                Back
              </Button>
            )}
            <Button
              onClick={handleNext}
              disabled={!answers[currentQuestion.id]}
              className="ml-auto"
            >
              {step === questions.length - 1 ? 'Generate Report' : 'Next'}
              {step < questions.length - 1 && <ArrowRight size={16} />}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
