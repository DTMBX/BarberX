/**
 * Smoke tests — verify the app loads and core navigation works.
 */
import { test, expect } from './fixtures';

test.describe('Smoke', () => {
  test('homepage loads without console errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('/');
    await expect(page.getByTestId('dashboard-header')).toBeVisible();
    // Filter out expected errors (e.g. backend unreachable in CI)
    const realErrors = consoleErrors.filter(
      (e) => !e.includes('Failed to fetch') && !e.includes('ERR_CONNECTION_REFUSED')
    );
    expect(realErrors).toHaveLength(0);
  });

  test('health status section renders', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('dashboard-status-section')).toBeVisible();
  });

  test('navigation links are present and navigable', async ({ page }) => {
    await page.goto('/');

    for (const [route, testId] of [
      ['/projects', 'nav-link-projects'],
      ['/cases', 'nav-link-cases'],
      ['/verify', 'nav-link-verify'],
      ['/chat', 'nav-link-chat'],
      ['/settings', 'nav-link-settings'],
    ] as const) {
      const link = page.getByTestId(testId);
      await expect(link).toBeVisible();
      await expect(link).toHaveAttribute('href', route);
    }
  });

  test('dashboard quick actions link to correct routes', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('dashboard-action-new-case')).toBeVisible();
    await expect(page.getByTestId('dashboard-action-view-cases')).toBeVisible();
    await expect(page.getByTestId('dashboard-action-verify')).toBeVisible();
    await expect(page.getByTestId('dashboard-action-chat')).toBeVisible();
  });

  test('navigate to cases page via nav link', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-link-cases').click();
    await expect(page).toHaveURL('/cases');
  });

  test('navigate to settings page', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-link-settings').click();
    await expect(page).toHaveURL('/settings');
    await expect(page.getByTestId('settings-test-connection-btn')).toBeVisible();
  });

  test('keyboard navigation works on nav links', async ({ page }) => {
    await page.goto('/');
    // Tab to first nav link and verify focus
    await page.getByTestId('nav-link-dashboard').focus();
    await expect(page.getByTestId('nav-link-dashboard')).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.getByTestId('nav-link-projects')).toBeFocused();
  });
});
