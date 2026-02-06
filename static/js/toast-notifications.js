// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Professional Toast Notification System
 * Replaces alert() popups with elegant, accessible notifications
 */

class ToastNotification {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = "toast-container";
      this.container.setAttribute("role", "status");
      this.container.setAttribute("aria-live", "polite");
      this.container.setAttribute("aria-atomic", "true");
      document.body.appendChild(this.container);
    }
  }

  show(message, type = "info", duration = 5000) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icons = {
      success: "✓",
      error: "✕",
      warning: "⚠",
      info: "ⓘ",
    };

    const icon = icons[type] || icons.info;

    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-icon" aria-hidden="true">${icon}</span>
        <span class="toast-message">${this.escapeHtml(message)}</span>
      </div>
      <button class="toast-close" aria-label="Close notification">×</button>
    `;

    toast.querySelector(".toast-close").addEventListener("click", () => {
      this.dismiss(toast);
    });

    this.container.appendChild(toast);

    setTimeout(() => toast.classList.add("toast-show"), 10);

    if (duration > 0) {
      setTimeout(() => this.dismiss(toast), duration);
    }

    return toast;
  }

  dismiss(toast) {
    toast.classList.remove("toast-show");
    toast.classList.add("toast-hide");
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  success(message, duration = 5000) {
    return this.show(message, "success", duration);
  }

  error(message, duration = 7000) {
    return this.show(message, "error", duration);
  }

  warning(message, duration = 6000) {
    return this.show(message, "warning", duration);
  }

  info(message, duration = 5000) {
    return this.show(message, "info", duration);
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize global toast instance
const toast = new ToastNotification();

// Add CSS dynamically
const toastNotificationStyle = document.createElement("style");
toastNotificationStyle.textContent = `
  #toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 420px;
    pointer-events: none;
  }

  .toast {
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: auto;
    min-width: 320px;
  }

  .toast-show {
    opacity: 1;
    transform: translateX(0);
  }

  .toast-hide {
    opacity: 0;
    transform: translateX(100%);
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
  }

  .toast-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
  }

  .toast-message {
    color: #1e293b;
    font-size: 14px;
    line-height: 1.5;
    font-weight: 500;
  }

  .toast-close {
    background: transparent;
    border: none;
    color: #64748b;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
    flex-shrink: 0;
    line-height: 1;
  }

  .toast-close:hover {
    background: #f1f5f9;
    color: #1e293b;
  }

  .toast-close:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  /* Success Toast */
  .toast-success {
    border-left: 4px solid #10b981;
  }

  .toast-success .toast-icon {
    background: #d1fae5;
    color: #059669;
  }

  /* Error Toast */
  .toast-error {
    border-left: 4px solid #ef4444;
  }

  .toast-error .toast-icon {
    background: #fee2e2;
    color: #dc2626;
  }

  /* Warning Toast */
  .toast-warning {
    border-left: 4px solid #f59e0b;
  }

  .toast-warning .toast-icon {
    background: #fef3c7;
    color: #d97706;
  }

  /* Info Toast */
  .toast-info {
    border-left: 4px solid #3b82f6;
  }

  .toast-info .toast-icon {
    background: #dbeafe;
    color: #2563eb;
  }

  /* Mobile Responsive */
  @media (max-width: 480px) {
    #toast-container {
      top: auto;
      bottom: 20px;
      left: 12px;
      right: 12px;
      max-width: none;
    }

    .toast {
      min-width: auto;
      transform: translateY(100%);
    }

    .toast-show {
      transform: translateY(0);
    }

    .toast-hide {
      transform: translateY(100%);
    }
  }

  /* Reduce motion for accessibility */
  @media (prefers-reduced-motion: reduce) {
    .toast {
      transition: opacity 0.3s;
      transform: none !important;
    }
  }
`;
document.head.appendChild(toastNotificationStyle);

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = ToastNotification;
}
