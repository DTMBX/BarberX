'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface HealthStatus {
  status: string;
  database: string;
  redis: string;
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then(setHealth)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">System Status</h2>
        {error && (
          <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4 mb-4">
            <p className="text-red-200">Backend connection failed: {error}</p>
          </div>
        )}
        {health && (
          <div className="grid grid-cols-3 gap-4">
            <StatusCard
              title="API"
              status={health.status === 'healthy' ? 'ok' : 'error'}
            />
            <StatusCard
              title="Database"
              status={health.database === 'connected' ? 'ok' : 'error'}
            />
            <StatusCard
              title="Redis"
              status={health.redis === 'connected' ? 'ok' : 'error'}
            />
          </div>
        )}
        {!health && !error && (
          <p className="text-slate-400">Checking system status...</p>
        )}
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <ActionCard
            href="/cases/new"
            title="New Case"
            description="Create a new evidence case"
          />
          <ActionCard
            href="/cases"
            title="View Cases"
            description="Browse existing cases"
          />
          <ActionCard
            href="/verify"
            title="Verify Manifest"
            description="Validate evidence integrity"
          />
          <ActionCard
            href="/audit"
            title="Audit Log"
            description="Review system audit trail"
          />
        </div>
      </section>

      <section className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Forensic Guarantees</h2>
        <ul className="space-y-2 text-slate-300">
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">✓</span>
            SHA-256 hashing for all evidence files
          </li>
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">✓</span>
            HMAC-signed manifests for tamper detection
          </li>
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">✓</span>
            Write-once object storage (WORM policy)
          </li>
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">✓</span>
            Immutable audit trail with replay verification
          </li>
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">✓</span>
            Duplicate prevention via case_id + sha256 constraint
          </li>
        </ul>
      </section>
    </div>
  );
}

function StatusCard({ title, status }: { title: string; status: 'ok' | 'error' }) {
  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h3 className="text-sm font-medium text-slate-400 uppercase">{title}</h3>
      <p
        className={`text-lg font-semibold ${
          status === 'ok' ? 'text-emerald-400' : 'text-red-400'
        }`}
      >
        {status === 'ok' ? 'Connected' : 'Error'}
      </p>
    </div>
  );
}

function ActionCard({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="bg-slate-800 hover:bg-slate-700 rounded-lg p-4 border border-slate-700 transition-colors"
    >
      <h3 className="font-semibold text-blue-400">{title}</h3>
      <p className="text-sm text-slate-400 mt-1">{description}</p>
    </Link>
  );
}
