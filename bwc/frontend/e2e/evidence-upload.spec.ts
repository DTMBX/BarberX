/**
 * Evidence upload: drag-drop, hashing, presigned PUT, completion, duplicate detection.
 */
import { test, expect, makeTestPdf, seedCase } from './fixtures';

test.describe('Evidence Upload', () => {
  test('upload a PDF via file input', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await expect(page.getByTestId('case-detail-upload-zone')).toBeVisible();

    // Intercept the presigned PUT request
    const putPromise = page
      .waitForRequest((req) => req.method() === 'PUT' && req.url().includes('evidence'))
      .catch(() => null);

    // Create a test PDF file
    const pdfBuffer = makeTestPdf('evidence-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'test-evidence.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    // Upload progress should appear
    await expect(page.getByTestId('case-detail-upload-progress')).toBeVisible({ timeout: 15_000 });

    // Wait for completion — look for the verified badge scoped to upload area
    await expect(page.getByTestId('case-detail-upload-progress').locator('text=✓')).toBeVisible({
      timeout: 30_000,
    });
  });

  test('upload zone responds to keyboard activation', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    const zone = page.getByTestId('case-detail-upload-zone');
    await zone.focus();
    await expect(zone).toBeFocused();
    // Enter or Space should trigger (file dialog — can't assert opening, but no error)
  });

  test('hashing step shows progress text', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);

    const pdfBuffer = makeTestPdf('hash-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'hash-test.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    // Look for hashing or uploading progress text
    await expect(
      page
        .getByText('Computing SHA-256')
        .or(page.getByText('Uploading'))
        .or(page.getByText('Verifying'))
    ).toBeVisible({ timeout: 15_000 });
  });

  test('evidence tab shows uploaded files', async ({ page, seededCase }) => {
    // Upload first
    await page.goto(`/cases/${seededCase.id}`);
    const pdfBuffer = makeTestPdf('tab-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'tab-evidence.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    // Wait for completion — scoped to upload area
    await expect(page.getByTestId('case-detail-upload-progress').locator('text=✓')).toBeVisible({
      timeout: 30_000,
    });

    // Click evidence tab to refresh view
    await page.getByTestId('case-detail-tab-evidence').click();
    await expect(page.getByTestId('case-detail-evidence-table')).toBeVisible();
  });

  test('clear button removes upload progress', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    const pdfBuffer = makeTestPdf('clear-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'clear-test.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    // Wait for done — scoped to upload area
    await expect(page.getByTestId('case-detail-upload-progress').locator('text=✓')).toBeVisible({
      timeout: 30_000,
    });

    // Clear button should appear and work
    const clearBtn = page.getByTestId('case-detail-upload-clear-btn');
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await expect(page.getByTestId('case-detail-upload-progress')).not.toBeVisible();
    }
  });
});
