import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { useEngine } from '@/hooks/use-engine'
import { 
  Database, 
  FileText, 
  MagnifyingGlass, 
  UsersThree, 
  Graph,
  FileArrowDown,
  ClockCounterClockwise,
  Gear,
  Flask,
  Code,
  PlayCircle,
  GitPullRequest,
  Queue,
  Notepad,
  Warning
} from '@phosphor-icons/react'
import { 
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarInset,
  SidebarTrigger
} from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { initializeSampleData } from '@/lib/seedData'
import { ConnectionDialog } from '@/components/ConnectionDialog'
import { ModeIndicator } from '@/components/ModeIndicator'

import { SourcesView } from '@/views/SourcesView'
import { IngestionRunsView } from '@/views/IngestionRunsView'
import { DocumentsView } from '@/views/DocumentsView'
import { SearchView } from '@/views/SearchView'
import { EntitiesView } from '@/views/EntitiesView'
import { GraphView } from '@/views/GraphView'
import { AuditLogView } from '@/views/AuditLogView'
import { SystemInfoView } from '@/views/SystemInfoView'
import { AnalysisScriptsView } from '@/views/AnalysisScriptsView'
import { ScriptRunsView } from '@/views/ScriptRunsView'
import { ProposalsView } from '@/views/ProposalsView'
import { ReviewQueuesView } from '@/views/ReviewQueuesView'
import { AnnotationsView } from '@/views/AnnotationsView'

type ViewType = 'sources' | 'runs' | 'documents' | 'search' | 'entities' | 'graph' | 'audit' | 'system' | 'scripts' | 'script-runs' | 'proposals' | 'review-queues' | 'annotations'

const navigation = [
  {
    label: 'Data Management',
    items: [
      { id: 'sources' as ViewType, label: 'Sources', icon: Database },
      { id: 'runs' as ViewType, label: 'Ingestion Runs', icon: FileArrowDown },
      { id: 'documents' as ViewType, label: 'Documents', icon: FileText }
    ]
  },
  {
    label: 'Analysis',
    items: [
      { id: 'search' as ViewType, label: 'Search', icon: MagnifyingGlass },
      { id: 'entities' as ViewType, label: 'Entities', icon: UsersThree },
      { id: 'graph' as ViewType, label: 'Relationship Graph', icon: Graph }
    ]
  },
  {
    label: 'Automation',
    items: [
      { id: 'scripts' as ViewType, label: 'Analysis Scripts', icon: Code },
      { id: 'script-runs' as ViewType, label: 'Script Runs', icon: PlayCircle },
      { id: 'proposals' as ViewType, label: 'Proposals', icon: GitPullRequest }
    ]
  },
  {
    label: 'Quality & Review',
    items: [
      { id: 'review-queues' as ViewType, label: 'Review Queues', icon: Queue },
      { id: 'annotations' as ViewType, label: 'Annotations', icon: Notepad }
    ]
  },
  {
    label: 'System',
    items: [
      { id: 'audit' as ViewType, label: 'Audit Log', icon: ClockCounterClockwise },
      { id: 'system' as ViewType, label: 'Architecture', icon: Gear }
    ]
  }
]

