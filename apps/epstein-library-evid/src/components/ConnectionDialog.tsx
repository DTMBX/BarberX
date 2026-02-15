import { useState } from 'react'
import { useEngine } from '@/hooks/use-engine'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Desktop,
  Globe,
  Browser,
  Warning,
  CheckCircle,
  CircleNotch
} from '@phosphor-icons/react'
import { Badge } from '@/components/ui/badge'

interface ConnectionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ConnectionDialog({ open, onOpenChange }: ConnectionDialogProps) {
  const { mode, setMode, connect, status } = useEngine()
  const [selectedMode, setSelectedMode] = useState(mode)
  const [localUrl, setLocalUrl] = useState('http://localhost:8080')
  const [teamUrl, setTeamUrl] = useState('')
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnect = async () => {
    setIsConnecting(true)
    
    try {
      setMode(selectedMode)
      
      if (selectedMode === 'local' || selectedMode === 'team') {
        await connect(selectedMode === 'local' ? localUrl : teamUrl)
      }
      
      onOpenChange(false)
    } catch (error) {
      console.error('Connection failed:', error)
    } finally {
      setIsConnecting(false)
    }
  }

  const modes = [
    {
      id: 'demo' as const,
      icon: Browser,
      title: 'Browser-Only Mode',
      description: 'Limited interface with official DOJ data structure',
      status: 'No engine required',
      features: ['Browse UI', 'DOJ document metadata', 'No processing']
    },
    {
      id: 'local' as const,
      icon: Desktop,
      title: 'Local Engine',
      description: 'Full features with local processing',
      status: 'Requires Local Worker Service',
      features: ['Your API keys', 'Full OCR/Whisper', 'Local storage', 'Private data']
    },
    {
      id: 'team' as const,
      icon: Globe,
      title: 'Team Server',
      description: 'Collaborate with your team',
      status: 'Requires team server setup',
      features: ['Multi-user', 'Shared projects', 'RBAC', 'Team API keys']
    }
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="text-2xl">Connect to Engine</DialogTitle>
          <DialogDescription>
            Choose how you want to run the analysis platform
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          {modes.map((modeOption) => {
            const Icon = modeOption.icon
            const isSelected = selectedMode === modeOption.id
            
            return (
              <button
                key={modeOption.id}
                onClick={() => setSelectedMode(modeOption.id)}
                className={`
                  flex items-start gap-4 p-4 rounded-lg border-2 transition-all text-left
                  ${isSelected 
                    ? 'border-accent bg-accent/10' 
                    : 'border-border hover:border-accent/50'
                  }
                `}
              >
                <div className={`
                  p-3 rounded-lg
                  ${isSelected ? 'bg-accent text-accent-foreground' : 'bg-muted'}
                `}>
                  <Icon size={24} weight="duotone" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">{modeOption.title}</h3>
                    {isSelected && (
                      <CheckCircle size={16} weight="fill" className="text-accent" />
                    )}
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-2">
                    {modeOption.description}
                  </p>
                  
                  <Badge variant="outline" className="mb-2 text-xs">
                    {modeOption.status}
                  </Badge>
                  
                  <div className="flex flex-wrap gap-2">
                    {modeOption.features.map((feature) => (
                      <span key={feature} className="text-xs text-muted-foreground">
                        • {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </button>
            )
          })}

          {selectedMode === 'local' && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="local-url">Local Engine URL</Label>
                <Input
                  id="local-url"
                  value={localUrl}
                  onChange={(e) => setLocalUrl(e.target.value)}
                  placeholder="http://localhost:8080"
                  className="font-mono text-sm"
                />
              </div>

              <Alert>
                <Desktop size={20} />
                <AlertDescription className="text-sm">
                  <strong>Setup Required:</strong> Install the Local Worker Service first.
                  <br />
                  Download from GitHub Releases or run: <code className="text-xs bg-muted px-1 py-0.5 rounded">docker-compose up</code>
                </AlertDescription>
              </Alert>
            </div>
          )}

          {selectedMode === 'team' && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="team-url">Team Server URL</Label>
                <Input
                  id="team-url"
                  value={teamUrl}
                  onChange={(e) => setTeamUrl(e.target.value)}
                  placeholder="https://your-team-server.com"
                  className="font-mono text-sm"
                />
              </div>

              <Alert>
                <Globe size={20} />
                <AlertDescription className="text-sm">
                  <strong>Admin Setup Required:</strong> Your team administrator must provide the server URL and complete deployment.
                </AlertDescription>
              </Alert>
            </div>
          )}

          {selectedMode === 'demo' && (
            <Alert className="border-accent/30 bg-accent/10">
              <Warning className="text-accent" size={20} />
              <AlertDescription className="text-sm">
                <strong>Demo Mode:</strong> All data is simulated. No actual processing will occur. Connect a Local Engine or Team Server for full functionality.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleConnect}
            disabled={isConnecting || (selectedMode === 'team' && !teamUrl)}
          >
            {isConnecting ? (
              <>
                <CircleNotch size={16} className="animate-spin" />
                Connecting...
              </>
            ) : (
              'Connect'
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
