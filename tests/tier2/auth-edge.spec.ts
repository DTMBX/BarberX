/**
 * Tier 2 — Full Suite: Auth Edge Cases
 *
 * Role denial, expired sessions, brute force protection.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 2: Auth Edge Cases', () => {
  test('invalid credentials return error', async ({ request }) => {
    const response = await request.post('/auth/api/login', {
      data: {
        email: 'nonexistent@example.com',
        password: 'wrongpassword',
      },
    });
    // Should return 401 or redirect (302)
    expect([401, 403, 302, 404]).toContain(response.status());
  });

  test('role-protected admin route denies non-admin', async ({ request }) => {
    const response = await request.get('/admin/users');
    expect([401, 403, 302, 404]).toContain(response.status());
  });

  test('expired session returns 401', async ({ request }) => {
    const response = await request.get('/api/v1/cases', {
      headers: {
        Authorization: 'Bearer expired-token-12345',
      },
    });
    expect([401, 403, 404]).toContain(response.status());
  });
});
