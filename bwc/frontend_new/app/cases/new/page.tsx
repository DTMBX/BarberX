'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createCase } from '@/lib/api';

export default function NewCasePage() {
  const router = useRouter();
  const [caseNumber, setCaseNumber] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const newCase = await createCase(caseNumber, description || undefined);
      router.push(`/cases/${newCase.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case');
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold mb-6">Create New Case</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        <div>
          <label
            htmlFor="caseNumber"
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            Case Number *
          </label>
          <input
            type="text"
            id="caseNumber"
            value={caseNumber}
            onChange={(e) => setCaseNumber(e.target.value)}
            required
            pattern="[A-Z0-9\-]+"
            placeholder="e.g., BWC-2026-001"
            className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-slate-500 mt-1">
            Uppercase letters, numbers, and hyphens only
          </p>
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="Optional case description..."
            className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={submitting || !caseNumber}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed
                       px-6 py-2 rounded-lg transition-colors font-medium"
          >
            {submitting ? 'Creating...' : 'Create Case'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="bg-slate-700 hover:bg-slate-600 px-6 py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
