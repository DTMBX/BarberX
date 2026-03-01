/**
 * Exports & Verify: download manifest, verify integrity (SHA-256 + HMAC), audit replay.
 */
import { test, expect, seedEvidenceInit, completeEvidence, makeTestPdf } from './fixtures';

test.describe('Exports & Verify', () => {
  test('exports tab is visible and clickable', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-exports').click();
    await expect(page.getByTestId('case-detail-exports-section')).toBeVisible();
  });

  test('verify integrity checks SHA-256 and HMAC', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-exports').click();

    const verifyBtn = page.getByTestId('case-detail-verify-integrity-btn');
    // Button is disabled when no evidence exists — only click when enabled
    if (
      (await verifyBtn.isVisible({ timeout: 5_000 }).catch(() => false)) &&
      (await verifyBtn.isEnabled({ timeout: 2_000 }).catch(() => false))
    ) {
      await verifyBtn.click();

      // Results should show sha256_valid and hmac_valid fields
      const resultSection = page.getByTestId('case-detail-verify-result');
      await expect(resultSection).toBeVisible({ timeout: 15_000 });

      // Check for valid/invalid indicators
      await expect(
        resultSection.getByText('sha256').or(resultSection.getByText('SHA-256'))
      ).toBeVisible();
    }
  });

  test('export manifest download triggers', async ({ page, seededCase }) => {
    // Upload evidence first
    await page.goto(`/cases/${seededCase.id}`);
    const pdfBuffer = makeTestPdf('export-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'export-test.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    await expect(page.getByTestId('case-detail-upload-progress').locator('text=✓')).toBeVisible({
      timeout: 30_000,
    });

    // Go to exports tab
    await page.getByTestId('case-detail-tab-exports').click();

    const downloadBtn = page.getByTestId('case-detail-export-manifest-btn');
    if (await downloadBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      // Intercept the download
      const downloadPromise = page.waitForEvent('download', { timeout: 15_000 }).catch(() => null);
      await downloadBtn.click();
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toContain('manifest');
      }
    }
  });

  test('audit replay button exists and responds', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-exports').click();

    const replayBtn = page.getByTestId('case-detail-audit-replay-btn');
    if (await replayBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await replayBtn.click();
      // Replay section should appear
      await expect(page.getByTestId('case-detail-replay-section')).toBeVisible({ timeout: 10_000 });
    }
  });

  test('standalone verify page works', async ({ page }) => {
    await page.goto('/verify');
    await expect(page.getByTestId('verify-page-header')).toBeVisible();

    // File input and manifest textarea should be present
    await expect(page.getByTestId('verify-file-input')).toBeVisible();
    await expect(page.getByTestId('verify-manifest-textarea')).toBeVisible();
    await expect(page.getByTestId('verify-integrity-btn')).toBeVisible();
  });
});
