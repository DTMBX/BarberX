'use client';

import { clsx } from 'clsx';
import { SkeletonTable } from '../ui/loading';
import type { Evidence } from '@/lib/api';

interface EvidenceTableProps {
  evidence: Evidence[];
  isLoading?: boolean;
  onView?: (id: string) => void;
  onReVerify?: (id: string) => void;
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString();
}

function getMimeIcon(contentType: string) {
  if (contentType.startsWith('video/')) return '🎬';
  if (contentType.startsWith('audio/')) return '🎵';
  if (contentType.startsWith('image/')) return '🖼';
  if (contentType === 'application/pdf') return '📄';
  return '📎';
}

function getStatusBadge(sha256: string | null) {
  if (sha256) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">
        ✓ Verified
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-900/50 text-yellow-300 border border-yellow-700/50">
      ⏳ Pending
    </span>
  );
}

export function EvidenceTable({ evidence, isLoading, onView, onReVerify }: EvidenceTableProps) {
  if (isLoading) {
    return <SkeletonTable rows={5} />;
  }

  if (evidence.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-800 rounded-lg border border-slate-700">
        <div className="text-slate-500 text-4xl mb-4">📂</div>
        <p className="text-slate-400">No evidence files yet</p>
        <p className="text-slate-500 text-sm mt-1">Upload evidence to get started</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg overflow-x-auto border border-slate-700">
      <table className="w-full text-sm">
        <thead className="bg-slate-700/50 border-b border-slate-600">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">File</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Type</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Size</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">SHA-256</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Status</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Uploaded</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {evidence.map((item) => (
            <tr key={item.id} className="hover:bg-slate-750 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getMimeIcon(item.content_type)}</span>
                  <span className="font-medium truncate max-w-[200px]">{item.original_filename}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-400">{item.content_type}</td>
              <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                {formatFileSize(item.size_bytes)}
              </td>
              <td className="px-4 py-3">
                {item.sha256 ? (
                  <code className="text-xs font-mono text-slate-400">
                    {item.sha256.slice(0, 16)}...
                  </code>
                ) : (
                  <span className="text-xs text-slate-500">—</span>
                )}
              </td>
              <td className="px-4 py-3">{getStatusBadge(item.sha256)}</td>
              <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                {formatDate(item.uploaded_at)}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  {item.sha256 && onReVerify && (
                    <button
                      onClick={() => onReVerify(item.id)}
                      className="px-2 py-1 text-xs bg-emerald-900/50 text-emerald-300 rounded
                                 hover:bg-emerald-800/50 border border-emerald-700/50 transition-colors"
                    >
                      Re-verify
                    </button>
                  )}
                  {onView && (
                    <button
                      onClick={() => onView(item.id)}
                      className="px-2 py-1 text-xs bg-blue-900/50 text-blue-300 rounded
                                 hover:bg-blue-800/50 border border-blue-700/50 transition-colors"
                    >
                      View
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
