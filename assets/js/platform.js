// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Technologies - Interactive Features
 * Legal-Grade Evidence Processing & Verification Platform
 */

(function () {
  "use strict";

  /**
   * Initialize all platform features
   */
  function initPlatform() {
    initScrollAnimations();
    initNavigationHighlight();
    initSmoothScroll();
    initTooltips();
    initStatsCounter();
    initSearchEnhancement();
    initAccessibilityFeatures();
    initPerformanceMonitoring();
  }

  /**
   * Intersection Observer for scroll animations
   */
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-fade-in");
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe feature cards, stats, and other animated elements
    document
      .querySelectorAll(".feature-card, .stat-card, .card")
      .forEach((el) => {
        observer.observe(el);
      });
  }

  /**
   * Highlight active navigation item based on scroll position
   */
  function initNavigationHighlight() {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll('nav a[href^="#"]');

    function highlightNavigation() {
      let current = "";

      sections.forEach((section) => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 200) {
          current = section.getAttribute("id");
        }
      });

      navLinks.forEach((link) => {
        link.classList.remove("active");
        if (link.getAttribute("href").includes(current)) {
          link.classList.add("active");
        }
      });
    }

    window.addEventListener("scroll", highlightNavigation);
    highlightNavigation(); // Initial call
  }

  /**
   * Smooth scrolling for anchor links
   */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const targetId = this.getAttribute("href");
        if (targetId === "#") return;

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      });
    });
  }

  /**
   * Enhanced tooltips for features
   */
  function initTooltips() {
    const tooltipElements = document.querySelectorAll("[data-tooltip]");

    tooltipElements.forEach((element) => {
      const tooltip = document.createElement("div");
      tooltip.className = "tooltip";
      tooltip.textContent = element.getAttribute("data-tooltip");
      tooltip.style.cssText = `
        position: absolute;
        background: var(--gray-900);
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s;
        z-index: 1000;
      `;

      element.style.position = "relative";
      element.appendChild(tooltip);

      element.addEventListener("mouseenter", () => {
        tooltip.style.opacity = "1";
      });

      element.addEventListener("mouseleave", () => {
        tooltip.style.opacity = "0";
      });
    });
  }

  /**
   * Animated counter for statistics
   */
  function initStatsCounter() {
    const statValues = document.querySelectorAll(".stat-value");

    const animateCounter = (element) => {
      const target = parseInt(element.textContent.replace(/[^0-9]/g, ""));
      const duration = 2000;
      const start = 0;
      const increment = target / (duration / 16);
      let current = start;

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          element.textContent = formatStatValue(target, element.dataset.format);
          clearInterval(timer);
        } else {
          element.textContent = formatStatValue(
            Math.floor(current),
            element.dataset.format,
          );
        }
      }, 16);
    };

    const formatStatValue = (value, format) => {
      if (format === "percent") return value + "%";
      if (format === "currency") return "$" + value.toLocaleString();
      if (format === "hours") return value.toLocaleString() + "hr";
      return value.toLocaleString();
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 },
    );

    statValues.forEach((stat) => observer.observe(stat));
  }

  /**
   * Enhanced search functionality
   */
  function initSearchEnhancement() {
    const searchInput = document.querySelector("#platform-search");
    if (!searchInput) return;

    let searchTimeout;

    searchInput.addEventListener("input", function (e) {
      clearTimeout(searchTimeout);

      searchTimeout = setTimeout(() => {
        const query = e.target.value.toLowerCase();
        performSearch(query);
      }, 300);
    });

    function performSearch(query) {
      if (query.length < 3) return;

      const searchableElements = document.querySelectorAll("[data-searchable]");
      let matches = [];

      searchableElements.forEach((element) => {
        const content = element.textContent.toLowerCase();
        if (content.includes(query)) {
          matches.push({
            element: element,
            relevance: calculateRelevance(content, query),
          });
        }
      });

      displaySearchResults(matches);
    }

    function calculateRelevance(content, query) {
      const index = content.indexOf(query);
      const frequency = (content.match(new RegExp(query, "g")) || []).length;
      return frequency * 100 - index;
    }

    function displaySearchResults(matches) {
      // Sort by relevance
      matches.sort((a, b) => b.relevance - a.relevance);

      // Highlight matches
      matches.forEach((match) => {
        match.element.scrollIntoView({ behavior: "smooth", block: "nearest" });
        match.element.classList.add("search-highlight");

        setTimeout(() => {
          match.element.classList.remove("search-highlight");
        }, 2000);
      });
    }
  }

  /**
   * Accessibility enhancements
   */
  function initAccessibilityFeatures() {
    // Skip to main content link
    const skipLink = document.querySelector(".skip-link");
    if (skipLink) {
      skipLink.addEventListener("click", (e) => {
        e.preventDefault();
        const mainContent = document.querySelector("main");
        if (mainContent) {
          mainContent.setAttribute("tabindex", "-1");
          mainContent.focus();
        }
      });
    }

    // Keyboard navigation improvements
    document.addEventListener("keydown", (e) => {
      // ESC key closes modals/dropdowns
      if (e.key === "Escape") {
        document
          .querySelectorAll(".modal.active, .dropdown.active")
          .forEach((el) => {
            el.classList.remove("active");
          });
      }
    });

    // ARIA live region for dynamic updates
    const liveRegion = document.createElement("div");
    liveRegion.setAttribute("aria-live", "polite");
    liveRegion.setAttribute("aria-atomic", "true");
    liveRegion.className = "sr-only";
    liveRegion.id = "live-region";
    document.body.appendChild(liveRegion);

    window.announceToScreenReader = function (message) {
      liveRegion.textContent = message;
      setTimeout(() => {
        liveRegion.textContent = "";
      }, 1000);
    };
  }

  /**
   * Performance monitoring
   */
  function initPerformanceMonitoring() {
    if ("PerformanceObserver" in window) {
      // Monitor Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log("LCP:", lastEntry.renderTime || lastEntry.loadTime);
      });

      lcpObserver.observe({ entryTypes: ["largest-contentful-paint"] });

      // Monitor First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          console.log("FID:", entry.processingStart - entry.startTime);
        });
      });

      fidObserver.observe({ entryTypes: ["first-input"] });

      // Monitor Cumulative Layout Shift (CLS)
      let clsScore = 0;
      const clsObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsScore += entry.value;
            console.log("CLS:", clsScore);
          }
        });
      });

      clsObserver.observe({ entryTypes: ["layout-shift"] });
    }
  }

  /**
   * Feature Cards Interactive Enhancement
   */
  class FeatureCardEnhancer {
    constructor() {
      this.cards = document.querySelectorAll(".feature-card");
      this.init();
    }

    init() {
      this.cards.forEach((card) => {
        this.addHoverEffect(card);
        this.addClickExpansion(card);
      });
    }

    addHoverEffect(card) {
      card.addEventListener("mouseenter", (e) => {
        const icon = card.querySelector(".feature-icon");
        if (icon) {
          icon.style.transform = "scale(1.1) rotate(5deg)";
        }
      });

      card.addEventListener("mouseleave", (e) => {
        const icon = card.querySelector(".feature-icon");
        if (icon) {
          icon.style.transform = "scale(1) rotate(0deg)";
        }
      });
    }

    addClickExpansion(card) {
      const moreInfo = card.dataset.moreInfo;
      if (!moreInfo) return;

      card.style.cursor = "pointer";
      card.addEventListener("click", () => {
        const existingInfo = card.querySelector(".expanded-info");
        if (existingInfo) {
          existingInfo.remove();
        } else {
          const infoDiv = document.createElement("div");
          infoDiv.className = "expanded-info";
          infoDiv.style.cssText = `
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-light);
            color: var(--text-secondary);
            font-size: 0.875rem;
            animation: fadeIn 0.3s ease-out;
          `;
          infoDiv.textContent = moreInfo;
          card.appendChild(infoDiv);
        }
      });
    }
  }

  /**
   * Loading State Manager
   */
  class LoadingStateManager {
    static show(element, message = "Loading...") {
      const loader = document.createElement("div");
      loader.className = "loading-overlay";
      loader.innerHTML = `
        <div class="loading-spinner"></div>
        <p class="loading-message">${message}</p>
      `;
      loader.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 999;
        border-radius: inherit;
      `;

      element.style.position = "relative";
      element.appendChild(loader);
      element.setAttribute("aria-busy", "true");
    }

    static hide(element) {
      const loader = element.querySelector(".loading-overlay");
      if (loader) {
        loader.remove();
        element.removeAttribute("aria-busy");
      }
    }
  }

  /**
   * Form Validation Enhancement
   */
  class FormValidator {
    constructor(formElement) {
      this.form = formElement;
      this.init();
    }

    init() {
      this.form.addEventListener("submit", (e) => {
        if (!this.validate()) {
          e.preventDefault();
        }
      });

      // Real-time validation
      this.form.querySelectorAll("input, textarea, select").forEach((field) => {
        field.addEventListener("blur", () => this.validateField(field));
        field.addEventListener("input", () => this.clearFieldError(field));
      });
    }

    validate() {
      let isValid = true;
      this.form.querySelectorAll("[required]").forEach((field) => {
        if (!this.validateField(field)) {
          isValid = false;
        }
      });
      return isValid;
    }

    validateField(field) {
      const value = field.value.trim();
      const type = field.type;

      // Required check
      if (field.hasAttribute("required") && !value) {
        this.showError(field, "This field is required");
        return false;
      }

      // Email validation
      if (type === "email" && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          this.showError(field, "Please enter a valid email address");
          return false;
        }
      }

      // Phone validation
      if (field.name === "phone" && value) {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        if (!phoneRegex.test(value)) {
          this.showError(field, "Please enter a valid phone number");
          return false;
        }
      }

      this.clearFieldError(field);
      return true;
    }

    showError(field, message) {
      this.clearFieldError(field);

      field.classList.add("error");
      field.setAttribute("aria-invalid", "true");

      const error = document.createElement("div");
      error.className = "field-error";
      error.textContent = message;
      error.style.cssText = `
        color: var(--error-red);
        font-size: 0.875rem;
        margin-top: 0.25rem;
      `;

      field.parentElement.appendChild(error);
    }

    clearFieldError(field) {
      field.classList.remove("error");
      field.removeAttribute("aria-invalid");

      const error = field.parentElement.querySelector(".field-error");
      if (error) {
        error.remove();
      }
    }
  }

  /**
   * Export utilities for global access
   */
  window.EvidentPlatform = {
    LoadingState: LoadingStateManager,
    FormValidator: FormValidator,
    announceToScreenReader: window.announceToScreenReader,
  };

  /**
   * Initialize when DOM is ready
   */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlatform);
  } else {
    initPlatform();
  }

  // Initialize feature card enhancements
  new FeatureCardEnhancer();

  // Initialize form validators
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    new FormValidator(form);
  });
})();
