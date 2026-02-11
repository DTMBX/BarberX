/**
 * Theme.js – Modern, flexible theme system
 * Evident Technologies
 *
 * Features:
 * - Light/dark mode toggle
 * - Persistent user preference (localStorage)
 * - System preference detection
 * - Smooth transitions
 */

class ThemeManager {
  constructor() {
    this.storageKey = 'evident-theme';
    this.htmlElement = document.documentElement;
    this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

    this.init();
  }

  init() {
    // Apply stored or system preference on page load
    const stored = this.getStoredTheme();
    if (stored) {
      this.setTheme(stored);
    } else {
      const system = this.prefersDark.matches ? 'dark' : 'light';
      this.setTheme(system);
    }

    // Listen for system preference changes
    this.prefersDark.addEventListener('change', (e) => {
      if (!this.getStoredTheme()) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });

    // Add theme toggle button if header exists
    this.addThemeToggle();
  }

  setTheme(theme) {
    const isDark = theme === 'dark';
    this.htmlElement.style.colorScheme = theme;
    this.htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);

    // Dispatch custom event for other scripts to listen to
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  getStoredTheme() {
    return localStorage.getItem(this.storageKey);
  }

  toggleTheme() {
    const current = this.htmlElement.style.colorScheme || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  }

  addThemeToggle() {
    const headerActions = document.querySelector('.header-actions');
    if (!headerActions) return;

    const btn = document.createElement('button');
    btn.className = 'btn-icon btn-ghost';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.setAttribute('title', 'Toggle dark mode');
    btn.innerHTML = `
      <svg class="theme-icon-light" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" style="display: none;">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <svg class="theme-icon-dark" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" style="display: none;">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    `;

    btn.addEventListener('click', () => this.toggleTheme());

    // Insert before the mobile nav button
    const mobileBtn = document.getElementById('mobile-nav-btn');
    if (mobileBtn) {
      mobileBtn.parentElement.insertBefore(btn, mobileBtn);
    } else {
      headerActions.appendChild(btn);
    }

    this.updateThemeIcon();
    window.addEventListener('themechange', () => this.updateThemeIcon());
  }

  updateThemeIcon() {
    const lightIcon = document.querySelector('.theme-icon-light');
    const darkIcon = document.querySelector('.theme-icon-dark');
    if (!lightIcon || !darkIcon) return;

    const isDark = this.htmlElement.style.colorScheme === 'dark';
    lightIcon.style.display = isDark ? 'block' : 'none';
    darkIcon.style.display = isDark ? 'none' : 'block';
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
  });
} else {
  new ThemeManager();
}
