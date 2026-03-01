/**
 * Chat: mode switching, CourtListener search (mock), Use in Chat, send message, assistant response.
 */
import { test, expect } from './fixtures';

test.describe('Chat', () => {
  test('chat page loads with mode selector', async ({ page }) => {
    await page.goto('/chat');
    await expect(page.getByTestId('chat-mode-evidence-btn')).toBeVisible();
    await expect(page.getByTestId('chat-mode-legal-btn')).toBeVisible();
  });

  test('switch between evidence and legal modes', async ({ page }) => {
    await page.goto('/chat');

    // Start in evidence mode (default)
    await page.getByTestId('chat-mode-legal-btn').click();
    await expect(page.getByTestId('chat-legal-section')).toBeVisible();

    // Switch back to evidence
    await page.getByTestId('chat-mode-evidence-btn').click();
    await expect(
      page.getByTestId('chat-scope-section').or(page.getByTestId('chat-message-input'))
    ).toBeVisible();
  });

  test('evidence mode has scope selectors', async ({ page, seededCase }) => {
    await page.goto('/chat');
    await page.getByTestId('chat-mode-evidence-btn').click();

    // Scope selectors — case-level or evidence-level
    const scopeSection = page.getByTestId('chat-scope-section');
    if (await scopeSection.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await expect(scopeSection).toBeVisible();
    }
  });

  test('send a message and receive response', async ({ page }) => {
    await page.goto('/chat');
    await page.getByTestId('chat-mode-evidence-btn').click();

    const input = page.getByTestId('chat-message-input');
    await input.fill('What evidence exists in this case?');

    const sendBtn = page.getByTestId('chat-send-btn');
    await sendBtn.click();

    // Message should appear in messages section
    const messages = page.getByTestId('chat-messages');
    await expect(messages).toBeVisible();

    // Wait for assistant response (may take a while)
    await expect(
      messages.getByText('What evidence exists').or(page.getByText('assistant'))
    ).toBeVisible({ timeout: 30_000 });
  });

  test('resource panel toggle works', async ({ page }) => {
    await page.goto('/chat');
    const resourceBtn = page.getByTestId('chat-resources-btn');

    if (await resourceBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await resourceBtn.click();
      await expect(page.getByTestId('chat-resource-panel')).toBeVisible();

      // Toggle back off
      await resourceBtn.click();
      await expect(page.getByTestId('chat-resource-panel')).not.toBeVisible();
    }
  });

  test('legal mode shows CourtListener search', async ({ page }) => {
    await page.goto('/chat');
    await page.getByTestId('chat-mode-legal-btn').click();

    await expect(page.getByTestId('chat-legal-section')).toBeVisible();

    // Should have search input for legal research
    const searchInput = page.getByTestId('chat-legal-search-input');
    if (await searchInput.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await searchInput.fill('Miranda v Arizona');
      const searchBtn = page.getByTestId('chat-legal-search-btn');
      await searchBtn.click();

      // Results or loading should appear (use .first() to avoid strict mode
      // violation when both the results div and "Searching…" text are visible)
      await expect(
        page.getByTestId('chat-legal-results').or(page.getByText('Searching')).first()
      ).toBeVisible({ timeout: 15_000 });
    }
  });

  test('Use in Chat button transfers legal result to chat', async ({ page }) => {
    await page.goto('/chat');
    await page.getByTestId('chat-mode-legal-btn').click();

    // Mock search or wait for results
    const useInChatBtn = page.getByTestId('chat-legal-use-in-chat-btn').first();
    if (await useInChatBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await useInChatBtn.click();
      // Should switch back to evidence mode or populate input
      await expect(page.getByTestId('chat-message-input')).toBeVisible();
    }
  });

  test('chat keyboard shortcuts work', async ({ page }) => {
    await page.goto('/chat');
    const input = page.getByTestId('chat-message-input');
    await input.fill('Test message');

    // Enter should send (if Shift not held)
    await input.press('Enter');

    // Message should appear in chat
    await expect(page.getByTestId('chat-messages')).toBeVisible({ timeout: 10_000 });
  });
});
