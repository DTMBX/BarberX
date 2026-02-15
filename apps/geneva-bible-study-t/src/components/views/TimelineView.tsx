import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Clock, Warning, BookOpen } from '@phosphor-icons/react'
import { timelineEvents } from '@/lib/data'
import InteractiveTimeline from '@/components/timeline/InteractiveTimeline'
import type { HistoricalEvent } from '@/lib/types'

const confidenceColors = {
  traditional: 'bg-amber-500',
  'scholarly-consensus': 'bg-green-500',
  debated: 'bg-orange-500',
  speculative: 'bg-red-500'
}

const confidenceLabels = {
  traditional: 'Traditional View',
  'scholarly-consensus': 'Scholarly Consensus',
  debated: 'Debated',
  speculative: 'Speculative'
}

const categoryColors = {
  narrative: 'border-l-blue-500',
  composition: 'border-l-purple-500',
  'canon-formation': 'border-l-green-500',
  'community-history': 'border-l-amber-500'
}

const categoryLabels = {
  narrative: 'Biblical Narrative',
  composition: 'Text Composition',
  'canon-formation': 'Canon Formation',
  'community-history': 'Community History'
}

export default function TimelineView() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const filteredEvents = selectedCategory === 'all'
    ? timelineEvents
    : timelineEvents.filter(event => event.category === selectedCategory)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 text-foreground flex items-center gap-3" style={{ fontFamily: 'var(--font-heading)' }}>
          <Clock size={32} weight="duotone" className="text-primary" />
          Historical Timeline
        </h2>
        <p className="text-muted-foreground">
          Explore how the biblical library formed across history and traditions
        </p>
      </div>

      <Card className="mb-6 bg-secondary/30">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Warning size={20} weight="duotone" className="text-accent" />
            Understanding Confidence Labels
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="font-medium">Scholarly Consensus:</span>
              <span className="text-muted-foreground">Widely accepted by historians</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="font-medium">Traditional:</span>
              <span className="text-muted-foreground">Traditional religious view</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="font-medium">Debated:</span>
              <span className="text-muted-foreground">Ongoing scholarly discussion</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="font-medium">Speculative:</span>
              <span className="text-muted-foreground">Theoretical or contested</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="narrative">Narrative</TabsTrigger>
          <TabsTrigger value="composition">Composition</TabsTrigger>
          <TabsTrigger value="canon-formation">Canon</TabsTrigger>
          <TabsTrigger value="community-history">History</TabsTrigger>
        </TabsList>
      </Tabs>

      <InteractiveTimeline events={filteredEvents} selectedCategory={selectedCategory} />

      <Card className="mt-8 bg-muted/30">
        <CardHeader>
          <CardTitle className="text-lg">Timeline Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-3">
              <div className="w-1 h-6 bg-blue-500 rounded" />
              <div>
                <p className="font-medium">Biblical Narrative</p>
                <p className="text-muted-foreground">Events described within biblical texts</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1 h-6 bg-purple-500 rounded" />
              <div>
                <p className="font-medium">Text Composition</p>
                <p className="text-muted-foreground">When scholars believe texts were written/compiled</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1 h-6 bg-green-500 rounded" />
              <div>
                <p className="font-medium">Canon Formation</p>
                <p className="text-muted-foreground">How different traditions formed their biblical canons</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1 h-6 bg-amber-500 rounded" />
              <div>
                <p className="font-medium">Community History</p>
                <p className="text-muted-foreground">Major events in Jewish and Christian history</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
