// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * THEME SYSTEM - System Preference Only
 * Automatically uses system dark/light mode preference
 * No manual toggle - respects user's OS settings
 */

(function () {
  'use strict';

  // Apply theme based on system preference
  function applySystemTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = prefersDark ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);

    // Update meta theme color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', prefersDark ? '#0a0a0a' : '#ffffff');
    }
  }

  // Apply immediately to prevent flash
  applySystemTheme();

  // Listen for system preference changes
  const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

  // Modern browsers
  if (darkModeQuery.addEventListener) {
    darkModeQuery.addEventListener('change', applySystemTheme);
  }
  // Legacy browsers
  else if (darkModeQuery.addListener) {
    darkModeQuery.addListener(applySystemTheme);
  }

  // Re-apply on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applySystemTheme);
  } else {
    applySystemTheme();
  }
})();
