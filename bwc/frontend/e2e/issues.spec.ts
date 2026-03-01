/**
 * Issues: create issue, verify in list, status/confidence badges.
 */
import { test, expect } from './fixtures';

test.describe('Issues', () => {
  test('create an issue via the form', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-issues').click();
    await expect(page.getByTestId('case-detail-issues-section')).toBeVisible();

    // Open the new issue form
    await page.getByTestId('issues-new-btn').click();

    // Fill issue form
    await page.getByTestId('issue-title-input').fill('Broken chain of custody');
    await page.getByTestId('issue-description-input').fill('Evidence bag seal was compromised');
    await page.getByTestId('issue-submit-btn').click();

    // Issue should appear in the list
    await expect(page.getByText('Broken chain of custody')).toBeVisible({ timeout: 10_000 });
  });

  test('issue list shows status badge', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-issues').click();

    // Open the new issue form
    await page.getByTestId('issues-new-btn').click();

    // Create an issue first
    await page.getByTestId('issue-title-input').fill('Status badge test');
    await page.getByTestId('issue-description-input').fill('Testing status badge rendering');
    await page.getByTestId('issue-submit-btn').click();

    await expect(page.getByText('Status badge test')).toBeVisible({ timeout: 10_000 });
    // Status badge should be present (open, in_progress, etc.)
    await expect(page.getByText('open').or(page.getByText('Open')).first()).toBeVisible();
  });

  test('issue list shows confidence badge when present', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-issues').click();

    // Open the new issue form first
    await page.getByTestId('issues-new-btn').click();

    // If there's a confidence selector, use it
    const confidenceSelect = page.getByTestId('issue-confidence-select');
    if (await confidenceSelect.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await page.getByTestId('issue-title-input').fill('Confidence test');
      await page.getByTestId('issue-description-input').fill('Testing confidence');
      await confidenceSelect.selectOption('high');
      await page.getByTestId('issue-submit-btn').click();
      await expect(page.getByText('high').or(page.getByText('High'))).toBeVisible({
        timeout: 10_000,
      });
    }
  });

  test('issues tab is accessible via keyboard', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    const tab = page.getByTestId('case-detail-tab-issues');
    await tab.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByTestId('case-detail-issues-section')).toBeVisible();
  });
});
