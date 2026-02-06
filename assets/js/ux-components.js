// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident UX Components
 * Toast notifications, form validation, loading states
 */

// ===========================
// Toast Notification System
// ===========================
class ToastManager {
  constructor() {
    this.container = null;
    this.toasts = new Map();
    this.init();
  }

  init() {
    // Create container if it doesn't exist
    if (!document.querySelector(".toast-container")) {
      this.container = document.createElement("div");
      this.container.className = "toast-container";
      this.container.setAttribute("role", "alert");
      this.container.setAttribute("aria-live", "polite");
      document.body.appendChild(this.container);
    } else {
      this.container = document.querySelector(".toast-container");
    }
  }

  show(options) {
    const {
      type = "info",
      title = "",
      message = "",
      duration = 5000,
      dismissible = true,
      icon = null,
    } = options;

    const id = "toast-" + Date.now();
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.id = id;

    const icons = {
      success: "✓",
      error: "✕",
      warning: "⚠",
      info: "ℹ",
    };

    toast.innerHTML = `
      <div class="toast-icon">${icon || icons[type] || icons.info}</div>
      <div class="toast-content">
        ${title ? `<div class="toast-title">${title}</div>` : ""}
        <div class="toast-message">${message}</div>
      </div>
      ${dismissible ? '<button class="toast-close" aria-label="Dismiss">✕</button>' : ""}
      ${duration > 0 ? '<div class="toast-progress"><div class="toast-progress-bar"></div></div>' : ""}
    `;

    // Add close handler
    if (dismissible) {
      toast
        .querySelector(".toast-close")
        .addEventListener("click", () => this.dismiss(id));
    }

    // Set progress bar duration
    if (duration > 0) {
      const progressBar = toast.querySelector(".toast-progress-bar");
      if (progressBar) {
        progressBar.style.animationDuration = `${duration}ms`;
      }
    }

    this.container.appendChild(toast);
    this.toasts.set(id, toast);

    // Auto dismiss
    if (duration > 0) {
      setTimeout(() => this.dismiss(id), duration);
    }

    return id;
  }

  dismiss(id) {
    const toast = this.toasts.get(id);
    if (toast) {
      toast.style.animation = "toast-out 0.3s var(--ease-out) forwards";
      setTimeout(() => {
        toast.remove();
        this.toasts.delete(id);
      }, 300);
    }
  }

  dismissAll() {
    this.toasts.forEach((_, id) => this.dismiss(id));
  }

  // Convenience methods
  success(message, title = "Success") {
    return this.show({ type: "success", title, message });
  }

  error(message, title = "Error") {
    return this.show({ type: "error", title, message, duration: 8000 });
  }

  warning(message, title = "Warning") {
    return this.show({ type: "warning", title, message });
  }

  info(message, title = "") {
    return this.show({ type: "info", title, message });
  }
}

// Global toast instance
window.toast = new ToastManager();

// ===========================
// Form Validation
// ===========================
class FormValidator {
  constructor(form, options = {}) {
    this.form = typeof form === "string" ? document.querySelector(form) : form;
    if (!this.form) return;

    this.options = {
      validateOnBlur: true,
      validateOnInput: true,
      showSuccessState: true,
      ...options,
    };

    this.validators = {
      required: (value) => value.trim() !== "",
      email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
      minLength: (value, min) => value.length >= parseInt(min),
      maxLength: (value, max) => value.length <= parseInt(max),
      pattern: (value, pattern) => new RegExp(pattern).test(value),
      match: (value, fieldName) => {
        const matchField = this.form.querySelector(`[name="${fieldName}"]`);
        return matchField && value === matchField.value;
      },
      password: (value) => {
        // At least 8 chars, 1 uppercase, 1 lowercase, 1 number
        return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(value);
      },
    };

    this.messages = {
      required: "This field is required",
      email: "Please enter a valid email address",
      minLength: "Must be at least {min} characters",
      maxLength: "Must be no more than {max} characters",
      pattern: "Please match the requested format",
      match: "Fields do not match",
      password:
        "Password must be at least 8 characters with uppercase, lowercase, and number",
    };

    this.init();
  }

  init() {
    const inputs = this.form.querySelectorAll("input, select, textarea");

    inputs.forEach((input) => {
      if (this.options.validateOnBlur) {
        input.addEventListener("blur", () => this.validateField(input));
      }
      if (this.options.validateOnInput) {
        input.addEventListener("input", () => this.validateField(input, true));
      }
    });

    this.form.addEventListener("submit", (e) => {
      if (!this.validateAll()) {
        e.preventDefault();
        // Focus first invalid field
        const firstInvalid = this.form.querySelector(".is-invalid");
        if (firstInvalid) firstInvalid.focus();
      }
    });
  }

