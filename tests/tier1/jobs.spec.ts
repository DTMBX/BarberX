/**
 * Tier 1 — PR Gate Smoke: Jobs
 *
 * Must pass on every PR. Verifies job endpoints respond.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Jobs', () => {
  test('jobs API endpoint responds', async ({ request }) => {
    const response = await request.get('/api/v1/jobs');
    expect([200, 401, 403, 404]).toContain(response.status());
  });
});
