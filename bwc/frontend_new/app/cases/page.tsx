'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listCases, type Case } from '@/lib/api';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCases()
      .then(setCases)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Cases</h1>
        <Link
          href="/cases/new"
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
        >
          New Case
        </Link>
      </div>

      {loading && <p className="text-slate-400">Loading cases...</p>}
      {error && (
        <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4">
          <p className="text-red-200">Error: {error}</p>
        </div>
      )}

      {!loading && !error && cases.length === 0 && (
        <div className="bg-slate-800 rounded-lg p-8 text-center">
          <p className="text-slate-400 mb-4">No cases yet</p>
          <Link
            href="/cases/new"
            className="text-blue-400 hover:text-blue-300"
          >
            Create your first case →
          </Link>
        </div>
      )}

      {cases.length > 0 && (
        <div className="bg-slate-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-700">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                  Case Number
                </th>
                <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                  Description
                </th>
                <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                  Created
                </th>
                <th className="text-right px-4 py-3 text-sm font-medium text-slate-300">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-slate-750">
                  <td className="px-4 py-3 font-mono text-blue-400">
                    <Link href={`/cases/${c.id}`}>{c.case_number}</Link>
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {c.description || '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-sm">
                    {new Date(c.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/cases/${c.id}`}
                      className="text-blue-400 hover:text-blue-300 text-sm"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
