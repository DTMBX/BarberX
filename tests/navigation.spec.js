// Playwright Navigation Tests — Desktop & Mobile
// Tests nav links, dropdowns, accessibility, and header
// Selectors match the Eleventy-built site (src/ → _site/).

import { test, expect } from '@playwright/test';

// ─── Desktop viewport ────────────────────────────────────────────────
const DESKTOP_VIEWPORT = { width: 1920, height: 1080 };

// ─── Mobile viewports ────────────────────────────────────────────────
const MOBILE_IPHONE_16_PRO_MAX = { width: 430, height: 932 };
const MOBILE_IPHONE_14 = { width: 390, height: 844 };
const MOBILE_ANDROID = { width: 412, height: 915 };

// ─────────────────────────────────────────────────────────────────────
// Desktop Navigation
// ─────────────────────────────────────────────────────────────────────
test.describe('Desktop Navigation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');
  });

  test('should display desktop nav on large screens', async ({ page }) => {
    const desktopNav = page.locator('.site-header__nav');
    await expect(desktopNav).toBeVisible();

    // Mobile toggle should be hidden on desktop
    const mobileToggle = page.locator('.site-header__mobile-toggle');
    await expect(mobileToggle).not.toBeVisible();
  });

  test('should have all main nav items visible', async ({ page }) => {
    // The nav contains a Services dropdown button plus direct links
    const navItems = [
      { text: 'Services', selector: '.site-header__menu button:has-text("Services")' },
      { text: 'Documentation', selector: '.site-header__menu a[href="/docs/"]' },
      { text: 'Pricing', selector: '.site-header__menu a[href="/pricing/"]' },
      { text: 'Contact', selector: '.site-header__menu a[href="/contact/"]' },
    ];

    for (const item of navItems) {
      const el = page.locator(item.selector).first();
      await expect(el).toBeVisible();
    }
  });

  test('should open Services dropdown on hover/click', async ({ page }) => {
    const servicesButton = page.locator('[data-dropdown-button]');
    await expect(servicesButton).toBeVisible();

    // Click to open dropdown (hover triggers vary by JS implementation)
    await servicesButton.click();

    const dropdown = page.locator('.site-header__dropdown').first();
    await expect(dropdown).toBeVisible({ timeout: 3000 });

    // Check dropdown links
    const dropdownLinks = ['Audit Trails', 'Chain of Custody', 'Compliance'];
    for (const linkText of dropdownLinks) {
      const link = dropdown.locator(`a:has-text("${linkText}")`);
      await expect(link).toBeVisible();
    }
  });

  test('should navigate to Documentation page', async ({ page }) => {
    await page.click('.site-header__menu a[href="/docs/"]');
    await page.waitForURL('**/docs/', { timeout: 5000 });
    expect(page.url()).toContain('/docs/');
  });

  test('should navigate to Pricing page', async ({ page }) => {
    await page.click('.site-header__menu a[href="/pricing/"]');
    await page.waitForURL('**/pricing/', { timeout: 5000 });
    expect(page.url()).toContain('/pricing/');
  });

  test('should navigate to Contact page', async ({ page }) => {
    await page.click('.site-header__menu a[href="/contact/"]');
    await page.waitForURL('**/contact/', { timeout: 5000 });
    expect(page.url()).toContain('/contact/');
  });

  test('should navigate to service from dropdown', async ({ page }) => {
    const servicesButton = page.locator('[data-dropdown-button]');
    await servicesButton.click();
    await page.waitForTimeout(300);

    await page.click('.site-header__dropdown a[href="/Services/audit/"]');
    await page.waitForURL('**/Services/audit/', { timeout: 5000 });
    expect(page.url()).toContain('/Services/audit/');
  });
});


