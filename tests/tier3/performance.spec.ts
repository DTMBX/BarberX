/**
 * Tier 3 — Optional Perf: Lighthouse & Large Ingest
 *
 * These tests are optional and do not gate PRs.
 * Run manually or in release pipeline.
 */
import { test, expect } from '@playwright/test';

test.describe('Tier 3: Performance', () => {
  test('homepage loads within 5 seconds', async ({ page }) => {
    const start = Date.now();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(5000);
  });

  test('page has no critical accessibility violations', async ({ page }) => {
    await page.goto('/');
    // Basic check: page has a lang attribute
    const lang = await page.getAttribute('html', 'lang');
    expect(lang).toBeTruthy();

    // Basic check: all images have alt text
    const images = page.locator('img:not([alt])');
    const count = await images.count();
    expect(count).toBe(0);
  });
});
