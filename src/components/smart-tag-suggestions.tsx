import { useState, useEffect, useMemo } from 'react'
import { SavedCitation, Section, Document, DocumentType, AuthorityLevel } from '@/lib/types'
import { TagDefinition } from '@/components/tag-manager'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Sparkle, Check, X, Lightbulb, Brain, MagicWand } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface SmartTagSuggestionsProps {
  citation: SavedCitation
  section: Section | undefined
  document: Document | undefined
  allTags: TagDefinition[]
  currentTags: string[]
  onApplySuggestion: (tagName: string) => void
  onDismissSuggestion: (tagName: string) => void
}

interface TagSuggestion {
  tagName: string
  confidence: 'high' | 'medium' | 'low'
  reason: string
  tagDef: TagDefinition | undefined
  source: 'keyword' | 'llm' | 'structural'
}

interface LLMAnalysisResult {
  suggestedTags: string[]
  legalConcepts: string[]
  practiceAreas: string[]
  constitutionalIssues: string[]
  reasoning: string
}

const CONSTITUTIONAL_KEYWORDS = {
  'Commerce Clause': ['commerce', 'interstate', 'trade', 'regulation of commerce', 'among the several states'],
  'Due Process': ['due process', 'liberty', 'property', 'life, liberty', 'deprivation', 'procedural', 'substantive'],
  'Equal Protection': ['equal protection', 'discrimination', 'classification', 'suspect class', 'rational basis', 'strict scrutiny'],
  'First Amendment': ['speech', 'religion', 'press', 'assembly', 'petition', 'establishment', 'free exercise', 'expression'],
  'Supremacy Clause': ['supremacy', 'supreme law', 'preemption', 'preempt', 'conflict', 'binding'],
  'Tenth Amendment': ['reserved', 'powers not delegated', 'states respectively', 'enumerated powers'],
  'Necessary and Proper': ['necessary and proper', 'elastic clause', 'implied powers', 'carry into execution'],
  'Fourth Amendment': ['search', 'seizure', 'warrant', 'probable cause', 'unreasonable', 'privacy'],
  'Fifth Amendment': ['self-incrimination', 'double jeopardy', 'grand jury', 'takings', 'just compensation'],
  'Fourteenth Amendment': ['citizenship', 'privileges or immunities', 'incorporation', 'state action'],
}

const TOPIC_KEYWORDS = {
  'Federalism': ['federalism', 'federal', 'state power', 'division of power', 'dual sovereignty', 'cooperative'],
  'Preemption': ['preemption', 'preempt', 'supersede', 'conflict', 'field preemption', 'express preemption', 'implied'],
  'Separation of Powers': ['separation', 'executive', 'legislative', 'judicial', 'checks and balances', 'branches'],
  'Statutory Interpretation': ['interpretation', 'construe', 'legislative intent', 'plain meaning', 'ambiguous'],
  'Administrative Law': ['agency', 'regulation', 'administrative', 'rulemaking', 'chevron', 'deference'],
  'Civil Rights': ['civil rights', 'rights', 'discrimination', 'voting', 'access', 'equality'],
  'Criminal Law': ['criminal', 'prosecution', 'defendant', 'crime', 'offense', 'punishment', 'sentencing'],
  'Constitutional Law': ['constitutional', 'unconstitutional', 'constitutionality', 'fundamental right'],
}

const PRACTICE_AREA_KEYWORDS = {
  'Immigration': ['immigration', 'alien', 'naturalization', 'visa', 'deportation', 'citizenship'],
  'Environmental': ['environment', 'pollution', 'clean air', 'clean water', 'epa', 'endangered'],
  'Employment': ['employment', 'labor', 'workplace', 'employee', 'employer', 'discrimination', 'wages'],
  'Education': ['education', 'school', 'student', 'university', 'college', 'educational institution'],
  'Healthcare': ['health', 'medical', 'healthcare', 'patient', 'hospital', 'medicaid', 'medicare'],
  'Housing': ['housing', 'landlord', 'tenant', 'rent', 'eviction', 'zoning', 'residential'],
}

