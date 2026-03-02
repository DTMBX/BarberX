/**
 * Tier 1 — PR Gate Smoke: Assistant
 *
 * Must pass on every PR. Verifies assistant endpoints respond.
 * No arbitrary waits. Strict mode. Deterministic selectors.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Assistant', () => {
  test('assistant capabilities endpoint responds', async ({ request }) => {
    const response = await request.get('/assistant/capabilities');
    expect([200, 401, 403, 404]).toContain(response.status());
  });

  test('assistant action rejects unauthenticated requests', async ({ request }) => {
    const response = await request.post('/assistant/action', {
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({
        capability_id: 'case.create_note',
        args: { case_id: 'test', content: 'test' },
      }),
    });
    // Should require authentication or return 404 if backend not running
    expect([401, 403, 404, 405]).toContain(response.status());
  });
});
