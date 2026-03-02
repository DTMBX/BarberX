/**
 * Tier 1 — PR Gate Smoke: Evidence
 *
 * Must pass on every PR. Verifies evidence endpoints respond.
 * No arbitrary waits. Strict mode. Deterministic selectors.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Evidence', () => {
  test('evidence API endpoint responds', async ({ request }) => {
    const response = await request.get('/api/v1/evidence');
    // Should return 200, 401, or 404 depending on auth state
    expect([200, 401, 403, 404]).toContain(response.status());
  });
});
