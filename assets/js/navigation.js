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
    this.mobileNavBtn = document.querySelector('[data-nav-toggle]');
    this.mobileNav = document.getElementById('header-nav-mobile');
    this.isOpen = false;

    if (this.mobileNavBtn && this.mobileNav) {
      this.init();
    }
  }

  init() {
    // Toggle menu on button click
    this.mobileNavBtn.addEventListener('click', () => this.toggleMenu());

    // Close menu on link click
    this.mobileNav.querySelectorAll('a').forEach((link) => {
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
      if (
        this.isOpen &&
        !e.target.closest('.site-header') &&
        !e.target.closest('.header-nav-mobile')
      ) {
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
    this.mobileNav.hidden = false;
    this.mobileNavBtn.setAttribute('aria-expanded', 'true');
    this.mobileNavBtn.classList.add('active');
  }

  closeMenu() {
    this.isOpen = false;
    this.mobileNav.hidden = true;
    this.mobileNavBtn.setAttribute('aria-expanded', 'false');
    this.mobileNavBtn.classList.remove('active');
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
