#!/usr/bin/env node

/**
 * MOBILE WEB APP REPAIR SCRIPT
 * Fixes all mobile experience issues for optimal touch/mobile performance
 */

const fs = require('fs');
const path = require('path');

console.log('📱 REPAIRING MOBILE WEB APP EXPERIENCE...\n');

// ============================================================================
// 1. CREATE COMPREHENSIVE MOBILE FIX CSS
// ============================================================================

const mobileMasterFix = `/* ============================================================
   MOBILE WEB APP MASTER FIX
   Comprehensive mobile experience optimization
   ============================================================ */

/* ===== CORE MOBILE FOUNDATION ===== */
@media (max-width: 1080px) {
  /* Enable natural scrolling */
  html, body {
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
    height: auto;
    min-height: 100vh;
    min-height: 100dvh; /* Dynamic viewport for iOS */
  }
  
  /* Ensure content is always visible */
  .ts-main-content,
  main,
  #main-content {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative;
    overflow: visible;
    min-height: 50vh;
  }
  
  /* Prevent horizontal scroll */
  * {
    max-width: 100vw;
  }
  
  /* Smooth touch interactions */
  * {
    -webkit-tap-highlight-color: rgba(0, 163, 92, 0.2);
    touch-action: manipulation;
  }
  
  a, button, [role="button"], input, select, textarea {
    touch-action: manipulation;
  }
}

/* ===== TOUCH TARGET SIZES (48x48 minimum) ===== */
@media (max-width: 768px) {
  button,
  a.btn,
  .btn,
  [role="button"],
  .mobile-nav__toggle,
  .mobile-nav__close,
  input[type="submit"],
  input[type="button"] {
    min-height: 48px;
    min-width: 48px;
    padding: 12px 20px;
    font-size: 16px; /* Prevent iOS zoom */
  }
  
  /* Form inputs - prevent zoom */
  input[type="text"],
  input[type="email"],
  input[type="tel"],
  input[type="number"],
  input[type="search"],
  textarea,
  select {
    font-size: 16px !important; /* Critical: prevents iOS zoom */
    min-height: 48px;
    padding: 12px 16px;
  }
}

/* ===== MOBILE NAVIGATION ===== */
@media (max-width: 1080px) {
  .mobile-nav {
    position: fixed;
    top: 0;
    right: -100%;
    width: 85vw;
    max-width: 320px;
    height: 100vh;
    height: 100dvh;
    z-index: 10000;
    background: #f8f7f5;
    box-shadow: -4px 0 20px rgba(0,0,0,0.3);
    transition: right 0.3s ease;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .mobile-nav[aria-hidden="false"],
  .mobile-nav.is-open {
    right: 0;
  }
  
  /* Hamburger menu */
  .mobile-nav__toggle {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 6px;
    width: 48px;
    height: 48px;
    background: transparent;
    border: none;
    cursor: pointer;
    z-index: 10001;
  }
  
  .hamburger {
    width: 24px;
    height: 2px;
    background: #ffffff;
    border-radius: 2px;
    transition: transform 0.3s ease, opacity 0.3s ease;
  }
  
  .mobile-nav__toggle[aria-expanded="true"] .hamburger:nth-child(1) {
    transform: rotate(45deg) translate(7px, 7px);
  }
  
  .mobile-nav__toggle[aria-expanded="true"] .hamburger:nth-child(2) {
    opacity: 0;
  }
  
  .mobile-nav__toggle[aria-expanded="true"] .hamburger:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -7px);
  }
}

/* ===== HEADER FIXES ===== */
@media (max-width: 1080px) {
  .ts-header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(26, 28, 26, 0.95);
    backdrop-filter: blur(10px);
  }
  
  .desktop-nav {
    display: none;
  }
}

/* ===== STICKY CTA BAR ===== */
@media (max-width: 768px) {
  .sticky-cta-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: rgba(26, 28, 26, 0.98);
    backdrop-filter: blur(10px);
    padding: 12px 16px;
    padding-bottom: calc(12px + env(safe-area-inset-bottom));
    box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
  }
  
  .sticky-cta-bar .btn {
    width: 100%;
  }
}

/* ===== SAFE AREAS (iOS notch) ===== */
@supports (padding: env(safe-area-inset-top)) {
  .ts-header {
    padding-top: env(safe-area-inset-top);
  }
  
  .sticky-cta-bar {
    padding-bottom: calc(12px + env(safe-area-inset-bottom));
  }
}

/* ===== SPACING & LAYOUT ===== */
@media (max-width: 768px) {
  .container,
  .ts-hero__inner {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .section {
    padding: 2rem 0;
  }
  
  h1 { font-size: clamp(2rem, 7vw, 3rem); }
  h2 { font-size: clamp(1.5rem, 6vw, 2rem); }
  h3 { font-size: clamp(1.25rem, 5vw, 1.75rem); }
}

/* ===== PERFORMANCE ===== */
@media (max-width: 768px) {
  /* Reduce animations on mobile */
  * {
    animation-duration: 0.3s !important;
    transition-duration: 0.3s !important;
  }
  
  /* Optimize rendering */
  .ts-header,
  .mobile-nav,
  .sticky-cta-bar {
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
  }
}

/* ===== FIX COMMON MOBILE ISSUES ===== */
@media (max-width: 768px) {
  /* Kill transforms that break layout */
  .ts-main-content > * {
    transform: none !important;
  }
  
  /* Prevent content jump */
  img, video {
    max-width: 100%;
    height: auto;
  }
  
  /* Fix tables */
  table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  /* Stack cards */
  .grid,
  .card-grid {
    grid-template-columns: 1fr !important;
  }
}
`;

