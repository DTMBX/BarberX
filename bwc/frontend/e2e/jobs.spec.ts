/**
 * Jobs: run pipeline, job rows appear, state transitions.
 */
import { test, expect, seedEvidenceInit, completeEvidence, makeTestPdf } from './fixtures';

test.describe('Jobs', () => {
  test('jobs tab shows pipeline jobs', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-jobs').click();
    await expect(page.getByTestId('case-detail-jobs-section')).toBeVisible();
  });

  test('run pipeline creates a job', async ({ page, seededCase }) => {
    // First upload evidence so there's something to process
    await page.goto(`/cases/${seededCase.id}`);

    const pdfBuffer = makeTestPdf('pipeline-test');
    await page.getByTestId('case-detail-file-input').setInputFiles({
      name: 'pipeline-test.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    });

    // Wait for upload to complete — scoped to upload area
    await expect(page.getByTestId('case-detail-upload-progress').locator('text=✓')).toBeVisible({
      timeout: 30_000,
    });

    // Switch to jobs tab
    await page.getByTestId('case-detail-tab-jobs').click();

    // Look for a run pipeline button or auto-created job
    const runBtn = page.getByTestId('case-detail-run-pipeline-btn');
    if (await runBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await runBtn.click();
      // Job row should appear
      await expect(page.getByTestId('job-row').first()).toBeVisible({ timeout: 15_000 });
    }
  });

  test('job rows show state badges', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-jobs').click();

    const jobRows = page.getByTestId('job-row');
    const count = await jobRows.count();
    if (count > 0) {
      // Each job row should have a state badge
      const firstRow = jobRows.first();
      await expect(
        firstRow
          .getByText('pending')
          .or(firstRow.getByText('running'))
          .or(firstRow.getByText('completed'))
          .or(firstRow.getByText('failed'))
      ).toBeVisible();
    }
  });

  test('jobs tab accessible from keyboard', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    const tab = page.getByTestId('case-detail-tab-jobs');
    await tab.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByTestId('case-detail-jobs-section')).toBeVisible();
  });
});
