// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * PAGE TRANSITIONS & SCROLL REVEALS
 *
 * Handles smooth page transitions and scroll-triggered animations
 * Uses Intersection Observer for performance
 */

(function () {
  "use strict";

  /**
   * Initialize scroll reveal animations
   */
  function initScrollReveal() {
    const revealElements = document.querySelectorAll(
      ".reveal-on-scroll, .scroll-reveal-left, .scroll-reveal-right, .scroll-reveal-up, .scale-reveal, .blur-reveal"
    );

    if (revealElements.length === 0) return;

    const observerOptions = {
      root: null,
      rootMargin: "0px 0px -100px 0px",
      threshold: 0.1,
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          // Optionally unobserve after revealing
          // observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    revealElements.forEach((el) => observer.observe(el));
  }

  /**
   * Create and manage progress bar
   */
  function createProgressBar() {
    const progressBar = document.createElement("div");
    progressBar.className = "page-transition-progress";
    document.body.appendChild(progressBar);
    return progressBar;
  }

  /**
   * Update progress bar
   */
  function updateProgress(progressBar, percent) {
    progressBar.style.width = `${percent}%`;
  }

  /**
   * Simulate page load progress
   */
  function simulateProgress(progressBar, duration = 300) {
    let progress = 0;
    const increment = 100 / (duration / 16); // 60fps

    progressBar.classList.add("is-loading");

    const interval = setInterval(() => {
      progress += increment;
      if (progress >= 95) {
        clearInterval(interval);
        progress = 95;
      }
      updateProgress(progressBar, progress);
    }, 16);

    return {
      complete: () => {
        clearInterval(interval);
        updateProgress(progressBar, 100);
        progressBar.classList.add("is-complete");
        setTimeout(() => {
          progressBar.classList.remove("is-loading", "is-complete");
          updateProgress(progressBar, 0);
        }, 300);
      },
    };
  }

  /**
   * Handle link clicks for smooth transitions
   */
  function initSmoothLinks(progressBar) {
    // Only for internal links
    const internalLinks = document.querySelectorAll('a[href^="/"], a[href^="./"], a[href^="../"]');

    internalLinks.forEach((link) => {
      // Skip if link has data-no-transition attribute
      if (link.hasAttribute("data-no-transition")) return;

      link.addEventListener("click", function (e) {
        const href = this.getAttribute("href");

        // Skip if it's a hash link or download
        if (href.startsWith("#") || this.hasAttribute("download")) return;

        e.preventDefault();

        // Start transition
        document.body.classList.add("is-transitioning");
        const progress = simulateProgress(progressBar);

        // Navigate after animation
        setTimeout(() => {
          progress.complete();
          window.location.href = href;
        }, 300);
      });
    });
  }

  /**
   * Handle browser back/forward buttons
   */
  function initPopStateHandler(progressBar) {
    window.addEventListener("popstate", () => {
      const progress = simulateProgress(progressBar, 200);
      setTimeout(() => {
        progress.complete();
      }, 200);
    });
  }

  /**
   * Add staggered animation classes to child elements
   */
  function initStaggeredAnimations() {
    const staggerContainers = document.querySelectorAll("[data-stagger]");

    staggerContainers.forEach((container) => {
      const children = Array.from(container.children);
      children.forEach((child, index) => {
        child.classList.add("reveal-on-scroll");
        child.style.transitionDelay = `${index * 0.1}s`;
      });
    });
  }

  /**
   * Lazy load images with fade-in
   */
  function initLazyImages() {
    const lazyImages = document.querySelectorAll("img[data-src]");

    if (lazyImages.length === 0) return;

    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.add("blur-reveal");

          img.addEventListener("load", () => {
            img.classList.add("is-visible");
            imageObserver.unobserve(img);
          });
        }
      });
    });

    lazyImages.forEach((img) => imageObserver.observe(img));
  }

  /**
   * Add animation to elements as they enter viewport
   */
  function animateOnScroll() {
    const elements = document.querySelectorAll(".animate-on-scroll");

    if (elements.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const animation = entry.target.dataset.animation || "fade-in";
            entry.target.classList.add(`animate-${animation}`);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.2,
      }
    );

    elements.forEach((el) => observer.observe(el));
  }

  /**
   * Initialize all transition features
   */
  function init() {
    // Skip if reduced motion is preferred
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    // Create progress bar
    const progressBar = createProgressBar();

    // Initialize features
    initScrollReveal();
    initStaggeredAnimations();
    initSmoothLinks(progressBar);
    initPopStateHandler(progressBar);
    initLazyImages();
    animateOnScroll();

    // Show initial progress
    const initialProgress = simulateProgress(progressBar, 200);
    window.addEventListener("load", () => {
      initialProgress.complete();
    });

    // Remove transitioning class after page load
    window.addEventListener("pageshow", () => {
      document.body.classList.remove("is-transitioning");
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
