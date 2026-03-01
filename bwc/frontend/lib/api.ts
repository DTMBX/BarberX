/**
 * BWC Backend API Client
 * Typed client for the FastAPI evidence management backend.
 * All endpoints match the backend OpenAPI schema.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

// ── Types ─────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_by: string;
  created_at: string;
}

export interface Case {
  id: string;
  project_id: string | null;
  title: string;
  created_by: string;
  status: string;
  created_at: string;
}

export interface Evidence {
  id: string;
  case_id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  sha256: string | null;
  minio_object_key: string;
  uploaded_at: string;
}

export interface EvidenceArtifact {
  id: string;
  evidence_id: string;
  case_id: string;
  artifact_type: string;
  minio_object_key: string;
  sha256: string | null;
  content_preview: string | null;
  created_at: string;
}

export interface Job {
  id: string;
  case_id: string;
  evidence_id: string;
  task_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  evidence_id: string | null;
  metadata: Record<string, unknown> | null;
}

export interface Manifest {
  case: Case;
  evidence: Evidence[];
  audit: AuditEvent[];
  manifest_sha256: string;
  manifest_hmac: string;
}

export interface AuditEvent {
  id: string;
  case_id: string | null;
  event_type: string;
  payload_json: Record<string, unknown>;
  created_at: string;
}

export interface VerifyResult {
  sha256_valid: boolean;
  hmac_valid: boolean;
  detail: string;
}

export interface AuditReplayResult {
  ok: boolean;
  events_checked: number;
  evidence_checked: number;
  sha256_mismatches: Array<Record<string, unknown>>;
  detail: string;
}

export interface ChatCitation {
  source_type: string;
  source_id: string | null;
  url: string | null;
  title: string | null;
  snippet: string | null;
  court: string | null;
  date: string | null;
  verification_status: string;
}

export interface ChatResponse {
  message_id: string;
  answer: string;
  citations: ChatCitation[];
  verification_status: string;
}

export interface ChatMessage {
  id: string;
  scope: string;
  project_id: string | null;
  case_id: string | null;
  role: string;
  content: string;
  citations: ChatCitation[] | null;
  verification_status: string | null;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  database: string;
  redis: string;
  minio: string;
}

// ── Error ─────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ── Request helper ────────────────────────────────────────────────

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body || res.statusText);
  }

  return res.json();
}

// ── Health ────────────────────────────────────────────────────────

export async function healthCheck(): Promise<HealthStatus> {
  return request('/health');
}

// ── Projects ─────────────────────────────────────────────────────

export async function listProjects(): Promise<Project[]> {
  return request<Project[]>('/projects');
}

export async function createProject(
  name: string,
  created_by: string,
  description?: string
): Promise<Project> {
  return request<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify({ name, created_by, description }),
  });
}

export async function getProject(id: string): Promise<Project> {
  return request<Project>(`/projects/${id}`);
}

// ── Cases ────────────────────────────────────────────────────────

export async function listCases(projectId?: string): Promise<Case[]> {
  const params = projectId ? `?project_id=${projectId}` : '';
  return request<Case[]>(`/cases${params}`);
}

export async function createCase(
  title: string,
  created_by: string,
  project_id?: string
): Promise<Case> {
  return request<Case>('/cases', {
    method: 'POST',
    body: JSON.stringify({ title, created_by, project_id }),
  });
}

export async function getCase(caseId: string): Promise<Case> {
  return request<Case>(`/cases/${caseId}`);
}

// ── Evidence ─────────────────────────────────────────────────────

export async function listEvidence(caseId: string): Promise<Evidence[]> {
  return request<Evidence[]>(`/evidence?case_id=${caseId}`);
}

export async function initUpload(
  caseId: string,
  filename: string,
  contentType: string,
  sizeBytes: number
): Promise<{ evidence_id: string; upload_url: string }> {
  return request('/evidence/init', {
    method: 'POST',
    body: JSON.stringify({
      case_id: caseId,
      filename,
      content_type: contentType,
      size_bytes: sizeBytes,
    }),
  });
}

export async function batchInitUpload(
  caseId: string,
  files: Array<{ filename: string; content_type: string; size_bytes: number }>
): Promise<{ items: Array<{ evidence_id: string; upload_url: string }> }> {
  return request('/evidence/batch/init', {
    method: 'POST',
    body: JSON.stringify({ case_id: caseId, files }),
  });
}

export async function completeUpload(evidenceId: string): Promise<Evidence> {
  return request<Evidence>('/evidence/complete', {
    method: 'POST',
    body: JSON.stringify({ evidence_id: evidenceId }),
  });
}

// ── Jobs ─────────────────────────────────────────────────────────

export async function enqueueJobs(
  evidenceIds: string[],
  tasks: string[] = ['ocr', 'transcribe', 'metadata']
): Promise<Job[]> {
  return request<Job[]>('/jobs/enqueue', {
    method: 'POST',
    body: JSON.stringify({ evidence_ids: evidenceIds, tasks }),
  });
}

export async function listJobs(caseId?: string): Promise<Job[]> {
  const params = caseId ? `?case_id=${caseId}` : '';
  return request<Job[]>(`/jobs${params}`);
}

// ── Timeline ─────────────────────────────────────────────────────

export async function getTimeline(caseId: string): Promise<TimelineEvent[]> {
  return request<TimelineEvent[]>(`/cases/${caseId}/timeline`);
}

// ── Manifest & Verify ────────────────────────────────────────────

export async function exportManifest(caseId: string): Promise<Manifest> {
  return request<Manifest>(`/cases/${caseId}/export/manifest`);
}

export async function verifyManifest(manifest: Manifest): Promise<VerifyResult> {
  return request<VerifyResult>('/verify/manifest', {
    method: 'POST',
    body: JSON.stringify(manifest),
  });
}

export async function auditReplay(caseId: string): Promise<AuditReplayResult> {
  return request<AuditReplayResult>(`/verify/cases/${caseId}/audit-replay`);
}

// ── Chat ─────────────────────────────────────────────────────────

export async function chatAsk(
  question: string,
  scope: string = 'global',
  caseId?: string,
  projectId?: string
): Promise<ChatResponse> {
  return request<ChatResponse>('/chat/ask', {
    method: 'POST',
    body: JSON.stringify({
      question,
      scope,
      case_id: caseId,
      project_id: projectId,
    }),
  });
}

export async function chatHistory(
  scope: string = 'global',
  caseId?: string,
  projectId?: string,
  limit: number = 50
): Promise<ChatMessage[]> {
  const params = new URLSearchParams({ scope, limit: String(limit) });
  if (caseId) params.set('case_id', caseId);
  if (projectId) params.set('project_id', projectId);
  return request<ChatMessage[]>(`/chat/history?${params}`);
}

export async function chatContext(
  scope: string = 'global',
  caseId?: string
): Promise<Record<string, unknown>> {
  const params = new URLSearchParams({ scope });
  if (caseId) params.set('case_id', caseId);
  return request(`/chat/context?${params}`);
}

// ── Artifacts ────────────────────────────────────────────────────

export async function listArtifacts(
  caseId?: string,
  evidenceId?: string,
  artifactType?: string
): Promise<EvidenceArtifact[]> {
  const params = new URLSearchParams();
  if (caseId) params.set('case_id', caseId);
  if (evidenceId) params.set('evidence_id', evidenceId);
  if (artifactType) params.set('artifact_type', artifactType);
  return request<EvidenceArtifact[]>(`/artifacts?${params}`);
}

// ── Issues / Violations ──────────────────────────────────────────

export interface Issue {
  id: string;
  case_id: string;
  title: string;
  narrative: string;
  jurisdiction: string | null;
  code_reference: string | null;
  courtlistener_cites: unknown[] | null;
  supporting_sources: unknown[];
  confidence: string;
  status: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface IssueCreate {
  case_id: string;
  title: string;
  narrative: string;
  jurisdiction?: string;
  code_reference?: string;
  courtlistener_cites?: unknown[];
  supporting_sources?: unknown[];
  confidence?: string;
  status?: string;
  created_by?: string;
}

export async function listIssues(caseId?: string, status?: string): Promise<Issue[]> {
  const params = new URLSearchParams();
  if (caseId) params.set('case_id', caseId);
  if (status) params.set('status', status);
  return request<Issue[]>(`/issues?${params}`);
}

export async function createIssue(issue: IssueCreate): Promise<Issue> {
  return request<Issue>('/issues', { method: 'POST', body: JSON.stringify(issue) });
}

export async function getIssue(id: string): Promise<Issue> {
  return request<Issue>(`/issues/${id}`);
}

export async function updateIssue(id: string, patch: Record<string, unknown>): Promise<Issue> {
  return request<Issue>(`/issues/${id}`, { method: 'PATCH', body: JSON.stringify(patch) });
}

// ── Legal Search (CourtListener) ─────────────────────────────────

export interface LegalOpinion {
  id: number;
  absolute_url: string | null;
  case_name: string | null;
  court: string | null;
  date_filed: string | null;
  snippet: string | null;
  citation_count: number | null;
  cluster_id: number | null;
}

export async function legalSearch(
  query: string,
  opts?: {
    jurisdiction?: string;
    court?: string;
    dateFrom?: string;
    dateTo?: string;
    page?: number;
  }
): Promise<LegalOpinion[]> {
  const params = new URLSearchParams({ q: query });
  if (opts?.jurisdiction) params.set('jurisdiction', opts.jurisdiction);
  if (opts?.court) params.set('court', opts.court);
  if (opts?.dateFrom) params.set('date_from', opts.dateFrom);
  if (opts?.dateTo) params.set('date_to', opts.dateTo);
  if (opts?.page) params.set('page', String(opts.page));
  return request<LegalOpinion[]>(`/legal/search?${params}`);
}

// ── Utility ──────────────────────────────────────────────────────

export async function computeSha256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}