async function analyzeCitationWithLLM(
  citation: SavedCitation,
  section: Section | undefined,
  document: Document | undefined,
  availableTags: TagDefinition[]
): Promise<LLMAnalysisResult | null> {
  try {
    const contentToAnalyze = [
      `Title: ${citation.title}`,
      `Citation: ${citation.canonicalCitation}`,
      citation.notes ? `Notes: ${citation.notes}` : '',
      section?.title ? `Section: ${section.title}` : '',
      section?.text ? `Text: ${section.text.substring(0, 1000)}` : '',
      document?.title ? `Document: ${document.title}` : '',
      document?.description ? `Description: ${document.description}` : '',
    ].filter(Boolean).join('\n')

    const tagList = availableTags
      .map(t => `- ${t.name} (${t.category}): ${t.description}`)
      .join('\n')

    const promptText = `You are a legal research assistant analyzing a citation from a law reference application. Your task is to suggest the most relevant tags from the available tag list.

CITATION CONTENT TO ANALYZE:
${contentToAnalyze}

AVAILABLE TAGS:
${tagList}

ANALYSIS INSTRUCTIONS:
1. Identify the key legal concepts, constitutional provisions, and practice areas mentioned
2. Suggest 3-8 most relevant tags from the available tag list
3. Focus on tags that would be most useful for legal research and case organization
4. Consider both explicit mentions and implicit legal themes
5. Prioritize accuracy and relevance over quantity

Return your analysis as a JSON object with this exact structure:
{
  "suggestedTags": ["Tag Name 1", "Tag Name 2", "Tag Name 3"],
  "legalConcepts": ["concept1", "concept2"],
  "practiceAreas": ["area1", "area2"],
  "constitutionalIssues": ["issue1", "issue2"],
  "reasoning": "Brief explanation of why these tags are relevant"
}`

    const response = await window.spark.llm(promptText, 'gpt-4o-mini', true)
    const result = JSON.parse(response) as LLMAnalysisResult
    
    return result
  } catch (error) {
    console.error('LLM analysis error:', error)
    return null
  }
}

