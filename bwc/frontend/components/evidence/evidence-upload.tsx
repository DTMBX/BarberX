'use client';

import { useState, useCallback, useRef } from 'react';
import { clsx } from 'clsx';
import { LoadingSpinner } from '../ui/loading';
import { useToast } from '../ui/toast';
import { initUpload, completeUpload } from '@/lib/api';

interface FileUploadState {
  file: File;
  status: 'queued' | 'hashing' | 'init' | 'uploading' | 'completing' | 'done' | 'error';
  progress: number;
  localHash?: string;
  evidenceId?: string;
  errorMessage?: string;
}

interface EvidenceUploadProps {
  caseId: string;
  onUploadComplete?: () => void;
  accept?: string;
}

async function computeSha256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export function EvidenceUpload({
  caseId,
  onUploadComplete,
  accept = 'video/*,audio/*,image/*,application/pdf',
}: EvidenceUploadProps) {
  const [uploads, setUploads] = useState<FileUploadState[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { addToast } = useToast();

  const updateUpload = useCallback((index: number, patch: Partial<FileUploadState>) => {
    setUploads((prev) => prev.map((u, i) => (i === index ? { ...u, ...patch } : u)));
  }, []);

  const processFile = useCallback(
    async (file: File, index: number) => {
      try {
        // Step 1: Hash
        updateUpload(index, { status: 'hashing', progress: 10 });
        const localHash = await computeSha256(file);
        updateUpload(index, { localHash, progress: 25 });

        // Step 2: Init — get presigned URL
        updateUpload(index, { status: 'init', progress: 30 });
        const { evidence_id, upload_url } = await initUpload(
          caseId,
          file.name,
          file.type || 'application/octet-stream',
          file.size
        );
        updateUpload(index, { evidenceId: evidence_id, progress: 40 });

        // Step 3: Upload directly to MinIO via presigned URL
        updateUpload(index, { status: 'uploading', progress: 50 });
        const putRes = await fetch(upload_url, {
          method: 'PUT',
          body: file,
          headers: { 'Content-Type': file.type || 'application/octet-stream' },
        });
        if (!putRes.ok) {
          throw new Error(`Storage upload failed (HTTP ${putRes.status})`);
        }
        updateUpload(index, { progress: 75 });

        // Step 4: Complete — server verifies SHA-256 + dedup
        updateUpload(index, { status: 'completing', progress: 80 });
        await completeUpload(evidence_id);

        updateUpload(index, { status: 'done', progress: 100 });
        addToast('success', `Uploaded and verified: ${file.name}`);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Upload failed';
        updateUpload(index, { status: 'error', errorMessage: message });
        addToast('error', `${file.name}: ${message}`);
      }
    },
    [caseId, updateUpload, addToast]
  );

  const handleFiles = useCallback(
    (files: FileList) => {
      const offset = uploads.length;
      const newUploads: FileUploadState[] = Array.from(files).map((file) => ({
        file,
        status: 'queued' as const,
        progress: 0,
      }));
      setUploads((prev) => [...prev, ...newUploads]);

      // Start all uploads
      Array.from(files).forEach((file, i) => {
        processFile(file, offset + i);
      });
    },
    [uploads.length, processFile]
  );

  // Check if all uploads are done
  const allDone = uploads.length > 0 && uploads.every((u) => u.status === 'done' || u.status === 'error');
  const anyActive = uploads.some((u) => !['done', 'error', 'queued'].includes(u.status));

  // Fire callback when all done
  const prevAllDone = useRef(false);
  if (allDone && !prevAllDone.current && onUploadComplete) {
    prevAllDone.current = true;
    onUploadComplete();
  }
  if (!allDone) prevAllDone.current = false;

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        className={clsx(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
          dragOver
            ? 'border-blue-400 bg-blue-900/20'
            : 'border-slate-600 bg-slate-800/50 hover:border-slate-500',
          anyActive && 'pointer-events-none opacity-60'
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          accept={accept}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFiles(e.target.files);
              e.target.value = '';
            }
          }}
        />
        <div className="text-slate-400 text-4xl mb-2">📁</div>
        <p className="text-slate-300 font-medium">
          {dragOver ? 'Drop files here' : 'Drop evidence files or click to browse'}
        </p>
        <p className="text-slate-500 text-sm mt-1">
          Supported: Video, Audio, Images, PDF. Files are SHA-256 hashed and stored immutably.
        </p>
      </div>

      {/* Upload list */}
      {uploads.length > 0 && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-300">
              Uploads ({uploads.filter((u) => u.status === 'done').length}/{uploads.length})
            </h3>
            {allDone && (
              <button
                onClick={() => setUploads([])}
                className="text-xs text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            )}
          </div>

          {uploads.map((u, i) => (
            <div key={i} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  {u.status !== 'done' && u.status !== 'error' && u.status !== 'queued' && (
                    <LoadingSpinner size="sm" />
                  )}
                  {u.status === 'done' && <span className="text-emerald-400">✓</span>}
                  {u.status === 'error' && <span className="text-red-400">✕</span>}
                  <span className="truncate font-mono text-xs">{u.file.name}</span>
                </div>
                <span className="text-slate-500 text-xs ml-2">
                  {formatFileSize(u.file.size)}
                </span>
              </div>

              {/* Progress bar */}
              {u.status !== 'queued' && (
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className={clsx(
                      'h-full transition-all duration-300',
                      u.status === 'error' ? 'bg-red-500' : u.status === 'done' ? 'bg-emerald-500' : 'bg-blue-500'
                    )}
                    style={{ width: `${u.progress}%` }}
                  />
                </div>
              )}

              {/* Status text */}
              <div className="text-xs text-slate-500">
                {u.status === 'queued' && 'Queued'}
                {u.status === 'hashing' && 'Computing SHA-256...'}
                {u.status === 'init' && 'Requesting upload URL...'}
                {u.status === 'uploading' && 'Uploading to secure storage...'}
                {u.status === 'completing' && 'Verifying integrity...'}
                {u.status === 'done' && u.localHash && (
                  <span className="font-mono">SHA-256: {u.localHash.slice(0, 24)}...</span>
                )}
                {u.status === 'error' && (
                  <span className="text-red-400">{u.errorMessage}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
