// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Modern Header Navigation - Interactive Functionality
 * Handles mobile menu, dropdowns, and accessibility
 */

(function () {
  "use strict";

  // Wait for DOM to be ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    initMobileMenu();
    initDropdowns();
    initThemeToggle();
    initKeyboardNavigation();
  }

  /**
   * Mobile Menu Toggle
   */
  function initMobileMenu() {
    const toggle = document.querySelector(".mobile-menu-toggle");
    const nav = document.querySelector(".nav-mobile");
    const overlay = document.querySelector(".mobile-nav-overlay");
    const closeBtn = document.querySelector(".mobile-nav-close");

    if (!toggle || !nav || !overlay) return;

    // Toggle mobile menu
    toggle.addEventListener("click", () => {
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";

      if (isExpanded) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });

    // Close button
    if (closeBtn) {
      closeBtn.addEventListener("click", closeMobileMenu);
    }

    // Overlay click
    overlay.addEventListener("click", closeMobileMenu);

    // Close on escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !nav.hidden) {
        closeMobileMenu();
        toggle.focus();
      }
    });

    function openMobileMenu() {
      toggle.setAttribute("aria-expanded", "true");
      nav.removeAttribute("hidden");
      overlay.classList.add("active");
      document.body.style.overflow = "hidden";

      // Focus first link in menu
      const firstLink = nav.querySelector(".mobile-nav-link");
      if (firstLink) {
        setTimeout(() => firstLink.focus(), 100);
      }
    }

    function closeMobileMenu() {
      toggle.setAttribute("aria-expanded", "false");
      nav.setAttribute("hidden", "");
      overlay.classList.remove("active");
      document.body.style.overflow = "";
    }

    // Handle mobile submenu toggles
    const submenuToggles = nav.querySelectorAll(".submenu-toggle");
    submenuToggles.forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", !isExpanded);
      });
    });
  }

  /**
   * Desktop Dropdown Menus
   */
  function initDropdowns() {
    const dropdowns = document.querySelectorAll(".has-dropdown");

    dropdowns.forEach((dropdown) => {
      const toggle = dropdown.querySelector(".dropdown-toggle");
      const menu = dropdown.querySelector(".dropdown-menu");

      if (!toggle || !menu) return;

      // Keyboard navigation
      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";
        closeAllDropdowns();

        if (!isExpanded) {
          toggle.setAttribute("aria-expanded", "true");
          // Focus first item in dropdown
          const firstLink = menu.querySelector(".dropdown-link");
          if (firstLink) {
            setTimeout(() => firstLink.focus(), 100);
          }
        }
      });

      // Close on escape
      dropdown.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          toggle.setAttribute("aria-expanded", "false");
          toggle.focus();
        }
      });

      // Arrow key navigation in dropdown
      menu.addEventListener("keydown", (e) => {
        const links = Array.from(menu.querySelectorAll(".dropdown-link"));
        const currentIndex = links.indexOf(document.activeElement);

        if (e.key === "ArrowDown") {
          e.preventDefault();
          const nextIndex = currentIndex + 1;
          if (links[nextIndex]) {
            links[nextIndex].focus();
          } else {
            links[0].focus();
          }
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          const prevIndex = currentIndex - 1;
          if (links[prevIndex]) {
            links[prevIndex].focus();
          } else {
            links[links.length - 1].focus();
          }
        }
      });
    });

    // Close dropdowns when clicking outside
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".has-dropdown")) {
        closeAllDropdowns();
      }
    });

    function closeAllDropdowns() {
      dropdowns.forEach((dropdown) => {
        const toggle = dropdown.querySelector(".dropdown-toggle");
        if (toggle) {
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  /**
   * Theme Toggle (Light/Dark Mode)
   */
  function initThemeToggle() {
    const toggleBtn = document.querySelector(".header-actions .icon-button:nth-child(2)");
    if (!toggleBtn) return;

    const lightIcon = toggleBtn.querySelector(".theme-icon-light");
    const darkIcon = toggleBtn.querySelector(".theme-icon-dark");

    // Check for saved theme preference or default to light
    const currentTheme = localStorage.getItem("theme") || "light";
    setTheme(currentTheme);

    toggleBtn.addEventListener("click", () => {
      const newTheme =
        document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(newTheme);
    });

    function setTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem("theme", theme);

      if (lightIcon && darkIcon) {
        if (theme === "dark") {
          lightIcon.style.display = "none";
          darkIcon.style.display = "block";
          toggleBtn.setAttribute("aria-label", "Switch to light mode");
        } else {
          lightIcon.style.display = "block";
          darkIcon.style.display = "none";
          toggleBtn.setAttribute("aria-label", "Switch to dark mode");
        }
      }
    }
  }

  /**
   * Enhanced Keyboard Navigation
   */
  function initKeyboardNavigation() {
    // Global search shortcut (Ctrl+K or Cmd+K)
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        const searchBtn = document.querySelector(".header-actions .icon-button:first-child");
        if (searchBtn) {
          searchBtn.click();
        }
      }
    });

    // Trap focus in mobile menu when open
    const mobileNav = document.querySelector(".nav-mobile");
    if (mobileNav) {
      mobileNav.addEventListener("keydown", (e) => {
        if (e.key === "Tab" && !mobileNav.hidden) {
          const focusableElements = mobileNav.querySelectorAll(
            'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
          );
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      });
    }
  }

  /**
   * Sticky Header on Scroll (adds shadow)
   */
  let lastScroll = 0;
  window.addEventListener("scroll", () => {
    const header = document.querySelector(".Evident-header");
    if (!header) return;

    const currentScroll = window.pageYOffset;

    if (currentScroll > 10) {
      header.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.1)";
    } else {
      header.style.boxShadow = "0 1px 2px 0 rgba(0, 0, 0, 0.05)";
    }

    lastScroll = currentScroll;
  });
})();
