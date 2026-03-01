(function() {
  'use strict';

  // // // // // // // // // // // // // // // console.log('[TILLERSTEAD] Initializing - No Bounce Edition'); // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED

  // Header scroll - NO BOUNCE
  const header = document.getElementById('site-header');
  if (header) {
    let lastScroll = 0;
    let ticking = false;

    function updateHeader() {
      const scrollY = window.pageYOffset;

      // Only update class, not position
      if (scrollY > 50) {
        header.classList.add('ts-header--scrolled');
      } else {
        header.classList.remove('ts-header--scrolled');
      }

      lastScroll = scrollY;
      ticking = false;
    }

    // Use requestAnimationFrame to prevent jank
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(updateHeader);
        ticking = true;
      }
    }, { passive: true });
  }

  // Rest of navigation code...
  initNav();
  initAnimations();

  function initNav() {
    // Desktop dropdown navigation
    const dropdowns = document.querySelectorAll('.has-dropdown');

    dropdowns.forEach(item => {
      const trigger = item.querySelector('.desktop-nav__trigger');
      const dropdown = item.querySelector('.desktop-nav__dropdown');

      if (!trigger || !dropdown) return;

      // Click handler
      trigger.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();

        const isOpen = item.classList.contains('is-open');

        // Close all other dropdowns
        dropdowns.forEach(other => {
          if (other !== item) {
            other.classList.remove('is-open');
            const t = other.querySelector('.desktop-nav__trigger');
            if (t) t.setAttribute('aria-expanded', 'false');
          }
        });

        // Toggle this dropdown
        if (isOpen) {
          item.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
        } else {
          item.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
        }
      });

      // Hover handlers for desktop only
      if (window.innerWidth >= 1080) {
        item.addEventListener('mouseenter', () => {
          item.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
        });

        item.addEventListener('mouseleave', () => {
          item.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
        });

        // Keep dropdown open when hovering over it
        dropdown.addEventListener('mouseenter', () => {
          item.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
        });

        dropdown.addEventListener('mouseleave', () => {
          item.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
        });
      }
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', e => {
      if (!e.target.closest('.has-dropdown')) {
        dropdowns.forEach(item => {
          item.classList.remove('is-open');
          const t = item.querySelector('.desktop-nav__trigger');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    });

    // Close dropdowns on ESC key
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        dropdowns.forEach(item => {
          item.classList.remove('is-open');
          const t = item.querySelector('.desktop-nav__trigger');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    });

    // Mobile nav
    const toggle = document.querySelector('.mobile-nav__toggle');
    const nav = document.getElementById('mobile-nav');
    const close = document.querySelector('.mobile-nav__close');
    const MOBILE_BREAKPOINT = 1080;
    const isMobile = () => window.innerWidth < MOBILE_BREAKPOINT;

    if (toggle && nav) {
      toggle.addEventListener('click', () => {
        const isOpen = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
        nav.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
        // ONLY block scroll on mobile
        if (isMobile()) {
          // Natural scrolling - no body lock
        }
      });
    }

    if (close && nav) {
      close.addEventListener('click', () => {
        nav.setAttribute('aria-hidden', 'true');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        // ONLY unblock scroll on mobile
        if (isMobile()) {
          document.body.style.overflow = '';
        }
      });
    }

    // Mobile accordions
    const accordions = document.querySelectorAll('.mobile-nav__accordion-trigger');
    accordions.forEach(acc => {
      acc.addEventListener('click', function() {
        const isOpen = this.getAttribute('aria-expanded') === 'true';
        const panel = this.nextElementSibling;
        this.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
        if (panel) panel.hidden = isOpen;
      });
    });
  }

  function initAnimations() {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
  }

  // Don't force scroll styles - let scroll-fix.js handle it

  // // // // // // // // // // // // // // // console.log('[TILLERSTEAD] ✅ Ready - No Bounce!'); // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED // AUTO-DISABLED
})();

/**
 * UX Enhancements JavaScript
 * Handles: Form feedback, back-to-top, loading states, error visibility
 */

