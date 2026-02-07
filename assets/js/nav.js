// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Premium Navigation System
 *
 * Features:
 * - Smooth slide-from-right mobile drawer
 * - Nested dropdown/submenu support
 * - Focus trap for accessibility
 * - Keyboard navigation (Escape, Tab, Arrow keys)
 * - High contrast brass/gold accents
 * - Performance optimized with RAF
 */
(function () {
  "use strict";

  // Selectors
  var SELECTORS = {
    toggle: ".premium-nav-toggle",
    nav: "#premium-nav-mobile",
    overlay: ".premium-nav-overlay",
    closeBtn: ".premium-nav__close",
    submenuToggle: ".premium-nav__submenu-toggle",
    submenu: ".premium-nav__submenu",
    dropdownToggle: ".premium-nav__dropdown-toggle",
    dropdown: ".premium-nav__dropdown",
    link: ".premium-nav__link",
    header: ".premium-header",
  };

  // State
  var state = {
    isOpen: false,
    initialized: false,
  };

  /**
   * Get all focusable elements within a container
   */
  function getFocusableElements(container) {
    return container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
  }

  /**
   * Create and append the overlay element
   */
  function createOverlay() {
    var existing = document.querySelector(SELECTORS.overlay);
    if (existing) return existing;

    var overlay = document.createElement("div");
    overlay.className = "premium-nav-overlay";
    overlay.setAttribute("aria-hidden", "true");
    document.body.appendChild(overlay);
    return overlay;
  }

  /**
   * Open the mobile navigation drawer
   */
  function openNav(toggle, nav, overlay) {
    if (state.isOpen) return;

    requestAnimationFrame(function () {
      state.isOpen = true;

      // Update ARIA and classes
      nav.classList.add("is-open");
      nav.setAttribute("aria-hidden", "false");
      toggle.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      overlay.classList.add("is-visible");

      // Lock body scroll
      document.body.style.overflow = "hidden";
      document.body.classList.add("nav-open");

      // Focus first focusable element
      var focusable = getFocusableElements(nav);
      if (focusable.length) {
        setTimeout(function () {
          focusable[0].focus({ preventScroll: true });
        }, 100);
      }
    });
  }

  /**
   * Close the mobile navigation drawer
   */
  function closeNav(toggle, nav, overlay, restoreFocus) {
    if (!state.isOpen) return;

    requestAnimationFrame(function () {
      state.isOpen = false;

      // Update ARIA and classes
      nav.classList.remove("is-open");
      nav.setAttribute("aria-hidden", "true");
      toggle.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      overlay.classList.remove("is-visible");

      // Unlock body scroll
      document.body.style.overflow = "";
      document.body.classList.remove("nav-open");

      // Close any open submenus
      closeAllSubmenus(nav);

      // Restore focus to toggle button
      if (restoreFocus) {
        setTimeout(function () {
          toggle.focus({ preventScroll: true });
        }, 50);
      }
    });
  }

  /**
   * Close all open submenus
   */
  function closeAllSubmenus(nav) {
    var openSubmenus = nav.querySelectorAll(SELECTORS.submenu + ".is-open");
    var openToggles = nav.querySelectorAll(SELECTORS.submenuToggle + "[aria-expanded='true']");

    openSubmenus.forEach(function (submenu) {
      submenu.classList.remove("is-open");
    });

    openToggles.forEach(function (toggle) {
      toggle.setAttribute("aria-expanded", "false");
    });
  }

  /**
   * Toggle a submenu (accordion style)
   */
  function toggleSubmenu(toggleBtn) {
    var parentItem = toggleBtn.closest(".premium-nav__item--has-children");
    if (!parentItem) return;

    var submenu = parentItem.querySelector(SELECTORS.submenu);
    if (!submenu) return;

    var isOpen = submenu.classList.contains("is-open");

    // Close other submenus (accordion behavior)
    var nav = toggleBtn.closest(SELECTORS.nav);
    if (nav) closeAllSubmenus(nav);

    // Toggle this submenu
    if (!isOpen) {
      submenu.classList.add("is-open");
      toggleBtn.setAttribute("aria-expanded", "true");
    }
  }

  /**
   * Toggle desktop dropdown
   */
  function toggleDropdown(toggleBtn) {
    var parentItem = toggleBtn.closest(".premium-nav__item--has-dropdown");
    if (!parentItem) return;

    var dropdown = parentItem.querySelector(SELECTORS.dropdown);
    if (!dropdown) return;

    var isOpen = dropdown.classList.contains("is-open");

    // Close other dropdowns
    document.querySelectorAll(SELECTORS.dropdown + ".is-open").forEach(function (d) {
      d.classList.remove("is-open");
      var t = d.closest(".premium-nav__item--has-dropdown").querySelector(SELECTORS.dropdownToggle);
      if (t) t.setAttribute("aria-expanded", "false");
    });

    // Toggle this dropdown
    if (!isOpen) {
      dropdown.classList.add("is-open");
      toggleBtn.setAttribute("aria-expanded", "true");
    }
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeydown(e, toggle, nav, overlay) {
    if (!state.isOpen) return;

    // Escape key closes nav
    if (e.key === "Escape") {
      e.preventDefault();
      closeNav(toggle, nav, overlay, true);
      return;
    }

    // Tab key focus trap
    if (e.key === "Tab") {
      var focusable = getFocusableElements(nav);
      if (!focusable.length) return;

      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      var active = document.activeElement;

      if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  /**
   * Handle scroll for header shrink effect
   */
  function handleScroll() {
    var header = document.querySelector(SELECTORS.header);
    if (!header) return;

    if (window.scrollY > 50) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  }

  /**
   * Initialize the navigation system
   */
  function initNav() {
    var toggle = document.querySelector(SELECTORS.toggle);
    var nav = document.getElementById("premium-nav-mobile");

    // Exit if already initialized or missing elements
    if (!toggle || !nav || state.initialized) {
      return;
    }

    state.initialized = true;

    var overlay = createOverlay();
    var closeBtn = nav.querySelector(SELECTORS.closeBtn);

    // Set initial ARIA states
    toggle.setAttribute("aria-expanded", "false");
    nav.setAttribute("aria-hidden", "true");

    // Toggle button click
    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      if (state.isOpen) {
        closeNav(toggle, nav, overlay, false);
      } else {
        openNav(toggle, nav, overlay);
      }
    });

    // Close button click
    if (closeBtn) {
      closeBtn.addEventListener("click", function (e) {
        e.preventDefault();
        closeNav(toggle, nav, overlay, true);
      });
    }

    // Overlay click closes nav
    overlay.addEventListener("click", function () {
      closeNav(toggle, nav, overlay, true);
    });

    // Link clicks close nav (after small delay for smooth UX)
    nav.addEventListener("click", function (e) {
      var link = e.target.closest("a");
      if (link && state.isOpen) {
        setTimeout(function () {
          closeNav(toggle, nav, overlay, false);
        }, 150);
      }
    });

    // Submenu toggles
    var submenuToggles = nav.querySelectorAll(SELECTORS.submenuToggle);
    submenuToggles.forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        toggleSubmenu(btn);
      });
    });

    // Desktop dropdown toggles
    document.querySelectorAll(SELECTORS.dropdownToggle).forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        toggleDropdown(btn);
      });

      // Close on mouse leave (desktop)
      var parentItem = btn.closest(".premium-nav__item--has-dropdown");
      if (parentItem) {
        parentItem.addEventListener("mouseleave", function () {
          var dropdown = parentItem.querySelector(SELECTORS.dropdown);
          if (dropdown) {
            dropdown.classList.remove("is-open");
            btn.setAttribute("aria-expanded", "false");
          }
        });
      }
    });

    // Keyboard handler
    document.addEventListener("keydown", function (e) {
      handleKeydown(e, toggle, nav, overlay);
    });

    // Scroll handler for header effect
    var scrollTimeout;
    window.addEventListener(
      "scroll",
      function () {
        if (scrollTimeout) return;
        scrollTimeout = setTimeout(function () {
          handleScroll();
          scrollTimeout = null;
        }, 10);
      },
      { passive: true }
    );

    // Close on resize to desktop
    var resizeTimeout;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(function () {
        if (window.innerWidth >= 1025 && state.isOpen) {
          closeNav(toggle, nav, overlay, false);
        }
      }, 150);
    });

    // Close dropdowns on click outside (desktop)
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".premium-nav__item--has-dropdown")) {
        document.querySelectorAll(SELECTORS.dropdown + ".is-open").forEach(function (d) {
          d.classList.remove("is-open");
          var t = d
            .closest(".premium-nav__item--has-dropdown")
            .querySelector(SELECTORS.dropdownToggle);
          if (t) t.setAttribute("aria-expanded", "false");
        });
      }
    });

    // Initial scroll check
    handleScroll();
  }

  /**
   * DOM Ready helper
   */
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  // Initialize on DOM ready
  ready(function () {
    if (typeof window !== "undefined") {
      window.FFNav = window.FFNav || {};
      window.FFNav.initNav = initNav;
      window.FFNav.state = state;
    }
    initNav();
  });
})();
