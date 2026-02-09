// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * ENHANCED ANIMATIONS SYSTEM v2.0
 * Modern ES6+ Animation Engine with GPU-accelerated effects
 *
 * Features:
 * - Intersection Observer API for performance
 * - GPU-accelerated transforms
 * - Parallax scrolling effects
 * - Smooth reveal animations
 * - Counter animations
 * - Particle effects
 * - Magnetic hover effects
 */

class AnimationEngine {
  constructor() {
    this.observers = new Map();
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.init();
  }

  init() {
    if (this.prefersReducedMotion) {
      document.documentElement.classList.add('reduced-motion');
      return;
    }

    this.setupScrollReveal();
    this.setupParallax();
    this.setupCounters();
    this.setupHoverEffects();
    this.setupPageTransitions();
    this.setupSmoothScroll();
  }

  /**
   * SCROLL REVEAL ANIMATIONS
   * Reveal elements as they enter viewport with various effects
   */
  setupScrollReveal() {
    const revealOptions = {
      root: null,
      rootMargin: '0px 0px -100px 0px',
      threshold: [0, 0.1, 0.5, 1.0],
    };

    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.delay || 0;

          setTimeout(() => {
            entry.target.classList.add('revealed');

            // Trigger custom event for chaining
            entry.target.dispatchEvent(
              new CustomEvent('element-revealed', {
                bubbles: true,
                detail: { target: entry.target },
              })
            );
          }, delay);

          // Unobserve after reveal for performance
          revealObserver.unobserve(entry.target);
        }
      });
    }, revealOptions);

    // Observe all reveal elements
    const selectors = [
      '.fade-in',
      '.slide-up',
      '.slide-down',
      '.slide-left',
      '.slide-right',
      '.zoom-in',
      '.zoom-out',
      '.rotate-in',
      '.flip-in',
      '.blur-in',
    ];

    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((el) => {
        revealObserver.observe(el);
      });
    });

    this.observers.set('reveal', revealObserver);
  }

  /**
   * PARALLAX SCROLLING
   * Create depth with scroll-based transforms
   */
  setupParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    if (parallaxElements.length === 0) return;

    let ticking = false;

    const updateParallax = () => {
      const scrollY = window.pageYOffset;

      parallaxElements.forEach((el) => {
        const speed = parseFloat(el.dataset.parallax) || 0.5;
        const direction = el.dataset.parallaxDirection || 'up';
        const yPos = scrollY * speed;

        let transform = '';
        switch (direction) {
          case 'up':
            transform = `translate3d(0, ${-yPos}px, 0)`;
            break;
          case 'down':
            transform = `translate3d(0, ${yPos}px, 0)`;
            break;
          case 'left':
            transform = `translate3d(${-yPos}px, 0, 0)`;
            break;
          case 'right':
            transform = `translate3d(${yPos}px, 0, 0)`;
            break;
        }

        el.style.transform = transform;
      });

      ticking = false;
    };

    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          requestAnimationFrame(updateParallax);
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  /**
   * ANIMATED COUNTERS
   * Count up numbers when they become visible
   */
  setupCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length === 0) return;

    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const target = entry.target;
            const endValue = parseInt(target.dataset.counter);
            const duration = parseInt(target.dataset.counterDuration) || 2000;
            const startValue = parseInt(target.dataset.counterStart) || 0;

            this.animateCounter(target, startValue, endValue, duration);
            counterObserver.unobserve(target);
          }
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((counter) => counterObserver.observe(counter));
    this.observers.set('counter', counterObserver);
  }

  animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;
    const prefix = element.dataset.counterPrefix || '';
    const suffix = element.dataset.counterSuffix || '';

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }

      element.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
    }, 16);
  }

  /**
   * MAGNETIC HOVER EFFECTS
   * Elements follow cursor on hover
   */
  setupHoverEffects() {
    const magneticElements = document.querySelectorAll('[data-magnetic]');

    magneticElements.forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        const strength = parseFloat(el.dataset.magnetic) || 0.3;

        el.style.transform = `translate3d(${x * strength}px, ${y * strength}px, 0)`;
      });

      el.addEventListener('mouseleave', () => {
        el.style.transform = 'translate3d(0, 0, 0)';
      });
    });

    // Ripple effect on click
    const rippleElements = document.querySelectorAll('[data-ripple]');

    rippleElements.forEach((el) => {
      el.addEventListener('click', (e) => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        el.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
      });
    });
  }

  /**
   * PAGE TRANSITIONS
   * Smooth page load and navigation animations
   */
  setupPageTransitions() {
    // Fade in on page load
    document.body.classList.add('page-loaded');

    // Smooth internal navigation
    document.querySelectorAll('a[href^="/"], a[href^="./"], a[href^="../"]').forEach((link) => {
      if (link.dataset.noTransition) return;

      link.addEventListener('click', (e) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) return; // Allow opening in new tab

        const href = link.getAttribute('href');
        if (!href || href === '#') return;

        e.preventDefault();

        document.body.classList.add('page-transitioning');

        setTimeout(() => {
          window.location.href = href;
        }, 300);
      });
    });
  }

  /**
   * SMOOTH SCROLL
   * Enhanced smooth scrolling to anchors
   */
  setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', (e) => {
        const href = anchor.getAttribute('href');
        if (href === '#') return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        const offsetTop = target.getBoundingClientRect().top + window.pageYOffset;
        const offset = parseInt(anchor.dataset.scrollOffset) || 80;

        window.scrollTo({
          top: offsetTop - offset,
          behavior: 'smooth',
        });

        // Update URL without triggering navigation
        if (history.pushState) {
          history.pushState(null, null, href);
        }
      });
    });
  }

  /**
   * STAGGER ANIMATIONS
   * Animate child elements in sequence
   */
  static stagger(container, selector, delay = 100) {
    const elements = container.querySelectorAll(selector);

    elements.forEach((el, index) => {
      el.style.animationDelay = `${index * delay}ms`;
      el.classList.add('stagger-item');
    });
  }

  /**
   * CLEANUP
   * Disconnect all observers
   */
  destroy() {
    this.observers.forEach((observer) => observer.disconnect());
    this.observers.clear();
  }
}

