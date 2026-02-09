// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Professional Loading States Component
 * Provides consistent loading indicators across the platform
 */

class LoadingState {
  /**
   * Show loading spinner on a button
   * @param {HTMLElement} button - The button element
   * @param {string} loadingText - Text to show while loading (optional)
   */
  static showButtonLoading(button, loadingText = 'Loading...') {
    if (!button) return;

    // Store original content
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.classList.add('loading');

    const spinner = `
      <span class="btn-spinner" role="status" aria-live="polite">
        <svg class="spinner-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"/>
          <path class="spinner-path" d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
        </svg>
        <span class="spinner-text">${loadingText}</span>
      </span>
    `;

    button.innerHTML = spinner;
  }

  /**
   * Hide loading spinner and restore button
   * @param {HTMLElement} button - The button element
   */
  static hideButtonLoading(button) {
    if (!button) return;

    button.disabled = false;
    button.classList.remove('loading');

    if (button.dataset.originalText) {
      button.innerHTML = button.dataset.originalText;
      delete button.dataset.originalText;
    }
  }

  /**
   * Show full-page loading overlay
   * @param {string} message - Loading message (optional)
   */
  static showPageLoading(message = 'Loading...') {
    let overlay = document.getElementById('page-loading-overlay');

    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'page-loading-overlay';
      overlay.setAttribute('role', 'alert');
      overlay.setAttribute('aria-live', 'assertive');
      overlay.setAttribute('aria-busy', 'true');

      overlay.innerHTML = `
        <div class="page-loading-content">
          <div class="page-spinner">
            <svg class="spinner-icon-lg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path class="spinner-path" d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <p class="page-loading-message">${message}</p>
        </div>
      `;

      document.body.appendChild(overlay);
    }

    setTimeout(() => overlay.classList.add('active'), 10);
  }

  /**
   * Hide full-page loading overlay
   */
  static hidePageLoading() {
    const overlay = document.getElementById('page-loading-overlay');
    if (overlay) {
      overlay.classList.remove('active');
      setTimeout(() => overlay.remove(), 300);
    }
  }

  /**
   * Show loading skeleton in a container
   * @param {HTMLElement} container - Container to show skeleton in
   * @param {string} type - Type of skeleton ('text', 'card', 'list')
   */
  static showSkeleton(container, type = 'text') {
    if (!container) return;

    container.dataset.originalContent = container.innerHTML;

    const skeletons = {
      text: `
        <div class="skeleton-loader">
          <div class="skeleton-line"></div>
          <div class="skeleton-line" style="width: 85%"></div>
          <div class="skeleton-line" style="width: 70%"></div>
        </div>
      `,
      card: `
        <div class="skeleton-loader">
          <div class="skeleton-image"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line" style="width: 90%"></div>
          <div class="skeleton-line" style="width: 60%"></div>
        </div>
      `,
      list: `
        <div class="skeleton-loader">
          <div class="skeleton-list-item"></div>
          <div class="skeleton-list-item"></div>
          <div class="skeleton-list-item"></div>
          <div class="skeleton-list-item"></div>
        </div>
      `,
    };

    container.innerHTML = skeletons[type] || skeletons.text;
    container.classList.add('skeleton-active');
  }

  /**
   * Hide loading skeleton and restore content
   * @param {HTMLElement} container - Container with skeleton
   */
  static hideSkeleton(container) {
    if (!container) return;

    if (container.dataset.originalContent) {
      container.innerHTML = container.dataset.originalContent;
      delete container.dataset.originalContent;
    }
    container.classList.remove('skeleton-active');
  }

  /**
   * Show inline spinner in an element
   * @param {HTMLElement} element - Element to show spinner in
   * @param {string} size - Size ('sm', 'md', 'lg')
   */
  static showInlineSpinner(element, size = 'md') {
    if (!element) return;

    const sizeClasses = {
      sm: 'spinner-sm',
      md: 'spinner-md',
      lg: 'spinner-lg',
    };

    const spinner = document.createElement('span');
    spinner.className = `inline-spinner ${sizeClasses[size]}`;
    spinner.setAttribute('role', 'status');
    spinner.setAttribute('aria-label', 'Loading');
    spinner.innerHTML = `
      <svg class="spinner-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"/>
        <path class="spinner-path" d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
      </svg>
    `;

    element.appendChild(spinner);
    return spinner;
  }

  /**
   * Create a progress bar
   * @param {HTMLElement} container - Container for progress bar
   * @param {number} progress - Progress percentage (0-100)
   * @param {string} label - Progress label (optional)
   */
  static showProgress(container, progress = 0, label = '') {
    if (!container) return;

    let progressBar = container.querySelector('.progress-bar-container');

    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.className = 'progress-bar-container';
      progressBar.setAttribute('role', 'progressbar');
      progressBar.setAttribute('aria-valuemin', '0');
      progressBar.setAttribute('aria-valuemax', '100');

      progressBar.innerHTML = `
        <div class="progress-bar-label"></div>
        <div class="progress-bar-track">
          <div class="progress-bar-fill"></div>
        </div>
        <div class="progress-bar-percentage"></div>
      `;

      container.appendChild(progressBar);
    }

    const fill = progressBar.querySelector('.progress-bar-fill');
    const labelEl = progressBar.querySelector('.progress-bar-label');
    const percentageEl = progressBar.querySelector('.progress-bar-percentage');

    fill.style.width = `${Math.min(100, Math.max(0, progress))}%`;
    progressBar.setAttribute('aria-valuenow', progress);

    if (label) labelEl.textContent = label;
    percentageEl.textContent = `${Math.round(progress)}%`;
  }
}

