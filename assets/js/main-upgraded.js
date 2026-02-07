// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * MAIN.JS v2.0 - Modern ES6+ Rewrite
 * Evident Technologies Platform
 *
 * Features:
 * - ES6+ syntax (const/let, arrow functions, classes)
 * - Async/await for API calls
 * - Modern DOM manipulation
 * - Performance optimizations
 */

class EvidentApp {
  constructor() {
    this.config = {
      headerCompactThreshold: 12,
      verseAPI: {
        timeout: 4500,
        cacheKey: "evident-daily-verse",
        timezone: "America/New_York",
      },
    };

    this.init();
  }

  /**
   * Initialize application
   */
  init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.boot());
    } else {
      this.boot();
    }
  }

  /**
   * Boot sequence
   */
  boot() {
    this.initHeaderCompaction();
    this.initDailyVerse();
    this.initLazyLoading();
    this.initSmoothScroll();
    this.initFormValidation();

    // Dispatch custom event for other modules
    document.dispatchEvent(new CustomEvent("evident:ready"));
  }

  /**
   * HEADER COMPACTION
   * Shrink header on scroll for better UX
   */
  initHeaderCompaction() {
    const header = document.querySelector(".site-header");
    if (!header) return;

    let ticking = false;

    const updateHeader = () => {
      const shouldCompact = window.scrollY > this.config.headerCompactThreshold;
      header.classList.toggle("is-compact", shouldCompact);
      ticking = false;
    };

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          requestAnimationFrame(updateHeader);
          ticking = true;
        }
      },
      { passive: true }
    );

    // Initial check
    updateHeader();
  }

  /**
   * DAILY VERSE SYSTEM
   * Fetch and display daily inspiration with multiple API fallbacks
   */
  initDailyVerse() {
    const container = document.getElementById("daily-verse");
    if (!container) return;

    const dateKey = this.getNYCDateKey();
    const cacheKey = `${this.config.verseAPI.cacheKey}-${dateKey}`;

    // Check cache first
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      this.renderVerse(container, cached);
      return;
    }

    // Fetch new verse
    this.fetchDailyVerse()
      .then((verse) => {
        this.renderVerse(container, verse);
        this.saveToCache(cacheKey, verse);
      })
      .catch(() => {
        // Fallback to static verse
        const fallback = this.getFallbackVerse(dateKey);
        this.renderVerse(container, fallback);
      });
  }

  /**
   * Get NYC timezone date key for verse caching
   */
  getNYCDateKey() {
    try {
      const fmt = new Intl.DateTimeFormat("en-US", {
        timeZone: this.config.verseAPI.timezone,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });

      const parts = fmt.formatToParts(new Date());
      const year = parts.find((p) => p.type === "year").value;
      const month = parts.find((p) => p.type === "month").value;
      const day = parts.find((p) => p.type === "day").value;

      return `${year}-${month}-${day}`;
    } catch (error) {
      const dt = new Date();
      return `${dt.getFullYear()}-${dt.getMonth() + 1}-${dt.getDate()}`;
    }
  }

  /**
   * Fetch daily verse from APIs with fallback strategy
   */
  async fetchDailyVerse() {
    const apis = [
      {
        name: "BibleGateway",
        url: "https://www.biblegateway.com/votd/get/?format=json&version=NIV",
        parse: (data) =>
          data?.votd
            ? {
                text: data.votd.text || "",
                reference: data.votd.reference || "",
              }
            : null,
      },
      {
        name: "OurManna",
        url: "https://beta.ourmanna.com/api/v1/get/?format=json",
        parse: (data) =>
          data?.verse?.details
            ? {
                text: data.verse.details.text || "",
                reference: data.verse.details.reference || "",
              }
            : null,
      },
    ];

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.config.verseAPI.timeout);

    try {
      for (const api of apis) {
        try {
          const response = await fetch(api.url, { signal: controller.signal });
          const data = await response.json();
          const verse = api.parse(data);

          if (verse?.text && verse?.reference) {
            clearTimeout(timeout);
            return verse;
          }
        } catch (error) {
          // Try next API
          continue;
        }
      }

      throw new Error("All APIs failed");
    } catch (error) {
      clearTimeout(timeout);
      throw error;
    }
  }

  /**
   * Render verse in container
   */
  renderVerse(container, verse) {
    const textEl = container.querySelector(".dv-text");
    const refEl = container.querySelector(".dv-ref");

    // Decode HTML entities
    const text = this.decodeHTML(verse.text || "Daily verse unavailable.");
    const reference = verse.reference || "";

    if (textEl) {
      textEl.textContent = text;
    }

    if (refEl && reference) {
      refEl.innerHTML = `— ${reference} · ${this.createVersionLinks(reference)}`;
    }

    // Fade in
    container.style.opacity = "0";
    requestAnimationFrame(() => {
      container.style.transition = "opacity 250ms ease";
      container.style.opacity = "1";
    });
  }

  /**
   * Create Bible version links
   */
  createVersionLinks(reference) {
    const versions = [
      { label: "GNV (Geneva)", version: "GNV" },
      { label: "KJV", version: "KJV" },
      { label: "AKJV", version: "AKJV" },
      { label: "NIV", version: "NIV" },
      { label: "ESV", version: "ESV" },
      { label: "NRSV", version: "NRSV" },
    ];

    return versions
      .map(
        (v) =>
          `<a href="https://www.biblegateway.com/passage/?search=${encodeURIComponent(reference)}&version=${encodeURIComponent(v.version)}" 
         target="_blank" rel="noopener" class="verse-version-link">${v.label}</a>`
      )
      .join(" · ");
  }

  /**
   * Get fallback verse based on date
   */
  getFallbackVerse(dateKey) {
    const verses = [
      {
        reference: "Genesis 1:1",
        text: "In the beginning God created the heaven and the earth.",
      },
      {
        reference: "Psalm 23:1",
        text: "The LORD is my shepherd; I shall not want.",
      },
      {
        reference: "Proverbs 3:5-6",
        text: "Trust in the LORD with all thine heart; and lean not unto thine own understanding.",
      },
      {
        reference: "John 3:16",
        text: "For God so loved the world, that he gave his only begotten Son.",
      },
      {
        reference: "Matthew 6:33",
        text: "Seek ye first the kingdom of God, and his righteousness.",
      },
      {
        reference: "Philippians 4:13",
        text: "I can do all things through Christ which strengtheneth me.",
      },
      {
        reference: "Romans 8:28",
        text: "All things work together for good to them that love God.",
      },
      {
        reference: "Isaiah 40:31",
        text: "They that wait upon the LORD shall renew their strength.",
      },
    ];

    // Hash date to get deterministic verse selection
    let hash = 0;
    for (let i = 0; i < dateKey.length; i++) {
      hash = (hash << 5) - hash + dateKey.charCodeAt(i);
      hash = hash & hash;
    }

    const index = Math.abs(hash) % verses.length;
    return verses[index];
  }

  /**
   * LAZY LOADING
   * Load images as they enter viewport
   */
  initLazyLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ("loading" in HTMLImageElement.prototype) {
      // Browser supports native lazy loading
      return;
    }

    // Fallback for older browsers
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove("lazy");
          imageObserver.unobserve(img);
        }
      });
    });

    images.forEach((img) => imageObserver.observe(img));
  }

  /**
   * SMOOTH SCROLL
   * Smooth scrolling to anchor links
   */
  initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        const href = anchor.getAttribute("href");
        if (href === "#") return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        const offsetTop = target.getBoundingClientRect().top + window.pageYOffset;
        const offset = 80; // Header height

        window.scrollTo({
          top: offsetTop - offset,
          behavior: "smooth",
        });

        // Update URL
        if (history.pushState) {
          history.pushState(null, null, href);
        }
      });
    });
  }

  /**
   * FORM VALIDATION
   * Enhanced form validation with better UX
   */
  initFormValidation() {
    const forms = document.querySelectorAll("form[data-validate]");

    forms.forEach((form) => {
      const inputs = form.querySelectorAll("input[required], textarea[required]");

      inputs.forEach((input) => {
        input.addEventListener("blur", () => this.validateField(input));
        input.addEventListener("input", () => this.clearFieldError(input));
      });

      form.addEventListener("submit", (e) => {
        let isValid = true;

        inputs.forEach((input) => {
          if (!this.validateField(input)) {
            isValid = false;
          }
        });

        if (!isValid) {
          e.preventDefault();
          const firstError = form.querySelector(".has-error");
          if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }
      });
    });
  }

  /**
   * Validate form field
   */
  validateField(field) {
    if (!field.checkValidity()) {
      this.showFieldError(field, field.validationMessage);
      return false;
    }

    this.clearFieldError(field);
    return true;
  }

  /**
   * Show field error
   */
  showFieldError(field, message) {
    field.classList.add("has-error");

    let errorEl = field.parentElement.querySelector(".field-error");
    if (!errorEl) {
      errorEl = document.createElement("div");
      errorEl.className = "field-error";
      field.parentElement.appendChild(errorEl);
    }

    errorEl.textContent = message;
    field.setAttribute("aria-invalid", "true");
  }

  /**
   * Clear field error
   */
  clearFieldError(field) {
    field.classList.remove("has-error");
    field.removeAttribute("aria-invalid");

    const errorEl = field.parentElement.querySelector(".field-error");
    if (errorEl) {
      errorEl.remove();
    }
  }

  /**
   * UTILITY FUNCTIONS
   */

  decodeHTML(html) {
    const txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
  }

  getFromCache(key) {
    try {
      const cached = localStorage.getItem(key);
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      return null;
    }
  }

  saveToCache(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      // Quota exceeded or disabled
    }
  }
}

// Initialize app
const app = new EvidentApp();

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = EvidentApp;
}
