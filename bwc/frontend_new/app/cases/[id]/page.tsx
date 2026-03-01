'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  getCase,
  listEvidence,
  initUpload,
  confirmUpload,
  exportManifest,
  type Case,
  type Evidence,
} from '@/lib/api';

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [c, e] = await Promise.all([getCase(caseId), listEvidence(caseId)]);
      setCaseData(c);
      setEvidence(e);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress('Initializing upload...');
    setError(null);

    try {
      // Step 1: Get pre-signed URL
      const { upload_url, evidence_id } = await initUpload(caseId, file.name);

      // Step 2: Upload directly to S3/MinIO
      setUploadProgress('Uploading file...');
      const uploadRes = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type || 'application/octet-stream',
        },
      });

      if (!uploadRes.ok) {
        throw new Error('Failed to upload file to storage');
      }

      // Step 3: Calculate SHA-256 hash
      setUploadProgress('Computing hash...');
      const sha256 = await computeSha256(file);

      // Step 4: Confirm upload with hash
      setUploadProgress('Confirming upload...');
      await confirmUpload(caseId, evidence_id, sha256);

      // Reload evidence list
      setUploadProgress(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(null);
      // Reset file input
      e.target.value = '';
    }
  }

  async function handleExportManifest() {
    try {
      const manifest = await exportManifest(caseId);
      const blob = new Blob([JSON.stringify(manifest, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manifest-${caseData?.case_number || caseId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export manifest');
    }
  }

  if (loading) {
    return <p className="text-slate-400">Loading case...</p>;
  }

  if (error && !caseData) {
    return (
      <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4">
        <p className="text-red-200">Error: {error}</p>
        <Link href="/cases" className="text-blue-400 hover:text-blue-300 mt-2 inline-block">
          ← Back to cases
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link href="/cases" className="text-slate-400 hover:text-slate-300 text-sm">
            ← Cases
          </Link>
          <h1 className="text-2xl font-bold mt-1">{caseData?.case_number}</h1>
          {caseData?.description && (
            <p className="text-slate-400 mt-1">{caseData.description}</p>
          )}
        </div>
        <button
          onClick={handleExportManifest}
          disabled={evidence.length === 0}
          className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed
                     px-4 py-2 rounded-lg transition-colors"
        >
          Export Manifest
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-600/30 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Upload Section */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-semibold mb-4">Upload Evidence</h2>
        <div className="flex items-center gap-4">
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            className="flex-1"
          />
          {uploadProgress && (
            <span className="text-blue-400 text-sm">{uploadProgress}</span>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Files are hashed (SHA-256) and stored immutably. No modifications or deletions allowed.
        </p>
      </div>

      {/* Evidence List */}
      <div>
        <h2 className="text-lg font-semibold mb-4">
          Evidence ({evidence.length})
        </h2>
        {evidence.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-8 text-center border border-slate-700">
            <p className="text-slate-400">No evidence uploaded yet</p>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
            <table className="w-full">
              <thead className="bg-slate-700/50">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                    Filename
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                    SHA-256
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                    Size
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-slate-300">
                    Uploaded
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {evidence.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-750">
                    <td className="px-4 py-3 font-mono text-sm">{e.filename}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">
                      {e.sha256.substring(0, 16)}...
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {formatBytes(e.size)}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400">
                      {new Date(e.uploaded_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// Compute SHA-256 in browser using Web Crypto API
async function computeSha256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
