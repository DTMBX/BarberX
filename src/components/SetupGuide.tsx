import { useEngine } from '@/hooks/use-engine'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Desktop,
  DownloadSimple,
  Terminal,
  CheckCircle,
  ArrowRight,
  Globe
} from '@phosphor-icons/react'
import { Badge } from '@/components/ui/badge'

interface SetupGuideProps {
  onConnect: () => void
}

export function SetupGuide({ onConnect }: SetupGuideProps) {
  const { mode } = useEngine()

  if (mode !== 'demo') {
    return null
  }

  return (
    <Card className="border-accent/30 bg-accent/5">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Desktop size={24} weight="duotone" />
              Get Started with Full Features
            </CardTitle>
            <CardDescription className="mt-2">
              Install the Local Worker Service to process official DOJ Epstein Library releases with OCR, Whisper transcription, vector search, and graph computation while keeping your data and API keys secure.
            </CardDescription>
          </div>
          <Badge variant="outline">Browser-Only Mode</Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="grid md:grid-cols-3 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <div className="flex items-center justify-center w-6 h-6 rounded-full bg-accent text-accent-foreground text-xs">
                1
              </div>
              Download Local Engine
            </div>
            <p className="text-xs text-muted-foreground pl-8">
              Get the companion service for your operating system (Windows/macOS/Linux) or use Docker.
            </p>
            <div className="pl-8 flex flex-col gap-2">
              <Button variant="outline" size="sm" className="justify-start" asChild>
                <a href="https://github.com/your-repo/releases" target="_blank" rel="noopener noreferrer">
                  <DownloadSimple size={16} />
                  GitHub Releases
                </a>
              </Button>
              <Button variant="outline" size="sm" className="justify-start">
                <Terminal size={16} />
                Docker Compose
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <div className="flex items-center justify-center w-6 h-6 rounded-full bg-accent text-accent-foreground text-xs">
                2
              </div>
              Install & Launch
            </div>
            <p className="text-xs text-muted-foreground pl-8">
              Run the installer or docker-compose up. The service will start on localhost:8080 by default.
            </p>
            <div className="pl-8">
              <code className="text-xs bg-muted px-2 py-1 rounded block font-mono">
                docker-compose up -d
              </code>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <div className="flex items-center justify-center w-6 h-6 rounded-full bg-accent text-accent-foreground text-xs">
                3
              </div>
              Connect & Pair
            </div>
            <p className="text-xs text-muted-foreground pl-8">
              Click the connection button, select Local Engine, and enter the pairing code shown in your engine UI.
            </p>
            <div className="pl-8">
              <Button size="sm" onClick={onConnect} className="w-full">
                <ArrowRight size={16} />
                Connect Now
              </Button>
            </div>
          </div>
        </div>

        <Alert className="bg-background/50">
          <CheckCircle size={20} weight="duotone" className="text-accent" />
          <AlertDescription className="text-xs">
            <strong>Your data stays yours:</strong> The Local Engine processes everything on your machine. API keys (OpenAI, Gemini, Claude) are stored in your OS keychain, never sent to the browser. Export only the evidence slices you need—raw documents stay local.
          </AlertDescription>
        </Alert>

        <div className="pt-4 border-t flex items-center justify-between text-xs text-muted-foreground">
          <span>
            Advanced users can also deploy on a private team server
          </span>
          <Button variant="ghost" size="sm" onClick={onConnect}>
            <Globe size={16} />
            Configure Team Server
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
