// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * MOBILE NAVIGATION DRAWER
 *
 * Modern slide-out navigation with:
 * - Animated hamburger icon (3-line → X)
 * - Smooth slide-in drawer from right
 * - Backdrop overlay with blur effect
 * - Body scroll lock when open
 * - ESC key support
 * - Touch gesture support (swipe to close)
 * - Accessible (ARIA, keyboard navigation)
 * - Nested submenu support
 */

(function () {
  "use strict";

  // Configuration
  const CONFIG = {
    breakpoint: 1024,
    drawerWidth: "85%",
    maxDrawerWidth: "400px",
    animationDuration: 300,
    swipeThreshold: 50,
    backdropBlur: "8px",
  };

  // State
  let isOpen = false;
  let touchStartX = 0;
  let touchCurrentX = 0;
  let isDragging = false;

  // Elements
  const hamburger = document.querySelector(".mobile-nav-hamburger");
  const drawer = document.querySelector(".mobile-nav-drawer");
  const backdrop = document.querySelector(".mobile-nav-backdrop");
  const closeBtn = document.querySelector(".mobile-nav-close");
  const body = document.body;

  // Initialize if elements exist
  if (hamburger && drawer && backdrop) {
    init();
  }

  function init() {
    // Event listeners
    hamburger.addEventListener("click", toggleDrawer);
    backdrop.addEventListener("click", closeDrawer);
    closeBtn?.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", handleKeyPress);

    // Touch gestures
    drawer.addEventListener("touchstart", handleTouchStart, { passive: true });
    drawer.addEventListener("touchmove", handleTouchMove, { passive: false });
    drawer.addEventListener("touchend", handleTouchEnd, { passive: true });

    // Window resize
    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        if (window.innerWidth > CONFIG.breakpoint && isOpen) {
          closeDrawer();
        }
      }, 250);
    });

    // Close on link click
    const navLinks = drawer.querySelectorAll("a:not([data-submenu-toggle])");
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        setTimeout(closeDrawer, 100);
      });
    });

    // Submenu toggles
    const submenuToggles = drawer.querySelectorAll("[data-submenu-toggle]");
    submenuToggles.forEach((toggle) => {
      toggle.addEventListener("click", handleSubmenuToggle);
    });
  }

  function toggleDrawer(e) {
    e?.preventDefault();
    isOpen ? closeDrawer() : openDrawer();
  }

  function openDrawer() {
    isOpen = true;

    // Update elements
    hamburger.classList.add("is-active");
    hamburger.setAttribute("aria-expanded", "true");
    hamburger.setAttribute("aria-label", "Close navigation menu");

    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");

    backdrop.classList.add("is-visible");

    // Lock body scroll
    lockBodyScroll();

    // Focus first link for accessibility
    setTimeout(() => {
      const firstLink = drawer.querySelector("a, button");
      firstLink?.focus();
    }, CONFIG.animationDuration);

    // Announce to screen readers
    announceToScreenReader("Navigation menu opened");
  }

  function closeDrawer() {
    if (!isOpen) return;

    isOpen = false;

    // Update elements
    hamburger.classList.remove("is-active");
    hamburger.setAttribute("aria-expanded", "false");
    hamburger.setAttribute("aria-label", "Open navigation menu");

    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");

    backdrop.classList.remove("is-visible");

    // Unlock body scroll
    unlockBodyScroll();

    // Return focus to hamburger
    hamburger.focus();

    // Announce to screen readers
    announceToScreenReader("Navigation menu closed");
  }

  function handleKeyPress(e) {
    if (e.key === "Escape" && isOpen) {
      closeDrawer();
    }
  }

  // Touch gesture handling
  function handleTouchStart(e) {
    if (!isOpen) return;
    touchStartX = e.touches[0].clientX;
    isDragging = true;
  }

  function handleTouchMove(e) {
    if (!isDragging || !isOpen) return;

    touchCurrentX = e.touches[0].clientX;
    const deltaX = touchCurrentX - touchStartX;

    // Only allow swipe to right (close)
    if (deltaX > 0) {
      const translateX = Math.min(deltaX, drawer.offsetWidth);
      drawer.style.transform = `translateX(${translateX}px)`;

      // Fade backdrop proportionally
      const opacity = 1 - translateX / drawer.offsetWidth;
      backdrop.style.opacity = opacity;

      e.preventDefault();
    }
  }

  function handleTouchEnd(e) {
    if (!isDragging || !isOpen) return;

    isDragging = false;
    const deltaX = touchCurrentX - touchStartX;

    // Reset styles
    drawer.style.transform = "";
    backdrop.style.opacity = "";

    // Close if swiped past threshold
    if (deltaX > CONFIG.swipeThreshold) {
      closeDrawer();
    }

    touchStartX = 0;
    touchCurrentX = 0;
  }

  // Submenu handling
  function handleSubmenuToggle(e) {
    e.preventDefault();
    const toggle = e.currentTarget;
    const submenu = toggle.nextElementSibling;
    const isExpanded = toggle.getAttribute("aria-expanded") === "true";

    // Toggle state
    toggle.setAttribute("aria-expanded", !isExpanded);
    toggle.classList.toggle("is-active");

    if (submenu) {
      submenu.classList.toggle("is-open");

      // Smooth height animation
      if (!isExpanded) {
        submenu.style.maxHeight = submenu.scrollHeight + "px";
      } else {
        submenu.style.maxHeight = "0";
      }
    }
  }

  // Body scroll lock
  function lockBodyScroll() {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    body.style.overflow = "hidden";
    body.style.paddingRight = `${scrollbarWidth}px`;
  }

  function unlockBodyScroll() {
    body.style.overflow = "";
    body.style.paddingRight = "";
  }

  // Accessibility announcements
  function announceToScreenReader(message) {
    const announcement = document.createElement("div");
    announcement.setAttribute("role", "status");
    announcement.setAttribute("aria-live", "polite");
    announcement.className = "sr-only";
    announcement.textContent = message;

    body.appendChild(announcement);

    setTimeout(() => {
      announcement.remove();
    }, 1000);
  }

  // Public API
  window.MobileNav = {
    open: openDrawer,
    close: closeDrawer,
    toggle: toggleDrawer,
    isOpen: () => isOpen,
  };
})();
