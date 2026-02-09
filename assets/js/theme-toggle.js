// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * DARK/LIGHT MODE TOGGLE
 *
 * Handles theme switching with localStorage persistence
 * Respects user's prefers-color-scheme setting
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'faith-frontier-theme';
  const THEME_LIGHT = 'light';
  const THEME_DARK = 'dark';

  /**
   * Get saved theme or system preference
   */
  function getInitialTheme() {
    // Check localStorage first
    const savedTheme = localStorage.getItem(STORAGE_KEY);
    if (savedTheme) {
      return savedTheme;
    }

    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return THEME_LIGHT;
    }

    // Default to dark
    return THEME_DARK;
  }

  /**
   * Apply theme to document
   */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    // Update meta theme-color for mobile browsers
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }

    metaThemeColor.content = theme === THEME_LIGHT ? '#dcd9d2' : '#050d1c';
  }

  /**
   * Toggle theme
   */
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;

    applyTheme(newTheme);
    localStorage.setItem(STORAGE_KEY, newTheme);

    // Announce to screen readers
    announceThemeChange(newTheme);
  }

  /**
   * Announce theme change to screen readers
   */
  function announceThemeChange(theme) {
    const announcement = theme === THEME_LIGHT ? 'Light mode activated' : 'Dark mode activated';

    let announcer = document.getElementById('theme-announcer');
    if (!announcer) {
      announcer = document.createElement('div');
      announcer.id = 'theme-announcer';
      announcer.setAttribute('role', 'status');
      announcer.setAttribute('aria-live', 'polite');
      announcer.style.position = 'absolute';
      announcer.style.left = '-10000px';
      announcer.style.width = '1px';
      announcer.style.height = '1px';
      announcer.style.overflow = 'hidden';
      document.body.appendChild(announcer);
    }

    announcer.textContent = announcement;
  }

  /**
   * Create and append theme toggle button
   */
  function createToggleButton() {
    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'Toggle dark/light mode');
    button.setAttribute('title', 'Toggle theme');

    // SVG icons
    const sunIcon = `
      <svg class="theme-toggle-icon theme-toggle-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      </svg>
    `;

    const moonIcon = `
      <svg class="theme-toggle-icon theme-toggle-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      </svg>
    `;

    button.innerHTML = sunIcon + moonIcon;
    button.addEventListener('click', toggleTheme);

    document.body.appendChild(button);
  }

  /**
   * Watch for system theme changes
   */
  function watchSystemTheme() {
    if (!window.matchMedia) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');

    const handleChange = (e) => {
      // Only auto-switch if user hasn't set a preference
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? THEME_LIGHT : THEME_DARK);
      }
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else if (mediaQuery.addListener) {
      // Legacy browsers
      mediaQuery.addListener(handleChange);
    }
  }

  /**
   * Initialize theme system
   */
  function init() {
    // Apply initial theme immediately (before page renders)
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);

    // Create toggle button when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createToggleButton);
    } else {
      createToggleButton();
    }

    // Watch for system theme changes
    watchSystemTheme();
  }

  // Initialize immediately
  init();
})();
