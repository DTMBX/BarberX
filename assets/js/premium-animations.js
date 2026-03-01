/**
 * PREMIUM ANIMATIONS SYSTEM
 * Apple/Stripe-inspired smooth animations
 * Zero dependencies, pure CSS + Vanilla JS
 */

class PremiumAnimations {
  constructor() {
    this.observers = [];
    this.init();
  }

  init() {
    // Initialize all animation systems
    this.setupScrollAnimations();
    this.setupParallax();
    this.setupMagneticButtons();
    this.setupScrollProgress();
    this.setupStaggerAnimations();
    this.setupHoverEffects();
  }

  /**
   * Scroll-triggered animations (Intersection Observer)
   * Like Apple's product pages
   */
  setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.delay || 0;
          setTimeout(() => {
            entry.target.classList.add('animated');
          }, delay);

          // Unobserve after animation
          if (!entry.target.dataset.repeat) {
            observer.unobserve(entry.target);
          }
        } else if (entry.target.dataset.repeat) {
          entry.target.classList.remove('animated');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
    this.observers.push(observer);
  }

  /**
   * Parallax scrolling effects
   * Subtle depth like Stripe
   */
  setupParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');

    if (parallaxElements.length === 0) return;

    const handleScroll = () => {
      const scrolled = window.pageYOffset;

      parallaxElements.forEach(el => {
        const speed = parseFloat(el.dataset.parallax) || 0.5;
        const yPos = -(scrolled * speed);
        el.style.transform = `translate3d(0, ${yPos}px, 0)`;
      });
    };

    // Use requestAnimationFrame for smooth performance
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  /**
   * Magnetic buttons that follow cursor
   * Like Linear.app
   */
  setupMagneticButtons() {
    const magneticButtons = document.querySelectorAll('[data-magnetic]');

    magneticButtons.forEach(button => {
      button.addEventListener('mousemove', (e) => {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        // Limit movement
        const strength = parseFloat(button.dataset.magnetic) || 0.3;
        const moveX = x * strength;
        const moveY = y * strength;

        button.style.transform = `translate(${moveX}px, ${moveY}px)`;
      });

      button.addEventListener('mouseleave', () => {
        button.style.transform = 'translate(0, 0)';
      });
    });
  }

  /**
   * Scroll progress indicator
   * Common on premium sites
   */
  setupScrollProgress() {
    let progressBar = document.querySelector('.scroll-progress');

    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.className = 'scroll-progress';
      document.body.appendChild(progressBar);
    }

    const updateProgress = () => {
      const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = (window.pageYOffset / windowHeight) * 100;
      progressBar.style.width = `${scrolled}%`;
    };

    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  /**
   * Stagger animations for lists
   * Like Apple's feature lists
   */
  setupStaggerAnimations() {
    const staggerContainers = document.querySelectorAll('[data-stagger]');

    staggerContainers.forEach(container => {
      const items = container.children;
      const delay = parseInt(container.dataset.staggerDelay) || 100;

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            Array.from(items).forEach((item, index) => {
              setTimeout(() => {
                item.classList.add('stagger-animate');
              }, index * delay);
            });
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });

      observer.observe(container);
      this.observers.push(observer);
    });
  }

  /**
   * Advanced hover effects
   * Smooth transitions and micro-interactions
   */
  setupHoverEffects() {
    // Ripple effect on buttons
    const rippleButtons = document.querySelectorAll('[data-ripple]');

    rippleButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';

        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
      });
    });

    // Shine effect on cards
    const shineCards = document.querySelectorAll('[data-shine]');

    shineCards.forEach(card => {
      card.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        this.style.setProperty('--mouse-x', `${x}%`);
        this.style.setProperty('--mouse-y', `${y}%`);
      });
    });
  }

  /**
   * Cleanup when needed
   */
  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.premiumAnimations = new PremiumAnimations();
  });
} else {
  window.premiumAnimations = new PremiumAnimations();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PremiumAnimations;
}
