'use client';

import { useState } from 'react';
import { PageHeader, Card, CardHeader, CardContent, Input, Button, Badge } from '@/components/ui';
import { useHealth } from '@/lib/hooks';

export default function SettingsPage() {
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealth();

  // Backend URL config (display only — set via env)
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Placeholder settings state
  const [autoHash, setAutoHash] = useState(true);
  const [maxConcurrent, setMaxConcurrent] = useState('3');

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="System configuration and diagnostics" />

      {/* ── Backend Connection ─────────────────────────── */}
      <Card>
        <CardHeader
          title="Backend Connection"
          description="API endpoint and health status"
          action={
            <Button
              variant="secondary"
              size="sm"
              onClick={() => refetchHealth()}
              loading={healthLoading}
              data-testid="settings-test-connection-btn"
            >
              Test Connection
            </Button>
          }
        />
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">API URL</span>
              <code className="text-sm bg-slate-700 px-2 py-0.5 rounded">{backendUrl}</code>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Status</span>
              {health ? (
                <Badge variant={health.status === 'healthy' ? 'verified' : 'error'}>
                  {health.status}
                </Badge>
              ) : (
                <Badge variant="neutral">Unknown</Badge>
              )}
            </div>
            {health && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Database</span>
                  <Badge variant={health.database === 'connected' ? 'verified' : 'error'}>
                    {health.database}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Storage (MinIO)</span>
                  <Badge variant={health.minio === 'connected' ? 'verified' : 'error'}>
                    {health.minio}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Redis</span>
                  <Badge variant={health.redis === 'connected' ? 'verified' : 'error'}>
                    {health.redis}
                  </Badge>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* ── Upload Settings ────────────────────────────── */}
      <Card>
        <CardHeader title="Upload Settings" description="Configure evidence upload behavior" />
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-200">Auto-hash on upload</p>
                <p className="text-xs text-slate-400">
                  Automatically compute SHA-256 hash for integrity verification
                </p>
              </div>
              <button
                role="switch"
                aria-checked={autoHash}
                onClick={() => setAutoHash((v) => !v)}
                data-testid="settings-auto-hash-toggle"
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  autoHash ? 'bg-blue-600' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                    autoHash ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="max-w-xs">
              <Input
                label="Max concurrent uploads"
                type="number"
                min={1}
                max={10}
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(e.target.value)}
                helperText="Number of files uploaded in parallel (1-10)"
                data-testid="settings-max-concurrent-input"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Forensic Integrity ─────────────────────────── */}
      <Card>
        <CardHeader
          title="Forensic Integrity"
          description="Chain-of-custody and verification settings"
        />
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-200">Hash Algorithm</p>
                <p className="text-xs text-slate-400">Used for evidence integrity verification</p>
              </div>
              <Badge variant="verified">SHA-256</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-200">Audit Logging</p>
                <p className="text-xs text-slate-400">
                  All evidence operations are logged with timestamps
                </p>
              </div>
              <Badge variant="verified">Enabled</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-200">Tamper Detection</p>
                <p className="text-xs text-slate-400">Server-side re-hashing on every access</p>
              </div>
              <Badge variant="verified">Active</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Environment ────────────────────────────────── */}
      <Card>
        <CardHeader title="Environment" description="Runtime information" />
        <CardContent>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <span className="text-slate-400">Frontend</span>
            <span>Next.js 14 (App Router)</span>
            <span className="text-slate-400">Node</span>
            <span>{typeof process !== 'undefined' ? (process.version ?? 'N/A') : 'Browser'}</span>
            <span className="text-slate-400">Environment</span>
            <span>{process.env.NODE_ENV}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
