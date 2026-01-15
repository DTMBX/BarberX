/**
 * PREMIUM HEADER INTERACTIONS
 *
 * Handles scroll-triggered animations and mobile navigation.
 * Optimized for performance with requestAnimationFrame.
 *
 * Fixes / upgrades:
 * - Null-safe guards (header/nav may not exist on every page)
 * - Robust current-page highlighting (handles trailing slashes + relative URLs)
 * - Smooth-scroll only for same-page anchors (won't break /opra/#section)
 * - Mobile nav: ESC, overlay, focus management, body scroll lock, and cleanup
 * - Avoids forcing focus on toggle when nav wasn't opened (e.g., desktop)
 */

(function () {
  'use strict';

  // Configuration
  const SCROLL_THRESHOLD = 50;
  const SCROLL_CLASS = 'is-scrolled';
  const MOBILE_BREAKPOINT = 1024;

  // Elements
  const header = document.querySelector('.premium-header');
  const navToggle = document.querySelector('.premium-nav-toggle');
  const nav = document.querySelector('.premium-nav--mobile');
  const navClose = document.querySelector('.premium-nav__close');
  const navLinks = document.querySelectorAll('.premium-nav--mobile .premium-nav__link');

  // State
  let lastScroll = 0;
  let ticking = false;
  let navOverlay = null;
  let lastFocusedEl = null;

  // -------------------------
  // Scroll handling (RAF)
  // -------------------------

  function handleScroll() {
    lastScroll = window.pageYOffset || document.documentElement.scrollTop || 0;

    if (!ticking) {
      window.requestAnimationFrame(() => {
        updateHeaderState(lastScroll);
        ticking = false;
      });
      ticking = true;
    }
  }

  function updateHeaderState(scrollPos) {
    if (!header) return;

    if (scrollPos > SCROLL_THRESHOLD) {
      header.classList.add(SCROLL_CLASS);
    } else {
      header.classList.remove(SCROLL_CLASS);
    }
  }

  // -------------------------
  // Mobile nav overlay
  // -------------------------

  function createNavOverlay() {
    if (navOverlay) return navOverlay;

    navOverlay = document.createElement('div');
    navOverlay.className = 'premium-nav-overlay';
    navOverlay.setAttribute('aria-hidden', 'true');
    navOverlay.addEventListener('click', closeNav);
    document.body.appendChild(navOverlay);

    return navOverlay;
  }

  // -------------------------
  // Mobile nav open/close
  // -------------------------

  function openNav() {
    if (!nav || !navToggle) return;

    // Remember where focus was
    lastFocusedEl = document.activeElement;

    const overlay = createNavOverlay();

    navToggle.setAttribute('aria-expanded', 'true');
    nav.setAttribute('aria-hidden', 'false');

    nav.classList.add('is-open');
    overlay.classList.add('is-visible');

    // Prevent body scroll (simple + reliable)
    document.body.style.overflow = 'hidden';

    // Focus first link for accessibility
    const firstLink = nav.querySelector('.premium-nav__link');
    if (firstLink) {
      window.setTimeout(() => firstLink.focus(), 200);
    }
  }

  function closeNav() {
    if (!nav || !navToggle) return;

    // Only act if open
    const wasOpen = nav.classList.contains('is-open');

    navToggle.setAttribute('aria-expanded', 'false');
    nav.setAttribute('aria-hidden', 'true');

    nav.classList.remove('is-open');
    if (navOverlay) {
      navOverlay.classList.remove('is-visible');
    }

    document.body.style.overflow = '';

    // Return focus gracefully
    if (wasOpen) {
      if (lastFocusedEl && typeof lastFocusedEl.focus === 'function') {
        lastFocusedEl.focus();
      } else {
        navToggle.focus();
      }
    }
  }

  function toggleNav() {
    if (!nav) return;

    if (nav.classList.contains('is-open')) {
      closeNav();
    } else {
      openNav();
    }
  }

  function handleEscape(event) {
    if (event.key !== 'Escape') return;
    if (nav && nav.classList.contains('is-open')) {
      closeNav();
    }
  }

  function handleNavLinkClick() {
    if (window.innerWidth <= MOBILE_BREAKPOINT) {
      closeNav();
    }
  }

  function handleResize() {
    if (window.innerWidth > MOBILE_BREAKPOINT && nav && nav.classList.contains('is-open')) {
      closeNav();
    }
  }

  // -------------------------
  // Smooth scroll (same-page only)
  // -------------------------

  function initSmoothScroll() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach((link) => {
      link.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        // Close mobile nav if open
        if (nav && nav.classList.contains('is-open')) {
          closeNav();
        }

        const headerHeight = header ? header.offsetHeight : 0;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth',
        });

        // Update URL hash without full jump
        history.pushState(null, '', href);

        // Accessibility: focus target
        const prevTabIndex = target.getAttribute('tabindex');
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
        if (prevTabIndex === null) {
          target.removeAttribute('tabindex');
        } else {
          target.setAttribute('tabindex', prevTabIndex);
        }
      });
    });
  }

  // -------------------------
  // Current page highlighting
  // -------------------------

  function normalizePath(pathname) {
    if (!pathname) return '/';
    // Ensure leading slash
    let p = pathname.startsWith('/') ? pathname : `/${pathname}`;
    // Normalize trailing slash (except root)
    if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
    return p;
  }

  function highlightCurrentPage() {
    if (!navLinks || navLinks.length === 0) return;

    const currentPath = normalizePath(window.location.pathname);

    navLinks.forEach((link) => {
      // Some links may be relative; URL() needs a base.
      let linkPath = '';
      try {
        linkPath = normalizePath(new URL(link.getAttribute('href'), window.location.origin).pathname);
      } catch {
        return;
      }

      if (linkPath === currentPath) {
        link.classList.add('is-active');
        link.setAttribute('aria-current', 'page');
      }
    });
  }

  // -------------------------
  // Init
  // -------------------------

  function init() {
    // Scroll state
    updateHeaderState(window.pageYOffset || document.documentElement.scrollTop || 0);
    window.addEventListener('scroll', handleScroll, { passive: true });

    // Mobile nav controls
    if (navToggle) navToggle.addEventListener('click', toggleNav);
    if (navClose) navClose.addEventListener('click', closeNav);

    navLinks.forEach((link) => {
      link.addEventListener('click', handleNavLinkClick);
    });

    document.addEventListener('keydown', handleEscape);

    // Resize (debounced)
    let resizeTimeout;
    window.addEventListener('resize', () => {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(handleResize, 150);
    });

    initSmoothScroll();
    highlightCurrentPage();

    // Loaded class for animations
    window.setTimeout(() => {
      if (header) header.classList.add('is-loaded');
    }, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Cleanup overlay
  window.addEventListener('beforeunload', () => {
    if (navOverlay && navOverlay.parentNode) {
      navOverlay.parentNode.removeChild(navOverlay);
    }
  });
})();
