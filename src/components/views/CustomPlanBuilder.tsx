import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Trash, BookOpen } from '@phosphor-icons/react'
import { bibleBooks } from '@/lib/data'
import { getBookDisplayName } from '@/lib/reading-plans'
import type { ReadingPlan, PassageReference } from '@/lib/types'
import { toast } from 'sonner'

interface CustomPlanBuilderProps {
  open: boolean
  onClose: () => void
  onCreatePlan: (plan: ReadingPlan) => void
}

interface DayReading {
  day: number
  readings: PassageReference[]
}

export default function CustomPlanBuilder({ open, onClose, onCreatePlan }: CustomPlanBuilderProps) {
  const [planName, setPlanName] = useState('')
  const [planDescription, setPlanDescription] = useState('')
  const [selectedBooks, setSelectedBooks] = useState<string[]>([])
  const [dayReadings, setDayReadings] = useState<DayReading[]>([
    { day: 1, readings: [] }
  ])
  const [currentDay, setCurrentDay] = useState(1)
  const [selectedBookForDay, setSelectedBookForDay] = useState<string>('')
  const [chaptersPerDay, setChaptersPerDay] = useState(3)

  const toggleBook = (bookId: string) => {
    setSelectedBooks(prev => 
      prev.includes(bookId) 
        ? prev.filter(id => id !== bookId)
        : [...prev, bookId]
    )
  }

  const addReadingToDay = (day: number, bookId: string, chapters: number[]) => {
    setDayReadings(prev => {
      const existingDay = prev.find(d => d.day === day)
      if (existingDay) {
        return prev.map(d => {
          if (d.day === day) {
            const newReadings = chapters.map(ch => ({
              workId: bookId,
              chapterNumber: ch,
              verseNumber: 1
            }))
            return {
              ...d,
              readings: [...d.readings, ...newReadings]
            }
          }
          return d
        })
      } else {
        return [...prev, {
          day,
          readings: chapters.map(ch => ({
            workId: bookId,
            chapterNumber: ch,
            verseNumber: 1
          }))
        }].sort((a, b) => a.day - b.day)
      }
    })
  }

  const removeReadingFromDay = (day: number, index: number) => {
    setDayReadings(prev => 
      prev.map(d => {
        if (d.day === day) {
          return {
            ...d,
            readings: d.readings.filter((_, i) => i !== index)
          }
        }
        return d
      }).filter(d => d.readings.length > 0)
    )
  }

  const autoGeneratePlan = () => {
    if (selectedBooks.length === 0) {
      toast.error('Please select at least one book')
      return
    }

    const newDayReadings: DayReading[] = []
    let currentDayNum = 1
    let currentDayChapters = 0

    for (const bookId of selectedBooks) {
      const book = bibleBooks.find(b => b.id === bookId)
      if (!book) continue

      for (let chapter = 1; chapter <= book.chaptersCount; chapter++) {
        if (currentDayChapters === 0) {
          newDayReadings.push({ day: currentDayNum, readings: [] })
        }

        newDayReadings[newDayReadings.length - 1].readings.push({
          workId: bookId,
          chapterNumber: chapter,
          verseNumber: 1
        })

        currentDayChapters++

        if (currentDayChapters >= chaptersPerDay) {
          currentDayNum++
          currentDayChapters = 0
        }
      }
    }

    setDayReadings(newDayReadings)
    toast.success(`Generated ${newDayReadings.length}-day plan`)
  }

  const handleCreate = () => {
    if (!planName.trim()) {
      toast.error('Please enter a plan name')
      return
    }

    if (dayReadings.length === 0 || dayReadings.every(d => d.readings.length === 0)) {
      toast.error('Please add at least one reading')
      return
    }

    const plan: ReadingPlan = {
      id: `custom-${Date.now()}`,
      name: planName,
      description: planDescription || 'Custom reading plan',
      duration: dayReadings.length,
      category: 'custom',
      days: dayReadings.map(dr => ({
        day: dr.day,
        readings: dr.readings
      })),
      isCustom: true,
      createdAt: Date.now()
    }

    onCreatePlan(plan)
    
    setPlanName('')
    setPlanDescription('')
    setSelectedBooks([])
    setDayReadings([{ day: 1, readings: [] }])
    toast.success('Custom plan created!')
  }

  const currentDayData = dayReadings.find(d => d.day === currentDay) || { day: currentDay, readings: [] }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Create Custom Reading Plan</DialogTitle>
          <DialogDescription>
            Design your own Bible reading journey by selecting books and organizing daily readings
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="plan-name">Plan Name</Label>
              <Input
                id="plan-name"
                placeholder="My Custom Reading Plan"
                value={planName}
                onChange={(e) => setPlanName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="plan-description">Description (Optional)</Label>
              <Textarea
                id="plan-description"
                placeholder="Describe your reading plan..."
                value={planDescription}
                onChange={(e) => setPlanDescription(e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Select Books to Include</Label>
                <Badge variant="secondary">
                  {selectedBooks.length} book{selectedBooks.length !== 1 ? 's' : ''} selected
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 p-4 border rounded-lg bg-muted/20">
                {bibleBooks.map(book => (
                  <div key={book.id} className="flex items-center gap-2">
                    <Checkbox
                      id={book.id}
                      checked={selectedBooks.includes(book.id)}
                      onCheckedChange={() => toggleBook(book.id)}
                    />
                    <Label
                      htmlFor={book.id}
                      className="text-sm cursor-pointer"
                    >
                      {book.shortName}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Auto-Generate Plan</Label>
              </div>
              <div className="flex gap-3 items-end">
                <div className="flex-1 space-y-2">
                  <Label htmlFor="chapters-per-day">Chapters per day</Label>
                  <Input
                    id="chapters-per-day"
                    type="number"
                    min="1"
                    max="10"
                    value={chaptersPerDay}
                    onChange={(e) => setChaptersPerDay(parseInt(e.target.value) || 1)}
                  />
                </div>
                <Button onClick={autoGeneratePlan} variant="secondary">
                  Generate Plan
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Automatically distribute selected books across days based on chapters per day
              </p>
            </div>

            {dayReadings.length > 0 && (
              <div className="space-y-3">
                <Label>Plan Overview</Label>
                <div className="p-4 border rounded-lg bg-card space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Total Days:</span>
                    <span className="font-semibold">{dayReadings.length}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Total Chapters:</span>
                    <span className="font-semibold">
                      {dayReadings.reduce((sum, d) => sum + d.readings.length, 0)}
                    </span>
                  </div>
                </div>

                <div className="space-y-2 mt-4">
                  <Label>Daily Readings Preview</Label>
                  <ScrollArea className="h-[300px] border rounded-lg p-4">
                    <div className="space-y-3">
                      {dayReadings.map(day => (
                        <div key={day.day} className="p-3 bg-muted/30 rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-sm">Day {day.day}</span>
                            <Badge variant="outline" className="text-xs">
                              {day.readings.length} chapter{day.readings.length !== 1 ? 's' : ''}
                            </Badge>
                          </div>
                          <div className="space-y-1">
                            {day.readings.map((reading, idx) => (
                              <div key={idx} className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">
                                  {getBookDisplayName(reading.workId)} {reading.chapterNumber}
                                </span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0"
                                  onClick={() => removeReadingFromDay(day.day, idx)}
                                >
                                  <Trash size={14} />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleCreate}>
            Create Plan
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