// Add CSS for loading states
const loadingStatesStyle = document.createElement('style');
loadingStatesStyle.textContent = `
  /* Button Loading States */
  button.loading {
    position: relative;
    cursor: not-allowed;
    opacity: 0.8;
  }

  .btn-spinner {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }

  .spinner-icon {
    width: 1rem;
    height: 1rem;
    animation: spin 1s linear infinite;
  }

  .spinner-track {
    opacity: 0.25;
  }

  .spinner-path {
    animation: spinDash 1.5s ease-in-out infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @keyframes spinDash {
    0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
    50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
    100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
  }

  /* Page Loading Overlay */
  #page-loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
  }

  #page-loading-overlay.active {
    opacity: 1;
    pointer-events: auto;
  }

  .page-loading-content {
    text-align: center;
  }

  .page-spinner {
    margin-bottom: 1.5rem;
  }

  .spinner-icon-lg {
    width: 3rem;
    height: 3rem;
    color: #667eea;
    animation: spin 1s linear infinite;
  }

  .page-loading-message {
    font-size: 1.125rem;
    color: #475569;
    font-weight: 500;
    margin: 0;
  }

  /* Inline Spinners */
  .inline-spinner {
    display: inline-block;
    vertical-align: middle;
  }

  .spinner-sm .spinner-icon { width: 0.875rem; height: 0.875rem; }
  .spinner-md .spinner-icon { width: 1.25rem; height: 1.25rem; }
  .spinner-lg .spinner-icon { width: 2rem; height: 2rem; }

  /* Skeleton Loaders */
  .skeleton-loader {
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  .skeleton-line {
    height: 1rem;
    background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.25rem;
    margin-bottom: 0.75rem;
  }

  .skeleton-image {
    height: 12rem;
    background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }

  .skeleton-list-item {
    height: 3rem;
    background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  /* Progress Bar */
  .progress-bar-container {
    width: 100%;
  }

  .progress-bar-label {
    font-size: 0.875rem;
    color: #475569;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .progress-bar-track {
    width: 100%;
    height: 0.5rem;
    background: #e2e8f0;
    border-radius: 9999px;
    overflow: hidden;
    position: relative;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 9999px;
    transition: width 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .progress-bar-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: progressShine 2s infinite;
  }

  @keyframes progressShine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  .progress-bar-percentage {
    text-align: right;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.375rem;
    font-weight: 600;
  }

  /* Dark theme support */
  @media (prefers-color-scheme: dark) {
    #page-loading-overlay {
      background: rgba(15, 23, 42, 0.95);
    }

    .page-loading-message {
      color: #cbd5e1;
    }

    .skeleton-line,
    .skeleton-image,
    .skeleton-list-item {
      background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
      background-size: 200% 100%;
    }

    .progress-bar-track {
      background: #334155;
    }
  }

  /* Reduce motion accessibility */
  @media (prefers-reduced-motion: reduce) {
    .spinner-icon,
    .spinner-icon-lg,
    .skeleton-loader,
    .progress-bar-fill::after {
      animation: none;
    }
  }
`;
document.head.appendChild(loadingStatesStyle);

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LoadingState;
}
