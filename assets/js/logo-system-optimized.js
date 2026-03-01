/**
 * Optimized Logo System for Tillerstead.com
 *
 * Consolidated, lazy-loaded logo utilities for web, print, and PDF contexts
 * Reduces initial bundle size by ~120KB
 */

(function() {
  'use strict';

  const LogoSystem = {
    // Configuration
    config: {
      svgSpritePath: '/assets/img/tillerstead-logo-sprite.svg',
      headerLogoId: 'logo-header',
      variants: {
        header: '/assets/img/logo/logo-header',
        compact: '/assets/img/logo/logo-compact',
        optimized: '/assets/img/logo/logo-optimized'
      },
      formats: ['webp', 'png']
    },

    // Lazy-loaded modules
    _modules: {
      base64Data: null,
      pdfRenderer: null
    },

    /**
     * Get optimal logo source for current context
     * @param {string} variant - 'header', 'compact', or 'optimized'
     * @param {boolean} retina - Whether to use @2x version
     * @returns {Object} {webp: string, png: string}
     */
    getLogoSrc(variant = 'header', retina = false) {
      const base = this.config.variants[variant];
      if (!base) {
        console.warn(`Unknown logo variant: ${variant}`);
        return null;
      }

      const suffix = retina ? '@2x' : '';
      return {
        webp: `${base}${suffix}.webp`,
        png: `${base}${suffix}.png`
      };
    },

    /**
     * Create responsive picture element
     * @param {Object} options - Configuration options
     * @returns {string} HTML string
     */
    createPicture(options = {}) {
      const {
        variant = 'header',
        alt = 'Tillerstead Logo',
        className = '',
        width = 60,
        height = 60,
        loading = 'eager',
        fetchpriority = 'auto'
      } = options;

      const sources = this.getLogoSrc(variant, true);
      const fallback = this.getLogoSrc(variant, false);

      return `
        <picture class="logo-picture ${className}">
          <source srcset="${sources.webp} 2x, ${fallback.webp} 1x" type="image/webp" />
          <source srcset="${sources.png} 2x, ${fallback.png} 1x" type="image/png" />
          <img 
            src="${fallback.png}" 
            alt="${alt}"
            width="${width}"
            height="${height}"
            loading="${loading}"
            fetchpriority="${fetchpriority}"
            class="logo-img"
          />
        </picture>
      `;
    },

    /**
     * Use SVG sprite symbol (most efficient for inline logos)
     * @param {string} symbolId - 'logo-mark', 'logo-full', or 'logo-stacked'
     * @param {Object} options - SVG options
     * @returns {string} SVG use element
     */
    useSpriteSymbol(symbolId = 'logo-mark', options = {}) {
      const {
        className = '',
        width = 60,
        height = 60,
        ariaLabel = 'Tillerstead Logo'
      } = options;

      return `
        <svg 
          class="logo-svg ${className}" 
          width="${width}" 
          height="${height}"
          aria-label="${ariaLabel}"
          role="img"
        >
          <use href="${this.config.svgSpritePath}#${symbolId}"></use>
        </svg>
      `;
    },

    /**
     * Preload SVG sprite (call in <head>)
     */
    preloadSprite() {
      if (document.querySelector(`link[href="${this.config.svgSpritePath}"]`)) {
        return; // Already preloaded
      }

      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = this.config.svgSpritePath;
      link.as = 'image';
      link.type = 'image/svg+xml';
      document.head.appendChild(link);
    },

    /**
     * Lazy-load base64 data module (for PDF/email contexts)
     * @returns {Promise<Object>} Base64 encoded logo data
     */
    async loadBase64Data() {
      if (this._modules.base64Data) {
        return this._modules.base64Data;
      }

      // Dynamically import heavy base64 module only when needed
      try {
        const module = await import('/assets/js/logo-data-uri.js');
        this._modules.base64Data = module.default || module;
        return this._modules.base64Data;
      } catch (err) {
        console.error('Failed to load logo base64 data:', err);
        return null;
      }
    },

    /**
     * Get logo as data URI (for PDF generation, email, etc.)
     * @param {string} format - 'svg' or 'png'
     * @returns {Promise<string>} Data URI
     */
    async getDataURI(format = 'svg') {
      const data = await this.loadBase64Data();
      if (!data) return null;

      return format === 'svg' ? data.svgDataUri : data.pngDataUri;
    },

    /**
     * Detect if user has high-DPI display
     * @returns {boolean}
     */
    isRetinaDisplay() {
      return window.devicePixelRatio >= 2 ||
             (window.matchMedia &&
              window.matchMedia('(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)').matches);
    },

    /**
     * Get optimal logo variant for current viewport
     * @returns {string} Variant name
     */
    getResponsiveVariant() {
      const width = window.innerWidth;

      if (width < 640) {
        return 'compact'; // Mobile
      } else if (width < 1024) {
        return 'header'; // Tablet
      } else {
        return 'optimized'; // Desktop
      }
    },

    /**
     * Initialize logo system
     */
    init() {
      // Preload sprite if on homepage or critical page
      if (document.body.classList.contains('page-home') ||
          document.querySelector('.hero')) {
        this.preloadSprite();
      }

      // Add utility class for retina detection
      if (this.isRetinaDisplay()) {
        document.documentElement.classList.add('retina-display');
      }

      // Expose to console for debugging (dev only)
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.LogoSystem = this;
        console.log('🎨 Logo System initialized', this.config);
      }
    }
  };

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => LogoSystem.init());
  } else {
    LogoSystem.init();
  }

  // Export for module usage
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = LogoSystem;
  } else {
    window.TillerstreadLogoSystem = LogoSystem;
  }

})();
