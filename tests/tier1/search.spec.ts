/**
 * Tier 1 — PR Gate Smoke: Search
 *
 * Must pass on every PR. Verifies search endpoints respond.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Search', () => {
  test('search API endpoint responds', async ({ request }) => {
    const response = await request.get('/api/v1/search');
    expect([200, 401, 403, 404]).toContain(response.status());
  });
});
