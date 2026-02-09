// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident UX Enhancements
 * Interactive features for improved user experience
 */

(function () {
  'use strict';

  // ========================================
  // Sticky Header on Scroll
  // ========================================
  function initStickyHeader() {
    const header = document.getElementById('siteHeader');
    if (!header) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    function updateHeader() {
      const scrollY = window.scrollY;

      if (scrollY > 100) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }

      lastScrollY = scrollY;
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(updateHeader);
        ticking = true;
      }
    });
  }

  // ========================================
  // Mobile Navigation
  // ========================================
  function initMobileNav() {
    const toggle = document.querySelector('[data-nav-toggle]');
    const nav = document.querySelector('[data-nav]');
    if (!toggle || !nav) return;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);

    function openNav() {
      nav.classList.add('is-open');
      overlay.classList.add('is-visible');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close menu');
      document.body.style.overflow = 'hidden';
    }

    function closeNav() {
      nav.classList.remove('is-open');
      overlay.classList.remove('is-visible');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open menu');
      document.body.style.overflow = '';
    }

    toggle.addEventListener('click', function () {
      const isOpen = nav.classList.contains('is-open');
      if (isOpen) {
        closeNav();
      } else {
        openNav();
      }
    });

    overlay.addEventListener('click', closeNav);

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        closeNav();
      }
    });

    // Close when clicking nav links
    const navLinks = nav.querySelectorAll('a');
    navLinks.forEach((link) => {
      link.addEventListener('click', closeNav);
    });
  }

  // ========================================
  // Toast Notifications
  // ========================================
  const ToastManager = {
    container: null,

    init() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-atomic', 'true');
        document.body.appendChild(this.container);
      }
    },

    show(message, type = 'info', duration = 5000) {
      this.init();

      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;
      toast.setAttribute('role', 'alert');

      const icons = {
        success:
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>',
        error:
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning:
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
      };

      toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
          <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Close notification">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="4" x2="4" y2="12"/>
            <line x1="4" y1="4" x2="12" y2="12"/>
          </svg>
        </button>
      `;

      this.container.appendChild(toast);

      // Close button
      const closeBtn = toast.querySelector('.toast-close');
      closeBtn.addEventListener('click', () => this.remove(toast));

      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => this.remove(toast), duration);
      }

      return toast;
    },

    remove(toast) {
      toast.classList.add('toast-exit');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    },

    success(message, duration) {
      return this.show(message, 'success', duration);
    },

    error(message, duration) {
      return this.show(message, 'error', duration);
    },

    warning(message, duration) {
      return this.show(message, 'warning', duration);
    },

    info(message, duration) {
      return this.show(message, 'info', duration);
    },
  };

  // Make ToastManager globally available
  window.Toast = ToastManager;

  // ========================================
  // Back to Top Button
  // ========================================
  function initBackToTop() {
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.setAttribute('aria-label', 'Back to top');
    button.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 19V5M5 12l7-7 7 7"/>
      </svg>
    `;
    document.body.appendChild(button);

    let ticking = false;

    function updateButtonVisibility() {
      const scrollY = window.scrollY;

      if (scrollY > 400) {
        button.classList.add('visible');
      } else {
        button.classList.remove('visible');
      }

      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(updateButtonVisibility);
        ticking = true;
      }
    });

    button.addEventListener('click', function () {
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    });
  }

  // ========================================
  // Form Validation Enhancement
  // ========================================
  function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach((form) => {
      const inputs = form.querySelectorAll('input, textarea, select');

      inputs.forEach((input) => {
        const field = input.closest('.form-field');
        if (!field) return;

        // Real-time validation
        input.addEventListener('blur', function () {
          validateField(input, field);
        });

        input.addEventListener('input', function () {
          if (field.classList.contains('has-error')) {
            validateField(input, field);
          }
        });
      });

      // Form submission
      form.addEventListener('submit', function (e) {
        let isValid = true;

        inputs.forEach((input) => {
          const field = input.closest('.form-field');
          if (field && !validateField(input, field)) {
            isValid = false;
          }
        });

        if (!isValid) {
          e.preventDefault();
          Toast.error('Please fix the errors in the form');

          // Focus first error
          const firstError = form.querySelector('.has-error input, .has-error textarea');
          if (firstError) {
            firstError.focus();
          }
        }
      });
    });
  }

  function validateField(input, field) {
    const errorEl = field.querySelector('.form-error') || createErrorElement(field);
    let isValid = true;
    let message = '';

    // Required check
    if (input.hasAttribute('required') && !input.value.trim()) {
      isValid = false;
      message = 'This field is required';
    }

    // Email check
    if (input.type === 'email' && input.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(input.value)) {
        isValid = false;
        message = 'Please enter a valid email address';
      }
    }

    // Min length check
    if (input.hasAttribute('minlength') && input.value) {
      const minLength = parseInt(input.getAttribute('minlength'));
      if (input.value.length < minLength) {
        isValid = false;
        message = `Must be at least ${minLength} characters`;
      }
    }

    // Pattern check
    if (input.hasAttribute('pattern') && input.value) {
      const pattern = new RegExp(input.getAttribute('pattern'));
      if (!pattern.test(input.value)) {
        isValid = false;
        message = input.getAttribute('data-pattern-message') || 'Invalid format';
      }
    }

    // Update UI
    if (isValid) {
      field.classList.remove('has-error');
      field.classList.add('has-success');
      errorEl.textContent = '';
    } else {
      field.classList.add('has-error');
      field.classList.remove('has-success');
      errorEl.textContent = message;
    }

    return isValid;
  }

  function createErrorElement(field) {
    const errorEl = document.createElement('div');
    errorEl.className = 'form-error';
    field.appendChild(errorEl);
    return errorEl;
  }

  // ========================================
  // Loading State for Buttons
  // ========================================
  function initButtonLoading() {
    document.addEventListener('click', function (e) {
      const button = e.target.closest('[data-loading]');
      if (!button) return;

      button.classList.add('is-loading');
      button.disabled = true;

      // Remove loading state after action completes
      // (Should be handled by form submission/AJAX callback)
    });
  }

  // ========================================
  // Smooth Scroll for Anchor Links
  // ========================================
  function initSmoothScroll() {
    document.addEventListener('click', function (e) {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;

      const href = link.getAttribute('href');
      if (href === '#') return;

      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();

      const headerOffset = 80;
      const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth',
      });

      // Update URL without jumping
      history.pushState(null, '', href);
    });
  }

  // ========================================
  // Lazy Load Images
  // ========================================
  function initLazyLoading() {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            if (img.dataset.srcset) {
              img.srcset = img.dataset.srcset;
              img.removeAttribute('data-srcset');
            }
            img.classList.remove('lazy');
            observer.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img[data-src], img[data-srcset]').forEach((img) => {
        imageObserver.observe(img);
      });
    }
  }

  // ========================================
  // Animated Counter (inspired by realfood.gov statistics)
  // ========================================
  function initAnimatedCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    if (!counters || counters.length === 0) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      counters.forEach((counter) => {
        counter.textContent = counter.getAttribute('data-counter');
      });
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const counter = entry.target;
          const target = parseFloat(counter.getAttribute('data-counter'));
          const duration = parseInt(counter.getAttribute('data-duration') || '2000', 10);
          const suffix = counter.getAttribute('data-suffix') || '';
          const prefix = counter.getAttribute('data-prefix') || '';
          
          animateValue(counter, 0, target, duration, prefix, suffix);
          observer.unobserve(counter);
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((counter) => observer.observe(counter));
  }

  function animateValue(element, start, end, duration, prefix, suffix) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    const isDecimal = end % 1 !== 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }
      const displayValue = isDecimal ? current.toFixed(1) : Math.floor(current);
      element.textContent = prefix + displayValue + suffix;
    }, 16);
  }

  // ========================================
  // Parallax Scrolling
  // ========================================
  function initParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    if (!parallaxElements || parallaxElements.length === 0) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    let ticking = false;

    function updateParallax() {
      const scrolled = window.pageYOffset;

      parallaxElements.forEach((el) => {
        const speed = parseFloat(el.getAttribute('data-parallax') || '0.5');
        const rect = el.getBoundingClientRect();
        const centerY = rect.top + rect.height / 2;
        const offset = (scrolled - centerY) * speed;
        el.style.transform = `translate3d(0, ${offset}px, 0)`;
      });

      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(updateParallax);
        ticking = true;
      }
    });
  }

  // ========================================
  // Scroll Progress Indicator
  // ========================================
  function initScrollProgress() {
    let progressBar = document.querySelector('.scroll-progress-bar');
    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.className = 'scroll-progress-bar';
      progressBar.innerHTML = '<div class="scroll-progress-fill"></div>';
      document.body.appendChild(progressBar);
    }

    const progressFill = progressBar.querySelector('.scroll-progress-fill');
    let ticking = false;

    function updateProgress() {
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      progressFill.style.width = scrolled + '%';
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(updateProgress);
        ticking = true;
      }
    });
  }

  // ========================================
  // Enhanced Card Interactions
  // ========================================
  function initCardInteractions() {
    const cards = document.querySelectorAll('.card, [class*="card-"]');
    if (!cards || cards.length === 0) return;

    cards.forEach((card) => {
      // Add magnetic effect on mouse move
      card.addEventListener('mouseenter', function () {
        this.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
      });

      card.addEventListener('mousemove', function (e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;

        this.style.transform = `perspective(1000px) rotateY(${deltaX * 5}deg) rotateX(${-deltaY * 5}deg) translateZ(10px)`;
      });

      card.addEventListener('mouseleave', function () {
        this.style.transform = 'perspective(1000px) rotateY(0) rotateX(0) translateZ(0)';
      });
    });
  }

  // ========================================
  // Logo Micro-Animations
  // ========================================
  function initLogoAnimations() {
    const logo = document.querySelector('.site-logo, .logo, [class*="logo"]');
    if (!logo) return;

    // Subtle pulse on scroll to top
    let lastScroll = window.pageYOffset;

    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;
      if (currentScroll < 100 && lastScroll >= 100) {
        logo.style.animation = 'none';
        setTimeout(() => {
          logo.style.animation = 'subtle-pulse 0.6s ease-out';
        }, 10);
      }
      lastScroll = currentScroll;
    });
  }

  // ========================================
  // Scroll Reveal / Intersection Observer
  // Enhanced with multiple animation types
  // ========================================
  function initScrollReveal() {
    const els = document.querySelectorAll('.will-animate');
    if (!els || els.length === 0) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      els.forEach((el) => el.classList.add('revealed'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;

          // per-element delay (ms)
          const delayAttr =
            el.getAttribute('data-animation-delay') || el.dataset.animationDelay || 0;
          const baseDelay = parseInt(delayAttr, 10) || 0;

          // Stagger children if container uses .stagger-container
          const staggerChildren = el.querySelectorAll('.stagger-container > *');
          if (staggerChildren && staggerChildren.length) {
            staggerChildren.forEach((child, i) => {
              const d = baseDelay + i * 100;
              setTimeout(() => child.classList.add('revealed'), d);
            });
          }

          // reveal the element itself (after base delay)
          setTimeout(() => el.classList.add('revealed'), baseDelay);

          obs.unobserve(el);
        });
      },
      {
        root: null,
        rootMargin: '0px 0px -8% 0px',
        threshold: 0.15,
      }
    );

    els.forEach((el) => {
      // ensure initial hidden state for elements that rely on the reveal system
      if (
        !el.classList.contains('fade-in') &&
        !el.classList.contains('slide-up') &&
        !el.classList.contains('slide-down') &&
        !el.classList.contains('slide-left') &&
        !el.classList.contains('slide-right') &&
        !el.classList.contains('zoom-in') &&
        !el.classList.contains('blur-in')
      ) {
        el.classList.add('fade-in');
      }

      observer.observe(el);
    });
  }

  // ========================================
  // Initialize All UX Enhancements
  // ========================================
  function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    initStickyHeader();
    initMobileNav();
    initBackToTop();
    initFormValidation();
    initButtonLoading();
    initSmoothScroll();
    initLazyLoading();
    initScrollReveal();
    initAnimatedCounters();
    initParallax();
    initScrollProgress();
    initCardInteractions();
    initLogoAnimations();

    // Mark page as loaded to trigger CSS page transition
    window.requestAnimationFrame(() => {
      setTimeout(() => {
        document.body.classList.add('page-loaded');
        document.body.classList.add('animations-ready');
      }, 80);
    });

    console.log('✨ Evident UX enhancements loaded — wholesome & modern');
  }

  init();
})();
