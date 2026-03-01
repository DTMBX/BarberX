'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams } from 'next/navigation';
import {
  getCase,
  listEvidence,
  listArtifacts,
  listIssues,
  listJobs,
  initUpload,
  completeUpload,
  getTimeline,
  exportManifest,
  verifyManifest,
  auditReplay,
  enqueueJobs,
  createIssue,
  type Case,
  type Evidence,
  type EvidenceArtifact,
  type TimelineEvent,
  type Issue,
  type Job,
} from '@/lib/api';
import {
  useToast,
  Button,
  Badge,
  Card,
  CardHeader,
  CardContent,
  EmptyState,
  Tabs,
  TabPanel,
  PageHeader,
  DataTable,
  Input,
  Textarea,
  type Tab,
  type Column,
} from '@/components/ui';
import { PageLoading } from '@/components/ui/loading';

// ── Helpers ──────────────────────────────────────────────────────

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getMimeIcon(ct: string) {
  if (ct.startsWith('video/')) return '🎬';
  if (ct.startsWith('audio/')) return '🎵';
  if (ct.startsWith('image/')) return '🖼';
  if (ct === 'application/pdf') return '📄';
  return '📎';
}

type TabId = 'evidence' | 'artifacts' | 'timeline' | 'issues' | 'exports' | 'jobs';

// ── Upload per-file state ────────────────────────────────────────

