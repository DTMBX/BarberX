'use client';

import { useState } from 'react';
import { verifyManifest, type Manifest, type VerifyResult } from '@/lib/api';

export default function VerifyPage() {
  const [manifestText, setManifestText] = useState('');
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    setManifestText(text);
    setResult(null);
    setError(null);
  }

  async function handleVerify() {
    setVerifying(true);
    setError(null);
    setResult(null);

    try {
      const manifest: Manifest = JSON.parse(manifestText);
      const verifyResult = await verifyManifest(manifest);
      setResult(verifyResult);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON format');
      } else {
        setError(err instanceof Error ? err.message : 'Verification failed');
      }
    } finally {
      setVerifying(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-6">Verify Manifest</h1>
      <p className="text-slate-400 mb-6">
        Upload a previously exported manifest to verify the integrity of evidence
        and check for tampering.
      </p>

      <div className="space-y-6">
        {/* File Upload */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Select Manifest File
          </label>
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFileSelect}
            className="block w-full"
          />
        </div>

        {/* Or paste JSON */}
        <div className="text-center text-slate-500">— or —</div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Paste Manifest JSON
          </label>
          <textarea
            value={manifestText}
            onChange={(e) => {
              setManifestText(e.target.value);
              setResult(null);
              setError(null);
            }}
            rows={10}
            placeholder='{"case_id": "...", "evidence": [...], "hmac_signature": "..."}'
            className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 font-mono text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={handleVerify}
          disabled={!manifestText || verifying}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed
                     py-3 rounded-lg transition-colors font-medium"
        >
          {verifying ? 'Verifying...' : 'Verify Integrity'}
        </button>

        {/* Error */}
        {error && (
          <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div
            className={`rounded-lg p-6 border ${
              result.valid
                ? 'bg-emerald-900/30 border-emerald-600/30'
                : 'bg-red-900/30 border-red-600/30'
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <span
                className={`text-3xl ${result.valid ? 'text-emerald-400' : 'text-red-400'}`}
              >
                {result.valid ? '✓' : '✗'}
              </span>
              <div>
                <h2
                  className={`text-xl font-bold ${
                    result.valid ? 'text-emerald-300' : 'text-red-300'
                  }`}
                >
                  {result.valid ? 'Verification Passed' : 'Verification Failed'}
                </h2>
                <p className="text-sm text-slate-400">
                  {result.checked_items} item(s) checked
                </p>
              </div>
            </div>

            {result.errors.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-medium text-red-300 mb-2">Errors:</h3>
                <ul className="space-y-1">
                  {result.errors.map((err, i) => (
                    <li key={i} className="text-sm text-red-200 font-mono">
                      • {err}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
