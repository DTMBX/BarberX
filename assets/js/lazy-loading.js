// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * IMAGE LAZY LOADING & OPTIMIZATION
 *
 * Automatically lazy loads images with IntersectionObserver
 * Supports srcset for responsive images
 * Includes blur-up placeholder effect
 */

(function () {
  'use strict';

  const config = {
    rootMargin: '50px 0px', // Start loading 50px before entering viewport
    threshold: 0.01,
    enableBlurUp: true,
    fadeInDuration: 400,
  };

  /**
   * Create blur-up placeholder
   */
  function createPlaceholder(img) {
    if (!config.enableBlurUp) return;

    const placeholder = document.createElement('div');
    placeholder.className = 'lazy-image-placeholder';
    placeholder.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, rgba(212, 165, 116, 0.1), rgba(16, 92, 74, 0.1));
      z-index: 1;
      transition: opacity ${config.fadeInDuration}ms ease;
    `;

    const wrapper = img.parentElement;
    if (wrapper && !wrapper.classList.contains('lazy-image-wrapper')) {
      const newWrapper = document.createElement('div');
      newWrapper.className = 'lazy-image-wrapper';
      newWrapper.style.position = 'relative';
      wrapper.insertBefore(newWrapper, img);
      newWrapper.appendChild(img);
      newWrapper.appendChild(placeholder);
    }

    return placeholder;
  }

  /**
   * Load image
   */
  function loadImage(img) {
    return new Promise((resolve, reject) => {
      const tempImg = new Image();

      tempImg.onload = () => {
        // Set src
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }

        // Set srcset for responsive images
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
        }

        // Set sizes
        if (img.dataset.sizes) {
          img.sizes = img.dataset.sizes;
        }

        // Mark as loaded
        img.classList.add('lazy-loaded');

        // Fade in
        img.style.opacity = '0';
        img.style.transition = `opacity ${config.fadeInDuration}ms ease`;

        setTimeout(() => {
          img.style.opacity = '1';
        }, 10);

        resolve(img);
      };

      tempImg.onerror = reject;
      tempImg.src = img.dataset.src || img.src;
    });
  }

  /**
   * Remove placeholder after image loads
   */
  function removePlaceholder(img) {
    const wrapper = img.closest('.lazy-image-wrapper');
    if (!wrapper) return;

    const placeholder = wrapper.querySelector('.lazy-image-placeholder');
    if (placeholder) {
      placeholder.style.opacity = '0';
      setTimeout(() => {
        placeholder.remove();
      }, config.fadeInDuration);
    }
  }

  /**
   * Handle intersection
   */
  function handleIntersection(entries, observer) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;

        loadImage(img)
          .then(() => {
            removePlaceholder(img);
            observer.unobserve(img);
          })
          .catch((error) => {
            console.error('Error loading image:', error);
            img.classList.add('lazy-error');
          });
      }
    });
  }

  /**
   * Initialize lazy loading
   */
  function init() {
    // Find all lazy images
    const lazyImages = document.querySelectorAll('img[data-src], img[loading="lazy"]');

    if (lazyImages.length === 0) return;

    // Create placeholders
    if (config.enableBlurUp) {
      lazyImages.forEach((img) => {
        if (!img.classList.contains('no-placeholder')) {
          createPlaceholder(img);
        }
      });
    }

    // Use native lazy loading if supported
    if ('loading' in HTMLImageElement.prototype) {
      lazyImages.forEach((img) => {
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
        }
        img.loading = 'lazy';
      });
      return;
    }

    // Fallback to IntersectionObserver
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(handleIntersection, {
        rootMargin: config.rootMargin,
        threshold: config.threshold,
      });

      lazyImages.forEach((img) => observer.observe(img));
    } else {
      // Fallback: Load all images immediately
      lazyImages.forEach((img) => {
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
        }
      });
    }
  }

  /**
   * Add responsive image helper
   */
  function createResponsiveImage(src, alt, sizes = '100vw') {
    // Generate srcset for common breakpoints
    const srcset = [
      `${src}?w=400 400w`,
      `${src}?w=800 800w`,
      `${src}?w=1200 1200w`,
      `${src}?w=1600 1600w`,
    ].join(', ');

    return `
      <img 
        data-src="${src}" 
        data-srcset="${srcset}"
        data-sizes="${sizes}"
        alt="${alt}"
        class="lazy-image"
        loading="lazy"
      >
    `;
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export helper function
  window.createResponsiveImage = createResponsiveImage;
})();
