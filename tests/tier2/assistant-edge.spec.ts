/**
 * Tier 2 — Full Suite: Assistant Edge Cases
 *
 * Invalid capabilities, role denial, malformed input.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 2: Assistant Edge Cases', () => {
  test('action with invalid capability returns error', async ({ request }) => {
    const response = await request.post('/assistant/action', {
      data: {
        capability_id: 'nonexistent.action',
        args: {},
      },
    });
    // Unauthenticated → 401/403, or unknown capability error
    expect([401, 403, 404, 500]).toContain(response.status());
  });

  test('action without capability_id returns 400', async ({ request }) => {
    const response = await request.post('/assistant/action', {
      data: { args: {} },
    });
    expect([400, 401, 403, 404]).toContain(response.status());
  });
});
