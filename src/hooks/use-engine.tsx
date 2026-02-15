import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useKV } from '@github/spark/hooks'
import { 
  EngineClient, 
  EngineMode, 
  ConnectionStatus, 
  EngineHealth,
  SessionToken,
  LLMProvider,
  createEngineClient
} from '@/lib/engineClient'

interface EngineContextValue {
  client: EngineClient
  mode: EngineMode
  status: ConnectionStatus
  health: EngineHealth | null
  providers: LLMProvider[]
  setMode: (mode: EngineMode) => void
  connect: (baseUrl?: string) => Promise<void>
  disconnect: () => void
  refreshHealth: () => Promise<void>
  refreshProviders: () => Promise<void>
}

const EngineContext = createContext<EngineContextValue | null>(null)

export function EngineProvider({ children }: { children: ReactNode }) {
  const [client] = useState(() => createEngineClient())
  const [mode, setModeState] = useKV<EngineMode>('engine-mode', 'demo')
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [health, setHealth] = useState<EngineHealth | null>(null)
  const [providers, setProviders] = useState<LLMProvider[]>([])
  const [sessionToken, setSessionToken] = useKV<SessionToken | null>('engine-session', null)

  useEffect(() => {
    if (mode) {
      client.setMode(mode)
    }

    if (sessionToken && sessionToken.mode === mode) {
      if (sessionToken.expiresAt > Date.now()) {
        client.setToken(sessionToken.token)
        setStatus('connected')
      } else {
        setSessionToken(() => null)
        setStatus('disconnected')
      }
    }
  }, [mode, sessionToken, client, setSessionToken])

  useEffect(() => {
    if (status === 'connected' && (mode === 'local' || mode === 'team')) {
      const interval = setInterval(async () => {
        const healthResult = await client.checkHealth()
        setHealth(healthResult)
        
        if (!healthResult) {
          setStatus('error')
        }
      }, 30000)

      client.checkHealth().then(setHealth)

      return () => clearInterval(interval)
    }
  }, [status, mode, client])

  const setMode = (newMode: EngineMode) => {
    setModeState(() => newMode)
    client.setMode(newMode)
    
    if (newMode === 'demo' || newMode === 'browser-only') {
      setStatus('connected')
      setHealth(null)
    } else {
      setStatus('disconnected')
    }
  }

  const connect = async (baseUrl?: string) => {
    if (mode === 'demo' || mode === 'browser-only') {
      setStatus('connected')
      return
    }

    setStatus('connecting')

    try {
      const healthResult = await client.checkHealth()
      
      if (healthResult) {
        setHealth(healthResult)
        setStatus('connected')
        
        const providersResult = await client.listProviders()
        setProviders(providersResult)
      } else {
        throw new Error('Engine not reachable')
      }
    } catch (error) {
      console.error('Connection failed:', error)
      setStatus('error')
    }
  }

  const disconnect = () => {
    setSessionToken(() => null)
    setStatus('disconnected')
    setHealth(null)
    setProviders([])
  }

  const refreshHealth = async () => {
    if (mode === 'demo' || mode === 'browser-only') {
      return
    }

    const healthResult = await client.checkHealth()
    setHealth(healthResult)
  }

  const refreshProviders = async () => {
    if (mode === 'demo' || mode === 'browser-only') {
      const demoProviders = await client.listProviders()
      setProviders(demoProviders)
      return
    }

    const providersResult = await client.listProviders()
    setProviders(providersResult)
  }

  useEffect(() => {
    if (mode === 'demo') {
      refreshProviders()
    }
  }, [mode])

  return (
    <EngineContext.Provider
      value={{
        client,
        mode: mode || 'demo',
        status,
        health,
        providers,
        setMode,
        connect,
        disconnect,
        refreshHealth,
        refreshProviders
      }}
    >
      {children}
    </EngineContext.Provider>
  )
}

export function useEngine() {
  const context = useContext(EngineContext)
  if (!context) {
    throw new Error('useEngine must be used within EngineProvider')
  }
  return context
}