const mobileMasterPath = path.join(__dirname, '..', 'assets', 'css', 'mobile-master-fix.css');
fs.writeFileSync(mobileMasterPath, mobileMasterFix, 'utf8');
console.log('✅ Created mobile-master-fix.css\n');

// ============================================================================
// 2. CREATE MOBILE JAVASCRIPT ENHANCER
// ============================================================================

const mobileJS = `/**
 * Mobile Web App Enhancer
 * Optimizes touch interactions and mobile UX
 */

(function() {
  'use strict';
  
  // Detect mobile
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || window.innerWidth <= 1080;
  
  if (!isMobile) return;
  
  console.log('📱 Mobile enhancer active');
  
  // ========================================
  // FAST CLICK (remove 300ms delay)
  // ========================================
  
  document.addEventListener('touchstart', function() {}, { passive: true });
  
  // ========================================
  // PREVENT ZOOM ON DOUBLE TAP
  // ========================================
  
  let lastTouchEnd = 0;
  document.addEventListener('touchend', function(e) {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
      e.preventDefault();
    }
    lastTouchEnd = now;
  }, { passive: false });
  
  // ========================================
  // FIX iOS BOUNCE (only on body, not scrollable areas)
  // ========================================
  
  let startY = 0;
  document.body.addEventListener('touchstart', function(e) {
    startY = e.touches[0].pageY;
  }, { passive: true });
  
  document.body.addEventListener('touchmove', function(e) {
    const y = e.touches[0].pageY;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    
    // At top and scrolling up
    if (scrollTop <= 0 && y > startY) {
      e.preventDefault();
    }
    // At bottom and scrolling down
    else if (scrollTop + clientHeight >= scrollHeight && y < startY) {
      e.preventDefault();
    }
  }, { passive: false });
  
  // ========================================
  // VIEWPORT HEIGHT FIX (address bar)
  // ========================================
  
  function setViewportHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', \`\${vh}px\`);
  }
  
  setViewportHeight();
  window.addEventListener('resize', setViewportHeight);
  window.addEventListener('orientationchange', setViewportHeight);
  
  // ========================================
  // TOUCH RIPPLE EFFECT
  // ========================================
  
  document.addEventListener('touchstart', function(e) {
    const target = e.target.closest('a, button, [role="button"]');
    if (!target) return;
    
    target.style.transform = 'scale(0.98)';
    target.style.transition = 'transform 0.1s ease';
  }, { passive: true });
  
  document.addEventListener('touchend', function(e) {
    const target = e.target.closest('a, button, [role="button"]');
    if (!target) return;
    
    setTimeout(() => {
      target.style.transform = '';
    }, 100);
  }, { passive: true });
  
  // ========================================
  // ORIENTATION CHANGE HANDLER
  // ========================================
  
  window.addEventListener('orientationchange', function() {
    // Prevent zoom on orientation change
    document.querySelector('meta[name="viewport"]')?.setAttribute(
      'content',
      'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
    );
    
    setTimeout(() => {
      document.querySelector('meta[name="viewport"]')?.setAttribute(
        'content',
        'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes'
      );
    }, 500);
  });
  
  console.log('📱 Mobile enhancements loaded');
  
})();
`;

const mobileJSPath = path.join(__dirname, '..', 'assets', 'js', 'mobile-enhancer.js');
fs.writeFileSync(mobileJSPath, mobileJS, 'utf8');
console.log('✅ Created mobile-enhancer.js\n');

// ============================================================================
// 3. UPDATE MOBILE EMERGENCY FIX
// ============================================================================

const emergencyFix = `/* Mobile Emergency Fix - Streamlined */

@media (max-width: 768px) {
  /* Ensure content visibility */
  html, body {
    overflow-y: auto;
    overflow-x: hidden;
    height: auto;
  }
  
  .ts-main-content {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative;
    overflow: visible;
  }
  
  /* Prevent off-screen content */
  * {
    max-width: 100vw;
  }
}
`;

const emergencyPath = path.join(__dirname, '..', 'assets', 'css', 'mobile-emergency-fix.css');
fs.writeFileSync(emergencyPath, emergencyFix, 'utf8');
console.log('✅ Updated mobile-emergency-fix.css\n');

console.log('\n' + '='.repeat(70));
console.log('✨ MOBILE WEB APP REPAIR COMPLETE ✨');
console.log('='.repeat(70));
console.log('\n📊 Created/Updated:');
console.log('   ✓ assets/css/mobile-master-fix.css (new)');
console.log('   ✓ assets/js/mobile-enhancer.js (new)');
console.log('   ✓ assets/css/mobile-emergency-fix.css (updated)');
console.log('\n🎯 Features Added:');
console.log('   • Natural touch scrolling');
console.log('   • 48x48px touch targets');
console.log('   • No iOS zoom on inputs (16px fonts)');
console.log('   • Fast tap (no 300ms delay)');
console.log('   • Viewport height fixes');
console.log('   • Safe area support (notch)');
console.log('   • Touch ripple effects');
console.log('   • Optimized animations');
console.log('\n📝 Next: Add these files to your HTML layout!\n');
