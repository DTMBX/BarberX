import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { Columns, Info, FloppyDisk, Star, Trash, BookmarkSimple } from '@phosphor-icons/react'
import { toast } from 'sonner'
import { translations, sampleVerses, bibleBooks } from '@/lib/data'
import type { UserProfile, TranslationPreset } from '@/lib/types'

interface CompareViewProps {
  userProfile: UserProfile
}

export default function CompareView({ userProfile }: CompareViewProps) {
  const [selectedTranslations, setSelectedTranslations] = useState(
    userProfile?.preferences?.comparisonSet || ['geneva', 'kjv', 'esv', 'niv']
  )
  const [currentPassage] = useState({ workId: 'gen', chapter: 1, verse: 1 })
  const [presets, setPresets] = useKV<TranslationPreset[]>('translation-presets', [])
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [presetName, setPresetName] = useState('')
  const [presetDescription, setPresetDescription] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)
  const [hasLoadedDefault, setHasLoadedDefault] = useState(false)

  useEffect(() => {
    if (!hasLoadedDefault && presets && presets.length > 0) {
      const defaultPreset = presets.find(p => p.isDefault)
      if (defaultPreset) {
        setSelectedTranslations(defaultPreset.translationIds)
        setHasLoadedDefault(true)
      }
    }
  }, [presets, hasLoadedDefault])

  const toggleTranslation = (translationId: string) => {
    setSelectedTranslations(current => {
      if (current.includes(translationId)) {
        return current.filter(id => id !== translationId)
      } else {
        return [...current, translationId]
      }
    })
  }

  const handleSavePreset = () => {
    if (!presetName.trim()) {
      toast.error('Please enter a preset name')
      return
    }

    if (selectedTranslations.length < 2) {
      toast.error('Please select at least 2 translations')
      return
    }

    const newPreset: TranslationPreset = {
      id: `preset-${Date.now()}`,
      name: presetName.trim(),
      description: presetDescription.trim() || undefined,
      translationIds: [...selectedTranslations],
      createdAt: Date.now(),
      isDefault: false
    }

    setPresets((currentPresets) => [...(currentPresets || []), newPreset])
    toast.success(`Preset "${newPreset.name}" saved!`)
    setSaveDialogOpen(false)
    setPresetName('')
    setPresetDescription('')
  }

  const handleLoadPreset = (preset: TranslationPreset) => {
    setSelectedTranslations(preset.translationIds)
    toast.success(`Loaded "${preset.name}"`)
  }

  const handleDeletePreset = (presetId: string) => {
    setPresets((currentPresets) => (currentPresets || []).filter(p => p.id !== presetId))
    toast.success('Preset deleted')
    setDeleteConfirmId(null)
  }

  const handleSetDefaultPreset = (presetId: string) => {
    setPresets((currentPresets) => 
      (currentPresets || []).map(p => ({
        ...p,
        isDefault: p.id === presetId
      }))
    )
    toast.success('Default preset updated')
  }

  const activeTranslations = translations.filter(t => selectedTranslations.includes(t.id))
  const book = bibleBooks.find(b => b.id === currentPassage.workId)

  const getVersesForPassage = () => {
    return selectedTranslations.map(transId => {
      const verse = sampleVerses.find(
        v => v.workId === currentPassage.workId &&
             v.chapterNumber === currentPassage.chapter &&
             v.verseNumber === currentPassage.verse &&
             v.translationId === transId
      )
      return { translationId: transId, verse }
    })
  }

  const verses = getVersesForPassage()

  return (
    <div className="h-full flex flex-col">
      <div className="p-6 border-b">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-2 text-foreground flex items-center gap-3" style={{ fontFamily: 'var(--font-heading)' }}>
            <Columns size={32} weight="duotone" className="text-primary" />
            Compare Translations
          </h2>
          <p className="text-muted-foreground mb-4">
            See how different English Bibles translate the same passage
          </p>

          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex flex-wrap gap-2 items-center flex-1">
                <span className="text-sm font-medium">Active translations:</span>
                {translations.map(trans => (
                  <Badge
                    key={trans.id}
                    variant={selectedTranslations.includes(trans.id) ? 'default' : 'outline'}
                    className="cursor-pointer transition-all hover:scale-105"
                    onClick={() => toggleTranslation(trans.id)}
                  >
                    {trans.shortCode}
                  </Badge>
                ))}
              </div>
              <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="default" size="sm" className="gap-2">
                    <FloppyDisk size={18} weight="duotone" />
                    Save Preset
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Save Translation Preset</DialogTitle>
                    <DialogDescription>
                      Save your current translation combination for quick access later
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="preset-name">Preset Name *</Label>
                      <Input
                        id="preset-name"
                        placeholder="e.g., Reformed Study Set"
                        value={presetName}
                        onChange={(e) => setPresetName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="preset-description">Description (optional)</Label>
                      <Textarea
                        id="preset-description"
                        placeholder="e.g., Geneva, KJV, and ESV for Reformed theology study"
                        value={presetDescription}
                        onChange={(e) => setPresetDescription(e.target.value)}
                        rows={3}
                      />
                    </div>
                    <div className="bg-muted p-3 rounded-md">
                      <p className="text-sm font-medium mb-2">Selected Translations ({selectedTranslations.length}):</p>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedTranslations.map(id => {
                          const trans = translations.find(t => t.id === id)
                          return trans ? (
                            <Badge key={id} variant="secondary" className="text-xs">
                              {trans.shortCode}
                            </Badge>
                          ) : null
                        })}
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setSaveDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleSavePreset}>
                      <FloppyDisk size={18} weight="duotone" className="mr-2" />
                      Save Preset
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>

            {presets && presets.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <BookmarkSimple size={18} weight="duotone" className="text-primary" />
                  <span className="text-sm font-medium">Saved Presets:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {presets.map(preset => {
                    const presetTranslations = preset.translationIds
                      .map(id => translations.find(t => t.id === id))
                      .filter(Boolean)
                    
                    return (
                      <Tooltip key={preset.id}>
                        <TooltipTrigger asChild>
                          <div className="group relative flex items-center gap-2 bg-card border rounded-lg px-3 py-2 hover:bg-accent transition-colors cursor-pointer">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-auto p-0 hover:bg-transparent"
                              onClick={() => handleLoadPreset(preset)}
                            >
                              <div className="flex items-center gap-2">
                                {preset.isDefault && (
                                  <Star size={14} weight="fill" className="text-accent" />
                                )}
                                <span className="text-sm font-medium">{preset.name}</span>
                                <Badge variant="outline" className="text-xs">
                                  {preset.translationIds.length}
                                </Badge>
                              </div>
                            </Button>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => handleSetDefaultPreset(preset.id)}
                                title="Set as default"
                              >
                                <Star size={14} weight={preset.isDefault ? "fill" : "regular"} />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                                onClick={() => setDeleteConfirmId(preset.id)}
                                title="Delete preset"
                              >
                                <Trash size={14} weight="duotone" />
                              </Button>
                            </div>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent side="bottom" className="max-w-xs">
                          <div className="space-y-1">
                            <p className="font-semibold">{preset.name}</p>
                            {preset.description && (
                              <p className="text-xs opacity-90">{preset.description}</p>
                            )}
                            <div className="flex flex-wrap gap-1 pt-1">
                              {presetTranslations.map(trans => (
                                trans && (
                                  <span key={trans.id} className="text-xs bg-primary-foreground text-primary px-1.5 py-0.5 rounded">
                                    {trans.shortCode}
                                  </span>
                                )
                              ))}
                            </div>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <Dialog open={deleteConfirmId !== null} onOpenChange={(open) => !open && setDeleteConfirmId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Preset?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this preset? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmId(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={() => deleteConfirmId && handleDeletePreset(deleteConfirmId)}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="flex-1 overflow-hidden">
        <div className="h-full max-w-7xl mx-auto p-6">
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-xl flex items-center justify-between">
                <span>
                  {book?.title} {currentPassage.chapter}:{currentPassage.verse}
                </span>
                <Select defaultValue={currentPassage.workId}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {bibleBooks.map(b => (
                      <SelectItem key={b.id} value={b.id}>
                        {b.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardTitle>
            </CardHeader>
          </Card>

          <ScrollArea className="h-[calc(100vh-20rem)]">
            <div className="space-y-6">
              {verses.map(({ translationId, verse }) => {
                const translation = translations.find(t => t.id === translationId)
                if (!translation) return null

                return (
                  <Card key={translationId} className="border-l-4" style={{ borderLeftColor: translationId === 'geneva' ? 'var(--primary)' : 'var(--accent)' }}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">{translation.name}</CardTitle>
                          <p className="text-sm text-muted-foreground">
                            {translation.year} • {translation.philosophy.replace(/-/g, ' ')}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Info size={20} weight="duotone" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {verse ? (
                        <div>
                          <p 
                            className="text-lg leading-relaxed"
                            style={{ 
                              fontFamily: 'var(--font-body)',
                              lineHeight: '1.75'
                            }}
                          >
                            <span className="font-mono text-xs text-muted-foreground mr-2" style={{ fontFamily: 'var(--font-mono)' }}>
                              {verse.verseNumber}
                            </span>
                            {verse.text}
                          </p>
                          {translationId === 'geneva' && (
                            <div className="mt-4 p-3 bg-secondary/50 rounded-md border-l-2 border-accent">
                              <p className="text-xs font-semibold mb-1 text-accent-foreground">Geneva Note:</p>
                              <p className="text-sm text-muted-foreground italic">
                                This verse establishes God as the sovereign creator, a foundational Reformed doctrine emphasizing divine sovereignty and purpose in creation.
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-muted-foreground italic">
                          Verse not available in this translation
                        </p>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </ScrollArea>

          {activeTranslations.length < 2 && (
            <Card className="mt-6 border-accent">
              <CardContent className="pt-6 text-center">
                <p className="text-muted-foreground">
                  Select at least two translations to compare passages side by side
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
