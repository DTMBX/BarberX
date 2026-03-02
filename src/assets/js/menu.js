/**
 * ============================================================================
 * Site Header – Menu, Dropdown, Mobile Drawer (CANONICAL VERSION 1.0.0)
 * Evident Technologies
 * ============================================================================
 *
 * DO NOT MODIFY WITHOUT ARCHITECTURAL REVIEW
 *
 * This is the finalized, court-defensible header behavior system.
 *
 * Features:
 * - Click-outside to close
 * - Mobile drawer slide-in/out
 * - Focus trap inside open drawer
 * - Scroll-lock when drawer is open
 */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  /* ================================================================
     DESKTOP DROPDOWNS
     ================================================================ */
  const dropdownButtons = document.querySelectorAll('[data-dropdown-button]');

  function closeAllDropdowns(except) {
    dropdownButtons.forEach(function (btn) {
      if (btn === except) return;
      btn.setAttribute('aria-expanded', 'false');
      var menu = btn.closest('[data-nav-item]').querySelector('[data-dropdown]');
      if (menu) menu.classList.remove('is-open');
    });
  }

  dropdownButtons.forEach(function (button) {
    var parent = button.closest('[data-nav-item]');
    var menu = parent && parent.querySelector('[data-dropdown]');
    if (!menu) return;

    // Toggle on click
    button.addEventListener('click', function (e) {
      e.stopPropagation();
      var expanded = button.getAttribute('aria-expanded') === 'true';
      closeAllDropdowns(button);
      button.setAttribute('aria-expanded', String(!expanded));
      menu.classList.toggle('is-open', !expanded);
    });

    // Keyboard: Escape closes, ArrowDown enters menu
    button.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        menu.classList.remove('is-open');
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (button.getAttribute('aria-expanded') !== 'true') {
          button.setAttribute('aria-expanded', 'true');
          menu.classList.add('is-open');
        }
        var firstLink = menu.querySelector('a');
        if (firstLink) firstLink.focus();
      }
    });

    // Keyboard navigation inside dropdown
    menu.addEventListener('keydown', function (e) {
      var links = Array.from(menu.querySelectorAll('a'));
      var idx = links.indexOf(document.activeElement);

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        var next = links[(idx + 1) % links.length];
        if (next) next.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var prev = links[(idx - 1 + links.length) % links.length];
        if (prev) prev.focus();
      } else if (e.key === 'Escape') {
        menu.classList.remove('is-open');
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      } else if (e.key === 'Tab') {
        // Allow natural tab-out, close dropdown
        menu.classList.remove('is-open');
        button.setAttribute('aria-expanded', 'false');
      }
    });
  });

  // Close dropdowns on any outside click
  document.addEventListener('click', function () {
    closeAllDropdowns(null);
  });

  /* ================================================================
     MOBILE DRAWER
     ================================================================ */
  var mobileToggle = document.getElementById('mobile-nav-toggle');
  var drawer = document.getElementById('mobile-drawer');
  if (!mobileToggle || !drawer) return;

  function openDrawer() {
    mobileToggle.setAttribute('aria-expanded', 'true');
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    // Focus first focusable element inside drawer
    var first = drawer.querySelector('a, button, [tabindex]');
    if (first) first.focus();
  }

  function closeDrawer() {
    mobileToggle.setAttribute('aria-expanded', 'false');
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    mobileToggle.focus();
  }

  mobileToggle.addEventListener('click', function () {
    var expanded = this.getAttribute('aria-expanded') === 'true';
    if (expanded) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });

  // Close drawer on Escape
  drawer.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeDrawer();
    }
  });

  // Focus trap inside open drawer
  drawer.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    var focusable = Array.from(
      drawer.querySelectorAll('a, button, details summary, [tabindex]:not([tabindex="-1"])')
    );
    if (focusable.length === 0) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  // Close drawer when a link inside is clicked
  drawer.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      closeDrawer();
    });
  });

  // Close drawer on window resize to desktop
  var mql = window.matchMedia('(min-width: 768px)');
  function onBreakpointChange(e) {
    if (e.matches && drawer.classList.contains('is-open')) {
      closeDrawer();
    }
  }
  if (mql.addEventListener) {
    mql.addEventListener('change', onBreakpointChange);
  }
});