export function SmartTagSuggestions({
  citation,
  section,
  document,
  allTags,
  currentTags,
  onApplySuggestion,
  onDismissSuggestion,
}: SmartTagSuggestionsProps) {
  const [dismissedSuggestions, setDismissedSuggestions] = useState<Set<string>>(new Set())
  const [isAnalyzing, setIsAnalyzing] = useState(true)
  const [llmAnalysis, setLlmAnalysis] = useState<LLMAnalysisResult | null>(null)
  const [useLLM, setUseLLM] = useState(true)
  const [llmError, setLlmError] = useState(false)

  useEffect(() => {
    const performAnalysis = async () => {
      setIsAnalyzing(true)
      setLlmError(false)
      
      if (useLLM && (section || document)) {
        const result = await analyzeCitationWithLLM(citation, section, document, allTags)
        if (result) {
          setLlmAnalysis(result)
        } else {
          setLlmError(true)
          setUseLLM(false)
        }
      }
      
      setIsAnalyzing(false)
    }

    performAnalysis()
  }, [citation.id, section?.id, useLLM])

  const suggestions = useMemo((): TagSuggestion[] => {
    if (!section && !document) return []

    const suggestedTags: TagSuggestion[] = []
    const alreadyApplied = new Set(currentTags)
    
    const contentToAnalyze = [
      citation.title,
      citation.canonicalCitation,
      citation.notes,
      section?.title || '',
      section?.text || '',
      document?.title || '',
      document?.description || '',
    ].join(' ').toLowerCase()

    if (llmAnalysis && useLLM) {
      llmAnalysis.suggestedTags.forEach((tagName) => {
        const tag = allTags.find(t => t.name === tagName)
        if (tag && !alreadyApplied.has(tag.name) && !dismissedSuggestions.has(tag.name)) {
          suggestedTags.push({
            tagName: tag.name,
            confidence: 'high',
            reason: `LLM Deep Analysis: ${llmAnalysis.reasoning.substring(0, 100)}...`,
            tagDef: tag,
            source: 'llm',
          })
        }
      })
    }

    const authorityLevel = document?.authorityLevel
    const documentType = document?.type

    if (authorityLevel) {
      const levelTagName = authorityLevel.charAt(0).toUpperCase() + authorityLevel.slice(1)
      const levelTag = allTags.find(t => t.name === levelTagName && t.category === 'authority-level')
      if (levelTag && !alreadyApplied.has(levelTag.name) && !dismissedSuggestions.has(levelTag.name)) {
        suggestedTags.push({
          tagName: levelTag.name,
          confidence: 'high',
          reason: `Document is at the ${authorityLevel} authority level`,
          tagDef: levelTag,
          source: 'structural',
        })
      }
    }

    if (documentType === 'constitution') {
      const constitutionalTag = allTags.find(t => t.name === 'Constitutional Law')
      if (constitutionalTag && !alreadyApplied.has(constitutionalTag.name) && !dismissedSuggestions.has(constitutionalTag.name)) {
        suggestedTags.push({
          tagName: constitutionalTag.name,
          confidence: 'high',
          reason: 'This is a constitutional provision',
          tagDef: constitutionalTag,
          source: 'structural',
        })
      }
    }

    Object.entries(CONSTITUTIONAL_KEYWORDS).forEach(([tagName, keywords]) => {
      const tag = allTags.find(t => t.name === tagName && t.category === 'constitutional-provision')
      if (!tag || alreadyApplied.has(tag.name) || dismissedSuggestions.has(tag.name)) return

      const matchedKeywords = keywords.filter(keyword => contentToAnalyze.includes(keyword.toLowerCase()))
      if (matchedKeywords.length > 0) {
        const confidence = matchedKeywords.length >= 2 ? 'high' : matchedKeywords.length === 1 ? 'medium' : 'low'
        suggestedTags.push({
          tagName: tag.name,
          confidence,
          reason: `Content mentions: "${matchedKeywords[0]}"`,
          tagDef: tag,
          source: 'keyword',
        })
      }
    })

    Object.entries(TOPIC_KEYWORDS).forEach(([tagName, keywords]) => {
      const tag = allTags.find(t => t.name === tagName && t.category === 'legal-topic')
      if (!tag || alreadyApplied.has(tag.name) || dismissedSuggestions.has(tag.name)) return

      const matchedKeywords = keywords.filter(keyword => contentToAnalyze.includes(keyword.toLowerCase()))
      if (matchedKeywords.length > 0) {
        const confidence = matchedKeywords.length >= 2 ? 'high' : matchedKeywords.length === 1 ? 'medium' : 'low'
        suggestedTags.push({
          tagName: tag.name,
          confidence,
          reason: `Topic detected: "${matchedKeywords[0]}"`,
          tagDef: tag,
          source: 'keyword',
        })
      }
    })

    Object.entries(PRACTICE_AREA_KEYWORDS).forEach(([tagName, keywords]) => {
      const tag = allTags.find(t => t.name === tagName && t.category === 'practice-area')
      if (!tag || alreadyApplied.has(tag.name) || dismissedSuggestions.has(tag.name)) return

      const matchedKeywords = keywords.filter(keyword => contentToAnalyze.includes(keyword.toLowerCase()))
      if (matchedKeywords.length > 0) {
        const confidence = matchedKeywords.length >= 2 ? 'high' : 'medium'
        suggestedTags.push({
          tagName: tag.name,
          confidence,
          reason: `Practice area: "${matchedKeywords[0]}"`,
          tagDef: tag,
          source: 'keyword',
        })
      }
    })

    const caseTypePatterns = {
      'Constitutional Challenge': ['unconstitutional', 'facial challenge', 'as-applied', 'invalidate'],
      'Preemption Dispute': ['preemption', 'preempt', 'conflict', 'supersede'],
      'Civil Litigation': ['plaintiff', 'defendant', 'civil action', 'damages'],
      'Injunctive Relief': ['injunction', 'preliminary', 'permanent', 'restraining order', 'enjoin'],
      'Administrative Appeal': ['agency decision', 'administrative review', 'appeal', 'hearing'],
    }

    Object.entries(caseTypePatterns).forEach(([tagName, keywords]) => {
      const tag = allTags.find(t => t.name === tagName && t.category === 'case-type')
      if (!tag || alreadyApplied.has(tag.name) || dismissedSuggestions.has(tag.name)) return

      const matchedKeywords = keywords.filter(keyword => contentToAnalyze.includes(keyword.toLowerCase()))
      if (matchedKeywords.length > 0) {
        suggestedTags.push({
          tagName: tag.name,
          confidence: 'medium',
          reason: `Case type indicator: "${matchedKeywords[0]}"`,
          tagDef: tag,
          source: 'keyword',
        })
      }
    })

    const uniqueTags = new Map<string, TagSuggestion>()
    suggestedTags.forEach(suggestion => {
      if (!uniqueTags.has(suggestion.tagName)) {
        uniqueTags.set(suggestion.tagName, suggestion)
      } else {
        const existing = uniqueTags.get(suggestion.tagName)!
        if (suggestion.source === 'llm' || (existing.source !== 'llm' && suggestion.confidence === 'high')) {
          uniqueTags.set(suggestion.tagName, suggestion)
        }
      }
    })

    return Array.from(uniqueTags.values())
      .sort((a, b) => {
        const sourceOrder = { llm: 3, structural: 2, keyword: 1 }
        const confidenceOrder = { high: 3, medium: 2, low: 1 }
        
        if (a.source !== b.source) {
          return sourceOrder[b.source] - sourceOrder[a.source]
        }
        
        return confidenceOrder[b.confidence] - confidenceOrder[a.confidence]
      })
      .slice(0, 10)
  }, [section, document, citation, allTags, currentTags, dismissedSuggestions, llmAnalysis, useLLM])

  const handleApply = (tagName: string) => {
    onApplySuggestion(tagName)
    toast.success(`Applied tag: ${tagName}`)
  }

  const handleDismiss = (tagName: string) => {
    setDismissedSuggestions(prev => new Set(prev).add(tagName))
    onDismissSuggestion(tagName)
  }

  const handleToggleLLM = () => {
    setUseLLM(!useLLM)
    if (!useLLM) {
      toast.info('Deep LLM analysis enabled')
    } else {
      toast.info('Using keyword-based analysis')
    }
  }

  if (isAnalyzing) {
    return (
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Sparkle className="w-4 h-4 animate-pulse" />
            <span>{useLLM ? 'Performing deep content analysis...' : 'Analyzing citation content...'}</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (suggestions.length === 0) {
    return null
  }

  const llmSuggestions = suggestions.filter(s => s.source === 'llm')
  const otherSuggestions = suggestions.filter(s => s.source !== 'llm')

  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          {useLLM && llmSuggestions.length > 0 ? (
            <Brain className="w-5 h-5 text-primary" weight="fill" />
          ) : (
            <Sparkle className="w-5 h-5 text-primary" weight="fill" />
          )}
          <div className="flex-1">
            <CardTitle className="text-base">
              {useLLM && llmSuggestions.length > 0 ? 'AI Deep Analysis' : 'Smart Tag Suggestions'}
            </CardTitle>
            <CardDescription className="text-xs">
              {useLLM && llmSuggestions.length > 0 
                ? 'LLM-powered semantic analysis of legal content'
                : 'Keyword-based recommendations'}
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1 text-xs"
            onClick={handleToggleLLM}
          >
            <MagicWand className="w-3 h-3" />
            {useLLM ? 'Quick' : 'Deep'}
          </Button>
        </div>
        {llmError && (
          <p className="text-xs text-destructive mt-2">
            Deep analysis unavailable. Using keyword-based suggestions.
          </p>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {llmSuggestions.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold text-primary">Deep Analysis Results</span>
            </div>
            {llmSuggestions.map((suggestion) => (
              <div
                key={suggestion.tagName}
                className="flex items-start gap-2 p-2 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className="text-xs font-medium"
                      style={{
                        borderColor: suggestion.tagDef?.color,
                        color: suggestion.tagDef?.color,
                      }}
                    >
                      {suggestion.tagName}
                    </Badge>
                    <Badge variant="secondary" className="text-xs px-1.5 py-0 bg-primary/10 text-primary border-primary/20">
                      AI Recommended
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {suggestion.reason}
                  </p>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 hover:bg-primary hover:text-primary-foreground"
                    onClick={() => handleApply(suggestion.tagName)}
                    title="Apply this tag"
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => handleDismiss(suggestion.tagName)}
                    title="Dismiss suggestion"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {llmSuggestions.length > 0 && otherSuggestions.length > 0 && <Separator />}

        {otherSuggestions.length > 0 && (
          <div className="space-y-2">
            {llmSuggestions.length > 0 && (
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs font-semibold text-muted-foreground">Additional Suggestions</span>
              </div>
            )}
            {otherSuggestions.map((suggestion) => (
              <div
                key={suggestion.tagName}
                className="flex items-start gap-2 p-2 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className="text-xs font-medium"
                      style={{
                        borderColor: suggestion.tagDef?.color,
                        color: suggestion.tagDef?.color,
                      }}
                    >
                      {suggestion.tagName}
                    </Badge>
                    {suggestion.confidence === 'high' && (
                      <Badge variant="secondary" className="text-xs px-1.5 py-0">
                        High confidence
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-1">
                    {suggestion.reason}
                  </p>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 hover:bg-primary hover:text-primary-foreground"
                    onClick={() => handleApply(suggestion.tagName)}
                    title="Apply this tag"
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => handleDismiss(suggestion.tagName)}
                    title="Dismiss suggestion"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {suggestions.length > 0 && (
          <>
            <Separator />
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                className="flex-1 h-8"
                onClick={() => {
                  suggestions.forEach(s => handleApply(s.tagName))
                }}
              >
                <Check className="w-3 h-3 mr-1" />
                Apply All
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="flex-1 h-8"
                onClick={() => {
                  suggestions.forEach(s => handleDismiss(s.tagName))
                }}
              >
                <X className="w-3 h-3 mr-1" />
                Dismiss All
              </Button>
            </div>
          </>
        )}

        {llmAnalysis && useLLM && (
          <div className="mt-3 p-3 bg-muted/50 rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold">Analysis Insights</span>
            </div>
            {llmAnalysis.legalConcepts.length > 0 && (
              <div className="text-xs">
                <span className="font-medium">Legal Concepts: </span>
                <span className="text-muted-foreground">{llmAnalysis.legalConcepts.join(', ')}</span>
              </div>
            )}
            {llmAnalysis.practiceAreas.length > 0 && (
              <div className="text-xs">
                <span className="font-medium">Practice Areas: </span>
                <span className="text-muted-foreground">{llmAnalysis.practiceAreas.join(', ')}</span>
              </div>
            )}
            {llmAnalysis.constitutionalIssues.length > 0 && (
              <div className="text-xs">
                <span className="font-medium">Constitutional Issues: </span>
                <span className="text-muted-foreground">{llmAnalysis.constitutionalIssues.join(', ')}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
