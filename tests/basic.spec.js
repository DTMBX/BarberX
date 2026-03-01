// Basic Playwright test — verifies homepage loads with correct title
import { test, expect } from '@playwright/test';

test('homepage has correct title', async ({ page }) => {
  await page.goto('/'); // baseURL is set in Playwright config
  await expect(page).toHaveTitle(/Evident|Tillerstead|Home/i);
});
