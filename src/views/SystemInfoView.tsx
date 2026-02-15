import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Flask, 
  Database, 
  Eye, 
  Microphone, 
  Graph,
  MagnifyingGlass,
  ShieldCheck,
  CloudArrowUp,
  CheckCircle,
  Warning,
  Calculator,
  ClockCounterClockwise,
  CurrencyDollar,
  ChartLine
} from '@phosphor-icons/react'

export function SystemInfoView() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Architecture</h1>
        <p className="text-muted-foreground mt-1">
          Technical requirements and implementation roadmap for production deployment
        </p>
      </div>
      
      <Alert className="border-[oklch(0.45_0.15_280)]/50 bg-[oklch(0.45_0.15_280)]/10">
        <Flask className="text-[oklch(0.65_0.18_280)]" size={20} weight="duotone" />
        <AlertDescription>
          <strong className="font-semibold">Prototype Status:</strong> This application demonstrates the complete user interface, 
          data models, and workflows for an audit-grade public records analysis platform. All data shown is simulated. 
          Production deployment requires backend infrastructure detailed below.
        </AlertDescription>
      </Alert>
      
      <Card className="border-accent/30 bg-accent/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl">
            <Calculator size={28} className="text-accent" weight="duotone" />
            Feasibility Analysis: Processing 3 Million PDFs
          </CardTitle>
          <CardDescription>
            Real-world constraints, timelines, and resource requirements for the justice.gov/epstein corpus
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert>
            <CheckCircle size={20} className="text-accent" weight="fill" />
            <AlertDescription className="font-semibold">
              YES, processing 3 million PDFs with OCR and Whisper is technically feasible with appropriate infrastructure, 
              but requires careful planning around rate limiting, costs, and processing time.
            </AlertDescription>
          </Alert>
          
          <Separator />
          
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <ClockCounterClockwise size={20} className="text-accent" weight="duotone" />
              Processing Timeline Breakdown
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="font-medium text-accent">Phase 1: Discovery & Download</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Polite crawling rate:</span>
                    <span className="font-mono text-right">5-10 req/second</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Discovery time:</span>
                    <span className="font-mono text-right">2-7 days</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Download (10 workers):</span>
                    <span className="font-mono text-right">15-30 days</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Avg doc size assumption:</span>
                    <span className="font-mono text-right">1-3 MB</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Total storage needed:</span>
                    <span className="font-mono text-right font-semibold">3-9 TB</span>
                  </div>
                </div>
                <Alert className="border-amber-500/30 bg-amber-500/10">
                  <Warning size={16} className="text-amber-400" weight="fill" />
                  <AlertDescription className="text-xs">
                    Must respect DOJ rate limits and Queue-it controls. May require weeks to avoid overloading servers.
                  </AlertDescription>
                </Alert>
              </div>
              
              <div className="space-y-3">
                <div className="font-medium text-accent">Phase 2: Text Extraction</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Native text extraction:</span>
                    <span className="font-mono text-right">2-5 days</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Est. scanned docs (30%):</span>
                    <span className="font-mono text-right">900K PDFs</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Avg pages per doc:</span>
                    <span className="font-mono text-right">10-50 pages</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-muted-foreground">Total pages needing OCR:</span>
                    <span className="font-mono text-right font-semibold">9M-45M pages</span>
                  </div>
                </div>
                <Badge variant="outline" className="text-xs">
                  Only OCR when native extraction yields insufficient text
                </Badge>
              </div>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Eye size={20} className="text-accent" weight="duotone" />
              OCR Processing: The Bottleneck
            </h3>
            
            <div className="grid md:grid-cols-3 gap-4">
              <Card className="bg-card/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Local Tesseract</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Speed per worker:</span>
                    <span className="font-mono">2-5 pages/sec</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">20 GPU workers:</span>
                    <span className="font-mono">40-100 pg/sec</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Time for 20M pages:</span>
                    <span className="font-mono font-semibold text-accent">55-140 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Hardware cost:</span>
                    <span className="font-mono">$5K-20K</span>
                  </div>
                  <Badge variant="secondary" className="text-xs mt-2">Best for controlled costs</Badge>
                </CardContent>
              </Card>
              
              <Card className="bg-card/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Cloud OCR (Azure/AWS)</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Speed (parallel):</span>
                    <span className="font-mono">100-500 pg/sec</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Time for 20M pages:</span>
                    <span className="font-mono font-semibold text-accent">11-55 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cost per page:</span>
                    <span className="font-mono">$0.0015-$0.003</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total cost:</span>
                    <span className="font-mono font-semibold text-destructive">$30K-$60K</span>
                  </div>
                  <Badge variant="secondary" className="text-xs mt-2">Fastest but expensive</Badge>
                </CardContent>
              </Card>
              
              <Card className="bg-card/50 border-accent/40">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Hybrid Approach ⭐</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">High-quality → Cloud:</span>
                    <span className="font-mono">20% of pages</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Standard → Local:</span>
                    <span className="font-mono">80% of pages</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Time estimate:</span>
                    <span className="font-mono font-semibold text-accent">20-40 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cost estimate:</span>
                    <span className="font-mono">$8K-$15K</span>
                  </div>
                  <Badge className="text-xs mt-2 bg-accent/20 text-accent border-accent/30">Recommended balance</Badge>
                </CardContent>
              </Card>
            </div>
            
            <Alert className="bg-primary/10 border-primary/30">
              <Calculator size={16} className="text-accent" weight="duotone" />
              <AlertDescription className="text-sm">
                <strong>Optimization strategy:</strong> Extract native text first. Analyze text quality/length. 
                Only OCR pages with {"<"}100 chars or low confidence. This could reduce OCR volume by 60-70%.
              </AlertDescription>
            </Alert>
          </div>
          
          <Separator />
          
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Microphone size={20} className="text-accent" weight="duotone" />
              Audio Transcription with Whisper
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="text-sm space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Whisper large-v3 speed:</span>
                    <span className="font-mono">0.5-2x realtime</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">1 hour audio processing:</span>
                    <span className="font-mono">30 min - 2 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">10 GPU workers (A100):</span>
                    <span className="font-mono">5-20x realtime</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Est. audio in corpus:</span>
                    <span className="font-mono">Unknown</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <Alert className="border-amber-500/30 bg-amber-500/10">
                  <Warning size={16} className="text-amber-400" weight="fill" />
                  <AlertDescription className="text-sm space-y-2">
                    <div><strong>Unknown audio volume:</strong> The DOJ Epstein Library page mentions potential audio releases 
                    with redaction tones, but the actual count is unclear.</div>
                    <div className="text-xs text-muted-foreground pt-2">
                      <strong>Example scenario:</strong> If 10K hours of audio exist:
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        <li>10 workers: 50-200 hours (2-8 days)</li>
                        <li>Cost: Minimal (local inference)</li>
                        <li>Storage: ~1-2GB transcripts</li>
                      </ul>
                    </div>
                  </AlertDescription>
                </Alert>
              </div>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <CurrencyDollar size={20} className="text-accent" weight="duotone" />
              Total Cost & Resource Estimates
            </h3>
            
            <div className="grid md:grid-cols-2 gap-4">
              <Card className="bg-card/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Infrastructure Costs</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Storage (10TB):</span>
                    <span className="font-mono">$200-500/mo</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">GPU workers (20x A100):</span>
                    <span className="font-mono">$5K-10K/mo</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Database/Search:</span>
                    <span className="font-mono">$500-1K/mo</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">OCR (cloud hybrid):</span>
                    <span className="font-mono">$8K-15K one-time</span>
                  </div>
                  <Separator className="my-3" />
                  <div className="flex justify-between font-semibold">
                    <span>3-month processing window:</span>
                    <span className="font-mono text-accent">$25K-50K</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-card/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Alternative: Local Cluster</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">20x GPU servers:</span>
                    <span className="font-mono">$40K-80K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Storage (NAS/SAN):</span>
                    <span className="font-mono">$5K-15K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Power/cooling:</span>
                    <span className="font-mono">$1K-2K/mo</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Processing time:</span>
                    <span className="font-mono">60-120 days</span>
                  </div>
                  <Separator className="my-3" />
                  <div className="flex justify-between font-semibold">
                    <span>Total (owned hardware):</span>
                    <span className="font-mono text-accent">$50K-100K</span>
                  </div>
                  <Badge variant="outline" className="text-xs mt-2">Better for long-term use</Badge>
                </CardContent>
              </Card>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <ChartLine size={20} className="text-accent" weight="duotone" />
              Realistic Production Timeline
            </h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 1-4:</div>
                <div>
                  <div className="font-medium">Infrastructure Setup & Discovery</div>
                  <div className="text-muted-foreground text-xs">Deploy crawlers, set up storage, discover all 3M document URLs</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 5-8:</div>
                <div>
                  <div className="font-medium">Polite Download Phase</div>
                  <div className="text-muted-foreground text-xs">Download with rate limiting, compute hashes, store immutably</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 9-10:</div>
                <div>
                  <div className="font-medium">Native Text Extraction</div>
                  <div className="text-muted-foreground text-xs">Fast extraction from text-native PDFs, identify scanned documents</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 11-16:</div>
                <div>
                  <div className="font-medium">OCR Processing (Hybrid)</div>
                  <div className="text-muted-foreground text-xs">OCR scanned pages with quality routing, page-level confidence tracking</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 17-18:</div>
                <div>
                  <div className="font-medium">Indexing & Search Setup</div>
                  <div className="text-muted-foreground text-xs">Build keyword and semantic indexes, test search quality</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 19-24:</div>
                <div>
                  <div className="font-medium">Entity Extraction & Graph</div>
                  <div className="text-muted-foreground text-xs">NER processing, disambiguation workflow, relationship generation</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/10">
                <div className="font-mono text-accent font-semibold min-w-[120px]">Week 25+:</div>
                <div>
                  <div className="font-medium">Audio Transcription (if needed)</div>
                  <div className="text-muted-foreground text-xs">Parallel Whisper processing of released audio files</div>
                </div>
              </div>
            </div>
            
            <Alert className="bg-accent/10 border-accent/40">
              <CheckCircle size={16} className="text-accent" weight="fill" />
              <AlertDescription className="font-semibold">
                <strong>Bottom line:</strong> Complete processing in 5-6 months with hybrid cloud approach, 
                or 3-4 months with aggressive cloud spending (~$100K+). Local-only extends to 8-12 months but with lower ongoing costs.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>
      
      <div className="text-sm text-muted-foreground bg-muted/30 p-4 rounded-lg space-y-2">
        <div className="font-semibold text-foreground">Critical Assumptions & Unknowns:</div>
        <ul className="list-disc list-inside space-y-1">
          <li>Actual document count at justice.gov/epstein may differ from 3M estimate</li>
          <li>Average pages per PDF and scan quality will significantly impact OCR costs</li>
          <li>DOJ rate limits and Queue-it controls may extend download timelines</li>
          <li>Audio/video volume is currently unknown and could add weeks if substantial</li>
          <li>Entity extraction accuracy depends on document quality and domain-specific NER tuning</li>
        </ul>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <CloudArrowUp size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>Ingestion Pipeline</CardTitle>
                <CardDescription>Polite crawling and document acquisition</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Polite web crawler respecting robots.txt and rate limits</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Document downloader with retry logic and hash verification</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Distributed job queue (e.g., BullMQ, Celery) for parallel processing</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>SHA-256 hashing and immutable storage for chain-of-custody</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">Estimated Capacity: 10K docs/hour</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <Eye size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>OCR Processing</CardTitle>
                <CardDescription>Text extraction from scanned documents</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Tesseract OCR or cloud OCR (Azure/AWS) for scanned PDFs</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Intelligent fallback: native PDF text extraction first, OCR when needed</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Page-level confidence scoring and quality metrics</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>GPU-accelerated workers for high-throughput processing</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">Estimated: 5-15 pages/second per worker</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <Microphone size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>Audio Transcription</CardTitle>
                <CardDescription>Whisper-based speech-to-text</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>OpenAI Whisper (large-v3) or cloud equivalent for audio/video</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Timestamp alignment for searchable transcripts</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Speaker diarization for multi-party recordings</span>
              </div>
              <div className="flex items-start gap-2">
                <Warning size={16} className="text-[oklch(0.65_0.10_70)] mt-0.5" weight="fill" />
                <span>Optional: Only activated if source includes audio/video files</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">Estimated: 0.5-2x realtime per worker</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <MagnifyingGlass size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>Search & Indexing</CardTitle>
                <CardDescription>Full-text and semantic search</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Elasticsearch or Typesense for keyword search with highlighting</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>PostgreSQL + pgvector for semantic search with embeddings</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Embedding generation (OpenAI ada-002 or open-source models)</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Faceted filtering by source, date, confidence, entity types</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">Sub-second query response at scale</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <Graph size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>Entity & Graph Analysis</CardTitle>
                <CardDescription>NLP extraction and relationship mapping</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Named Entity Recognition (spaCy, GPT-4, or specialized models)</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Entity disambiguation with confidence scoring</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Graph database (Neo4j or PostgreSQL) for relationship storage</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Evidence-backed edges with snippet citations and confidence</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">Reviewer approval workflow for high-confidence merges</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20">
                <ShieldCheck size={24} className="text-accent" weight="duotone" />
              </div>
              <div>
                <CardTitle>Security & Compliance</CardTitle>
                <CardDescription>Provenance and access control</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Role-based access control (Admin, Analyst, Reviewer, ReadOnly)</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Complete audit trail with actor tracking and change versioning</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>Tamper-evident storage with hash verification</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={16} className="text-accent mt-0.5" weight="fill" />
                <span>PII safeguards and optional redaction for exports</span>
              </div>
            </div>
            <div className="pt-2">
              <Badge variant="secondary">TLS everywhere, secrets in vault</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database size={24} weight="duotone" />
            Scale Considerations for 3M Documents
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <AlertDescription className="text-sm">
              Processing 3 million PDFs from justice.gov/epstein requires enterprise infrastructure with 
              horizontal scaling, distributed storage, and cost management controls.
            </AlertDescription>
          </Alert>
          
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="font-semibold mb-2">Storage Requirements</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Raw PDFs: 500GB - 5TB (varies by document size)</li>
                <li>• Extracted text/OCR: 50GB - 500GB</li>
                <li>• Search indices: 100GB - 1TB</li>
                <li>• Embeddings (if semantic search): 200GB - 2TB</li>
                <li>• Database (metadata/entities): 50GB - 200GB</li>
              </ul>
            </div>
            
            <div>
              <div className="font-semibold mb-2">Processing Timeline (Estimated)</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Download (10 workers @ 5 docs/min): 10-20 days</li>
                <li>• OCR (20 GPU workers @ 10 docs/min): 10-15 days</li>
                <li>• Text extraction: 2-5 days (parallel)</li>
                <li>• Indexing: 3-7 days</li>
                <li>• Entity extraction: 10-20 days</li>
                <li>• Total: 30-60 days (with parallelization)</li>
              </ul>
            </div>
            
            <div>
              <div className="font-semibold mb-2">Cost Optimization</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Only OCR when text extraction insufficient</li>
                <li>• Batch processing to maximize GPU utilization</li>
                <li>• Tiered storage (hot/warm/cold for older docs)</li>
                <li>• On-demand worker scaling during ingestion</li>
                <li>• Skip re-downloading by hash deduplication</li>
              </ul>
            </div>
            
            <div>
              <div className="font-semibold mb-2">Reliability Features</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Idempotent job processing (safe retries)</li>
                <li>• Dead-letter queue for failed tasks</li>
                <li>• Incremental, resumable indexing</li>
                <li>• Health checks and monitoring dashboards</li>
                <li>• Automated backups with point-in-time recovery</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Recommended Technology Stack</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="font-semibold mb-2 text-accent">Backend</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Python (FastAPI/Django)</li>
                <li>• Node.js (NestJS) alternative</li>
                <li>• PostgreSQL primary database</li>
                <li>• Redis for caching/queues</li>
              </ul>
            </div>
            
            <div>
              <div className="font-semibold mb-2 text-accent">Processing</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• BullMQ or Celery job queues</li>
                <li>• Tesseract or Azure OCR</li>
                <li>• Whisper (large-v3) for audio</li>
                <li>• spaCy or GPT-4 for NER</li>
              </ul>
            </div>
            
            <div>
              <div className="font-semibold mb-2 text-accent">Search & Storage</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Elasticsearch or Typesense</li>
                <li>• pgvector for embeddings</li>
                <li>• S3/MinIO for object storage</li>
                <li>• Neo4j or PostgreSQL graph</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
