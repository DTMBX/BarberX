/**
 * INTERACTIVE COMPONENTS - Premium Features
 * Tillerstead.com - Phase 2 Implementation
 *
 * Features:
 * - FAQ Accordion with smooth animations
 * - Before/After Image Slider
 * - Pricing Calculator
 * - Toast Notification System
 * - Advanced Image Gallery
 */

class InteractiveComponents {
  constructor() {
    this.init();
  }

  init() {
    // Initialize all components when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initializeAll());
    } else {
      this.initializeAll();
    }
  }

  initializeAll() {
    this.setupFAQAccordion();
    this.setupBeforeAfterSlider();
    this.setupPricingCalculator();
    this.setupToastSystem();
    this.setupImageGallery();
  }

  /**
   * FAQ ACCORDION - Smooth expand/collapse with ARIA support
   */
  setupFAQAccordion() {
    const accordions = document.querySelectorAll('[data-accordion]');

    accordions.forEach(accordion => {
      const items = accordion.querySelectorAll('[data-accordion-item]');

      items.forEach((item, index) => {
        const trigger = item.querySelector('[data-accordion-trigger]');
        const content = item.querySelector('[data-accordion-content]');

        if (!trigger || !content) return;

        // Set up ARIA attributes
        const id = `accordion-content-${index}`;
        trigger.setAttribute('aria-controls', id);
        trigger.setAttribute('aria-expanded', 'false');
        content.setAttribute('id', id);
        content.setAttribute('role', 'region');
        content.style.maxHeight = '0';
        content.style.overflow = 'hidden';
        content.style.transition = 'max-height 0.4s cubic-bezier(0.23, 1, 0.32, 1)';

        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          const isExpanded = trigger.getAttribute('aria-expanded') === 'true';

          // Close all items if you want exclusive accordion behavior
          const closeOthers = accordion.hasAttribute('data-accordion-exclusive');
          if (closeOthers) {
            items.forEach(otherItem => {
              if (otherItem !== item) {
                const otherTrigger = otherItem.querySelector('[data-accordion-trigger]');
                const otherContent = otherItem.querySelector('[data-accordion-content]');
                otherTrigger.setAttribute('aria-expanded', 'false');
                otherContent.style.maxHeight = '0';
                otherItem.classList.remove('is-expanded');
              }
            });
          }

          // Toggle current item
          if (isExpanded) {
            trigger.setAttribute('aria-expanded', 'false');
            content.style.maxHeight = '0';
            item.classList.remove('is-expanded');
          } else {
            trigger.setAttribute('aria-expanded', 'true');
            content.style.maxHeight = content.scrollHeight + 'px';
            item.classList.add('is-expanded');
          }
        });

        // Keyboard navigation
        trigger.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            trigger.click();
          }
        });
      });
    });
  }

  /**
   * BEFORE/AFTER IMAGE SLIDER - Touch-enabled comparison slider
   */
  setupBeforeAfterSlider() {
    const sliders = document.querySelectorAll('[data-before-after]');

    sliders.forEach(slider => {
      const handle = slider.querySelector('[data-ba-handle]');
      const overlay = slider.querySelector('[data-ba-overlay]');

      if (!handle || !overlay) return;

      let isDragging = false;
      let startX = 0;
      let currentPosition = 50; // Start at 50%

      const updatePosition = (x) => {
        const rect = slider.getBoundingClientRect();
        const relativeX = Math.max(0, Math.min(x - rect.left, rect.width));
        currentPosition = (relativeX / rect.width) * 100;

        overlay.style.clipPath = `inset(0 ${100 - currentPosition}% 0 0)`;
        handle.style.left = `${currentPosition}%`;
      };

      // Mouse events
      handle.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
        handle.classList.add('is-dragging');
      });

      document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        updatePosition(e.clientX);
      });

      document.addEventListener('mouseup', () => {
        if (isDragging) {
          isDragging = false;
          handle.classList.remove('is-dragging');
        }
      });

      // Touch events
      handle.addEventListener('touchstart', (e) => {
        isDragging = true;
        startX = e.touches[0].clientX;
        handle.classList.add('is-dragging');
      }, { passive: true });

      document.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        updatePosition(e.touches[0].clientX);
      }, { passive: true });

      document.addEventListener('touchend', () => {
        if (isDragging) {
          isDragging = false;
          handle.classList.remove('is-dragging');
        }
      });

      // Initialize position
      updatePosition(slider.getBoundingClientRect().left + (slider.offsetWidth / 2));
    });
  }

  /**
   * PRICING CALCULATOR - Interactive project estimator
   */
  setupPricingCalculator() {
    const calculators = document.querySelectorAll('[data-pricing-calculator]');

    calculators.forEach(calculator => {
      const inputs = calculator.querySelectorAll('[data-calc-input]');
      const output = calculator.querySelector('[data-calc-output]');

      if (!output) return;

      const calculate = () => {
        let total = 0;
        const values = {};

        inputs.forEach(input => {
          const name = input.name || input.dataset.calcInput;
          const value = parseFloat(input.value) || 0;
          const multiplier = parseFloat(input.dataset.multiplier) || 1;

          values[name] = value;
          total += value * multiplier;
        });

        // Custom calculation logic can be added here
        const basePrice = parseFloat(calculator.dataset.basePrice) || 0;
        total += basePrice;

        // Format and display
        output.textContent = `$${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        // Emit custom event
        calculator.dispatchEvent(new CustomEvent('calculationUpdate', {
          detail: { total, values }
        }));
      };

      // Listen for input changes
      inputs.forEach(input => {
        input.addEventListener('input', calculate);
        input.addEventListener('change', calculate);
      });

      // Initial calculation
      calculate();
    });
  }

  /**
   * TOAST NOTIFICATION SYSTEM - Modern alerts
   */
  setupToastSystem() {
    // Create toast container if it doesn't exist
    if (!document.querySelector('.toast-container')) {
      const container = document.createElement('div');
      container.className = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(container);
    }

    // Global toast function
    window.showToast = (message, type = 'info', duration = 3000) => {
      const container = document.querySelector('.toast-container');
      const toast = document.createElement('div');
      toast.className = `toast toast--${type}`;
      toast.setAttribute('role', 'status');

      const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
      };

      toast.innerHTML = `
        <span class="toast__icon">${icons[type] || icons.info}</span>
        <span class="toast__message">${message}</span>
        <button class="toast__close" aria-label="Close notification">×</button>
      `;

      const closeBtn = toast.querySelector('.toast__close');
      const removeToast = () => {
        toast.classList.add('toast--exit');
        setTimeout(() => toast.remove(), 300);
      };

      closeBtn.addEventListener('click', removeToast);

      container.appendChild(toast);

      // Trigger animation
      requestAnimationFrame(() => {
        toast.classList.add('toast--show');
      });

      // Auto remove after duration
      if (duration > 0) {
        setTimeout(removeToast, duration);
      }
    };
  }

  /**
   * IMAGE GALLERY - Lightbox with keyboard navigation
   */
  setupImageGallery() {
    const galleries = document.querySelectorAll('[data-gallery]');

    galleries.forEach(gallery => {
      const images = gallery.querySelectorAll('[data-gallery-item]');

      images.forEach((img, index) => {
        img.style.cursor = 'pointer';
        img.setAttribute('tabindex', '0');

        const openLightbox = () => {
          this.openImageLightbox(images, index);
        };

        img.addEventListener('click', openLightbox);
        img.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openLightbox();
          }
        });
      });
    });
  }

  openImageLightbox(images, startIndex) {
    let currentIndex = startIndex;

    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-modal', 'true');
    lightbox.setAttribute('aria-label', 'Image gallery');

    lightbox.innerHTML = `
      <div class="lightbox__backdrop"></div>
      <div class="lightbox__content">
        <button class="lightbox__close" aria-label="Close gallery">×</button>
        <button class="lightbox__prev" aria-label="Previous image">‹</button>
        <img class="lightbox__image" src="" alt="">
        <button class="lightbox__next" aria-label="Next image">›</button>
        <div class="lightbox__counter"></div>
      </div>
    `;

    const updateImage = () => {
      const img = images[currentIndex];
      const lightboxImg = lightbox.querySelector('.lightbox__image');
      const counter = lightbox.querySelector('.lightbox__counter');

      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || '';
      counter.textContent = `${currentIndex + 1} / ${images.length}`;
    };

    const close = () => {
      lightbox.classList.add('lightbox--exit');
      setTimeout(() => lightbox.remove(), 300);
      document.body.style.overflow = '';
    };

    const prev = () => {
      currentIndex = (currentIndex - 1 + images.length) % images.length;
      updateImage();
    };

    const next = () => {
      currentIndex = (currentIndex + 1) % images.length;
      updateImage();
    };

    lightbox.querySelector('.lightbox__close').addEventListener('click', close);
    lightbox.querySelector('.lightbox__prev').addEventListener('click', prev);
    lightbox.querySelector('.lightbox__next').addEventListener('click', next);
    lightbox.querySelector('.lightbox__backdrop').addEventListener('click', close);

    // Keyboard navigation
    document.addEventListener('keydown', function lightboxKeyHandler(e) {
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') prev();
      if (e.key === 'ArrowRight') next();

      if (e.key === 'Escape') {
        document.removeEventListener('keydown', lightboxKeyHandler);
      }
    });

    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';
    updateImage();

    requestAnimationFrame(() => {
      lightbox.classList.add('lightbox--show');
    });
  }
}

// Initialize interactive components
const interactiveComponents = new InteractiveComponents();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = InteractiveComponents;
}
