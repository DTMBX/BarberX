// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * ELEGANT HEADER NAVIGATION SYSTEM
 * Interactive JavaScript for desktop dropdowns and mobile drawer
 *
 * Features:
 * - Smooth dropdown menus with keyboard navigation
 * - Elegant mobile drawer with animations
 * - Accessibility support (ARIA, focus management, keyboard)
 * - Scroll detection for header styling
 * - Trap focus in mobile drawer
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
    initScrollDetection();
    initDesktopDropdowns();
    initMobileDrawer();
    initKeyboardShortcuts();
  }

  /**
   * Scroll Detection
   * Add class to header when scrolled for visual feedback
   */
  function initScrollDetection() {
    const header = document.querySelector(".elegant-header");
    if (!header) return;

    let lastScroll = 0;
    let ticking = false;

    window.addEventListener(
      "scroll",
      () => {
        lastScroll = window.pageYOffset;

        if (!ticking) {
          window.requestAnimationFrame(() => {
            if (lastScroll > 10) {
              header.classList.add("scrolled");
            } else {
              header.classList.remove("scrolled");
            }
            ticking = false;
          });
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  /**
   * Desktop Dropdown Menus
   * Handles hover and keyboard navigation
   */
  function initDesktopDropdowns() {
    const dropdownItems = document.querySelectorAll(".elegant-nav__item--dropdown");

    dropdownItems.forEach((item) => {
      const toggle = item.querySelector(".elegant-nav__link");
      const dropdown = item.querySelector(".elegant-dropdown");

      if (!toggle || !dropdown) return;

      // Click to toggle
      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";

        // Close all other dropdowns
        closeAllDropdowns();

        if (!isExpanded) {
          openDropdown(toggle, dropdown);
        }
      });

      // Hover to open (desktop only)
      if (window.innerWidth >= 1024) {
        item.addEventListener("mouseenter", () => {
          closeAllDropdowns();
          openDropdown(toggle, dropdown);
        });

        item.addEventListener("mouseleave", () => {
          closeDropdown(toggle, dropdown);
        });
      }

      // Escape to close
      item.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          closeDropdown(toggle, dropdown);
          toggle.focus();
        }
      });

      // Arrow key navigation in dropdown
      const links = dropdown.querySelectorAll(".elegant-dropdown__link");
      links.forEach((link, index) => {
        link.addEventListener("keydown", (e) => {
          if (e.key === "ArrowDown") {
            e.preventDefault();
            const nextLink = links[index + 1] || links[0];
            nextLink.focus();
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            const prevLink = links[index - 1] || links[links.length - 1];
            prevLink.focus();
          }
        });
      });
    });

    // Close dropdowns when clicking outside
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".elegant-nav__item--dropdown")) {
        closeAllDropdowns();
      }
    });

    function openDropdown(toggle, dropdown) {
      toggle.setAttribute("aria-expanded", "true");
      // Dropdown visibility is handled by CSS :hover and aria-expanded
    }

    function closeDropdown(toggle, dropdown) {
      toggle.setAttribute("aria-expanded", "false");
    }

    function closeAllDropdowns() {
      dropdownItems.forEach((item) => {
        const toggle = item.querySelector(".elegant-nav__link");
        if (toggle) {
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  /**
   * Mobile Navigation Drawer
   * Handles opening, closing, and expandable menus
   */
  function initMobileDrawer() {
    const toggle = document.querySelector(".elegant-mobile-toggle");
    const drawer = document.querySelector(".elegant-drawer");
    const overlay = document.querySelector(".elegant-drawer-overlay");
    const closeBtn = document.querySelector(".drawer-close");

    if (!toggle || !drawer || !overlay) return;

    let lastFocusedElement = null;

    // Open drawer
    toggle.addEventListener("click", () => {
      if (drawer.getAttribute("aria-hidden") === "true") {
        openDrawer();
      } else {
        closeDrawer();
      }
    });

    // Close button
    if (closeBtn) {
      closeBtn.addEventListener("click", closeDrawer);
    }

    // Overlay click
    overlay.addEventListener("click", closeDrawer);

    // Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.getAttribute("aria-hidden") === "false") {
        closeDrawer();
        toggle.focus();
      }
    });

    // Handle expandable submenus
    const expandableLinks = drawer.querySelectorAll(
      ".drawer-nav__item--expandable .drawer-nav__link"
    );
    expandableLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const isExpanded = link.getAttribute("aria-expanded") === "true";

        // Close all other submenus
        expandableLinks.forEach((otherLink) => {
          if (otherLink !== link) {
            otherLink.setAttribute("aria-expanded", "false");
          }
        });

        // Toggle current submenu
        link.setAttribute("aria-expanded", !isExpanded);
      });
    });

    // Close drawer on link click (except expandable toggles)
    const drawerLinks = drawer.querySelectorAll(
      ".drawer-nav__link:not(.drawer-nav__item--expandable .drawer-nav__link), .drawer-submenu__link"
    );
    drawerLinks.forEach((link) => {
      link.addEventListener("click", () => {
        // Small delay for smooth transition
        setTimeout(closeDrawer, 150);
      });
    });

    function openDrawer() {
      lastFocusedElement = document.activeElement;

      toggle.setAttribute("aria-expanded", "true");
      drawer.setAttribute("aria-hidden", "false");
      overlay.setAttribute("aria-hidden", "false");
      document.body.classList.add("drawer-open");

      // Focus first link
      const firstLink = drawer.querySelector(".drawer-nav__link");
      if (firstLink) {
        setTimeout(() => firstLink.focus(), 100);
      }

      // Trap focus in drawer
      trapFocus(drawer);
    }

    function closeDrawer() {
      toggle.setAttribute("aria-expanded", "false");
      drawer.setAttribute("aria-hidden", "true");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("drawer-open");

      // Restore focus
      if (lastFocusedElement) {
        lastFocusedElement.focus();
      }
    }

    /**
     * Trap focus within drawer when open
     */
    function trapFocus(element) {
      const focusableElements = element.querySelectorAll(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      element.addEventListener("keydown", handleTabKey);

      function handleTabKey(e) {
        if (e.key !== "Tab") return;

        if (element.getAttribute("aria-hidden") === "true") {
          element.removeEventListener("keydown", handleTabKey);
          return;
        }

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    }
  }

  /**
   * Keyboard Shortcuts
   * Global keyboard shortcuts for better UX
   */
  function initKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
      // Ctrl+K or Cmd+K for search
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        const searchBtn = document.querySelector(".elegant-icon-btn");
        if (searchBtn) {
          searchBtn.click();
        }
      }

      // Ctrl+M or Cmd+M for mobile menu
      if ((e.ctrlKey || e.metaKey) && e.key === "m") {
        e.preventDefault();
        const mobileToggle = document.querySelector(".elegant-mobile-toggle");
        if (mobileToggle && window.innerWidth < 1024) {
          mobileToggle.click();
        }
      }
    });
  }

  /**
   * Handle window resize
   * Close mobile drawer when resizing to desktop
   */
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 1024) {
        const drawer = document.querySelector(".elegant-drawer");
        const overlay = document.querySelector(".elegant-drawer-overlay");
        const toggle = document.querySelector(".elegant-mobile-toggle");

        if (drawer && drawer.getAttribute("aria-hidden") === "false") {
          drawer.setAttribute("aria-hidden", "true");
          overlay.setAttribute("aria-hidden", "true");
          toggle.setAttribute("aria-expanded", "false");
          document.body.classList.remove("drawer-open");
        }
      }
    }, 250);
  });

  /**
   * Smooth scroll for anchor links
   */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (!href || href === "#") return;

      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();

      const header = document.querySelector(".elegant-header");
      const headerHeight = header ? header.offsetHeight : 0;
      const targetPosition =
        target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      });

      // Update URL
      history.pushState(null, "", href);

      // Focus target for accessibility
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      setTimeout(() => target.removeAttribute("tabindex"), 1000);
    });
  });
})();
