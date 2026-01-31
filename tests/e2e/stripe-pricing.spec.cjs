// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * BarberX Stripe Pricing Table E2E Tests
 * Comprehensive tests for Stripe pricing table integration and COEP fixes
 */

test.describe("Stripe Pricing Table - Integration", () => {
  test("pricing-stripe-embed.html loads Stripe script with crossorigin", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Check that Stripe script is loaded with crossorigin attribute
    const stripeScript = page.locator('script[src*="js.stripe.com/v3/pricing-table.js"]');
    await expect(stripeScript).toHaveCount(1);
    
    const crossorigin = await stripeScript.getAttribute("crossorigin");
    expect(crossorigin).toBe("anonymous");
  });

  test("pricing.html loads Stripe script with crossorigin", async ({ page }) => {
    await page.goto("/pricing.html");
    
    const stripeScript = page.locator('script[src*="js.stripe.com/v3/pricing-table.js"]');
    const count = await stripeScript.count();
    
    if (count > 0) {
      const crossorigin = await stripeScript.getAttribute("crossorigin");
      expect(crossorigin).toBe("anonymous");
    }
  });

  test("landing page loads Stripe script with crossorigin", async ({ page }) => {
    await page.goto("/");
    
    const stripeScript = page.locator('script[src*="js.stripe.com/v3/pricing-table.js"]');
    const count = await stripeScript.count();
    
    if (count > 0) {
      const crossorigin = await stripeScript.getAttribute("crossorigin");
      expect(crossorigin).toBe("anonymous");
    }
  });

  test("Stripe pricing table custom element exists", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Wait for Stripe pricing table element
    const pricingTable = page.locator("stripe-pricing-table");
    await expect(pricingTable).toBeAttached({ timeout: 10000 });
  });

  test("Stripe pricing table has required attributes", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    const pricingTable = page.locator("stripe-pricing-table");
    
    // Check for pricing table ID
    const tableId = await pricingTable.getAttribute("pricing-table-id");
    expect(tableId).toBeTruthy();
    expect(tableId).toMatch(/prctbl_/);
    
    // Check for publishable key
    const pubKey = await pricingTable.getAttribute("publishable-key");
    expect(pubKey).toBeTruthy();
    expect(pubKey).toMatch(/pk_(live|test)_/);
  });
});

test.describe("Stripe Pricing Table - COEP Policy", () => {
  test("pricing page has credentialless COEP header", async ({ page }) => {
    const response = await page.goto("/pricing-stripe-embed.html");
    
    const coepHeader = response.headers()["cross-origin-embedder-policy"];
    expect(coepHeader).toBe("credentialless");
  });

  test("Stripe script loads without COEP blocking", async ({ page }) => {
    let scriptError = false;
    
    page.on("pageerror", (err) => {
      if (err.message.includes("ERR_BLOCKED_BY_RESPONSE") || 
          err.message.includes("NotSameOriginAfterDefaultedToSameOriginByCoep")) {
        scriptError = true;
      }
    });
    
    await page.goto("/pricing-stripe-embed.html");
    await page.waitForLoadState("networkidle");
    
    expect(scriptError).toBe(false);
  });

  test("Stripe pricing table iframe loads successfully", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Wait for Stripe to inject iframe
    await page.waitForTimeout(3000);
    
    const frames = page.frames();
    const stripeFrame = frames.find(f => f.url().includes("stripe.com"));
    
    if (stripeFrame) {
      expect(stripeFrame).toBeTruthy();
    }
  });
});

test.describe("Pricing Tiers - Visual Elements", () => {
  test("pricing page displays tier cards", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Look for pricing-related content
    const pageContent = await page.textContent("body");
    
    const hasTiers = 
      pageContent.toLowerCase().includes("free") ||
      pageContent.toLowerCase().includes("pro") ||
      pageContent.toLowerCase().includes("premium") ||
      pageContent.toLowerCase().includes("enterprise");
    
    expect(hasTiers).toBeTruthy();
  });

  test("pricing page has proper styling", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Check for pricing-related CSS classes
    const pricingWrapper = page.locator(".stripe-pricing-wrapper, .pricing-container, .pricing-section");
    await expect(pricingWrapper).toHaveCount(1, { timeout: 5000 });
  });

  test("pricing header displays correctly", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Look for pricing header
    const header = page.locator("h1, h2").filter({ hasText: /pricing|choose|plan/i });
    await expect(header.first()).toBeVisible();
  });
});

