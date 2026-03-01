/**
 * Case lifecycle: create → list → view detail.
 */
import { test, expect, seedCase } from './fixtures';

test.describe('Cases', () => {
  test('create a new case via UI', async ({ page }) => {
    await page.goto('/cases/new');
    await expect(page.getByTestId('new-case-form')).toBeVisible();

    await page.getByTestId('new-case-title-input').fill('E2E Test Case');
    await page.getByTestId('new-case-created-by-input').fill('playwright');
    await page.getByTestId('new-case-submit-btn').click();

    // Should redirect to the case detail page
    await expect(page).toHaveURL(/\/cases\/[a-f0-9-]+/);
    await expect(page.getByTestId('case-detail-header')).toBeVisible();
  });

  test('cases list shows created case', async ({ page, seededCase }) => {
    await page.goto('/cases');
    await expect(page.getByTestId('cases-table')).toBeVisible();
    // The seeded case title should appear in the table
    await expect(page.getByText(seededCase.title)).toBeVisible();
  });

  test('empty state shows create button', async ({ page }) => {
    // Navigate to cases — if empty, the empty state should show
    await page.goto('/cases');
    const table = page.getByTestId('cases-table');
    const emptyBtn = page.getByTestId('cases-empty-create-btn');
    // One of them should be visible
    await expect(table.or(emptyBtn)).toBeVisible();
  });

  test('click New Case button navigates to form', async ({ page }) => {
    await page.goto('/cases');
    await page.getByTestId('cases-new-btn').click();
    await expect(page).toHaveURL('/cases/new');
    await expect(page.getByTestId('new-case-form')).toBeVisible();
  });

  test('case detail renders all tabs', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await expect(page.getByTestId('case-detail-header')).toBeVisible();

    for (const tabId of ['evidence', 'artifacts', 'timeline', 'issues', 'jobs', 'exports']) {
      await expect(page.getByTestId(`case-detail-tab-${tabId}`)).toBeVisible();
    }
  });

  test('cancel button on new case navigates back', async ({ page }) => {
    await page.goto('/cases/new');
    await page.getByTestId('new-case-cancel-btn').click();
    await expect(page).not.toHaveURL('/cases/new');
  });
});