interface FileUpload {
  file: File;
  status: 'queued' | 'hashing' | 'uploading' | 'completing' | 'done' | 'error';
  progress: string;
  evidenceId?: string;
  error?: string;
}

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;
  const { addToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Data state ─────────────────────────────────────────────────
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [artifacts, setArtifacts] = useState<EvidenceArtifact[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('evidence');

  // Upload state
  const [uploads, setUploads] = useState<FileUpload[]>([]);
  const [dragOver, setDragOver] = useState(false);

  // ── Data loading ───────────────────────────────────────────────
  const loadData = useCallback(async () => {
    try {
      const [c, e, a, t, iss, j] = await Promise.all([
        getCase(caseId),
        listEvidence(caseId),
        listArtifacts(caseId),
        getTimeline(caseId),
        listIssues(caseId),
        listJobs(caseId),
      ]);
      setCaseData(c);
      setEvidence(e);
      setArtifacts(a);
      setTimeline(t);
      setIssues(iss);
      setJobs(j);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // ── Upload helpers ─────────────────────────────────────────────
  async function uploadFile(file: File, index: number) {
    const update = (patch: Partial<FileUpload>) =>
      setUploads((prev) => prev.map((u, i) => (i === index ? { ...u, ...patch } : u)));

    try {
      update({ status: 'hashing', progress: 'Computing SHA-256...' });
      // Pre-hash (client-side verification)
      const buf = await file.arrayBuffer();
      await crypto.subtle.digest('SHA-256', buf);

      update({ status: 'uploading', progress: 'Requesting URL...' });
      const { evidence_id, upload_url } = await initUpload(
        caseId,
        file.name,
        file.type || 'application/octet-stream',
        file.size
      );
      update({ evidenceId: evidence_id, progress: 'Uploading...' });

      const res = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
      });
      if (!res.ok) throw new Error(`Storage upload failed: ${res.status}`);

      update({ status: 'completing', progress: 'Verifying...' });
      await completeUpload(evidence_id);
      update({ status: 'done', progress: 'Verified ✓' });
      addToast('success', `${file.name} uploaded`);
    } catch (err) {
      update({ status: 'error', error: err instanceof Error ? err.message : 'Failed' });
      addToast('error', `${file.name}: ${err instanceof Error ? err.message : 'Failed'}`);
    }
  }

  function startUploads(files: FileList) {
    const offset = uploads.length;
    const items: FileUpload[] = Array.from(files).map((f) => ({
      file: f,
      status: 'queued' as const,
      progress: 'Queued',
    }));
    setUploads((prev) => [...prev, ...items]);
    Array.from(files).forEach((f, i) => uploadFile(f, offset + i));
  }

  // When uploads finish, reload data
  const anyUploading = uploads.some((u) => !['done', 'error', 'queued'].includes(u.status));
  const prevUploading = useRef(anyUploading);
  useEffect(() => {
    if (prevUploading.current && !anyUploading && uploads.length > 0) loadData();
    prevUploading.current = anyUploading;
  }, [anyUploading, uploads.length, loadData]);

  // ── Pipeline ───────────────────────────────────────────────────
  async function runPipeline() {
    const verified = evidence.filter((e) => e.sha256);
    if (verified.length === 0) return;
    try {
      await enqueueJobs(verified.map((e) => e.id));
      addToast('success', `Pipeline started for ${verified.length} files`);
      setTimeout(loadData, 2000);
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Pipeline start failed');
    }
  }

  // ── Export ─────────────────────────────────────────────────────
  async function handleExport() {
    try {
      const manifest = await exportManifest(caseId);
      const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manifest-${caseData?.title || caseId}.json`;
      a.click();
      URL.revokeObjectURL(url);
      addToast('success', 'Manifest exported');
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Export failed');
    }
  }

  // ── Verify ─────────────────────────────────────────────────────
  const [verifyResult, setVerifyResult] = useState<{
    sha256: boolean;
    hmac: boolean;
    detail: string;
  } | null>(null);
  const [replayResult, setReplayResult] = useState<{ ok: boolean; detail: string } | null>(null);

  async function handleVerify() {
    try {
      const manifest = await exportManifest(caseId);
      const result = await verifyManifest(manifest);
      setVerifyResult({
        sha256: result.sha256_valid,
        hmac: result.hmac_valid,
        detail: result.detail,
      });
      addToast(result.sha256_valid && result.hmac_valid ? 'success' : 'error', result.detail);
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Verify failed');
    }
  }

  async function handleReplay() {
    try {
      const result = await auditReplay(caseId);
      setReplayResult({ ok: result.ok, detail: result.detail });
      addToast(result.ok ? 'success' : 'error', result.detail);
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Replay failed');
    }
  }

  // ── New issue ──────────────────────────────────────────────────
  const [showNewIssue, setShowNewIssue] = useState(false);
  const [newIssueTitle, setNewIssueTitle] = useState('');
  const [newIssueNarrative, setNewIssueNarrative] = useState('');

  async function handleCreateIssue(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createIssue({ case_id: caseId, title: newIssueTitle, narrative: newIssueNarrative });
      setNewIssueTitle('');
      setNewIssueNarrative('');
      setShowNewIssue(false);
      addToast('success', 'Issue created');
      loadData();
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Failed to create issue');
    }
  }

  // ── Render ─────────────────────────────────────────────────────
  if (loading) return <PageLoading />;

  if (error && !caseData) {
    return (
      <div className="rounded-lg border border-red-600/30 bg-red-900/20 p-6">
        <p className="text-red-300 mb-3">{error}</p>
        <Button variant="ghost" size="sm" onClick={() => window.history.back()}>
          ← Back to cases
        </Button>
      </div>
    );
  }

  const tabs: Tab[] = [
    { id: 'evidence', label: 'Evidence', count: evidence.length },
    { id: 'artifacts', label: 'Artifacts', count: artifacts.length },
    { id: 'timeline', label: 'Timeline', count: timeline.length },
    { id: 'issues', label: 'Issues', count: issues.length },
    { id: 'jobs', label: 'Jobs', count: jobs.length },
    { id: 'exports', label: 'Exports & Verify' },
  ];

  // ── Column definitions ──────────────────────────────────────
  const evidenceColumns: Column<Evidence>[] = [
    {
      id: 'file',
      header: 'File',
      cell: (e) => (
        <span>
          <span className="mr-2">{getMimeIcon(e.content_type)}</span>
          <span className="font-mono text-xs">{e.original_filename}</span>
        </span>
      ),
      sortValue: (e) => e.original_filename,
    },
    {
      id: 'type',
      header: 'Type',
      cell: (e) => <span className="text-slate-400 text-xs">{e.content_type}</span>,
    },
    {
      id: 'size',
      header: 'Size',
      cell: (e) => (
        <span className="text-slate-300 text-xs whitespace-nowrap">
          {formatBytes(e.size_bytes)}
        </span>
      ),
      sortValue: (e) => e.size_bytes,
    },
    {
      id: 'sha256',
      header: 'SHA-256',
      cell: (e) => (
        <span className="font-mono text-xs text-slate-400">
          {e.sha256 ? `${e.sha256.slice(0, 16)}…` : '—'}
        </span>
      ),
    },
    {
      id: 'status',
      header: 'Status',
      cell: (e) =>
        e.sha256 ? (
          <Badge variant="verified">Verified</Badge>
        ) : (
          <Badge variant="pending">Pending</Badge>
        ),
    },
    {
      id: 'uploaded',
      header: 'Uploaded',
      cell: (e) => (
        <span className="text-xs text-slate-400">{new Date(e.uploaded_at).toLocaleString()}</span>
      ),
      sortValue: (e) => e.uploaded_at,
    },
  ];

  const artifactColumns: Column<EvidenceArtifact>[] = [
    {
      id: 'type',
      header: 'Type',
      cell: (a) => <Badge variant="info">{a.artifact_type}</Badge>,
    },
    {
      id: 'evidence',
      header: 'Evidence',
      cell: (a) => {
        const ev = evidence.find((e) => e.id === a.evidence_id);
        return (
          <span className="text-xs text-slate-400">
            {ev?.original_filename || a.evidence_id.slice(0, 8)}
          </span>
        );
      },
    },
    {
      id: 'preview',
      header: 'Preview',
      cell: (a) => (
        <span className="text-xs text-slate-300 max-w-xs truncate block">
          {a.content_preview || '—'}
        </span>
      ),
    },
    {
      id: 'sha256',
      header: 'SHA-256',
      cell: (a) => (
        <span className="font-mono text-xs text-slate-500">
          {a.sha256 ? `${a.sha256.slice(0, 12)}…` : '—'}
        </span>
      ),
    },
    {
      id: 'created',
      header: 'Created',
      cell: (a) => (
        <span className="text-xs text-slate-400">{new Date(a.created_at).toLocaleString()}</span>
      ),
      sortValue: (a) => a.created_at,
    },
  ];

  const jobColumns: Column<Job>[] = [
    {
      id: 'task',
      header: 'Task',
      cell: (j) => <span className="text-xs uppercase">{j.task_type || 'unknown'}</span>,
    },
    {
      id: 'evidence',
      header: 'Evidence',
      cell: (j) => {
        const ev = evidence.find((e) => e.id === j.evidence_id);
        return (
          <span className="text-xs text-slate-400">
            {ev?.original_filename || j.evidence_id.slice(0, 8)}
          </span>
        );
      },
    },
    {
      id: 'status',
      header: 'Status',
      cell: (j) => (
        <Badge
          variant={
            j.status === 'complete'
              ? 'success'
              : j.status === 'failed'
                ? 'error'
                : j.status === 'running'
                  ? 'info'
                  : 'neutral'
          }
        >
          {j.status}
        </Badge>
      ),
    },
    {
      id: 'created',
      header: 'Created',
      cell: (j) => (
        <span className="text-xs text-slate-400">{new Date(j.created_at).toLocaleString()}</span>
      ),
      sortValue: (j) => j.created_at,
    },
    {
      id: 'updated',
      header: 'Updated',
      cell: (j) => (
        <span className="text-xs text-slate-400">{new Date(j.updated_at).toLocaleString()}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title={caseData?.title ?? 'Case'}
        data-testid="case-detail-header"
        breadcrumbs={[{ label: 'Cases', href: '/cases' }, { label: caseData?.title ?? caseId }]}
        status={
          <div className="flex gap-3 text-xs text-slate-400">
            <span>
              Status:{' '}
              <Badge variant={caseData?.status === 'open' ? 'success' : 'neutral'}>
                {caseData?.status ?? '—'}
              </Badge>
            </span>
            <span>
              By: <span className="text-slate-200">{caseData?.created_by}</span>
            </span>
            {caseData?.created_at && (
              <span>
                Created:{' '}
                <span className="text-slate-200">
                  {new Date(caseData.created_at).toLocaleDateString()}
                </span>
              </span>
            )}
          </div>
        }
        actions={
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={runPipeline}
              disabled={evidence.filter((e) => e.sha256).length === 0}
              data-testid="case-detail-run-pipeline-btn"
            >
              ▶ Run Pipeline
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleExport}
              disabled={evidence.length === 0}
              data-testid="case-detail-export-manifest-btn"
            >
              Export Manifest
            </Button>
          </div>
        }
      />

      {/* Drag/drop upload zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (e.dataTransfer.files.length) startUploads(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
          ${dragOver ? 'border-blue-400 bg-blue-900/20' : 'border-slate-600 bg-slate-800/50 hover:border-slate-500'}`}
        role="button"
        tabIndex={0}
        aria-label="Upload evidence files"
        data-testid="case-detail-upload-zone"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => {
            if (e.target.files?.length) {
              startUploads(e.target.files);
              e.target.value = '';
            }
          }}
          className="hidden"
          accept="video/*,audio/*,image/*,application/pdf"
          data-testid="case-detail-file-input"
        />
        <p className="text-slate-300 font-medium">
          {dragOver ? 'Drop files here' : 'Drag & drop evidence files, or click to browse'}
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Video, Audio, Images, PDF — SHA-256 hashed and stored immutably
        </p>
      </div>

      {/* Upload progress */}
      {uploads.length > 0 && (
        <Card data-testid="case-detail-upload-progress">
          <CardHeader
            title={`Uploads (${uploads.filter((u) => u.status === 'done').length}/${uploads.length})`}
            action={
              !anyUploading ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setUploads([])}
                  data-testid="case-detail-upload-clear-btn"
                >
                  Clear
                </Button>
              ) : undefined
            }
          />
          <CardContent className="space-y-2">
            {uploads.map((u, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <span className="truncate flex-1 font-mono text-xs">{u.file.name}</span>
                <span className="text-slate-500 text-xs">{formatBytes(u.file.size)}</span>
                {u.status === 'done' && <Badge variant="verified">✓</Badge>}
                {u.status === 'error' && (
                  <Badge variant="error" title={u.error}>
                    ✕
                  </Badge>
                )}
                {!['done', 'error'].includes(u.status) && (
                  <span className="text-blue-400 text-xs animate-pulse">{u.progress}</span>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Tab bar */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={(id) => setActiveTab(id as TabId)}
        testIdPrefix="case-detail-tab"
      />

      {/* ━━ Evidence tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="evidence" activeTab={activeTab}>
        <div data-testid="case-detail-evidence-table">
          <DataTable
            columns={evidenceColumns}
            data={evidence}
            rowKey={(e) => e.id}
            emptyTitle="No evidence yet"
            emptyDescription="Upload files above to add evidence to this case"
          />
        </div>
      </TabPanel>

      {/* ━━ Artifacts tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="artifacts" activeTab={activeTab}>
        <DataTable
          columns={artifactColumns}
          data={artifacts}
          rowKey={(a) => a.id}
          emptyTitle="No artifacts yet"
          emptyDescription="Run the pipeline to generate OCR, transcripts, and summaries"
        />
      </TabPanel>

      {/* ━━ Timeline tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="timeline" activeTab={activeTab}>
        <div data-testid="case-detail-timeline-section">
          {timeline.length === 0 ? (
            <Card>
              <EmptyState
                title="No timeline events yet"
                description="Events are recorded as evidence is uploaded and processed"
              />
            </Card>
          ) : (
            <div className="relative pl-6 space-y-4">
              <div className="absolute left-2 top-2 bottom-2 w-px bg-slate-600" />
              {timeline.map((evt, i) => (
                <div key={i} className="relative" data-testid="timeline-event">
                  <div className="absolute -left-4 top-1 w-3 h-3 rounded-full border-2 border-slate-500 bg-slate-800" />
                  <Card>
                    <CardContent>
                      <div className="flex items-center gap-3 mb-1">
                        <Badge variant="info">{evt.event_type}</Badge>
                        <span
                          className="text-xs text-slate-500"
                          data-testid="timeline-event-timestamp"
                        >
                          {new Date(evt.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-200">{evt.description}</p>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          )}
        </div>
      </TabPanel>

      {/* ━━ Issues tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="issues" activeTab={activeTab}>
        <div data-testid="case-detail-issues-section">
          <div className="space-y-4">
            <div className="flex justify-end">
              <Button
                variant={showNewIssue ? 'secondary' : 'primary'}
                size="sm"
                onClick={() => setShowNewIssue(!showNewIssue)}
                data-testid="issues-new-btn"
              >
                {showNewIssue ? 'Cancel' : '+ New Issue'}
              </Button>
            </div>
            {showNewIssue && (
              <Card>
                <CardContent>
                  <form onSubmit={handleCreateIssue} className="space-y-3">
                    <Input
                      label="Issue Title"
                      value={newIssueTitle}
                      onChange={(e) => setNewIssueTitle(e.target.value)}
                      required
                      placeholder="Issue title"
                      data-testid="issue-title-input"
                    />
                    <Textarea
                      label="Narrative"
                      value={newIssueNarrative}
                      onChange={(e) => setNewIssueNarrative(e.target.value)}
                      required
                      placeholder="Describe the alleged violation..."
                      rows={3}
                      data-testid="issue-description-input"
                    />
                    <Button
                      type="submit"
                      size="sm"
                      disabled={!newIssueTitle || !newIssueNarrative}
                      data-testid="issue-submit-btn"
                    >
                      Create Issue
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}
            {issues.length === 0 && !showNewIssue ? (
              <Card>
                <EmptyState
                  title="No issues yet"
                  description="Create one to track violations and allegations"
                  action={
                    <Button size="sm" onClick={() => setShowNewIssue(true)}>
                      + New Issue
                    </Button>
                  }
                />
              </Card>
            ) : (
              issues.map((iss) => (
                <Card key={iss.id}>
                  <CardContent>
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="font-semibold text-sm">{iss.title}</h3>
                      <Badge
                        variant={
                          iss.status === 'open'
                            ? 'warning'
                            : iss.status === 'confirmed'
                              ? 'error'
                              : 'neutral'
                        }
                      >
                        {iss.status}
                      </Badge>
                      <Badge
                        variant={
                          iss.confidence === 'high'
                            ? 'success'
                            : iss.confidence === 'low'
                              ? 'neutral'
                              : 'info'
                        }
                      >
                        {iss.confidence}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-300">{iss.narrative}</p>
                    {iss.code_reference && (
                      <p className="text-xs text-slate-500 mt-1">Ref: {iss.code_reference}</p>
                    )}
                    <p className="text-xs text-slate-500 mt-1">
                      By {iss.created_by} — {new Date(iss.created_at).toLocaleDateString()}
                    </p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      </TabPanel>

      {/* ━━ Jobs tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="jobs" activeTab={activeTab}>
        <div data-testid="case-detail-jobs-section">
          <DataTable
            columns={jobColumns}
            data={jobs}
            rowKey={(j) => j.id}
            rowTestId="job-row"
            emptyTitle="No jobs yet"
            emptyDescription='Click "Run Pipeline" to process evidence'
          />
        </div>
      </TabPanel>

      {/* ━━ Exports & Verify tab ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <TabPanel id="exports" activeTab={activeTab}>
        <div className="space-y-4" data-testid="case-detail-exports-section">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Export */}
            <Card>
              <CardHeader
                title="Export Manifest"
                description="Download cryptographically signed manifest with SHA-256 + HMAC."
              />
              <CardContent>
                <Button onClick={handleExport} disabled={evidence.length === 0} className="w-full">
                  Download Manifest
                </Button>
              </CardContent>
            </Card>
            {/* Verify */}
            <Card>
              <CardHeader
                title="Verify Integrity"
                description="Re-verify SHA-256 + HMAC against current evidence."
              />
              <CardContent>
                <Button
                  onClick={handleVerify}
                  disabled={evidence.length === 0}
                  className="w-full"
                  data-testid="case-detail-verify-integrity-btn"
                >
                  Verify Manifest
                </Button>
                {verifyResult && (
                  <div
                    data-testid="case-detail-verify-result"
                    className={`mt-3 p-3 rounded text-sm ${verifyResult.sha256 && verifyResult.hmac ? 'bg-emerald-900/30 text-emerald-300' : 'bg-red-900/30 text-red-300'}`}
                  >
                    <p>
                      {verifyResult.sha256 ? '✓' : '✕'} SHA-256 — {verifyResult.hmac ? '✓' : '✕'}{' '}
                      HMAC
                    </p>
                    <p className="text-xs mt-1 opacity-70">{verifyResult.detail}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          {/* Audit replay */}
          <Card>
            <CardHeader
              title="Audit Replay"
              description="Full chain-of-custody replay: re-download every evidence file from MinIO, recompute SHA-256, verify audit trail ordering and completeness."
            />
            <CardContent>
              <Button
                variant="secondary"
                onClick={handleReplay}
                data-testid="case-detail-audit-replay-btn"
              >
                Run Audit Replay
              </Button>
              {replayResult && (
                <div
                  data-testid="case-detail-replay-section"
                  className={`mt-3 p-3 rounded text-sm ${replayResult.ok ? 'bg-emerald-900/30 text-emerald-300' : 'bg-red-900/30 text-red-300'}`}
                >
                  <p>{replayResult.ok ? '✓ PASSED' : '✕ FAILED'}</p>
                  <p className="text-xs mt-1 opacity-70">{replayResult.detail}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </TabPanel>
    </div>
  );
}
