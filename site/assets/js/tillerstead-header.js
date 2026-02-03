/**
 * TILLERSTEAD SANCTUARY NAVIGATION SYSTEM
 * Interactive JavaScript for desktop dropdowns and mobile drawer
 * Peaceful, sanctuary-inspired interactions
 */

(function () {
  "use strict";

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    initScrollDetection();
    initDesktopDropdowns();
    initMobileDrawer();
    initSmoothScroll();
  }

  /**
   * Scroll Detection - add class to header when scrolled
   */
  function initScrollDetection() {
    const header = document.querySelector(".tillerstead-header");
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
      { passive: true },
    );
  }

  /**
   * Desktop Dropdown Menus
   */
  function initDesktopDropdowns() {
    const dropdownItems = document.querySelectorAll(
      ".tillerstead-nav__item--dropdown",
    );

    dropdownItems.forEach((item) => {
      const toggle = item.querySelector(".tillerstead-nav__link");
      const dropdown = item.querySelector(".tillerstead-dropdown");

      if (!toggle || !dropdown) return;

      // Click to toggle
      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";

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

      // Arrow key navigation
      const links = dropdown.querySelectorAll(".tillerstead-dropdown__link");
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
      if (!e.target.closest(".tillerstead-nav__item--dropdown")) {
        closeAllDropdowns();
      }
    });

    function openDropdown(toggle, dropdown) {
      toggle.setAttribute("aria-expanded", "true");
    }

    function closeDropdown(toggle, dropdown) {
      toggle.setAttribute("aria-expanded", "false");
    }

    function closeAllDropdowns() {
      dropdownItems.forEach((item) => {
        const toggle = item.querySelector(".tillerstead-nav__link");
        if (toggle) {
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  /**
   * Mobile Navigation Drawer
   */
  function initMobileDrawer() {
    const toggle = document.querySelector(".tillerstead-mobile-toggle");
    const drawer = document.querySelector(".tillerstead-drawer");
    const overlay = document.querySelector(".tillerstead-drawer-overlay");
    const closeBtn = document.querySelector(".drawer-close");

    if (!toggle || !drawer || !overlay) return;

    let lastFocusedElement = null;

    // Open/close drawer
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
      if (
        e.key === "Escape" &&
        drawer.getAttribute("aria-hidden") === "false"
      ) {
        closeDrawer();
        toggle.focus();
      }
    });

    // Expandable submenus
    const expandableLinks = drawer.querySelectorAll(
      ".drawer-nav__item--expandable .drawer-nav__link",
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

    // Close drawer on link click
    const drawerLinks = drawer.querySelectorAll(
      ".drawer-nav__link:not(.drawer-nav__item--expandable .drawer-nav__link), .drawer-submenu__link",
    );
    drawerLinks.forEach((link) => {
      link.addEventListener("click", () => {
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

      trapFocus(drawer);
    }

    function closeDrawer() {
      toggle.setAttribute("aria-expanded", "false");
      drawer.setAttribute("aria-hidden", "true");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("drawer-open");

      if (lastFocusedElement) {
        lastFocusedElement.focus();
      }
    }

    function trapFocus(element) {
      const focusableElements = element.querySelectorAll(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
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
   * Smooth Scroll for Anchor Links
   */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const href = this.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        const header = document.querySelector(".tillerstead-header");
        const headerHeight = header ? header.offsetHeight : 0;
        const targetPosition =
          target.getBoundingClientRect().top +
          window.pageYOffset -
          headerHeight -
          20;

        window.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        });

        history.pushState(null, "", href);

        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        setTimeout(() => target.removeAttribute("tabindex"), 1000);
      });
    });
  }

  /**
   * Handle Window Resize - close drawer on desktop
   */
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 1024) {
        const drawer = document.querySelector(".tillerstead-drawer");
        const overlay = document.querySelector(".tillerstead-drawer-overlay");
        const toggle = document.querySelector(".tillerstead-mobile-toggle");

        if (drawer && drawer.getAttribute("aria-hidden") === "false") {
          drawer.setAttribute("aria-hidden", "true");
          overlay.setAttribute("aria-hidden", "true");
          toggle.setAttribute("aria-expanded", "false");
          document.body.classList.remove("drawer-open");
        }
      }
    }, 250);
  });
})();
