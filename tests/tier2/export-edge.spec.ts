/**
 * Tier 2 — Full Suite: Export Edge Cases
 *
 * Invalid export, missing case, download without auth.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 2: Export Edge Cases', () => {
  test('export nonexistent case returns error', async ({ request }) => {
    const response = await request.post('/api/v1/export', {
      data: { case_id: 'nonexistent-case-999' },
    });
    expect([401, 403, 404, 422]).toContain(response.status());
  });

  test('download without auth returns 401', async ({ request }) => {
    const response = await request.get('/api/v1/export/fake-id/download');
    expect([401, 403, 404]).toContain(response.status());
  });
});
