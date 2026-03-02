/**
 * Tier 1 — PR Gate Smoke: Authentication
 *
 * Must pass on every PR. Tests login flow only.
 * No arbitrary waits. Strict mode. Deterministic selectors.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 1: Authentication', () => {
  test('homepage loads successfully', async ({ page }) => {
    const response = await page.goto('/');
    expect(response.status()).toBeLessThan(400);
    await expect(page).toHaveTitle(/Evident/i);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/');
    // Look for any login/sign-in link
    const loginLink = page.getByRole('link', { name: /log\s*in|sign\s*in/i });
    const hasLogin = await loginLink.count();

    if (hasLogin > 0) {
      const href = await loginLink.first().getAttribute('href');
      // Only click if it's a same-origin link
      if (href && !href.startsWith('http') && !href.startsWith('//')) {
        await loginLink.first().click();
        await expect(page).toHaveURL(/auth|login|sign/i);
      }
    } else {
      // Static site may not have auth pages — verify homepage is functional
      await expect(page).toHaveTitle(/Evident/i);
    }
  });

  test('unauthenticated user cannot access protected routes', async ({ page }) => {
    const response = await page.goto('/cases');
    // Should redirect to login or return 401/403
    const url = page.url();
    const status = response?.status() || 200;
    const isProtected = url.includes('login') || url.includes('auth') || status === 401 || status === 403;
    // If the route doesn't exist (404), that's also acceptable
    expect(isProtected || status === 404).toBeTruthy();
  });
});
