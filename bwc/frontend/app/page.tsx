'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { healthCheck, type HealthStatus } from '@/lib/api';
import { Card, CardHeader, CardContent, Badge, PageHeader, LoadingSpinner } from '@/components/ui';

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    healthCheck()
      .then(setHealth)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Forensic-grade evidence management platform"
        data-testid="dashboard-header"
      />

      <section data-testid="dashboard-status-section">
        <h2 className="text-lg font-semibold mb-4">System Status</h2>
        {loading && (
          <div
            className="flex items-center gap-2 text-slate-400"
            data-testid="dashboard-status-loading"
          >
            <LoadingSpinner size="sm" />
            <span className="text-sm">Checking system status...</span>
          </div>
        )}
        {error && (
          <div
            className="rounded-lg border border-red-600/30 bg-red-900/20 p-4 mb-4"
            data-testid="dashboard-status-error"
          >
            <p className="text-sm text-red-300">Backend connection failed: {error}</p>
          </div>
        )}
        {health && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatusCard title="API" status={health.status === 'healthy' ? 'ok' : 'error'} />
            <StatusCard
              title="Database"
              status={health.database === 'connected' ? 'ok' : 'error'}
            />
            <StatusCard title="Redis" status={health.redis === 'connected' ? 'ok' : 'error'} />
            <StatusCard title="MinIO" status={health.minio === 'connected' ? 'ok' : 'error'} />
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <ActionCard
            href="/cases/new"
            title="New Case"
            description="Create a new evidence case"
            testId="dashboard-action-new-case"
          />
          <ActionCard
            href="/cases"
            title="View Cases"
            description="Browse existing cases"
            testId="dashboard-action-view-cases"
          />
          <ActionCard
            href="/verify"
            title="Verify"
            description="Validate evidence integrity"
            testId="dashboard-action-verify"
          />
          <ActionCard
            href="/chat"
            title="Chat"
            description="AI research assistant"
            testId="dashboard-action-chat"
          />
        </div>
      </section>

      <Card>
        <CardHeader title="Forensic Guarantees" description="Chain-of-custody integrity features" />
        <CardContent>
          <ul className="space-y-2 text-slate-300">
            {[
              'SHA-256 hashing for all evidence files',
              'HMAC-signed manifests for tamper detection',
              'Write-once object storage (WORM policy)',
              'Immutable audit trail with replay verification',
              'Duplicate prevention via case_id + sha256 constraint',
            ].map((item) => (
              <li key={item} className="flex items-center gap-2 text-sm">
                <Badge variant="verified" className="px-1.5 py-0">
                  ✓
                </Badge>
                {item}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusCard({ title, status }: { title: string; status: 'ok' | 'error' }) {
  return (
    <Card>
      <CardContent className="py-4">
        <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</h3>
        <div className="mt-1">
          <Badge variant={status === 'ok' ? 'verified' : 'error'}>
            {status === 'ok' ? 'Connected' : 'Error'}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

function ActionCard({
  href,
  title,
  description,
  testId,
}: {
  href: string;
  title: string;
  description: string;
  testId?: string;
}) {
  return (
    <Link href={href} data-testid={testId}>
      <Card className="hover:bg-slate-700/50 transition-colors h-full">
        <CardContent className="py-4">
          <h3 className="font-semibold text-blue-400 text-sm">{title}</h3>
          <p className="text-xs text-slate-400 mt-1">{description}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
