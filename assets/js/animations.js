// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * MICRO-ANIMATIONS & PROGRESSIVE DISCLOSURE
 * Intersection Observer for fade-in effects
 */

(function () {
  "use strict";

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion) {
    // Skip animations for users who prefer reduced motion
    return;
  }

  // ==========================================================================
  // FADE IN ON SCROLL
  // ==========================================================================

  const observerOptions = {
    root: null,
    rootMargin: "0px 0px -100px 0px",
    threshold: 0.1,
  };

  const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        // Unobserve after animation to improve performance
        fadeInObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all fade-in elements
  document.querySelectorAll(".fade-in-up, .stagger-fade").forEach((el) => {
    fadeInObserver.observe(el);
  });

  // ==========================================================================
  // SCROLL PROGRESS INDICATOR
  // ==========================================================================

  const scrollProgress = document.createElement("div");
  scrollProgress.className = "scroll-progress";
  scrollProgress.setAttribute("aria-hidden", "true");
  document.body.appendChild(scrollProgress);

  function updateScrollProgress() {
    const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    scrollProgress.style.transform = `scaleX(${scrolled / 100})`;
  }

  let scrollTicking = false;
  window.addEventListener("scroll", () => {
    if (!scrollTicking) {
      window.requestAnimationFrame(() => {
        updateScrollProgress();
        scrollTicking = false;
      });
      scrollTicking = true;
    }
  });

  // ==========================================================================
  // PROGRESSIVE DISCLOSURE / ACCORDION
  // ==========================================================================

  function initDisclosure() {
    const triggers = document.querySelectorAll("[data-disclosure-trigger]");

    triggers.forEach((trigger) => {
      trigger.addEventListener("click", function () {
        const targetId = this.getAttribute("data-disclosure-trigger");
        const content = document.getElementById(targetId);

        if (!content) return;

        const isExpanded = this.getAttribute("aria-expanded") === "true";

        // Toggle expanded state
        this.setAttribute("aria-expanded", !isExpanded);

        if (isExpanded) {
          content.hidden = true;
        } else {
          content.hidden = false;
        }
      });
    });
  }

  // ==========================================================================
  // COUNT-UP ANIMATION
  // ==========================================================================

  function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }
      element.textContent = Math.floor(current).toLocaleString();
    }, 16);
  }

  const countUpObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const element = entry.target;
        const endValue = parseInt(element.getAttribute("data-count-to")) || 0;
        animateValue(element, 0, endValue, 2000);
        countUpObserver.unobserve(element);
      }
    });
  }, observerOptions);

  document.querySelectorAll(".count-up").forEach((el) => {
    countUpObserver.observe(el);
  });

  // ==========================================================================
  // SMOOTH SCROLL TO ANCHOR
  // ==========================================================================

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");

      // Skip if href is just "#"
      if (href === "#") return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

        // Update URL without triggering scroll
        if (history.pushState) {
          history.pushState(null, null, href);
        }

        // Focus target for accessibility
        target.focus({ preventScroll: true });
      }
    });
  });

  // ==========================================================================
  // RIPPLE EFFECT ON BUTTONS
  // ==========================================================================

  function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement("span");
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + "px";
    ripple.style.left = x + "px";
    ripple.style.top = y + "px";
    ripple.classList.add("ripple");

    button.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  document.querySelectorAll(".btn").forEach((button) => {
    button.addEventListener("click", createRipple);
  });

  // ==========================================================================
  // LAZY LOAD IMAGES
  // ==========================================================================

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.getAttribute("data-src");

        if (src) {
          img.src = src;
          img.removeAttribute("data-src");
          img.classList.remove("lazy");
          img.classList.add("loaded");
        }

        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll("img[data-src]").forEach((img) => {
    imageObserver.observe(img);
  });

  // ==========================================================================
  // INITIALIZE ON DOM READY
  // ==========================================================================

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDisclosure);
  } else {
    initDisclosure();
  }

  // ==========================================================================
  // ACTIVE NAV HIGHLIGHTING
  // ==========================================================================

  const sections = document.querySelectorAll("section[id]");
  const navItems = document.querySelectorAll('.nav-item[href^="#"]');

  function highlightNav() {
    let currentSection = "";

    sections.forEach((section) => {
      const sectionTop = section.offsetTop;

      if (window.pageYOffset >= sectionTop - 200) {
        currentSection = section.getAttribute("id");
      }
    });

    navItems.forEach((item) => {
      item.classList.remove("active");
      if (item.getAttribute("href") === "#" + currentSection) {
        item.classList.add("active");
      }
    });
  }

  window.addEventListener("scroll", () => {
    if (!scrollTicking) {
      window.requestAnimationFrame(() => {
        highlightNav();
        scrollTicking = false;
      });
      scrollTicking = true;
    }
  });

  // ==========================================================================
  // PARALLAX EFFECT (Subtle)
  // ==========================================================================

  const parallaxElements = document.querySelectorAll("[data-parallax]");

  if (parallaxElements.length > 0) {
    window.addEventListener("scroll", () => {
      parallaxElements.forEach((el) => {
        const speed = el.getAttribute("data-parallax") || 0.5;
        const yPos = -(window.pageYOffset * speed);
        el.style.transform = `translateY(${yPos}px)`;
      });
    });
  }
})();
