// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * THEME TOGGLE v2.0 - Modern ES6+ Rewrite
 * Advanced dark/light mode with smooth transitions
 *
 * Features:
 * - ES6 classes
 * - System preference detection
 * - Smooth color transitions
 * - localStorage persistence
 * - Custom properties for theming
 * - Accessibility announcements
 */

class ThemeManager {
  constructor() {
    this.config = {
      storageKey: "evident-theme",
      themes: {
        light: "light",
        dark: "dark",
      },
      metaColors: {
        light: "#ffffff",
        dark: "#0a0a0a",
      },
    };

    this.init();
  }

  /**
   * Initialize theme system
   */
  init() {
    // Apply theme immediately (before page renders)
    const initialTheme = this.getInitialTheme();
    this.applyTheme(initialTheme, false);

    // Setup when DOM is ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.setup());
    } else {
      this.setup();
    }
  }

  /**
   * Setup theme toggle after DOM ready
   */
  setup() {
    this.createToggleButton();
    this.watchSystemTheme();
    this.setupKeyboardShortcut();

    // Dispatch ready event
    document.dispatchEvent(
      new CustomEvent("theme:ready", {
        detail: { currentTheme: this.getCurrentTheme() },
      }),
    );
  }

  /**
   * Get initial theme from storage or system preference
   */
  getInitialTheme() {
    // Check localStorage first
    const saved = localStorage.getItem(this.config.storageKey);
    if (saved && Object.values(this.config.themes).includes(saved)) {
      return saved;
    }

    // Check system preference
    if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      return this.config.themes.dark;
    }

    if (window.matchMedia?.("(prefers-color-scheme: light)").matches) {
      return this.config.themes.light;
    }

    // Default to dark
    return this.config.themes.dark;
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return (
      document.documentElement.getAttribute("data-theme") ||
      this.config.themes.dark
    );
  }

  /**
   * Apply theme to document
   */
  applyTheme(theme, animate = true) {
    const html = document.documentElement;
    const currentTheme = this.getCurrentTheme();

    // Add transition class for smooth theme switching
    if (animate && currentTheme !== theme) {
      html.classList.add("theme-transitioning");
    }

    // Set theme attribute
    html.setAttribute("data-theme", theme);

    // Update meta theme-color
    this.updateMetaThemeColor(theme);

    // Update toggle button state
    this.updateToggleButton(theme);

    // Save to localStorage
    try {
      localStorage.setItem(this.config.storageKey, theme);
    } catch (error) {
      console.warn("Failed to save theme preference:", error);
    }

    // Remove transition class after animation
    if (animate) {
      setTimeout(() => {
        html.classList.remove("theme-transitioning");
      }, 300);
    }

    // Dispatch theme change event
    document.dispatchEvent(
      new CustomEvent("theme:change", {
        detail: { theme, previousTheme: currentTheme },
      }),
    );
  }

  /**
   * Toggle between themes
   */
  toggleTheme() {
    const current = this.getCurrentTheme();
    const next =
      current === this.config.themes.light
        ? this.config.themes.dark
        : this.config.themes.light;

    this.applyTheme(next);
    this.announceThemeChange(next);
  }

  /**
   * Update meta theme-color for mobile browsers
   */
  updateMetaThemeColor(theme) {
    let meta = document.querySelector('meta[name="theme-color"]');

    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "theme-color";
      document.head.appendChild(meta);
    }

    meta.content = this.config.metaColors[theme];
  }

  /**
   * Create theme toggle button with icons
   */
  createToggleButton() {
    const button = document.createElement("button");
    button.className = "theme-toggle";
    button.setAttribute("aria-label", "Toggle theme");
    button.setAttribute("title", "Toggle dark/light mode (Ctrl+Shift+D)");
    button.setAttribute("type", "button");

    // SVG icons with smooth transitions
    button.innerHTML = `
      <svg class="theme-toggle-icon theme-toggle-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
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
      <svg class="theme-toggle-icon theme-toggle-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      </svg>
    `;

    button.addEventListener("click", () => this.toggleTheme());

    // Add to page (find appropriate location)
    const header = document.querySelector(".site-header, header, .navbar");
    if (header) {
      header.appendChild(button);
    } else {
      document.body.appendChild(button);
    }

    this.toggleButton = button;
    this.updateToggleButton(this.getCurrentTheme());
  }

  /**
   * Update toggle button visual state
   */
  updateToggleButton(theme) {
    if (!this.toggleButton) return;

    this.toggleButton.setAttribute(
      "aria-label",
      theme === this.config.themes.light
        ? "Switch to dark mode"
        : "Switch to light mode",
    );

    this.toggleButton.setAttribute("data-theme", theme);
  }

  /**
   * Announce theme change to screen readers
   */
  announceThemeChange(theme) {
    const message =
      theme === this.config.themes.light
        ? "Light mode activated"
        : "Dark mode activated";

    let announcer = document.getElementById("theme-announcer");

    if (!announcer) {
      announcer = document.createElement("div");
      announcer.id = "theme-announcer";
      announcer.className = "sr-only";
      announcer.setAttribute("role", "status");
      announcer.setAttribute("aria-live", "polite");
      announcer.setAttribute("aria-atomic", "true");
      document.body.appendChild(announcer);
    }

    announcer.textContent = message;

    // Clear after announcement
    setTimeout(() => {
      announcer.textContent = "";
    }, 1000);
  }

  /**
   * Watch for system theme changes
   */
  watchSystemTheme() {
    const darkModeQuery = window.matchMedia?.("(prefers-color-scheme: dark)");

    if (!darkModeQuery) return;

    const handleChange = (e) => {
      // Only auto-switch if user hasn't manually set a preference
      if (!localStorage.getItem(this.config.storageKey)) {
        const newTheme = e.matches
          ? this.config.themes.dark
          : this.config.themes.light;
        this.applyTheme(newTheme);
      }
    };

    // Modern API
    if (darkModeQuery.addEventListener) {
      darkModeQuery.addEventListener("change", handleChange);
    }
    // Legacy API
    else if (darkModeQuery.addListener) {
      darkModeQuery.addListener(handleChange);
    }
  }

  /**
   * Setup keyboard shortcut (Ctrl+Shift+D)
   */
  setupKeyboardShortcut() {
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === "D") {
        e.preventDefault();
        this.toggleTheme();
      }
    });
  }

  /**
   * Get theme colors for programmatic use
   */
  getThemeColors() {
    const style = getComputedStyle(document.documentElement);
    return {
      primary: style.getPropertyValue("-color-primary").trim(),
      background: style.getPropertyValue("-color-background").trim(),
      text: style.getPropertyValue("-color-text").trim(),
    };
  }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Export for use in other modules
if (typeof window !== "undefined") {
  window.themeManager = themeManager;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = ThemeManager;
}
