import { defineConfig, devices } from '@playwright/test';

const SAFE_MODE = process.env.SAFE_MODE === '1' || process.env.SAFE_MODE === 'true';

export default defineConfig({
  testDir: './e2e',
  outputDir: './e2e-results',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,
  reporter: [['html', { open: 'never', outputFolder: 'playwright-report' }], ['list']],
  timeout: 60_000,
  expect: { timeout: 15_000 },

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    // SAFE_MODE: no traces/videos/screenshots by default to protect evidence
    trace: SAFE_MODE ? 'off' : 'on-first-retry',
    video: SAFE_MODE ? 'off' : 'retain-on-failure',
    screenshot: SAFE_MODE ? 'off' : 'only-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 45_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Optional: enable for cross-browser coverage
    // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    // { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  webServer: {
    command: 'pnpm dev',
    port: 3000,
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
    stdout: 'pipe',
    // Do NOT set NEXT_PUBLIC_API_URL — let the frontend use '/api' proxy
    // so browser requests stay same-origin (no CORS).
  },
});
