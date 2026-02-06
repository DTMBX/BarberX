// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Premium Navigation
 * Mobile menu toggle and scroll behavior
 */

(function () {
  "use strict";

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    initMobileNav();
    initScrollBehavior();
  }

  /**
   * Mobile Navigation
   */
  function initMobileNav() {
    const toggle = document.querySelector(".premium-nav-toggle");
    const mobileNav = document.querySelector(".premium-nav--mobile");
    const closeBtn = document.querySelector(".premium-nav__close");
    const overlay = document.querySelector(".premium-nav-overlay");

    if (!toggle || !mobileNav) return;

    // Open menu
    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      isOpen ? closeMenu() : openMenu();
    });

    // Close button
    if (closeBtn) {
      closeBtn.addEventListener("click", closeMenu);
    }

    // Overlay click
    if (overlay) {
      overlay.addEventListener("click", closeMenu);
    }

    // Close on escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && mobileNav.classList.contains("is-open")) {
        closeMenu();
        toggle.focus();
      }
    });

    // Close when clicking nav links
    mobileNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeMenu);
    });

    function openMenu() {
      toggle.setAttribute("aria-expanded", "true");
      mobileNav.classList.add("is-open");
      mobileNav.setAttribute("aria-hidden", "false");
      if (overlay) overlay.classList.add("is-visible");
      document.body.style.overflow = "hidden";

      // Focus first link
      const firstLink = mobileNav.querySelector("a");
      if (firstLink) setTimeout(() => firstLink.focus(), 100);
    }

    function closeMenu() {
      toggle.setAttribute("aria-expanded", "false");
      mobileNav.classList.remove("is-open");
      mobileNav.setAttribute("aria-hidden", "true");
      if (overlay) overlay.classList.remove("is-visible");
      document.body.style.overflow = "";
    }
  }

  /**
   * Scroll Behavior - add shadow on scroll
   */
  function initScrollBehavior() {
    const header = document.getElementById("siteHeader");
    if (!header) return;

    let ticking = false;

    window.addEventListener("scroll", () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (window.pageYOffset > 10) {
            header.classList.add("is-scrolled");
          } else {
            header.classList.remove("is-scrolled");
          }
          ticking = false;
        });
        ticking = true;
      }
    });
  }
})();