  validateField(input, isTyping = false) {
    const rules = this.getFieldRules(input);
    let isValid = true;
    let errorMessage = "";

    for (const [rule, param] of Object.entries(rules)) {
      const validator = this.validators[rule];
      if (validator && !validator(input.value, param)) {
        isValid = false;
        errorMessage =
          this.messages[rule]?.replace(`{${rule}}`, param) || "Invalid value";
        break;
      }
    }

    // Don't show error while typing unless field was already invalid
    if (isTyping && !input.classList.contains("is-invalid") && !isValid) {
      return isValid;
    }

    this.setFieldState(input, isValid, errorMessage);
    return isValid;
  }

  validateAll() {
    const inputs = this.form.querySelectorAll("input, select, textarea");
    let isFormValid = true;

    inputs.forEach((input) => {
      if (!this.validateField(input)) {
        isFormValid = false;
      }
    });

    return isFormValid;
  }

  getFieldRules(input) {
    const rules = {};

    if (input.required) rules.required = true;
    if (input.type === "email") rules.email = true;
    if (input.minLength > 0) rules.minLength = input.minLength;
    if (input.maxLength > 0 && input.maxLength < 524288)
      rules.maxLength = input.maxLength;
    if (input.pattern) rules.pattern = input.pattern;
    if (input.dataset.match) rules.match = input.dataset.match;
    if (input.dataset.validate === "password") rules.password = true;

    return rules;
  }

  setFieldState(input, isValid, message = "") {
    const group = input.closest(".form-group") || input.parentElement;
    let feedback = group.querySelector(".form-feedback");

    // Remove existing states
    input.classList.remove("is-valid", "is-invalid");

    if (isValid && this.options.showSuccessState && input.value) {
      input.classList.add("is-valid");
      if (feedback) {
        feedback.className = "form-feedback valid";
        feedback.innerHTML = "<span>✓</span> Looks good";
      }
    } else if (!isValid) {
      input.classList.add("is-invalid");
      if (!feedback) {
        feedback = document.createElement("div");
        group.appendChild(feedback);
      }
      feedback.className = "form-feedback invalid";
      feedback.innerHTML = `<span>!</span> ${message}`;
    } else if (feedback) {
      feedback.textContent = "";
    }
  }
}

// ===========================
// Password Strength Meter
// ===========================
class PasswordStrength {
  constructor(input, options = {}) {
    this.input =
      typeof input === "string" ? document.querySelector(input) : input;
    if (!this.input) return;

    this.options = {
      showMeter: true,
      showText: true,
      ...options,
    };

    this.init();
  }

  init() {
    const wrapper = document.createElement("div");
    wrapper.className = "password-strength";
    wrapper.innerHTML = `
      <div class="password-strength-bar">
        <div class="password-strength-segment"></div>
        <div class="password-strength-segment"></div>
        <div class="password-strength-segment"></div>
        <div class="password-strength-segment"></div>
      </div>
      <div class="password-strength-text"></div>
    `;

    this.input.parentElement.appendChild(wrapper);
    this.meter = wrapper;
    this.textEl = wrapper.querySelector(".password-strength-text");

    this.input.addEventListener("input", () => this.update());
  }

  update() {
    const strength = this.calculate(this.input.value);
    this.meter.dataset.strength = strength.score;
    this.textEl.textContent = strength.label;
  }

  calculate(password) {
    let score = 0;
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      numbers: /\d/.test(password),
      symbols: /[^a-zA-Z0-9]/.test(password),
      longPassword: password.length >= 12,
    };

    if (checks.length) score++;
    if (checks.lowercase && checks.uppercase) score++;
    if (checks.numbers) score++;
    if (checks.symbols || checks.longPassword) score++;

    const labels = ["", "Weak", "Fair", "Good", "Strong"];
    return { score, label: labels[score] || "" };
  }
}

// ===========================
// Skeleton Loader Helper
// ===========================
class SkeletonLoader {
  static card(count = 1) {
    return Array(count)
      .fill(
        `
      <div class="skeleton-card">
        <div class="skeleton skeleton-heading"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text medium"></div>
        <div class="skeleton skeleton-text short"></div>
      </div>
    `,
      )
      .join("");
  }