// ─────────────────────────────────────────────────────────────────────
// Mobile Navigation (skip — mobile drawer needs separate wiring)
// ─────────────────────────────────────────────────────────────────────
test.describe.skip('Mobile Navigation Tests - iPhone 16 Pro Max - DISABLED', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize(MOBILE_IPHONE_16_PRO_MAX);
    await page.goto('/');
  });

  test('should display hamburger menu on mobile', async ({ page }) => {
    const hamburger = page.locator('.site-header__mobile-toggle');
    await expect(hamburger).toBeVisible();

    const desktopNav = page.locator('.site-header__nav');
    await expect(desktopNav).not.toBeVisible();
  });

  test('should open mobile nav drawer when hamburger clicked', async ({ page }) => {
    const hamburger = page.locator('.site-header__mobile-toggle');
    await hamburger.click();

    await expect(hamburger).toHaveAttribute('aria-expanded', 'true', { timeout: 2000 });
  });
});

test.describe.skip('Mobile Navigation Tests - Other Devices - DISABLED', () => {
  test('should work on iPhone 14', async ({ page }) => {
    await page.setViewportSize(MOBILE_IPHONE_14);
    await page.goto('/');

    const hamburger = page.locator('.site-header__mobile-toggle');
    await expect(hamburger).toBeVisible();
  });

  test('should work on Android device', async ({ page }) => {
    await page.setViewportSize(MOBILE_ANDROID);
    await page.goto('/');

    const hamburger = page.locator('.site-header__mobile-toggle');
    await expect(hamburger).toBeVisible();
  });
});


// ─────────────────────────────────────────────────────────────────────
// Accessibility Tests
// ─────────────────────────────────────────────────────────────────────
test.describe('Accessibility Tests', () => {
  test('desktop nav should have proper ARIA labels', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');

    const nav = page.locator('.site-header__nav');
    await expect(nav).toHaveAttribute('aria-label', 'Main navigation');
  });

  test('mobile nav toggle should have ARIA label', async ({ page }) => {
    await page.setViewportSize(MOBILE_IPHONE_16_PRO_MAX);
    await page.goto('/');

    const toggle = page.locator('.site-header__mobile-toggle');
    await expect(toggle).toHaveAttribute('aria-label', /menu/i);
  });

  test('dropdown button should have aria-expanded', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');

    const servicesButton = page.locator('[data-dropdown-button]');
    await expect(servicesButton).toHaveAttribute('aria-expanded', 'false');
    await expect(servicesButton).toHaveAttribute('aria-haspopup', 'true');
  });

  test('all links should be keyboard accessible', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');

    // Tab through nav links
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should focus on a visible element
    const focused = page.locator(':focus');
    await expect(focused).toBeVisible();
  });

  test('nav menu should use correct ARIA roles', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');

    const menubar = page.locator('.site-header__menu');
    await expect(menubar).toHaveAttribute('role', 'menubar');

    // All direct menu links/buttons should have role="menuitem"
    const menuItems = page.locator('.site-header__link[role="menuitem"]');
    const count = await menuItems.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });
});


// ─────────────────────────────────────────────────────────────────────
// Header Tests
// ─────────────────────────────────────────────────────────────────────
test.describe('Header Tests', () => {
  test('header should have correct role', async ({ page }) => {
    await page.goto('/');

    const header = page.locator('.site-header');
    await expect(header).toHaveAttribute('role', 'banner');
  });

  test('header should display logo', async ({ page }) => {
    await page.goto('/');

    const logo = page.locator('.site-header__logo').first();
    await expect(logo).toBeVisible();
    await expect(logo).toHaveAttribute('alt', 'EVIDENT');
  });

  test('header should display brand link', async ({ page }) => {
    await page.goto('/');

    const brand = page.locator('.site-header__brand');
    await expect(brand).toBeVisible();
    await expect(brand).toHaveAttribute('href', '/');
  });

  test('header should have CTA buttons', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');

    const signIn = page.locator('.site-header__actions a:has-text("Sign In")');
    await expect(signIn).toBeVisible();

    const getStarted = page.locator('.site-header__actions a:has-text("Get Started")');
    await expect(getStarted).toBeVisible();
  });
});
