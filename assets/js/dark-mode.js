// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Dark Mode System
 * Persistent dark mode with smooth transitions
 */

class DarkMode {
  constructor() {
    this.darkMode = this.getSavedMode();
    this.init();
  }

  init() {
    // Apply saved mode
    this.apply(this.darkMode);

    // Create toggle button
    this.createToggleButton();

    // Listen for system preference changes
    this.watchSystemPreference();
  }

  createToggleButton() {
    const toggle = document.createElement('button');
    toggle.className = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle dark mode');
    toggle.innerHTML = this.darkMode ? '☀️' : '🌙';

    toggle.addEventListener('click', () => {
      this.toggle();
    });

    document.body.appendChild(toggle);
    this.toggleButton = toggle;
  }

  toggle() {
    this.darkMode = !this.darkMode;
    this.apply(this.darkMode);
    this.save(this.darkMode);
  }

  apply(isDark) {
    if (isDark) {
      document.body.classList.add('dark-mode');
      this.updateToggleIcon('☀️');
    } else {
      document.body.classList.remove('dark-mode');
      this.updateToggleIcon('🌙');
    }

    // Update meta theme-color
    this.updateThemeColor(isDark);

    // Trigger custom event
    document.dispatchEvent(
      new CustomEvent('darkmodechange', {
        detail: { darkMode: isDark },
      })
    );
  }

  updateToggleIcon(icon) {
    if (this.toggleButton) {
      this.toggleButton.innerHTML = icon;
    }
  }

  updateThemeColor(isDark) {
    let metaTheme = document.querySelector('meta[name="theme-color"]');

    if (!metaTheme) {
      metaTheme = document.createElement('meta');
      metaTheme.setAttribute('name', 'theme-color');
      document.head.appendChild(metaTheme);
    }

    metaTheme.setAttribute('content', isDark ? '#0f1419' : '#ffffff');
  }

  save(isDark) {
    try {
      localStorage.setItem('evident-dark-mode', isDark ? 'true' : 'false');
    } catch (e) {
      console.warn('Could not save dark mode preference:', e);
    }
  }

  getSavedMode() {
    try {
      const saved = localStorage.getItem('evident-dark-mode');

      // If user has a saved preference, use it
      if (saved !== null) {
        return saved === 'true';
      }

      // Otherwise, check system preference
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch (e) {
      return false;
    }
  }

  watchSystemPreference() {
    if (!window.matchMedia) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    mediaQuery.addEventListener('change', (e) => {
      // Only auto-switch if user hasn't manually set a preference
      const hasManualPreference = localStorage.getItem('evident-dark-mode') !== null;

      if (!hasManualPreference) {
        this.darkMode = e.matches;
        this.apply(this.darkMode);
      }
    });
  }
}

// Initialize on DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new DarkMode());
} else {
  new DarkMode();
}
