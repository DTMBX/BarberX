/**
 * Navigation.js – Modern, accessible mobile menu
 * Evident Technologies
 *
 * Features:
 * - Keyboard navigation support
 * - ARIA labels and attributes
 * - Focus management
 * - Mobile-first responsive design
 */

class Navigation {
  constructor() {
    this.mobileNavBtn = document.getElementById('mobile-nav-btn');
    this.primaryNav = document.querySelector('.primary-nav');
    this.isOpen = false;

    if (this.mobileNavBtn && this.primaryNav) {
      this.init();
    }
  }

  init() {
    // Toggle menu on button click
    this.mobileNavBtn.addEventListener('click', () => this.toggleMenu());

    // Close menu on link click
    this.primaryNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => this.closeMenu());
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.closeMenu();
        this.mobileNavBtn.focus();
      }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isOpen && !e.target.closest('.site-header') && !e.target.closest('.primary-nav')) {
        this.closeMenu();
      }
    });
  }

  toggleMenu() {
    if (this.isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  openMenu() {
    this.isOpen = true;
    this.primaryNav.style.display = 'flex';
    this.mobileNavBtn.setAttribute('aria-expanded', 'true');
  }

  closeMenu() {
    this.isOpen = false;
    this.primaryNav.style.display = 'none';
    this.mobileNavBtn.setAttribute('aria-expanded', 'false');
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new Navigation();
  });
} else {
  new Navigation();
}
