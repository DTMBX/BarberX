import { useEngine } from '@/hooks/use-engine'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import {
  Desktop,
  Globe,
  Browser,
  CheckCircle,
  Warning,
  Circle,
  CircleNotch
} from '@phosphor-icons/react'
import { Separator } from '@/components/ui/separator'

interface ModeIndicatorProps {
  onConnectionClick: () => void
}

export function ModeIndicator({ onConnectionClick }: ModeIndicatorProps) {
  const { mode, status, health, providers } = useEngine()

  const getModeIcon = () => {
    switch (mode) {
      case 'local':
        return <Desktop size={16} weight="duotone" />
      case 'team':
        return <Globe size={16} weight="duotone" />
      case 'demo':
        return <Browser size={16} weight="duotone" />
      case 'browser-only':
        return <Browser size={16} weight="duotone" />
    }
  }

  const getModeLabel = () => {
    switch (mode) {
      case 'local':
        return 'Local Engine'
      case 'team':
        return 'Team Server'
      case 'demo':
        return 'Browser-Only'
      case 'browser-only':
        return 'Browser Only'
    }
  }

  const getStatusIcon = () => {
    if (mode === 'demo' || mode === 'browser-only') {
      return <CheckCircle size={16} weight="fill" className="text-accent" />
    }

    switch (status) {
      case 'connected':
        return <CheckCircle size={16} weight="fill" className="text-green-500" />
      case 'connecting':
        return <CircleNotch size={16} className="animate-spin text-muted-foreground" />
      case 'error':
        return <Warning size={16} weight="fill" className="text-destructive" />
      case 'disconnected':
        return <Circle size={16} className="text-muted-foreground" />
    }
  }

  const getStatusColor = () => {
    if (mode === 'demo' || mode === 'browser-only') {
      return 'outline'
    }

    switch (status) {
      case 'connected':
        return 'default'
      case 'error':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={getStatusColor()}
          size="sm"
          className="gap-2 h-8"
        >
          {getModeIcon()}
          <span className="text-xs">{getModeLabel()}</span>
          {getStatusIcon()}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent className="w-80" align="end">
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-sm mb-1">Connection Status</h4>
            <p className="text-xs text-muted-foreground">
              {mode === 'demo' && 'Displaying official DOJ Epstein Library document structure'}
              {mode === 'browser-only' && 'Limited processing in browser only'}
              {mode === 'local' && status === 'connected' && 'Connected to local processing engine'}
              {mode === 'local' && status === 'disconnected' && 'Local engine not connected'}
              {mode === 'local' && status === 'error' && 'Local engine connection error'}
              {mode === 'team' && status === 'connected' && 'Connected to team server'}
              {mode === 'team' && status === 'disconnected' && 'Team server not connected'}
              {mode === 'team' && status === 'error' && 'Team server connection error'}
            </p>
          </div>

          {health && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold text-sm mb-2">Engine Health</h4>
                <div className="space-y-1.5">
                  {Object.entries(health.services).map(([service, isHealthy]) => (
                    <div key={service} className="flex items-center justify-between text-xs">
                      <span className="capitalize text-muted-foreground">{service}</span>
                      <Badge variant={isHealthy ? 'default' : 'destructive'} className="text-xs h-5">
                        {isHealthy ? 'OK' : 'Down'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {providers.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold text-sm mb-2">LLM Providers</h4>
                <div className="space-y-1.5">
                  {providers.map((provider) => (
                    <div key={provider.id} className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{provider.name}</span>
                      <Badge 
                        variant={provider.enabled ? 'default' : 'outline'} 
                        className="text-xs h-5"
                      >
                        {provider.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          <Separator />

          <Button 
            size="sm" 
            className="w-full"
            onClick={onConnectionClick}
          >
            Change Connection
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}
