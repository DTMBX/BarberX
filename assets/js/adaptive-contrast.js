// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Faith Frontier Adaptive Contrast Initializer
 * Automatically applies accessible text colors based on background
 * Runs on page load and can be triggered manually
 */

import { ContrastUtils } from "./contrast-utils.js";

class AdaptiveContrast {
  constructor() {
    this.initialized = false;
    this.brandTokens = {
      emerald500: "rgba(1, 138, 106, 1)",
      emerald400: "rgba(36, 181, 138, 1)",
      emerald600: "rgba(16, 92, 74, 1)",
      brass500: "rgba(212, 165, 116, 1)",
      brass400: "rgba(160, 122, 50, 1)",
      cream50: "rgba(249, 250, 251, 1)",
      ink900: "rgba(28, 27, 25, 1)",
      navy950: "rgba(5, 13, 28, 1)",
    };
  }

  /**
   * Initialize adaptive contrast system
   */
  init() {
    if (this.initialized) return;

    // Apply adaptive colors to key elements
    this.applyAdaptiveColors();

    // Set up mutation observer for dynamic content
    this.observeChanges();

    // Add debug command to console
    this.setupDebugCommands();

    this.initialized = true;
    console.log(
      "%c✓ Adaptive Contrast System Initialized",
      "color: #10b981; font-weight: bold;",
    );
  }

  /**
   * Apply adaptive colors to elements based on their backgrounds
   */
  applyAdaptiveColors() {
    // Find all elements with specific background colors
    const selectors = [
      ".hero",
      ".section",
      ".card",
      ".panel",
      ".hero-side-panel",
      '[style*="background"]',
      '[class*="bg-"]',
    ];

    selectors.forEach((selector) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element) => this.processElement(element));
    });
  }

  /**
   * Process a single element for contrast
   * @param {HTMLElement} element
   */
  processElement(element) {
    const styles = window.getComputedStyle(element);
    const bgColor = styles.backgroundColor;

    // Skip transparent backgrounds
    if (bgColor === "rgba(0, 0, 0, 0)" || !bgColor) return;

    // Apply accessible colors
    try {
      const result = ContrastUtils.applyAccessibleColors(element, bgColor, {
        brandTokens: this.brandTokens,
        minRatio: 4.5,
      });

      // Apply to child text if needed
      if (!result.meetsAA) {
        this.forceAccessibleText(element, bgColor);
      }
    } catch (error) {
      console.warn("Error processing element:", element, error);
    }
  }

  /**
   * Force accessible text color on element and children
   * @param {HTMLElement} element
   * @param {string} bgColor
   */
  forceAccessibleText(element, bgColor) {
    const textColor = ContrastUtils.getAccessibleTextColor(bgColor, {
      lightText: this.brandTokens.cream50,
      darkText: this.brandTokens.ink900,
    });

    // Apply to element
    element.style.setProperty("color", textColor, "important");

    // Apply to direct text children
    const textNodes = this.getTextElements(element);
    textNodes.forEach((node) => {
      node.style.setProperty("color", textColor, "important");
    });
  }

  /**
   * Get elements containing text
   * @param {HTMLElement} parent
   * @returns {Array<HTMLElement>}
   */
  getTextElements(parent) {
    const elements = [];
    const walker = document.createTreeWalker(parent, NodeFilter.SHOW_ELEMENT, {
      acceptNode: (node) => {
        // Skip script, style, etc.
        if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(node.tagName)) {
          return NodeFilter.FILTER_REJECT;
        }
        // Accept if has text content
        return node.textContent.trim()
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_SKIP;
      },
    });

    let node;
    while ((node = walker.nextNode())) {
      elements.push(node);
    }
    return elements;
  }

  /**
   * Observe DOM changes and apply contrast fixes
   */
  observeChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            // Element node
            this.processElement(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    this.observer = observer;
  }

  /**
   * Setup console debug commands
   */
  setupDebugCommands() {
    window.contrastAudit = () => {
      const issues = ContrastUtils.auditContrast();
      ContrastUtils.logAuditResults(issues);
      return issues;
    };

    window.contrastDebug = (enable = true) => {
      if (enable) {
        document.body.classList.add("contrast-debug");
        console.log(
          "%c🔍 Contrast Debug Mode ON",
          "color: #f59e0b; font-weight: bold;",
        );
        console.log("Contrast ratios will be displayed on elements.");
      } else {
        document.body.classList.remove("contrast-debug");
        console.log("%c✓ Contrast Debug Mode OFF", "color: #10b981;");
      }
    };

    window.contrastFix = () => {
      this.applyAdaptiveColors();
      console.log("%c✓ Contrast fixes reapplied", "color: #10b981;");
    };

    // Log available commands
    console.log("%cContrast Utilities Available:", "font-weight: bold;");
    console.log("  contrastAudit()  - Check all elements for contrast issues");
    console.log("  contrastDebug()  - Toggle visual debugging mode");
    console.log("  contrastFix()    - Reapply contrast fixes");
  }

  /**
   * Destroy and cleanup
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    this.initialized = false;
  }
}

// Auto-initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    const adaptiveContrast = new AdaptiveContrast();
    adaptiveContrast.init();
    window.adaptiveContrast = adaptiveContrast;
  });
} else {
  const adaptiveContrast = new AdaptiveContrast();
  adaptiveContrast.init();
  window.adaptiveContrast = adaptiveContrast;
}

export default AdaptiveContrast;