(function() {
  'use strict';

  const UXEnhancements = {
    /**
     * Initialize all UX enhancements
     */
    init() {
      this.initBackToTop();
      this.initFormEnhancements();
      this.initLoadingStates();
      this.initToastSystem();
      this.initErrorVisibility();
      this.initA11yEnhancements();
    },

    /**
     * Back to Top Button
     */
    initBackToTop() {
      // Create button
      const btn = document.createElement('button');
      btn.className = 'back-to-top';
      btn.setAttribute('aria-label', 'Back to top');
      btn.setAttribute('title', 'Back to top');
      btn.type = 'button';

      document.body.appendChild(btn);

      // Show/hide based on scroll
      let scrollTimeout;
      window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
          if (window.pageYOffset > 400) {
            btn.classList.add('visible');
          } else {
            btn.classList.remove('visible');
          }
        }, 100);
      }, { passive: true });

      // Scroll to top on click
      btn.addEventListener('click', () => {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });

        // Focus skip link after scrolling
        setTimeout(() => {
          const skipLink = document.querySelector('.skip-link');
          if (skipLink) skipLink.focus();
        }, 500);
      });
    },

    /**
     * Form Enhancement - Loading states and success feedback
     */
    initFormEnhancements() {
      const forms = document.querySelectorAll('form[action]');

      forms.forEach(form => {
        form.addEventListener('submit', (e) => {
          // Skip if form is invalid
          if (!form.checkValidity()) {
            this.showFormErrors(form);
            return;
          }

          // Add loading state
          form.classList.add('form--loading');

          const submitBtn = form.querySelector('[type="submit"]');
          if (submitBtn) {
            submitBtn.classList.add('btn--loading');
            submitBtn.setAttribute('aria-busy', 'true');
            submitBtn.disabled = true;
          }

          // For Netlify forms, show success toast after redirect
          if (form.hasAttribute('data-netlify')) {
            sessionStorage.setItem('form-submitted', 'true');
          }
        });

        // Real-time validation on blur
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
          input.addEventListener('blur', () => {
            this.validateField(input);
          });

          // Clear error on input
          input.addEventListener('input', () => {
            input.classList.remove('error');
            const errorMsg = input.parentElement.querySelector('.error-message');
            if (errorMsg) errorMsg.remove();
          });
        });
      });

      // Check for success message on load
      if (sessionStorage.getItem('form-submitted') === 'true') {
        sessionStorage.removeItem('form-submitted');
        this.showSuccessToast('Thank you! We\'ll get back to you soon.');
      }
    },

    /**
     * Validate individual field
     */
    validateField(field) {
      const isValid = field.checkValidity();

      if (!isValid) {
        field.classList.add('error');

        // Remove existing error message
        const existingError = field.parentElement.querySelector('.error-message');
        if (existingError) existingError.remove();

        // Add error message
        const errorMsg = document.createElement('span');
        errorMsg.className = 'error-message';
        errorMsg.textContent = field.validationMessage || 'This field is required';
        errorMsg.id = `${field.id || field.name}-error`;

        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', errorMsg.id);

        field.parentElement.appendChild(errorMsg);
      } else {
        field.classList.remove('error');
        field.removeAttribute('aria-invalid');
        field.removeAttribute('aria-describedby');
      }

      return isValid;
    },

    /**
     * Show form errors summary
     */
    showFormErrors(form) {
      const invalidFields = form.querySelectorAll(':invalid');

      // Validate all invalid fields
      invalidFields.forEach(field => this.validateField(field));

      // Create or update error summary
      let errorSummary = form.querySelector('.error-summary');
      if (!errorSummary) {
        errorSummary = document.createElement('div');
        errorSummary.className = 'error-summary';
        errorSummary.setAttribute('role', 'alert');
        errorSummary.setAttribute('aria-live', 'assertive');
        form.insertBefore(errorSummary, form.firstChild);
      }

      errorSummary.innerHTML = `
        <strong class="error-summary__title">Please fix the following errors:</strong>
        <ul class="error-list">
          ${Array.from(invalidFields).map(field => {
    const label = form.querySelector(`label[for="${field.id}"]`);
    const fieldName = label ? label.textContent : field.name;
    return `<li><a href="#${field.id}">${fieldName}: ${field.validationMessage}</a></li>`;
  }).join('')}
        </ul>
      `;

      errorSummary.classList.add('visible');
      errorSummary.removeAttribute('hidden');
      errorSummary.setAttribute('aria-hidden', 'false');

      // Focus first invalid field
      if (invalidFields.length > 0) {
        invalidFields[0].focus();
      }
    },

    /**
     * Loading states for async operations
     */
    initLoadingStates() {
      // Add loading state to buttons with data-loading attribute
      const loadingButtons = document.querySelectorAll('[data-loading]');

      loadingButtons.forEach(btn => {
        btn.addEventListener('click', function() {
          this.classList.add('btn--loading');
          this.setAttribute('aria-busy', 'true');
          this.disabled = true;

          // Auto-remove after 5 seconds (safety)
          setTimeout(() => {
            this.classList.remove('btn--loading');
            this.setAttribute('aria-busy', 'false');
            this.disabled = false;
          }, 5000);
        });
      });
    },

    /**
     * Toast notification system
     */
    initToastSystem() {
      // Create toast container if it doesn't exist
      if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'true');
        container.style.cssText = `
          position: fixed;
          top: 2rem;
          right: 2rem;
          z-index: 9999;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          max-width: 400px;
        `;
        document.body.appendChild(container);
      }
    },

    /**
     * Show success toast
     */
    showSuccessToast(message, duration = 5000) {
      const container = document.getElementById('toast-container');

      const toast = document.createElement('div');
      toast.className = 'toast--success';
      toast.setAttribute('role', 'status');
      toast.textContent = message;

      // Add close button
      const closeBtn = document.createElement('button');
      closeBtn.innerHTML = '×';
      closeBtn.setAttribute('aria-label', 'Close notification');
      closeBtn.style.cssText = `
        background: none;
        border: none;
        color: inherit;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
        line-height: 1;
      `;
      closeBtn.addEventListener('click', () => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
      });

      toast.appendChild(closeBtn);
      container.appendChild(toast);

      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => {
          toast.style.opacity = '0';
          toast.style.transform = 'translateX(100%)';
          setTimeout(() => toast.remove(), 300);
        }, duration);
      }

      return toast;
    },

    /**
     * Show error toast
     */
    showErrorToast(message, duration = 7000) {
      const container = document.getElementById('toast-container');

      const toast = document.createElement('div');
      toast.className = 'toast--success'; // Reuse styles
      toast.setAttribute('role', 'alert');
      toast.style.cssText = `
        background: #FEF2F2;
        border-color: #DC2626;
        color: #991B1B;
      `;
      toast.textContent = message;

      container.appendChild(toast);

      if (duration > 0) {
        setTimeout(() => toast.remove(), duration);
      }

      return toast;
    },

    /**
     * Enhanced error visibility
     */
    initErrorVisibility() {
      // Check URL for error parameters (Netlify redirects)
      const params = new URLSearchParams(window.location.search);
      if (params.get('error')) {
        this.showErrorToast('There was a problem submitting your form. Please try again.');
      }
      if (params.get('success')) {
        this.showSuccessToast('Thank you! Your message has been sent successfully.');
      }
    },

    /**
     * Accessibility enhancements
     */
    initA11yEnhancements() {
      // Add skip to main content functionality
      const skipLink = document.querySelector('.skip-link');
      if (skipLink) {
        skipLink.addEventListener('click', (e) => {
          e.preventDefault();
          const mainContent = document.getElementById('main-content') || document.querySelector('main');
          if (mainContent) {
            mainContent.setAttribute('tabindex', '-1');
            mainContent.focus();
            setTimeout(() => mainContent.removeAttribute('tabindex'), 1000);
          }
        });
      }

      // Announce page title to screen readers on route change (for SPAs)
      const pageTitle = document.querySelector('h1');
      if (pageTitle) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'visually-hidden';
        announcement.textContent = `Page loaded: ${pageTitle.textContent}`;
        document.body.appendChild(announcement);

        setTimeout(() => announcement.remove(), 2000);
      }

      // Enhance focus management for modals/dialogs
      this.trapFocusInModals();
    },

    /**
     * Trap focus in modals
     */
    trapFocusInModals() {
      const modals = document.querySelectorAll('[role="dialog"], .modal, .lead-magnet');

      modals.forEach(modal => {
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            if (mutation.attributeName === 'aria-hidden') {
              const isHidden = modal.getAttribute('aria-hidden') === 'true';

              if (!isHidden) {
                // Modal opened - trap focus
                const focusableElements = modal.querySelectorAll(
                  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );

                if (focusableElements.length > 0) {
                  focusableElements[0].focus();
                }
              }
            }
          });
        });

        observer.observe(modal, { attributes: true });
      });
    }
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => UXEnhancements.init());
  } else {
    UXEnhancements.init();
  }

  // Expose global API
  window.tsUXEnhancements = UXEnhancements;

})();

