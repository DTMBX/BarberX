/**
 * Main Application Entry Point
 * Integrates all premium features: animations, performance, and optimization
 */

import { initAnimations } from './animations.js';
import { initPerformance } from './performance.js';

// Initialize everything when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('🎯 Initializing Tillerstead Premium Features...');

  // Initialize performance optimizations first
  initPerformance();

  // Then initialize animations
  initAnimations();

  // Additional initializations
  initSmoothScroll();
  initFormEnhancements();
  initInteractiveElements();

  console.log('✅ All premium features loaded successfully!');
}

// Native anchor scrolling - browser handles it
function initSmoothScroll() {
  // Let browser handle anchor links natively - faster and more responsive
  // Remove this function if not needed
}

// Enhanced form handling
function initFormEnhancements() {
  const forms = document.querySelectorAll('form[data-enhanced]');

  forms.forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Add loading state
      const submitBtn = form.querySelector('[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Sending...';
      submitBtn.disabled = true;

      // Simulate form submission (replace with actual logic)
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Show success message
      submitBtn.textContent = '✓ Sent!';
      
      setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        form.reset();
      }, 2000);
    });
  });
}

// Interactive element enhancements
function initInteractiveElements() {
  // Add ripple effect to buttons
  document.querySelectorAll('.btn, button').forEach((btn) => {
    btn.addEventListener('click', createRipple);
  });

  // Parallax backgrounds
  const parallaxElements = document.querySelectorAll('[data-parallax]');
  if (parallaxElements.length > 0) {
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      
      parallaxElements.forEach((el) => {
        const speed = el.dataset.parallaxSpeed || 0.5;
        el.style.transform = `translateY(${scrolled * speed}px)`;
      });
    });
  }

  // Intersection Observer for counting animations
  const counters = document.querySelectorAll('[data-counter]');
  if (counters.length > 0) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((counter) => observer.observe(counter));
  }
}

// Ripple effect
function createRipple(e) {
  const button = e.currentTarget;
  const ripple = document.createElement('span');
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = e.clientX - rect.left - size / 2;
  const y = e.clientY - rect.top - size / 2;

  ripple.style.width = ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.classList.add('ripple');

  const existingRipple = button.querySelector('.ripple');
  if (existingRipple) existingRipple.remove();

  button.appendChild(ripple);

  setTimeout(() => ripple.remove(), 600);
}

// Counter animation
function animateCounter(element) {
  const target = parseInt(element.dataset.counter);
  const duration = 2000;
  const increment = target / (duration / 16);
  let current = 0;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target.toLocaleString();
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current).toLocaleString();
    }
  }, 16);
}

// Export for use in other modules
export { init, initSmoothScroll, initFormEnhancements, initInteractiveElements };
