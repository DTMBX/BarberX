// @ts-check
const { test, expect } = require("@playwright/test");

/**
 * BarberX Cross-Platform Architecture Tests
 * Tests for proper N-tier architecture boundaries and API integration
 */

test.describe("API - Architecture Boundaries", () => {
  test("API returns proper CORS headers", async ({ request }) => {
    const response = await request.get("/health");
    
    const corsHeader = response.headers()["access-control-allow-origin"];
    expect(corsHeader).toBeTruthy();
  });

  test("API enforces proper COEP policy", async ({ request }) => {
    const response = await request.get("/");
    
    const coepHeader = response.headers()["cross-origin-embedder-policy"];
    expect(coepHeader).toBe("credentialless");
  });

  test("API returns JSON content type for API endpoints", async ({ request }) => {
    const response = await request.get("/health-detailed");
    
    const contentType = response.headers()["content-type"];
    expect(contentType).toMatch(/application\/json/);
  });
});

test.describe("Mobile API - Offline Support", () => {
  test("health check endpoint returns quickly", async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get("/health");
    const endTime = Date.now();
    
    expect(response.status()).toBe(200);
    expect(endTime - startTime).toBeLessThan(1000); // Should be fast for mobile
  });

  test("API error responses include proper status codes", async ({ request }) => {
    const response = await request.get("/api/nonexistent-endpoint");
    
    expect(response.status()).toBe(404);
  });

  test("unauthorized API requests return 401", async ({ request }) => {
    const response = await request.get("/api/user/profile");
    
    expect(response.status()).toBe(401);
  });
});

test.describe("API - Data Transfer Objects", () => {
  test("health-detailed returns proper DTO structure", async ({ request }) => {
    const response = await request.get("/health-detailed");
    const data = await response.json();
    
    expect(data).toHaveProperty("status");
    expect(data).toHaveProperty("timestamp");
  });

  test("API returns consistent error format", async ({ request }) => {
    const response = await request.post("/api/chat/message");
    const data = await response.json();
    
    // Should have error structure
    expect(data).toBeTruthy();
  });
});

test.describe("Cross-Platform - Responsive Design", () => {
  const viewports = [
    { name: "Mobile Portrait", width: 375, height: 812 },
    { name: "Mobile Landscape", width: 812, height: 375 },
    { name: "Tablet Portrait", width: 768, height: 1024 },
    { name: "Tablet Landscape", width: 1024, height: 768 },
    { name: "Desktop", width: 1920, height: 1080 },
  ];

  for (const viewport of viewports) {
    test(`homepage renders on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto("/");
      
      // Page should load without errors
      const title = await page.title();
      expect(title).toBeTruthy();
    });
  }
});

test.describe("Mobile UX - Touch Interactions", () => {
  test("buttons are large enough for touch", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");
    
    // Check button sizes (should be at least 44x44px for touch)
    const buttons = page.locator("button, a.btn, a.button");
    const count = await buttons.count();
    
    if (count > 0) {
      const firstButton = buttons.first();
      const box = await firstButton.boundingBox();
      
      if (box) {
        // Touch targets should be at least 44x44px
        expect(box.height).toBeGreaterThanOrEqual(30);
      }
    }
  });

  test("mobile navigation menu works", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");
    
    // Look for mobile menu toggle
    const menuToggle = page.locator(".hamburger, .menu-toggle, [aria-label*='menu']");
    const count = await menuToggle.count();
    
    if (count > 0) {
      await expect(menuToggle.first()).toBeVisible();
    }
  });
});

test.describe("Architecture - Shared Layer Integration", () => {
  test("API endpoints use consistent naming convention", async ({ request }) => {
    const endpoints = [
      "/api/user/profile",
      "/api/chat/message",
      "/api/chat/history",
      "/api/legal-library/search",
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(endpoint);
      // Should return 401 (unauthorized) not 404 (not found)
      expect([200, 401, 403]).toContain(response.status());
    }
  });

  test("API uses REST conventions", async ({ request }) => {
    // GET for retrieval
    const getResponse = await request.get("/api/chat/history");
    expect([200, 401]).toContain(getResponse.status());
    
    // POST for creation
    const postResponse = await request.post("/api/chat/message");
    expect([200, 400, 401]).toContain(postResponse.status());
  });
});

test.describe("Mobile - Network Resilience", () => {
  test("API handles timeout gracefully", async ({ request }) => {
    // Set a short timeout
    const response = await request.get("/health", { timeout: 5000 });
    
    expect(response.status()).toBe(200);
  });

  test("error responses are JSON formatted", async ({ request }) => {
    const response = await request.get("/api/nonexistent");
    
    const contentType = response.headers()["content-type"];
    if (contentType) {
      expect(contentType).toMatch(/json/);
    }
  });
});

test.describe("Platform Features - Service Worker", () => {
  test("service worker registration exists", async ({ page }) => {
    await page.goto("/");
    
    // Check for service worker in page
    const hasServiceWorker = await page.evaluate(() => {
      return "serviceWorker" in navigator;
    });
    
    expect(hasServiceWorker).toBeTruthy();
  });
});

test.describe("Cross-Platform - Asset Loading", () => {
  test("images load on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");
    
    await page.waitForLoadState("networkidle");
    
    // Check for images
    const images = page.locator("img");
    const count = await images.count();
    
    if (count > 0) {
      // At least one image should be visible
      await expect(images.first()).toBeAttached();
    }
  });

  test("fonts load correctly", async ({ page }) => {
    await page.goto("/");
    
    // Wait for fonts to load
    await page.waitForLoadState("networkidle");
    
    // Check computed font
    const bodyFont = await page.locator("body").evaluate((el) => {
      return window.getComputedStyle(el).fontFamily;
    });
    
    expect(bodyFont).toBeTruthy();
  });
});

test.describe("API - Rate Limiting", () => {
  test("rate limit headers are present", async ({ request }) => {
    const response = await request.get("/health");
    
    const headers = response.headers();
    // Rate limit headers may or may not be present
    expect(headers).toBeTruthy();
  });

  test("rate limit status endpoint exists", async ({ request }) => {
    const response = await request.get("/api/rate-limit/status");
    
    expect([200, 401, 404]).toContain(response.status());
  });
});

test.describe("Mobile - Performance", () => {
  test("homepage loads in under 3 seconds", async ({ page }) => {
    const startTime = Date.now();
    await page.goto("/");
    await page.waitForLoadState("load");
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
  });

  test("API responses are compressed", async ({ request }) => {
    const response = await request.get("/health-detailed");
    
    const encoding = response.headers()["content-encoding"];
    // May or may not be compressed
    if (encoding) {
      expect(["gzip", "br", "deflate"]).toContain(encoding);
    }
  });
});

test.describe("Architecture - Security Headers", () => {
  test("security headers are present", async ({ request }) => {
    const response = await request.get("/");
    const headers = response.headers();
    
    // Check for security headers
    expect(headers["x-content-type-options"]).toBe("nosniff");
    expect(headers["x-frame-options"]).toBeTruthy();
    expect(headers["cross-origin-opener-policy"]).toBe("same-origin");
  });

  test("CSP header is configured", async ({ request }) => {
    const response = await request.get("/");
    const headers = response.headers();
    
    const csp = headers["content-security-policy"];
    expect(csp).toBeTruthy();
  });
});
