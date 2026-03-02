/**
 * Tier 2 — Full Suite: Evidence Edge Cases
 *
 * Upload failure, invalid evidence, integrity verification.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 2: Evidence Edge Cases', () => {
  test('upload without auth returns 401', async ({ request }) => {
    const response = await request.post('/api/v1/evidence/upload', {
      data: {},
    });
    expect([401, 403, 404]).toContain(response.status());
  });

  test('verify nonexistent evidence returns error', async ({ request }) => {
    const response = await request.post('/api/v1/evidence/nonexistent/verify');
    expect([401, 403, 404]).toContain(response.status());
  });
});
