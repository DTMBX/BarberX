import { useEffect, useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { X, Translate, Copy, Check, Plus, Minus, BookmarkSimple } from '@phosphor-icons/react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { toast } from 'sonner'
import { fetchVerse } from '@/lib/bibleApi'
import { bibleBooks } from '@/lib/data'
import type { TranslationPreset } from '@/lib/types'

interface VerseComparisonDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  verseData: {
    bookId: string
    chapter: number
    verse: number
    text: string
    translation: string
  }
}

const AVAILABLE_TRANSLATIONS = [
  { id: 'kjv', name: 'King James Version', abbr: 'KJV' },
  { id: 'web', name: 'World English Bible', abbr: 'WEB' },
  { id: 'bbe', name: 'Bible in Basic English', abbr: 'BBE' },
  { id: 'ylt', name: "Young's Literal Translation", abbr: 'YLT' },
  { id: 'oeb-cw', name: 'Open English Bible', abbr: 'OEB' },
  { id: 'webbe', name: 'World English Bible, British Edition', abbr: 'WEBBE' },
  { id: 'wmb', name: 'World Messianic Bible', abbr: 'WMB' },
  { id: 'net', name: 'New English Translation', abbr: 'NET' },
]

interface TranslationVerse {
  translationId: string
  translationName: string
  translationAbbr: string
  text: string
  isLoading: boolean
  error?: boolean
}

