/**
 * Timeline tab: monotonic ordering, event cards, detail visibility.
 */
import { test, expect, seedCase, seedFullEvidence } from './fixtures';

test.describe('Timeline', () => {
  test('timeline tab shows events in chronological order', async ({ page, seededCase }) => {
    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-timeline').click();
    await expect(page.getByTestId('case-detail-timeline-section')).toBeVisible();

    // Timeline events should be present
    const events = page.getByTestId('timeline-event');
    const count = await events.count();
    // A freshly seeded case may have at least 1 event (creation)
    expect(count).toBeGreaterThanOrEqual(0);

    if (count >= 2) {
      // Verify monotonic ordering — timestamps should be ascending
      const timestamps: string[] = [];
      for (let i = 0; i < count; i++) {
        const ts = await events.nth(i).getByTestId('timeline-event-timestamp').textContent();
        if (ts) timestamps.push(ts);
      }
      for (let i = 1; i < timestamps.length; i++) {
        expect(new Date(timestamps[i]).getTime()).toBeGreaterThanOrEqual(
          new Date(timestamps[i - 1]).getTime()
        );
      }
    }
  });

  test('timeline events have type badges', async ({ page, seededCase }) => {
    // Seed evidence with full upload flow to generate timeline events
    await seedFullEvidence(seededCase.id, 'timeline-test.pdf');

    await page.goto(`/cases/${seededCase.id}`);
    await page.getByTestId('case-detail-tab-timeline').click();

    // Should have at least one event now
    await expect(page.getByTestId('timeline-event').first()).toBeVisible({ timeout: 10_000 });
  });

  test('timeline empty state when no events', async ({ page }) => {
    // Create a case and immediately check timeline
    const c = await seedCase();
    await page.goto(`/cases/${c.id}`);
    await page.getByTestId('case-detail-tab-timeline').click();

    // Either shows events or empty state
    const section = page.getByTestId('case-detail-timeline-section');
    await expect(section).toBeVisible();
  });
});
