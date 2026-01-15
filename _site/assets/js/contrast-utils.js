/**
 * Faith Frontier Contrast Utility
 * Modern, professional color contrast calculation system
 * Based on WCAG 2.1 standards for accessibility
 * 
 * Provides:
 * - Accurate contrast ratio calculation
 * - Automatic color selection based on background
 * - Brand token integration
 * - WCAG AA/AAA compliance checking
 */

export class ContrastUtils {
  /**
   * Parse RGBA color string to components
   * @param {string} rgba - Color in format "rgba(r, g, b, a)"
   * @returns {Object} {r, g, b, a}
   */
  static parseRGBA(rgba) {
    const match = rgba.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!match) {
      console.warn(`Unable to parse color: ${rgba}`);
      return { r: 0, g: 0, b: 0, a: 1 };
    }
    return {
      r: parseInt(match[1]),
      g: parseInt(match[2]),
      b: parseInt(match[3]),
      a: parseFloat(match[4] || '1')
    };
  }

  /**
   * Convert RGB component (0-255) to sRGB (0-1)
   * @param {number} component - RGB component value
   * @returns {number} sRGB value
   */
  static toLinear(component) {
    const c = component / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  }

  /**
   * Calculate relative luminance of a color
   * Based on WCAG 2.1 formula: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
   * @param {Object} rgb - Color object {r, g, b}
   * @returns {number} Relative luminance (0-1)
   */
  static getLuminance({ r, g, b }) {
    const red = this.toLinear(r);
    const green = this.toLinear(g);
    const blue = this.toLinear(b);
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
  }

  /**
   * Calculate contrast ratio between two colors
   * Based on WCAG 2.1 formula: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
   * @param {string} color1 - First color (foreground)
   * @param {string} color2 - Second color (background)
   * @returns {number} Contrast ratio (1-21)
   */
  static getContrastRatio(color1, color2) {
    const rgb1 = this.parseRGBA(color1);
    const rgb2 = this.parseRGBA(color2);
    
    const lum1 = this.getLuminance(rgb1);
    const lum2 = this.getLuminance(rgb2);
    
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * Check if contrast meets WCAG standards
   * @param {number} ratio - Contrast ratio
   * @param {string} level - 'AA' or 'AAA'
   * @param {string} size - 'normal' or 'large' (18pt+ or 14pt+ bold)
   * @returns {boolean} Whether contrast meets standard
   */
  static meetsWCAG(ratio, level = 'AA', size = 'normal') {
    const requirements = {
      AA: { normal: 4.5, large: 3.0 },
      AAA: { normal: 7.0, large: 4.5 }
    };
    return ratio >= requirements[level][size];
  }

  /**
   * Get accessible text color for a given background
   * @param {string} bgColor - Background color
   * @param {Object} options - Brand color tokens
   * @returns {string} Optimal text color
   */
  static getAccessibleTextColor(bgColor, options = {}) {
    const {
      lightText = 'rgba(249, 250, 251, 1)', // cream-50
      darkText = 'rgba(28, 27, 25, 1)',     // ink-900
      preferDark = false,
      minRatio = 4.5 // WCAG AA for normal text
    } = options;

    const lightRatio = this.getContrastRatio(lightText, bgColor);
    const darkRatio = this.getContrastRatio(darkText, bgColor);

    // If both meet requirements, use preferred
    if (lightRatio >= minRatio && darkRatio >= minRatio) {
      return preferDark ? darkText : lightText;
    }

    // Return whichever has better contrast
    return lightRatio > darkRatio ? lightText : darkText;
  }

  /**
   * Get accessible color pair for link/accent colors
   * @param {string} bgColor - Background color
   * @param {Object} brandTokens - Brand color tokens
   * @returns {Object} {primary, primaryHover, contrast}
   */
  static getAccessibleLinkColors(bgColor, brandTokens = {}) {
    const {
      emerald400 = 'rgba(36, 181, 138, 1)',
      emerald600 = 'rgba(16, 92, 74, 1)',
      brass500 = 'rgba(212, 165, 116, 1)',
      brass400 = 'rgba(160, 122, 50, 1)'
    } = brandTokens;

    const bgLuminance = this.getLuminance(this.parseRGBA(bgColor));
    const isDarkBg = bgLuminance < 0.5;

    if (isDarkBg) {
      // Dark background: use lighter emerald
      const primary = emerald400;
      const primaryHover = brass500;
      const contrast = this.getContrastRatio(primary, bgColor);
      return { primary, primaryHover, contrast };
    } else {
      // Light background: use darker emerald
      const primary = emerald600;
      const primaryHover = brass400;
      const contrast = this.getContrastRatio(primary, bgColor);
      return { primary, primaryHover, contrast };
    }
  }

  /**
   * Apply accessible colors to CSS custom properties
   * @param {HTMLElement} element - Element to apply colors to
   * @param {string} bgColor - Background color
   * @param {Object} options - Configuration options
   */
  static applyAccessibleColors(element, bgColor, options = {}) {
    const textColor = this.getAccessibleTextColor(bgColor, options);
    const linkColors = this.getAccessibleLinkColors(bgColor, options.brandTokens);

    element.style.setProperty('--adaptive-text', textColor);
    element.style.setProperty('--adaptive-link', linkColors.primary);
    element.style.setProperty('--adaptive-link-hover', linkColors.primaryHover);

    // Store contrast ratios as data attributes for debugging
    const textContrast = this.getContrastRatio(textColor, bgColor);
    element.dataset.textContrast = textContrast.toFixed(2);
    element.dataset.linkContrast = linkColors.contrast.toFixed(2);
    
    return {
      textColor,
      textContrast,
      linkColors,
      meetsAA: textContrast >= 4.5,
      meetsAAA: textContrast >= 7.0
    };
  }

  /**
   * Audit all elements for contrast issues
   * @param {HTMLElement} root - Root element to audit
   * @returns {Array} List of contrast issues
   */
  static auditContrast(root = document.body) {
    const issues = [];
    const elements = root.querySelectorAll('*');

    elements.forEach(element => {
      const styles = window.getComputedStyle(element);
      const color = styles.color;
      const bgColor = styles.backgroundColor;

      // Skip if transparent or no background
      if (bgColor === 'rgba(0, 0, 0, 0)' || !color) return;

      const ratio = this.getContrastRatio(color, bgColor);
      const fontSize = parseFloat(styles.fontSize);
      const fontWeight = parseInt(styles.fontWeight) || 400;
      const isLarge = fontSize >= 18 || (fontSize >= 14 && fontWeight >= 700);

      const meetsAA = this.meetsWCAG(ratio, 'AA', isLarge ? 'large' : 'normal');
      const meetsAAA = this.meetsWCAG(ratio, 'AAA', isLarge ? 'large' : 'normal');

      if (!meetsAA) {
        issues.push({
          element,
          color,
          bgColor,
          ratio: ratio.toFixed(2),
          fontSize: fontSize.toFixed(1) + 'px',
          fontWeight,
          isLarge,
          meetsAA,
          meetsAAA,
          selector: this.getSelector(element)
        });
      }
    });

    return issues;
  }

  /**
   * Generate CSS selector for an element
   * @param {HTMLElement} element
   * @returns {string} CSS selector
   */
  static getSelector(element) {
    if (element.id) return `#${element.id}`;
    if (element.className) {
      const classes = Array.from(element.classList).slice(0, 2).join('.');
      return `${element.tagName.toLowerCase()}.${classes}`;
    }
    return element.tagName.toLowerCase();
  }

  /**
   * Log contrast audit results to console
   * @param {Array} issues - Issues from auditContrast()
   */
  static logAuditResults(issues) {
    if (issues.length === 0) {
      console.log('%c✓ No contrast issues found!', 'color: #10b981; font-weight: bold;');
      return;
    }

    console.group(`%c⚠️ Found ${issues.length} contrast issues`, 'color: #f59e0b; font-weight: bold;');
    issues.forEach((issue, i) => {
      console.group(`${i + 1}. ${issue.selector}`);
      console.log('Contrast Ratio:', issue.ratio, issue.meetsAA ? '✓ AA' : '✗ AA', issue.meetsAAA ? '✓ AAA' : '✗ AAA');
      console.log('Colors:', issue.color, 'on', issue.bgColor);
      console.log('Font:', `${issue.fontSize}, weight ${issue.fontWeight}`, issue.isLarge ? '(large)' : '(normal)');
      console.log('Element:', issue.element);
      console.groupEnd();
    });
    console.groupEnd();
  }
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ContrastUtils = ContrastUtils;
}
