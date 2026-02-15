export type EngineMode = 'demo' | 'local' | 'team' | 'browser-only'

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

export interface EngineHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  services: {
    database: boolean
    search: boolean
    vector: boolean
    graph: boolean
    ocr: boolean
    transcription: boolean
  }
  version: string
  lastCheck: number
}

export interface EngineInfo {
  mode: EngineMode
  baseUrl: string
  version: string
  capabilities: string[]
}

export interface LLMProvider {
  id: string
  type: 'openai' | 'gemini' | 'claude' | 'local'
  name: string
  enabled: boolean
  capabilities: ('embeddings' | 'summarization' | 'classification' | 'extraction')[]
  spendingCap?: number
  tokensUsed?: number
}

export interface SessionToken {
  token: string
  expiresAt: number
  mode: EngineMode
  baseUrl: string
}

export class EngineClient {
  private baseUrl: string
  private token: string | null = null
  private mode: EngineMode = 'demo'

  constructor(baseUrl: string = 'http://localhost:8080') {
    this.baseUrl = baseUrl
  }

  setMode(mode: EngineMode) {
    this.mode = mode
  }

  getMode(): EngineMode {
    return this.mode
  }

  setToken(token: string) {
    this.token = token
  }

  async checkHealth(): Promise<EngineHealth | null> {
    if (this.mode === 'demo' || this.mode === 'browser-only') {
      return null
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: 'GET',
        headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {}
      })

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Engine health check failed:', error)
      return null
    }
  }

  async requestPairing(): Promise<{ pairingCode: string; pollUrl: string } | null> {
    if (this.mode === 'demo' || this.mode === 'browser-only') {
      return null
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/pairing/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (!response.ok) {
        throw new Error(`Pairing request failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Pairing request failed:', error)
      return null
    }
  }

  async completePairing(pairingCode: string): Promise<SessionToken | null> {
    if (this.mode === 'demo' || this.mode === 'browser-only') {
      return null
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/pairing/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pairingCode })
      })

      if (!response.ok) {
        throw new Error(`Pairing completion failed: ${response.status}`)
      }

      const data = await response.json()
      this.token = data.token

      return {
        token: data.token,
        expiresAt: data.expiresAt,
        mode: this.mode,
        baseUrl: this.baseUrl
      }
    } catch (error) {
      console.error('Pairing completion failed:', error)
      return null
    }
  }

  async listProviders(): Promise<LLMProvider[]> {
    if (this.mode === 'demo') {
      return [
        {
          id: 'demo-openai',
          type: 'openai',
          name: 'OpenAI (Demo)',
          enabled: true,
          capabilities: ['embeddings', 'summarization', 'classification', 'extraction'],
          spendingCap: 100,
          tokensUsed: 42
        }
      ]
    }

    if (!this.token || this.mode === 'browser-only') {
      return []
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/providers`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${this.token}` }
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch providers: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to fetch providers:', error)
      return []
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    const headers: HeadersInit = {}
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseUrl}/api${endpoint}`, {
      method: 'GET',
      headers
    })

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }

    return await response.json()
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseUrl}/api${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }

    return await response.json()
  }
}

export const createEngineClient = (baseUrl?: string) => new EngineClient(baseUrl)