export default function VerseComparisonDialog({ open, onOpenChange, verseData }: VerseComparisonDialogProps) {
  const [selectedTranslations, setSelectedTranslations] = useState<string[]>([verseData.translation])
  const [translationVerses, setTranslationVerses] = useState<TranslationVerse[]>([])
  const [copied, setCopied] = useState(false)
  const [showTranslationPicker, setShowTranslationPicker] = useState(false)
  const [presets] = useKV<TranslationPreset[]>('translation-presets', [])

  useEffect(() => {
    if (open) {
      loadTranslations()
    }
  }, [open, selectedTranslations, verseData])

  const loadTranslations = async () => {
    const verses: TranslationVerse[] = selectedTranslations.map(translationId => {
      const translation = AVAILABLE_TRANSLATIONS.find(t => t.id === translationId)
      return {
        translationId,
        translationName: translation?.name || translationId.toUpperCase(),
        translationAbbr: translation?.abbr || translationId.toUpperCase(),
        text: '',
        isLoading: true,
      }
    })

    setTranslationVerses(verses)

    for (let i = 0; i < selectedTranslations.length; i++) {
      const translationId = selectedTranslations[i]
      
      try {
        const today = new Date().toISOString().split('T')[0]
        const cacheKey = `verse-of-day-${today}-${translationId}`
        
        let cachedData = await window.spark.kv.get<{ text: string }>(cacheKey)
        
        if (cachedData && cachedData.text) {
          setTranslationVerses(prev => 
            prev.map((v, idx) => 
              idx === i ? { ...v, text: cachedData.text, isLoading: false } : v
            )
          )
        } else {
          const verseResult = await fetchVerse({
            translationId,
            bookId: verseData.bookId,
            chapter: verseData.chapter,
            verse: verseData.verse
          })

          if (verseResult && verseResult.text) {
            await window.spark.kv.set(cacheKey, { text: verseResult.text })
            setTranslationVerses(prev => 
              prev.map((v, idx) => 
                idx === i ? { ...v, text: verseResult.text, isLoading: false } : v
              )
            )
          } else {
            setTranslationVerses(prev => 
              prev.map((v, idx) => 
                idx === i ? { ...v, error: true, isLoading: false } : v
              )
            )
          }
        }
      } catch (error) {
        console.error(`Failed to load translation ${translationId}:`, error)
        setTranslationVerses(prev => 
          prev.map((v, idx) => 
            idx === i ? { ...v, error: true, isLoading: false } : v
          )
        )
      }
    }
  }

  const handleToggleTranslation = (translationId: string) => {
    setSelectedTranslations(prev => {
      if (prev.includes(translationId)) {
        if (prev.length === 1) {
          toast.error('At least one translation must be selected')
          return prev
        }
        return prev.filter(t => t !== translationId)
      } else {
        if (prev.length >= 6) {
          toast.error('Maximum 6 translations can be compared at once')
          return prev
        }
        return [...prev, translationId]
      }
    })
  }

  const handleLoadPreset = (preset: TranslationPreset) => {
    setSelectedTranslations(preset.translationIds)
    toast.success(`Loaded "${preset.name}"`)
  }

  const handleCopyAll = () => {
    const book = bibleBooks.find(b => b.id === verseData.bookId)
    const reference = `${book?.title} ${verseData.chapter}:${verseData.verse}`
    
    let text = `${reference}\n\n`
    translationVerses.forEach((verse, index) => {
      if (!verse.isLoading && !verse.error) {
        text += `${verse.translationAbbr}:\n"${verse.text}"\n\n`
      }
    })
    
    navigator.clipboard.writeText(text.trim())
    setCopied(true)
    toast.success('All translations copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  const book = bibleBooks.find(b => b.id === verseData.bookId)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col p-0">
        <DialogHeader className="shrink-0 px-6 pt-6 pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <DialogTitle className="text-2xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Translate size={28} weight="duotone" className="text-primary" />
                </div>
                Translation Comparison
              </DialogTitle>
              <div className="text-base text-muted-foreground mt-2 font-semibold">
                {book?.title} {verseData.chapter}:{verseData.verse}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Compare the verse across {selectedTranslations.length} translation{selectedTranslations.length !== 1 ? 's' : ''}
              </p>
            </div>
            <div className="flex gap-2 flex-wrap justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowTranslationPicker(!showTranslationPicker)}
                className="gap-2"
              >
                {showTranslationPicker ? <Minus size={16} /> : <Plus size={16} />}
                <span className="hidden sm:inline">{showTranslationPicker ? 'Hide' : 'Select'} Translations</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyAll}
                className="gap-2"
              >
                {copied ? <Check size={16} /> : <Copy size={16} />}
                <span className="hidden sm:inline">{copied ? 'Copied!' : 'Copy All'}</span>
              </Button>
            </div>
          </div>
        </DialogHeader>

        {showTranslationPicker && (
          <div className="shrink-0 px-6">
            <div className="bg-gradient-to-br from-muted/50 to-muted/30 rounded-lg p-4 border border-border">
              <Label className="text-sm font-medium mb-3 block flex items-center gap-2">
                <Translate size={18} weight="duotone" className="text-primary" />
                Select up to 6 translations to compare side-by-side
              </Label>
              
              {presets && presets.length > 0 && (
                <div className="mb-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <BookmarkSimple size={16} weight="duotone" className="text-primary" />
                    <span className="text-xs font-medium">Quick load preset:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {presets.map(preset => (
                      <Button
                        key={preset.id}
                        variant="outline"
                        size="sm"
                        onClick={() => handleLoadPreset(preset)}
                        className="text-xs h-7"
                      >
                        {preset.name} ({preset.translationIds.length})
                      </Button>
                    ))}
                  </div>
                  <Separator className="my-3" />
                </div>
              )}
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {AVAILABLE_TRANSLATIONS.map(translation => {
                  const isSelected = selectedTranslations.includes(translation.id)
                  return (
                    <div 
                      key={translation.id} 
                      className={`flex items-center gap-2 p-2 rounded-md transition-colors ${
                        isSelected ? 'bg-primary/10' : 'hover:bg-muted/50'
                      }`}
                    >
                      <Checkbox
                        id={translation.id}
                        checked={isSelected}
                        onCheckedChange={() => handleToggleTranslation(translation.id)}
                      />
                      <Label
                        htmlFor={translation.id}
                        className="text-sm cursor-pointer flex-1 font-medium"
                      >
                        {translation.abbr}
                      </Label>
                    </div>
                  )
                })}
              </div>
            </div>
            <Separator className="mt-4" />
          </div>
        )}

        <ScrollArea className="flex-1 px-6">
          <div className="space-y-6 pb-6 pt-2">
            {translationVerses.map((verse, index) => (
              <div 
                key={`${verse.translationId}-${index}`} 
                className="space-y-3 group"
              >
                <div className="flex items-center gap-3 sticky top-0 bg-background/95 backdrop-blur-sm py-2 z-10">
                  <Badge 
                    variant="default" 
                    className="font-bold text-sm px-3 py-1"
                  >
                    {verse.translationAbbr}
                  </Badge>
                  <span className="text-sm text-muted-foreground font-medium">
                    {verse.translationName}
                  </span>
                </div>
                
                {verse.isLoading ? (
                  <div className="space-y-2 animate-pulse">
                    <div className="h-5 bg-muted rounded w-full" />
                    <div className="h-5 bg-muted rounded w-5/6" />
                    <div className="h-5 bg-muted rounded w-4/6" />
                  </div>
                ) : verse.error ? (
                  <div className="text-sm text-destructive p-4 bg-destructive/10 rounded-lg border border-destructive/20 flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
                    Failed to load this translation
                  </div>
                ) : (
                  <div 
                    className="text-lg leading-relaxed p-5 bg-gradient-to-br from-card to-muted/20 rounded-lg border border-border hover:border-primary/50 hover:shadow-md transition-all duration-200"
                    style={{ fontFamily: 'var(--font-body)', lineHeight: '1.8' }}
                  >
                    <span className="text-muted-foreground text-xl mr-1">"</span>
                    {verse.text}
                    <span className="text-muted-foreground text-xl ml-1">"</span>
                  </div>
                )}
                
                {index < translationVerses.length - 1 && (
                  <Separator className="mt-6" />
                )}
              </div>
            ))}

            {translationVerses.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Translate size={64} weight="duotone" className="text-muted-foreground/40 mb-4" />
                <p className="text-muted-foreground text-lg">No translations selected</p>
                <p className="text-sm text-muted-foreground mt-1">Click "Select Translations" to choose versions to compare</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
