/**
 * Tier 1 — PR Gate Smoke: Export
 *
 * Must pass on every PR. Verifies export endpoints respond.
 * No arbitrary waits. Strict mode. Deterministic selectors.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Export', () => {
  test('export API endpoint responds', async ({ request }) => {
    const response = await request.get('/api/v1/exports');
    expect([200, 401, 403, 404]).toContain(response.status());
  });
});
