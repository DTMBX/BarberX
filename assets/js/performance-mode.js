/**
 * Performance Mode (Speedy Mode)
 * Reduces animations, simplifies effects for better performance
 */

(function() {
  'use strict';

  const PERF_KEY = 'ts:performance-mode';
  const REDUCE_MOTION_KEY = 'ts:reduce-motion';

  class PerformanceMode {
    constructor() {
      this.enabled = true;
      this.reducedMotion = this.checkReducedMotion();
      this.init();
    }

    init() {
      // Check system preference
      this.checkSystemPreferences();

      // Always enable performance mode
      this.enable();

      // Listen for preference changes
      this.listenForChanges();
    }

    checkSystemPreferences() {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      this.reducedMotion = mediaQuery.matches;

      if (this.reducedMotion) {
        this.enable();
      }

      // Listen for changes
      mediaQuery.addEventListener('change', (e) => {
        this.reducedMotion = e.matches;
        if (e.matches) {
          this.enable();
        }
      });
    }

    getStoredPreference() {
      // Always return true - performance mode is always on
      return true;
    }

    checkReducedMotion() {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    enable() {
      this.enabled = true;
      localStorage.setItem(PERF_KEY, 'true');

      // Add performance class to html
      document.documentElement.classList.add('performance-mode');
      document.documentElement.classList.add('reduce-motion');

      // Disable heavy animations
      this.disableHeavyAnimations();

      // Simplify effects
      this.simplifyEffects();
    }

    disable() {
      // Performance mode is always on - cannot be disabled
      return;
    }

    toggle() {
      // Performance mode is always on - cannot be toggled
      return;
    }

    disableHeavyAnimations() {
      // Disable parallax
      document.querySelectorAll('[data-parallax]').forEach(el => {
        el.style.transform = 'none';
      });

      // Disable 3D transforms
      document.querySelectorAll('[data-tilt]').forEach(el => {
        el.style.transform = 'none';
      });

      // Disable complex animations
      document.querySelectorAll('[data-magnetic]').forEach(el => {
        el.style.transition = 'none';
      });
    }

    enableAnimations() {
      // Re-enable by removing inline styles
      document.querySelectorAll('[data-parallax], [data-tilt], [data-magnetic]').forEach(el => {
        el.style.transform = '';
        el.style.transition = '';
      });
    }

    simplifyEffects() {
      // Reduce animation durations
      const style = document.createElement('style');
      style.id = 'performance-mode-styles';
      style.textContent = `
        .performance-mode *,
        .performance-mode *::before,
        .performance-mode *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
        
        .performance-mode .scroll-fade-in,
        .performance-mode .animate-on-scroll {
          opacity: 1 !important;
          transform: none !important;
        }
      `;

      // Remove old style if exists
      const oldStyle = document.getElementById('performance-mode-styles');
      if (oldStyle) {
        oldStyle.remove();
      }

      document.head.appendChild(style);
    }

    addToggleButton() {
      // Toggle button removed - performance mode is always on
      return;
    }

    listenForChanges() {
      // Listen for storage changes from other tabs
      window.addEventListener('storage', (e) => {
        if (e.key === PERF_KEY) {
          this.enabled = e.newValue === 'true';
          if (this.enabled) {
            this.enable();
          } else {
            this.disable();
          }
        }
      });
    }
  }

  // Initialize performance mode
  const perfMode = new PerformanceMode();

  // Expose globally
  window.tsPerformanceMode = perfMode;

})();
