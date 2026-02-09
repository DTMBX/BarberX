// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Stewardship Resources Page
 * Handles product filtering and dynamic display
 */

(function () {
  'use strict';

  // Get products from embedded data (loaded by Jekyll)
  const productsData = window.stewardshipProducts || null;

  // Create product card HTML
  function createProductCard(product) {
    const card = document.createElement('article');
    card.className = 'product-card';
    card.dataset.category = product.category;

    const personalNote = product.personal_note
      ? `<p class="product-note">"${escapeHtml(product.personal_note)}"</p>`
      : '';

    card.innerHTML = `
      <div class="product-category-badge">${escapeHtml(product.category)}</div>
      <h3 class="product-title">${escapeHtml(product.title)}</h3>
      <p class="product-description">${escapeHtml(product.description)}</p>
      ${personalNote}
      <a href="${escapeHtml(product.amazon_url)}" 
         class="product-link" 
         target="_blank" 
         rel="noopener nofollow sponsored">
        View on Amazon
      </a>
    `;

    return card;
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Filter products by category
  function filterProducts(category) {
    const cards = document.querySelectorAll('.product-card');

    cards.forEach((card) => {
      if (category === 'all' || card.dataset.category === category) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  }

  // Initialize page
  function init() {
    const grid = document.getElementById('resourcesGrid');
    const filterBtns = document.querySelectorAll('.filter-btn');

    // If products loaded, render them
    if (productsData && grid) {
      // Clear loading message
      grid.innerHTML = '';

      // Flatten products from all categories
      const allProducts = [];
      Object.keys(productsData).forEach((category) => {
        if (category === '_metadata') return; // Skip metadata
        if (Array.isArray(productsData[category])) {
          productsData[category].forEach((product) => {
            allProducts.push({ ...product, category });
          });
        }
      });

      // Sort by date_added (newest first)
      allProducts.sort((a, b) => {
        const dateA = a.date_added ? new Date(a.date_added) : new Date(0);
        const dateB = b.date_added ? new Date(b.date_added) : new Date(0);
        return dateB - dateA;
      });

      // Render cards
      allProducts.forEach((product) => {
        grid.appendChild(createProductCard(product));
      });

      // If no products, show message
      if (allProducts.length === 0) {
        grid.innerHTML = `
          <div class="resources-placeholder">
            <p><strong>No products added yet.</strong></p>
            <p>Check back soon for curated recommendations.</p>
          </div>
        `;
      }
    } else if (grid) {
      // No data available
      grid.innerHTML = `
        <div class="resources-placeholder">
          <p><strong>Products loading...</strong></p>
          <p>If this message persists, please refresh the page.</p>
        </div>
      `;
    }

    // Set up filter buttons
    filterBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        // Update active state
        filterBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        // Filter products
        const category = btn.dataset.category;
        filterProducts(category);
      });
    });
  }

  // Run when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