  static table(rows = 5) {
    return Array(rows)
      .fill(
        `
      <div class="skeleton-table-row">
        <div class="skeleton skeleton-table-cell"></div>
        <div class="skeleton skeleton-table-cell"></div>
        <div class="skeleton skeleton-table-cell"></div>
        <div class="skeleton skeleton-table-cell" style="flex: 0.5"></div>
      </div>
    `,
      )
      .join("");
  }

  static stats(count = 4) {
    return Array(count)
      .fill(
        `
      <div class="skeleton-card" style="text-align: center;">
        <div class="skeleton skeleton-stat" style="margin: 0 auto;"></div>
        <div class="skeleton skeleton-text short" style="margin: 0 auto;"></div>
      </div>
    `,
      )
      .join("");
  }

  static show(container, type = "card", count = 3) {
    const el =
      typeof container === "string"
        ? document.querySelector(container)
        : container;
    if (!el) return;

    el.dataset.originalContent = el.innerHTML;
    el.innerHTML = this[type] ? this[type](count) : this.card(count);
    el.classList.add("loading");
  }

  static hide(container) {
    const el =
      typeof container === "string"
        ? document.querySelector(container)
        : container;
    if (!el) return;

    if (el.dataset.originalContent) {
      el.innerHTML = el.dataset.originalContent;
      delete el.dataset.originalContent;
    }
    el.classList.remove("loading");
  }
}

window.SkeletonLoader = SkeletonLoader;

// ===========================
// Processing Indicator
// ===========================
class ProcessingIndicator {
  constructor(container, options = {}) {
    this.container =
      typeof container === "string"
        ? document.querySelector(container)
        : container;
    this.options = {
      title: "Processing",
      description: "Please wait while we process your request.",
      estimatedTime: null,
      steps: [],
      ...options,
    };
  }

  show() {
    const stepsHtml = this.options.steps
      .map(
        (step, i) => `
      <div class="processing-step ${i === 0 ? "active" : "pending"}" data-step="${i}">
        <div class="processing-step-icon">${i === 0 ? "●" : "○"}</div>
        <div class="processing-step-text">${step}</div>
      </div>
    `,
      )
      .join("");

    this.container.innerHTML = `
      <div class="processing-card">
        <div class="processing-icon spinning">⟳</div>
        <div class="processing-title">${this.options.title}</div>
        <div class="processing-description">${this.options.description}</div>
        ${
          this.options.estimatedTime
            ? `
          <div class="processing-estimate">
            <span class="processing-estimate-icon">⏱</span>
            Estimated time: ${this.options.estimatedTime}
          </div>
        `
            : ""
        }
        ${stepsHtml ? `<div class="processing-steps">${stepsHtml}</div>` : ""}
      </div>
    `;
  }

  updateStep(stepIndex) {
    const steps = this.container.querySelectorAll(".processing-step");
    steps.forEach((step, i) => {
      step.classList.remove("completed", "active", "pending");
      const icon = step.querySelector(".processing-step-icon");
      if (i < stepIndex) {
        step.classList.add("completed");
        icon.textContent = "✓";
      } else if (i === stepIndex) {
        step.classList.add("active");
        icon.textContent = "●";
      } else {
        step.classList.add("pending");
        icon.textContent = "○";
      }
    });
  }

  complete() {
    const card = this.container.querySelector(".processing-card");
    if (card) {
      const icon = card.querySelector(".processing-icon");
      icon.classList.remove("spinning");
      icon.textContent = "✓";
      icon.style.background = "linear-gradient(135deg, #22c55e, #16a34a)";

      card.querySelector(".processing-title").textContent = "Complete!";
      card.querySelector(".processing-description").textContent =
        "Your request has been processed successfully.";

      // Mark all steps complete
      this.updateStep(this.options.steps.length);
    }
  }
}

window.ProcessingIndicator = ProcessingIndicator;

// ===========================
// Utility: Debounce
// ===========================
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

window.debounce = debounce;

// ===========================
// Auto-init on DOM Ready
// ===========================
document.addEventListener("DOMContentLoaded", () => {
  // Auto-init form validation on forms with data-validate
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    new FormValidator(form);
  });

  // Auto-init password strength on inputs with data-password-strength
  document
    .querySelectorAll("input[data-password-strength]")
    .forEach((input) => {
      new PasswordStrength(input);
    });

  // Show toast on flash messages
  const flashMessages = document.querySelectorAll("[data-flash]");
  flashMessages.forEach((el) => {
    const type = el.dataset.flashType || "info";
    const message = el.textContent;
    window.toast.show({ type, message });
    el.remove();
  });
});