function App() {
  const { mode } = useEngine()
  const [currentView, setCurrentView] = useState<ViewType>('sources')
  const [globalSearch, setGlobalSearch] = useState('')
  const [dataInitialized, setDataInitialized] = useKV<boolean>('data-initialized', false)
  const [isInitializing, setIsInitializing] = useState(false)
  const [connectionDialogOpen, setConnectionDialogOpen] = useState(false)
  
  useEffect(() => {
    if (!dataInitialized && !isInitializing) {
      setIsInitializing(true)
      initializeSampleData().then(() => {
        setDataInitialized(() => true)
        setIsInitializing(false)
      }).catch((err) => {
        console.error('Failed to initialize sample data:', err)
        setIsInitializing(false)
      })
    }
  }, [dataInitialized, isInitializing, setDataInitialized])

  const renderView = () => {
    switch (currentView) {
      case 'sources':
        return <SourcesView />
      case 'runs':
        return <IngestionRunsView />
      case 'documents':
        return <DocumentsView />
      case 'search':
        return <SearchView initialQuery={globalSearch} />
      case 'entities':
        return <EntitiesView />
      case 'graph':
        return <GraphView />
      case 'scripts':
        return <AnalysisScriptsView />
      case 'script-runs':
        return <ScriptRunsView />
      case 'proposals':
        return <ProposalsView />
      case 'review-queues':
        return <ReviewQueuesView />
      case 'annotations':
        return <AnnotationsView />
      case 'audit':
        return <AuditLogView />
      case 'system':
        return <SystemInfoView />
      default:
        return <SourcesView />
    }
  }

  return (
    <>
      <ConnectionDialog 
        open={connectionDialogOpen} 
        onOpenChange={setConnectionDialogOpen} 
      />
      
      <SidebarProvider>
        <Sidebar>
          <SidebarContent>
            <div className="p-6">
              <h1 className="text-xl font-bold tracking-tight">
                Public Records
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Analysis Platform
              </p>
            </div>
          
          <Separator />
          
          {navigation.map((section) => (
            <SidebarGroup key={section.label}>
              <SidebarGroupLabel>{section.label}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {section.items.map((item) => (
                    <SidebarMenuItem key={item.id}>
                      <SidebarMenuButton
                        isActive={currentView === item.id}
                        onClick={() => setCurrentView(item.id)}
                      >
                        <item.icon size={20} />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ))}
        </SidebarContent>
      </Sidebar>
      
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-6" />
          <div className="flex-1 max-w-xl">
            <Input
              type="search"
              placeholder="Search documents, entities, or content..."
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && globalSearch.trim()) {
                  setCurrentView('search')
                }
              }}
              className="w-full"
            />
          </div>
          <ModeIndicator onConnectionClick={() => setConnectionDialogOpen(true)} />
        </header>
        
        <main className="flex-1 p-6">
          <Alert className="mb-6 border-[oklch(0.45_0.15_280)]/50 bg-[oklch(0.45_0.15_280)]/10">
            <Flask className="text-[oklch(0.65_0.18_280)]" size={20} weight="duotone" />
            <AlertDescription className="text-sm">
              <strong className="font-semibold">Current Mode: {mode === 'demo' ? 'Browser-Only (Limited)' : mode === 'local' ? 'Local Engine (Full)' : mode === 'team' ? 'Team Server (Full)' : 'Browser Only'}</strong>
              {mode === 'demo' && ' — Browser-only mode with limited processing. Connect a Local Engine for full capabilities (OCR, Whisper, vector search, entity extraction, graph computation). Data shown is from official DOJ releases at justice.gov/epstein.'}
              {mode === 'local' && ' — Connected to your local processing engine. Processing official DOJ Epstein Library releases. Your data and API keys remain under your control.'}
              {mode === 'team' && ' — Connected to your team server. Processing official DOJ releases with collaboration and shared projects enabled.'}
              {mode === 'browser-only' && ' — Limited processing in browser only. Install Local Engine for full features (OCR, Whisper, vector search, graph computation).'}
            </AlertDescription>
          </Alert>
          
          <Alert className="mb-6 border-accent/30 bg-accent/10">
            <Warning className="text-accent" size={20} />
            <AlertDescription className="text-sm">
              <strong className="font-semibold">Analysis Disclaimer:</strong> This platform demonstrates evidence-backed analysis patterns. All analysis outputs are probabilistic 
              and must be verified against source documents. No conclusions of guilt should be drawn from 
              automated mentions or relationships. Every assertion must cite source text and maintain chain-of-custody.
            </AlertDescription>
          </Alert>
          
          {renderView()}
        </main>
      </SidebarInset>
    </SidebarProvider>
    </>
  )
}

export default App
