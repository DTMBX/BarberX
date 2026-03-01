/**
 * Test fixtures for Playwright E2E tests.
 * Provides API helpers to seed data quickly and deterministic file generators.
 */
import { test as base, expect, type Page } from '@playwright/test';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/* ── API helpers ───────────────────────────────────────────────── */

export interface SeededCase {
  id: string;
  title: string;
  created_by: string;
}

export interface SeededEvidence {
  evidence_id: string;
  upload_url: string;
}

async function apiPost(path: string, body: Record<string, unknown>): Promise<any> {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

async function apiGet(path: string): Promise<any> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

/** Seed a fresh case via the API (avoids slow UI form fills). */
export async function seedCase(title?: string): Promise<SeededCase> {
  const caseTitle = title || `Test Case ${Date.now()}`;
  return apiPost('/cases', { title: caseTitle, created_by: 'e2e-test' });
}

/** Init evidence upload via the API. */
export async function seedEvidenceInit(
  caseId: string,
  filename: string,
  contentType: string,
  sizeBytes: number
): Promise<SeededEvidence> {
  return apiPost('/evidence/init', {
    case_id: caseId,
    filename: filename,
    content_type: contentType,
    size_bytes: sizeBytes,
  });
}

/** Complete evidence upload. */
export async function completeEvidence(evidenceId: string): Promise<any> {
  return apiPost('/evidence/complete', { evidence_id: evidenceId });
}

/**
 * Full evidence seed: init → upload actual bytes to presigned URL → complete.
 * Required because /evidence/complete downloads the file from MinIO to hash it.
 */
export async function seedFullEvidence(
  caseId: string,
  filename = 'seed.pdf',
  contentType = 'application/pdf'
): Promise<any> {
  const pdfBytes = makeTestPdf(filename);
  const ev = await seedEvidenceInit(caseId, filename, contentType, pdfBytes.length);
  // PUT the actual bytes to the presigned MinIO URL
  await fetch(ev.upload_url, {
    method: 'PUT',
    headers: { 'Content-Type': contentType },
    body: new Uint8Array(pdfBytes),
  });
  return completeEvidence(ev.evidence_id);
}

/** Fetch health check. */
export async function apiHealth(): Promise<any> {
  return apiGet('/health');
}

/* ── Deterministic file generators ─────────────────────────────── */

/** Creates a minimal valid PDF (deterministic, ~100 bytes). */
export function makeTestPdf(label = 'test'): Buffer {
  const content = [
    '%PDF-1.0',
    '1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj',
    '2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj',
    `3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj`,
    `4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (${label}) Tj ET\nendstream\nendobj`,
    'xref\n0 5\ntrailer<</Size 5/Root 1 0 R>>',
    'startxref\n0\n%%EOF',
  ].join('\n');
  return Buffer.from(content, 'utf-8');
}

/** Creates a minimal MP4-like file (just a header). */
export function makeTestVideo(): Buffer {
  // Minimal ftyp box (needed for a valid-ish mp4)
  const header = Buffer.alloc(32);
  header.writeUInt32BE(32, 0); // box length
  header.write('ftyp', 4); // box type
  header.write('isom', 8); // major brand
  header.writeUInt32BE(512, 12); // minor version
  header.write('isom', 16);
  header.write('iso2', 20);
  header.write('mp41', 24);
  return header;
}

/** Creates a deterministic plain-text file. */
export function makeTextFile(content = 'Evident E2E test file'): Buffer {
  return Buffer.from(content, 'utf-8');
}

/* ── Extended test fixture ─────────────────────────────────────── */

type TestFixtures = {
  /** Quick-seed a case via API and return its data. */
  seededCase: SeededCase;
  /** Helper to wait for app to be stable (no loading spinners). */
  waitForStable: (page: Page) => Promise<void>;
};

export const test = base.extend<TestFixtures>({
  seededCase: async ({}, use) => {
    const c = await seedCase();
    await use(c);
    // no teardown needed — ephemeral test DB
  },

  waitForStable: async ({}, use) => {
    await use(async (page: Page) => {
      // Wait for any loading spinners to disappear
      await page
        .waitForFunction(() => document.querySelectorAll('[class*="animate-pulse"]').length === 0, {
          timeout: 10_000,
        })
        .catch(() => {
          /* ok if none exist */
        });
    });
  },
});

export { expect };