/**
 * SCROLL PROGRESS INDICATOR
 * Shows reading progress at top of page
 */
class ScrollProgress {
  constructor() {
    this.progressBar = this.createProgressBar();
    this.init();
  }

  createProgressBar() {
    const bar = document.createElement('div');
    bar.className = 'scroll-progress-bar';
    bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = '<div class="scroll-progress-fill"></div>';
    document.body.appendChild(bar);
    return bar;
  }

  init() {
    let ticking = false;

    const updateProgress = () => {
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;

      const fill = this.progressBar.querySelector('.scroll-progress-fill');
      fill.style.width = `${scrolled}%`;

      ticking = false;
    };

    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          requestAnimationFrame(updateProgress);
          ticking = true;
        }
      },
      { passive: true }
    );
  }
}

/**
 * FLOATING ELEMENTS
 * Create subtle floating animation
 */
class FloatingAnimation {
  static apply(selector, options = {}) {
    const elements = document.querySelectorAll(selector);
    const { distance = 20, duration = 3000, delay = 0 } = options;

    elements.forEach((el, index) => {
      const animDelay = delay + index * 200;

      el.style.animation = `float ${duration}ms ease-in-out ${animDelay}ms infinite`;
      el.style.setProperty('-float-distance', `${distance}px`);
    });
  }
}

/**
 * TEXT ANIMATIONS
 * Animate text reveal character by character
 */
class TextReveal {
  static reveal(element, options = {}) {
    const { duration = 50, delay = 0, stagger = true } = options;

    const text = element.textContent;
    element.textContent = '';
    element.style.opacity = '1';

    const chars = text.split('');
    const spans = chars.map((char, i) => {
      const span = document.createElement('span');
      span.textContent = char === ' ' ? '\u00A0' : char;
      span.style.opacity = '0';
      span.style.display = 'inline-block';

      if (stagger) {
        span.style.animationDelay = `${delay + i * duration}ms`;
      }

      span.classList.add('char-reveal');
      element.appendChild(span);
      return span;
    });

    // Trigger animation
    setTimeout(() => {
      spans.forEach((span) => {
        span.style.opacity = '1';
      });
    }, delay);
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.animationEngine = new AnimationEngine();
    window.scrollProgress = new ScrollProgress();
  });
} else {
  window.animationEngine = new AnimationEngine();
  window.scrollProgress = new ScrollProgress();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AnimationEngine,
    ScrollProgress,
    FloatingAnimation,
    TextReveal,
  };
}
