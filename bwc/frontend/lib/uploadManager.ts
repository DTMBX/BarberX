/**
 * Upload state machine for forensic-grade evidence ingestion.
 *
 * Each file progresses through: queued → hashing → init → uploading → completing → verified | failed
 *
 * Features:
 * - Off-main-thread SHA-256 via Web Worker
 * - Per-file state tracking with Observable-like pattern (callback)
 * - Retry for transient network failures (up to 3 attempts)
 * - Filename sanitization to prevent path traversal
 * - Concurrent upload limit to avoid overwhelming the backend
 */

import { initUpload, completeUpload } from '@/lib/api';

// ── Types ──────────────────────────────────────────────────────────

export type UploadStatus =
  | 'queued'
  | 'hashing'
  | 'init'
  | 'uploading'
  | 'completing'
  | 'verified'
  | 'failed';

export interface UploadFile {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number; // 0-100
  statusText: string;
  hash?: string;
  evidenceId?: string;
  error?: string;
  retries: number;
}

export type UploadEvent =
  | { type: 'update'; file: UploadFile }
  | { type: 'done'; file: UploadFile }
  | { type: 'allDone' };

type UploadListener = (event: UploadEvent) => void;

// ── Config ──────────────────────────────────────────────────────────

const MAX_CONCURRENT = 3;
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

// ── Helpers ─────────────────────────────────────────────────────────

/** Sanitize filename: strip path segments, replace dangerous chars */
export function sanitizeFilename(name: string): string {
  // Remove path components
  const base = name.split(/[\\/]/).pop() || 'unnamed';
  // Remove null bytes and path traversals
  return (
    base
      .replace(/[\x00-\x1f]/g, '')
      .replace(/\.\./g, '_')
      .trim() || 'unnamed'
  );
}

/** Generate a unique ID for upload tracking */
function generateId(): string {
  return `upload-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/** Hash file using Web Worker */
function hashFileInWorker(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    // Create inline worker from blob if the worker file isn't available
    const workerCode = `
      self.onmessage = async (e) => {
        try {
          const digest = await crypto.subtle.digest('SHA-256', e.data);
          const hex = Array.from(new Uint8Array(digest))
            .map((b) => b.toString(16).padStart(2, '0'))
            .join('');
          self.postMessage({ type: 'result', hash: hex });
        } catch (err) {
          self.postMessage({ type: 'error', message: err.message || 'Hash failed' });
        }
      };
    `;
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    const worker = new Worker(URL.createObjectURL(blob));

    worker.onmessage = (e: MessageEvent) => {
      worker.terminate();
      if (e.data.type === 'result') {
        resolve(e.data.hash);
      } else {
        reject(new Error(e.data.message || 'Worker hash failed'));
      }
    };

    worker.onerror = (e) => {
      worker.terminate();
      reject(new Error(`Worker error: ${e.message}`));
    };

    file.arrayBuffer().then((buf) => worker.postMessage(buf, [buf]), reject);
  });
}

/** Hash file with fallback for environments without Worker support */
async function hashFile(file: File): Promise<string> {
  if (typeof Worker !== 'undefined') {
    return hashFileInWorker(file);
  }
  // Fallback: hash on main thread
  const buf = await file.arrayBuffer();
  const digest = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Sleep helper for retry backoff */
function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

// ── Upload Manager ─────────────────────────────────────────────────

export class UploadManager {
  private files: Map<string, UploadFile> = new Map();
  private listeners: Set<UploadListener> = new Set();
  private running = 0;
  private queue: string[] = [];
  private caseId: string;

  constructor(caseId: string) {
    this.caseId = caseId;
  }

  /**
   * Subscribe to upload events.
   * Returns an unsubscribe function.
   */
  subscribe(listener: UploadListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(event: UploadEvent) {
    Array.from(this.listeners).forEach((listener) => listener(event));
  }

  private updateFile(id: string, patch: Partial<UploadFile>) {
    const file = this.files.get(id);
    if (!file) return;
    Object.assign(file, patch);
    this.emit({ type: 'update', file: { ...file } });
  }

  /** Get current snapshot of all files */
  getFiles(): UploadFile[] {
    return Array.from(this.files.values()).map((f) => ({ ...f }));
  }

  /** Get count of files still in progress */
  get pendingCount(): number {
    return Array.from(this.files.values()).filter((f) => !['verified', 'failed'].includes(f.status))
      .length;
  }

  /** Add files to the upload queue */
  addFiles(files: FileList | File[]) {
    for (const file of Array.from(files)) {
      const id = generateId();
      const uploadFile: UploadFile = {
        id,
        file,
        status: 'queued',
        progress: 0,
        statusText: 'Queued',
        retries: 0,
      };
      this.files.set(id, uploadFile);
      this.queue.push(id);
      this.emit({ type: 'update', file: { ...uploadFile } });
    }
    this.processQueue();
  }

  /** Clear completed/failed uploads */
  clearDone() {
    Array.from(this.files.entries()).forEach(([id, file]) => {
      if (file.status === 'verified' || file.status === 'failed') {
        this.files.delete(id);
      }
    });
  }

  /** Process the upload queue with concurrency limit */
  private processQueue() {
    while (this.running < MAX_CONCURRENT && this.queue.length > 0) {
      const id = this.queue.shift()!;
      this.running++;
      this.processFile(id).finally(() => {
        this.running--;
        this.processQueue();
        if (this.running === 0 && this.queue.length === 0) {
          this.emit({ type: 'allDone' });
        }
      });
    }
  }

  /** Process a single file through the upload state machine */
  private async processFile(id: string, attempt = 1): Promise<void> {
    const uf = this.files.get(id);
    if (!uf) return;

    try {
      // 1. Hash
      this.updateFile(id, { status: 'hashing', statusText: 'Computing SHA-256...', progress: 10 });
      const hash = await hashFile(uf.file);
      this.updateFile(id, { hash, progress: 30 });

      // 2. Init upload (get presigned URL)
      this.updateFile(id, { status: 'init', statusText: 'Requesting upload URL...', progress: 40 });
      const sanitizedName = sanitizeFilename(uf.file.name);
      const contentType = uf.file.type || 'application/octet-stream';
      const { evidence_id, upload_url } = await initUpload(
        this.caseId,
        sanitizedName,
        contentType,
        uf.file.size
      );
      this.updateFile(id, { evidenceId: evidence_id, progress: 50 });

      // 3. Upload to presigned URL
      this.updateFile(id, { status: 'uploading', statusText: 'Uploading...', progress: 60 });
      const res = await fetch(upload_url, {
        method: 'PUT',
        body: uf.file,
        headers: { 'Content-Type': contentType },
      });
      if (!res.ok) throw new Error(`Storage upload failed: ${res.status}`);
      this.updateFile(id, { progress: 85 });

      // 4. Complete
      this.updateFile(id, {
        status: 'completing',
        statusText: 'Verifying integrity...',
        progress: 90,
      });
      await completeUpload(evidence_id);

      // 5. Done
      this.updateFile(id, { status: 'verified', statusText: 'Verified ✓', progress: 100 });
      this.emit({ type: 'done', file: { ...this.files.get(id)! } });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';

      if (attempt < MAX_RETRIES) {
        this.updateFile(id, {
          statusText: `Retrying (${attempt}/${MAX_RETRIES})...`,
          retries: attempt,
        });
        await sleep(RETRY_DELAY_MS * attempt);
        return this.processFile(id, attempt + 1);
      }

      this.updateFile(id, {
        status: 'failed',
        statusText: message,
        error: message,
      });
      this.emit({ type: 'done', file: { ...this.files.get(id)! } });
    }
  }
}
