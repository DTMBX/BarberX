'use client';

import { useState } from 'react';
import {
  verifyManifest,
  auditReplay,
  type Manifest,
  type VerifyResult,
  type AuditReplayResult,
} from '@/lib/api';
import {
  Button,
  Textarea,
  PageHeader,
  Card,
  CardHeader,
  CardContent,
  Badge,
} from '@/components/ui';

export default function VerifyPage() {
  const [manifestText, setManifestText] = useState('');
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [replayResult, setReplayResult] = useState<AuditReplayResult | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [replaying, setReplaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setManifestText(await file.text());
    setResult(null);
    setReplayResult(null);
    setError(null);
  }

  async function handleVerify() {
    setVerifying(true);
    setError(null);
    setResult(null);
    try {
      const manifest: Manifest = JSON.parse(manifestText);
      setResult(await verifyManifest(manifest));
    } catch (err) {
      setError(
        err instanceof SyntaxError
          ? 'Invalid JSON format'
          : err instanceof Error
            ? err.message
            : 'Verification failed'
      );
    } finally {
      setVerifying(false);
    }
  }

  async function handleReplay() {
    setReplaying(true);
    setError(null);
    setReplayResult(null);
    try {
      const manifest: Manifest = JSON.parse(manifestText);
      const caseId = manifest.case?.id;
      if (!caseId) throw new Error('Manifest missing case.id');
      setReplayResult(await auditReplay(caseId));
    } catch (err) {
      setError(
        err instanceof SyntaxError
          ? 'Invalid JSON'
          : err instanceof Error
            ? err.message
            : 'Replay failed'
      );
    } finally {
      setReplaying(false);
    }
  }

  const valid = result ? result.sha256_valid && result.hmac_valid : null;

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Verify Manifest"
        description="Upload a previously exported manifest to verify SHA-256 and HMAC integrity, or run a full audit replay."
        data-testid="verify-page-header"
      />

      <div className="mt-6 space-y-6">
        {/* File upload */}
        <Card>
          <CardContent>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              Select Manifest File
            </label>
            <input
              type="file"
              accept=".json"
              onChange={handleFileSelect}
              data-testid="verify-file-input"
              className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-slate-700 file:text-slate-200 hover:file:bg-slate-600"
            />
          </CardContent>
        </Card>

        <div className="text-center text-slate-500 text-sm">— or —</div>

        {/* Paste JSON */}
        <Textarea
          label="Paste Manifest JSON"
          value={manifestText}
          onChange={(e) => {
            setManifestText(e.target.value);
            setResult(null);
            setReplayResult(null);
            setError(null);
          }}
          rows={10}
          placeholder='{"case": { ... }, "evidence": [...], "manifest_sha256": "...", "manifest_hmac": "..."}'
          className="font-mono"
          data-testid="verify-manifest-textarea"
        />

        {/* Action buttons */}
        <div className="flex gap-4">
          <Button
            onClick={handleVerify}
            disabled={!manifestText}
            loading={verifying}
            className="flex-1"
            data-testid="verify-integrity-btn"
          >
            Verify Integrity
          </Button>
          <Button
            variant="secondary"
            onClick={handleReplay}
            disabled={!manifestText}
            loading={replaying}
            className="flex-1"
            data-testid="verify-replay-btn"
          >
            Audit Replay
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-red-600/30 bg-red-900/20 p-4">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Verify result */}
        {result && (
          <Card className={valid ? 'border-emerald-600/30' : 'border-red-600/30'}>
            <CardContent className={valid ? 'bg-emerald-900/10' : 'bg-red-900/10'}>
              <div className="flex items-center gap-3 mb-4">
                <span className={`text-3xl ${valid ? 'text-emerald-400' : 'text-red-400'}`}>
                  {valid ? '✓' : '✗'}
                </span>
                <h2 className={`text-xl font-bold ${valid ? 'text-emerald-300' : 'text-red-300'}`}>
                  {valid ? 'Verification Passed' : 'Verification Failed'}
                </h2>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant={result.sha256_valid ? 'verified' : 'tampered'}>
                    {result.sha256_valid ? '✓' : '✗'}
                  </Badge>
                  <span className="text-slate-300">SHA-256 integrity</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={result.hmac_valid ? 'verified' : 'tampered'}>
                    {result.hmac_valid ? '✓' : '✗'}
                  </Badge>
                  <span className="text-slate-300">HMAC signature</span>
                </div>
                {result.detail && <p className="text-slate-400 mt-2">{result.detail}</p>}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Audit replay result */}
        {replayResult && (
          <Card className={replayResult.ok ? 'border-emerald-600/30' : 'border-red-600/30'}>
            <CardContent className={replayResult.ok ? 'bg-emerald-900/10' : 'bg-red-900/10'}>
              <div className="flex items-center gap-3 mb-4">
                <span
                  className={`text-3xl ${replayResult.ok ? 'text-emerald-400' : 'text-red-400'}`}
                >
                  {replayResult.ok ? '✓' : '✗'}
                </span>
                <h2
                  className={`text-xl font-bold ${replayResult.ok ? 'text-emerald-300' : 'text-red-300'}`}
                >
                  {replayResult.ok ? 'Audit Replay Passed' : 'Audit Replay Failed'}
                </h2>
              </div>
              <div className="space-y-1 text-sm text-slate-300">
                <p>
                  Events checked: <span className="font-mono">{replayResult.events_checked}</span>
                </p>
                <p>
                  Evidence checked:{' '}
                  <span className="font-mono">{replayResult.evidence_checked}</span>
                </p>
                {replayResult.sha256_mismatches.length > 0 && (
                  <div className="mt-3">
                    <p className="text-red-300 font-medium">SHA-256 mismatches:</p>
                    <ul className="mt-1 space-y-1">
                      {replayResult.sha256_mismatches.map((m, i) => (
                        <li key={i} className="text-red-200 font-mono text-xs">
                          {JSON.stringify(m)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {replayResult.detail && (
                  <p className="text-slate-400 mt-2">{replayResult.detail}</p>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
