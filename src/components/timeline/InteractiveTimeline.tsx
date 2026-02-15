import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowsOut } from '@phosphor-icons/react'
import { useIsMobile } from '@/hooks/use-mobile'
import type { HistoricalEvent } from '@/lib/types'

interface InteractiveTimelineProps {
  events: HistoricalEvent[]
  selectedCategory?: string
}

interface TimelineEvent extends HistoricalEvent {
  dateValue: number
}

const confidenceColors: Record<string, string> = {
  traditional: '#f59e0b',
  'scholarly-consensus': '#10b981',
  debated: '#f97316',
  speculative: '#ef4444'
}

const categoryColors: Record<string, string> = {
  narrative: '#3b82f6',
  composition: '#a855f7',
  'canon-formation': '#10b981',
  'community-history': '#f59e0b'
}

function parseDateToValue(dateString: string): number {
  const match = dateString.match(/-?(\d+)/)
  if (match) {
    const year = parseInt(match[1])
    return dateString.includes('BCE') ? -year : year
  }
  return 0
}

export default function InteractiveTimeline({ events, selectedCategory }: InteractiveTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })

  const timelineEvents: TimelineEvent[] = events.map(event => ({
    ...event,
    dateValue: parseDateToValue(event.date)
  }))

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const width = containerRef.current.clientWidth
        const height = isMobile ? 300 : 500
        setDimensions({ width, height })
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [isMobile])

  useEffect(() => {
    if (!svgRef.current || timelineEvents.length === 0) return

    const { width, height } = dimensions
    const margin = { top: 40, right: 40, bottom: 60, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    d3.select(svgRef.current).selectAll('*').remove()

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const dateExtent = d3.extent(timelineEvents, d => d.dateValue) as [number, number]
    
    const xScale = d3.scaleLinear()
      .domain(dateExtent)
      .range([0, innerWidth])

    const categories = Array.from(new Set(timelineEvents.map(e => e.category)))
    const yScale = d3.scaleBand()
      .domain(categories)
      .range([0, innerHeight])
      .padding(0.2)

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 10])
      .translateExtent([[0, 0], [width, height]])
      .on('zoom', (event) => {
        g.attr('transform', `translate(${margin.left + event.transform.x},${margin.top + event.transform.y}) scale(${event.transform.k})`)
      })

    svg.call(zoom as any)

    const xAxis = d3.axisBottom(xScale)
      .ticks(isMobile ? 5 : 10)
      .tickFormat(d => {
        const year = Math.abs(d as number)
        return d < 0 ? `${year} BCE` : `${year} CE`
      })

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .style('font-family', 'var(--font-mono)')
      .style('font-size', '12px')

    const yAxis = d3.axisLeft(yScale)

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis)
      .style('font-family', 'var(--font-heading)')
      .style('font-size', '12px')

    g.append('line')
      .attr('x1', xScale(0))
      .attr('x2', xScale(0))
      .attr('y1', 0)
      .attr('y2', innerHeight)
      .attr('stroke', 'oklch(0.45 0.02 40)')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')

    const filteredEvents = selectedCategory && selectedCategory !== 'all'
      ? timelineEvents.filter(e => e.category === selectedCategory)
      : timelineEvents

    const eventGroups = g.selectAll('.event')
      .data(filteredEvents)
      .enter()
      .append('g')
      .attr('class', 'event')
      .attr('transform', d => `translate(${xScale(d.dateValue)},${yScale(d.category)! + yScale.bandwidth() / 2})`)
      .style('cursor', 'pointer')
      .on('click', (_, d) => {
        setSelectedEvent(d)
      })

    eventGroups.append('circle')
      .attr('r', isMobile ? 6 : 8)
      .attr('fill', d => categoryColors[d.category])
      .attr('stroke', d => confidenceColors[d.dateConfidence])
      .attr('stroke-width', 2)
      .style('transition', 'all 0.2s')
      .on('mouseenter', function() {
        d3.select(this)
          .attr('r', isMobile ? 9 : 12)
          .attr('stroke-width', 3)
      })
      .on('mouseleave', function() {
        d3.select(this)
          .attr('r', isMobile ? 6 : 8)
          .attr('stroke-width', 2)
      })

    if (!isMobile) {
      eventGroups.append('text')
        .text(d => d.title.length > 20 ? d.title.substring(0, 20) + '...' : d.title)
        .attr('x', 12)
        .attr('y', 4)
        .style('font-size', '11px')
        .style('font-family', 'var(--font-heading)')
        .style('fill', 'oklch(0.25 0.02 40)')
        .style('pointer-events', 'none')
    }

  }, [timelineEvents, dimensions, selectedCategory, isMobile])

  const handleReset = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().duration(750).call(
        d3.zoom<SVGSVGElement, unknown>().transform as any,
        d3.zoomIdentity
      )
    }
  }

  return (
    <div className="space-y-4">
      <div ref={containerRef} className="border border-border rounded-lg overflow-hidden bg-card">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant="secondary">Interactive Timeline</Badge>
            <span className="text-sm text-muted-foreground">Pan & Zoom enabled</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleReset}>
              <ArrowsOut size={16} weight="duotone" />
            </Button>
          </div>
        </div>
        <svg ref={svgRef} className="w-full" />
      </div>

      {selectedEvent && (
        <Card className="border-l-4" style={{ borderLeftColor: categoryColors[selectedEvent.category] }}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between gap-4 mb-3">
              <h3 className="text-lg font-semibold" style={{ fontFamily: 'var(--font-heading)' }}>
                {selectedEvent.title}
              </h3>
              <Button variant="ghost" size="sm" onClick={() => setSelectedEvent(null)}>
                ×
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              <Badge variant="outline">{selectedEvent.date}</Badge>
              <Badge variant="secondary">{selectedEvent.category}</Badge>
              <Badge style={{ backgroundColor: confidenceColors[selectedEvent.dateConfidence], color: 'white' }}>
                {selectedEvent.dateConfidence}
              </Badge>
            </div>
            <p className="text-sm text-foreground leading-relaxed mb-3">
              {selectedEvent.description}
            </p>
            {selectedEvent.sources.length > 0 && (
              <div className="text-xs text-muted-foreground">
                <p className="font-semibold mb-1">Sources:</p>
                {selectedEvent.sources.map(source => (
                  <p key={source.id}>• {source.title}{source.author && ` by ${source.author}`}</p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
