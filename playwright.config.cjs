// @ts-check
const { defineConfig, devices } = require("@playwright/test");

/**
 * Playwright Configuration for Evident Legal Tech
 * Tests all features and tier-based access levels
 */
module.exports = defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/*.spec.cjs",

  /* Run tests in files in parallel */
  fullyParallel: false, // Sequential for auth tests

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Output folder */
  outputDir: "playwright-results",

  /* Reporter to use */
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "playwright-results/results.json" }],
    ["list"],
  ],

  /* Shared settings for all the projects below */
  use: {
    /* Base URL for tests */
    baseURL: "http://localhost:5000",

    /* Collect trace on failure */
    trace: "on-first-retry",

    /* Screenshot on failure */
    screenshot: "only-on-failure",

    /* Video on failure */
    video: "retain-on-failure",

    /* Timeout for each action */
    actionTimeout: 15000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    // Uncomment for cross-browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  /* Run local dev server before starting tests */
  webServer: {
    command: "python app.py",
    url: "http://localhost:5000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    stdout: "pipe",
    stderr: "pipe",
  },

  /* Global timeout */
  timeout: 60 * 1000,
});
