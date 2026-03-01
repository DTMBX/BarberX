/**
 * BWC Backend API Client
 * Typed client for the FastAPI evidence management backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export interface Case {
  id: string;
  case_number: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: string;
  case_id: string;
  filename: string;
  sha256: string;
  size: number;
  content_type: string | null;
  metadata: Record<string, unknown> | null;
  uploaded_at: string;
  s3_key: string;
}

export interface Manifest {
  case_id: string;
  case_number: string;
  generated_at: string;
  evidence_count: number;
  evidence: Array<{
    id: string;
    filename: string;
    sha256: string;
    size: number;
    uploaded_at: string;
  }>;
  hmac_signature: string;
}

export interface VerifyResult {
  valid: boolean;
  errors: string[];
  checked_items: number;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
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

// Cases
export async function listCases(): Promise<Case[]> {
  return request<Case[]>('/cases/');
}

export async function createCase(caseNumber: string, description?: string): Promise<Case> {
  return request<Case>('/cases/', {
    method: 'POST',
    body: JSON.stringify({ case_number: caseNumber, description }),
  });
}

export async function getCase(caseId: string): Promise<Case> {
  return request<Case>(`/cases/${caseId}`);
}

// Evidence
export async function listEvidence(caseId: string): Promise<Evidence[]> {
  return request<Evidence[]>(`/cases/${caseId}/evidence/`);
}

export async function initUpload(
  caseId: string,
  filename: string
): Promise<{ upload_url: string; evidence_id: string }> {
  return request(`/cases/${caseId}/evidence/init`, {
    method: 'POST',
    body: JSON.stringify({ filename }),
  });
}

export async function confirmUpload(
  caseId: string,
  evidenceId: string,
  sha256: string
): Promise<Evidence> {
  return request<Evidence>(`/cases/${caseId}/evidence/${evidenceId}/confirm`, {
    method: 'POST',
    body: JSON.stringify({ sha256 }),
  });
}

// Manifest
export async function exportManifest(caseId: string): Promise<Manifest> {
  return request<Manifest>(`/cases/${caseId}/manifest`);
}

export async function verifyManifest(manifest: Manifest): Promise<VerifyResult> {
  return request<VerifyResult>('/verify/manifest', {
    method: 'POST',
    body: JSON.stringify(manifest),
  });
}

// Health
export async function healthCheck(): Promise<{ status: string; database: string; redis: string }> {
  return request('/health');
}