/**
 * Scroll Fix - Prevents nav-open from blocking scroll on desktop
 * Now uses ScrollLockManager for centralized control
 */

(function() {
  'use strict';

  const MOBILE_BREAKPOINT = 1080;
  let navIsOpen = false;

  function isMobile() {
    return window.innerWidth < MOBILE_BREAKPOINT;
  }

  function disableBodyScroll() {
    // ONLY disable scroll on mobile with nav drawer open
    if (!isMobile()) {
      return; // Never block scroll on desktop
    }

    // Use centralized scroll lock manager
    if (window.ScrollLockManager) {
      window.ScrollLockManager.lock('scroll-fix');
    }
  }

  function enableBodyScroll() {
    // Use centralized scroll lock manager
    if (window.ScrollLockManager) {
      window.ScrollLockManager.unlock('scroll-fix');
    }
  }

  // Monitor nav state changes via body class
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
        const hasNavOpen = document.body.classList.contains('nav-open');

        if (hasNavOpen !== navIsOpen) {
          navIsOpen = hasNavOpen;

          if (navIsOpen) {
            disableBodyScroll();
          } else {
            enableBodyScroll();
          }
        }
      }
    });
  });

  // Start observing
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['class']
  });

  // Handle window resize - close mobile nav if resized to desktop
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      // If we're on desktop and nav is open, close it
      if (!isMobile() && navIsOpen) {
        document.body.classList.remove('nav-open');
        enableBodyScroll();

        // Close mobile nav drawer
        const mobileNav = document.getElementById('mobile-nav-drawer');
        if (mobileNav) {
          mobileNav.setAttribute('aria-hidden', 'true');
        }
      }
    }, 150);
  }, { passive: true });

  // Expose global API
  window.tsScrollFix = {
    enable: enableBodyScroll,
    disable: disableBodyScroll,
    isEnabled: () => !navIsOpen || !isMobile()
  };

})();