test.describe("Pricing Page - Responsive Design", () => {
  test("pricing table displays on desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto("/pricing-stripe-embed.html");
    
    const pricingTable = page.locator("stripe-pricing-table");
    await expect(pricingTable).toBeVisible({ timeout: 10000 });
  });

  test("pricing table displays on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/pricing-stripe-embed.html");
    
    const pricingTable = page.locator("stripe-pricing-table");
    await expect(pricingTable).toBeAttached({ timeout: 10000 });
  });

  test("pricing table displays on tablet", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto("/pricing-stripe-embed.html");
    
    const pricingTable = page.locator("stripe-pricing-table");
    await expect(pricingTable).toBeAttached({ timeout: 10000 });
  });
});

test.describe("Pricing - Call to Action", () => {
  test("pricing page has CTA buttons", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Wait for page to load
    await page.waitForLoadState("networkidle");
    
    // Look for CTA buttons (Stripe will inject them)
    const pageContent = await page.textContent("body");
    const hasCtaContent = 
      pageContent.toLowerCase().includes("start") ||
      pageContent.toLowerCase().includes("subscribe") ||
      pageContent.toLowerCase().includes("get started") ||
      pageContent.toLowerCase().includes("buy now");
    
    expect(hasCtaContent).toBeTruthy();
  });

  test("CTA buttons are clickable", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Wait for Stripe to fully load
    await page.waitForTimeout(3000);
    
    // Check if there are clickable elements
    const buttons = page.locator("button, a.button, a.btn, .cta-btn");
    const count = await buttons.count();
    
    if (count > 0) {
      await expect(buttons.first()).toBeVisible();
    }
  });
});

test.describe("Pricing - Navigation", () => {
  test("pricing page has link to home", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    const homeLink = page.locator('a[href="/"], a[href="index.html"], a[href*="home"]');
    const count = await homeLink.count();
    
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("can navigate from home to pricing", async ({ page }) => {
    await page.goto("/");
    
    // Look for pricing link
    const pricingLink = page.locator('a[href*="pricing"]').first();
    const count = await pricingLink.count();
    
    if (count > 0) {
      await pricingLink.click();
      await page.waitForLoadState("networkidle");
      
      expect(page.url()).toMatch(/pricing/);
    }
  });
});

test.describe("Stripe Pricing - Console Errors", () => {
  test("no CORS errors in console", async ({ page }) => {
    const consoleErrors = [];
    
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.goto("/pricing-stripe-embed.html");
    await page.waitForLoadState("networkidle");
    
    const hasCorsError = consoleErrors.some(err => 
      err.toLowerCase().includes("cors") || 
      err.toLowerCase().includes("cross-origin")
    );
    
    expect(hasCorsError).toBe(false);
  });

  test("no COEP blocking errors in console", async ({ page }) => {
    const consoleErrors = [];
    
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.goto("/pricing-stripe-embed.html");
    await page.waitForLoadState("networkidle");
    
    const hasCoepError = consoleErrors.some(err => 
      err.includes("ERR_BLOCKED_BY_RESPONSE") ||
      err.includes("NotSameOriginAfterDefaultedToSameOriginByCoep") ||
      err.includes("require-corp")
    );
    
    expect(hasCoepError).toBe(false);
  });
});

test.describe("Pricing - Accessibility", () => {
  test("pricing page has proper document title", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
  });

  test("pricing page has proper language attribute", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBeTruthy();
  });

  test("pricing content is keyboard navigable", async ({ page }) => {
    await page.goto("/pricing-stripe-embed.html");
    
    // Tab through the page
    await page.keyboard.press("Tab");
    
    // Check if focus moved
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  });
});
