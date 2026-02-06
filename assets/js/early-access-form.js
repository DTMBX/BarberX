// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Early Access Form Handler
 * Redirects to role-specific thank you pages
 */

(function () {
  'use strict';

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    const form = document.querySelector('form[name="early-access"]');
    if (!form) return;

    form.addEventListener('submit', handleSubmit);
  }

  function handleSubmit(e) {
    const form = e.target;
    const interestSelect = form.querySelector('select[name="interest"]');

    if (!interestSelect) return;

    const interest = interestSelect.value;
    const thankYouPages = {
      supporter: '/thank-you/supporter/',
      developer: '/thank-you/developer/',
      reviewer: '/thank-you/reviewer/',
      curious: '/thank-you/curious/',
    };

    // Update form action to redirect to the correct thank you page
    const redirectUrl = thankYouPages[interest] || '/thank-you/curious/';
    form.setAttribute('action', redirectUrl);

    // Let form submit naturally - Netlify will handle it and redirect
  }

  // Add CSS for honeypot field
  const style = document.createElement('style');
  style.textContent = `
    .hidden {
      position: absolute;
      left: -9999px;
      opacity: 0;
      pointer-events: none;
    }
  `;
  document.head.appendChild(style);
})();
