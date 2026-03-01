/**
 * Minimal Scroll Fix - Only prevents body scroll when mobile nav is open
 * Native browser scrolling everywhere else for maximum speed
 */

(function() {
  'use strict';

  const isMobile = () => window.innerWidth < 1080;
  
  // Simple: lock scroll only on mobile with nav open
  const observer = new MutationObserver(() => {
    const navOpen = document.body.classList.contains('nav-open');
    
    if (isMobile() && navOpen) {
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
    } else {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    }
  });

  observer.observe(document.body, { 
    attributes: true, 
    attributeFilter: ['class'] 
  });

  // Close mobile nav on resize to desktop
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (!isMobile()) {
        document.body.classList.remove('nav-open');
      }
    }, 150);
  }, { passive: true });

})();
