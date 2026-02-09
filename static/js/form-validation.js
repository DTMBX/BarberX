// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Professional Form Validation System
 * Provides inline, accessible form validation feedback
 */

class FormValidator {
  constructor(formElement, options = {}) {
    this.form = formElement;
    this.options = {
      validateOnBlur: true,
      validateOnInput: false,
      showSuccessIcons: true,
      ...options,
    };
    this.init();
  }

  init() {
    if (!this.form) return;

    this.form.noValidate = true; // Disable browser validation

    this.form.addEventListener('submit', (e) => this.handleSubmit(e));

    if (this.options.validateOnBlur) {
      this.form.querySelectorAll('input, textarea, select').forEach((field) => {
        field.addEventListener('blur', () => this.validateField(field));
      });
    }

    if (this.options.validateOnInput) {
      this.form.querySelectorAll('input, textarea').forEach((field) => {
        field.addEventListener('input', () => {
          if (field.classList.contains('is-invalid') || field.classList.contains('is-valid')) {
            this.validateField(field);
          }
        });
      });
    }
  }

  handleSubmit(e) {
    e.preventDefault();

    const isValid = this.validateForm();

    if (isValid) {
      // Trigger custom event for form submission
      const submitEvent = new CustomEvent('validSubmit', {
        detail: { form: this.form },
      });
      this.form.dispatchEvent(submitEvent);
    } else {
      // Focus first invalid field
      const firstInvalid = this.form.querySelector('.is-invalid');
      if (firstInvalid) {
        firstInvalid.focus();
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    return isValid;
  }

  validateForm() {
    let isValid = true;
    const fields = this.form.querySelectorAll('input, textarea, select');

    fields.forEach((field) => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });

    return isValid;
  }

  validateField(field) {
    // Skip if field is disabled or readonly
    if (field.disabled || field.readOnly) {
      return true;
    }

    const validators = {
      required: () => this.validateRequired(field),
      email: () => this.validateEmail(field),
      minLength: () => this.validateMinLength(field),
      maxLength: () => this.validateMaxLength(field),
      pattern: () => this.validatePattern(field),
      match: () => this.validateMatch(field),
      custom: () => this.validateCustom(field),
    };

    let isValid = true;
    let errorMessage = '';

    // Check each validation rule
    for (const [rule, validator] of Object.entries(validators)) {
      if (field.hasAttribute(`data-${rule}`) || (rule === 'required' && field.required)) {
        const result = validator();
        if (!result.valid) {
          isValid = false;
          errorMessage = result.message;
          break;
        }
      }
    }

    this.showFieldFeedback(field, isValid, errorMessage);
    return isValid;
  }

  validateRequired(field) {
    const value = field.value.trim();
    if (!value) {
      return { valid: false, message: 'This field is required' };
    }
    return { valid: true };
  }

  validateEmail(field) {
    const value = field.value.trim();
    if (!value) return { valid: true }; // Skip if empty (use required for that)

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return { valid: false, message: 'Please enter a valid email address' };
    }
    return { valid: true };
  }

  validateMinLength(field) {
    const minLength = parseInt(field.getAttribute('data-minlength') || field.minLength);
    const value = field.value;

    if (value.length > 0 && value.length < minLength) {
      return {
        valid: false,
        message: `Must be at least ${minLength} characters`,
      };
    }
    return { valid: true };
  }

  validateMaxLength(field) {
    const maxLength = parseInt(field.getAttribute('data-maxlength') || field.maxLength);
    const value = field.value;

    if (maxLength > 0 && value.length > maxLength) {
      return {
        valid: false,
        message: `Must not exceed ${maxLength} characters`,
      };
    }
    return { valid: true };
  }

  validatePattern(field) {
    const pattern = field.getAttribute('data-pattern') || field.pattern;
    if (!pattern) return { valid: true };

    const value = field.value;
    if (!value) return { valid: true };

    const regex = new RegExp(pattern);
    if (!regex.test(value)) {
      const message = field.getAttribute('data-pattern-message') || 'Invalid format';
      return { valid: false, message };
    }
    return { valid: true };
  }

  validateMatch(field) {
    const matchField = field.getAttribute('data-match');
    if (!matchField) return { valid: true };

    const matchElement = this.form.querySelector(`[name="${matchField}"]`);
    if (!matchElement) return { valid: true };

    if (field.value !== matchElement.value) {
      const message = field.getAttribute('data-match-message') || 'Fields do not match';
      return { valid: false, message };
    }
    return { valid: true };
  }

  validateCustom(field) {
    const customValidator = field.getAttribute('data-custom');
    if (!customValidator) return { valid: true };

    // Custom validators can be defined globally
    if (window.customValidators && window.customValidators[customValidator]) {
      return window.customValidators[customValidator](field);
    }
    return { valid: true };
  }

  showFieldFeedback(field, isValid, errorMessage) {
    const fieldContainer = field.closest('.form-group') || field.parentElement;

    // Remove existing feedback
    field.classList.remove('is-valid', 'is-invalid');
    const existingFeedback = fieldContainer.querySelector('.field-feedback');
    if (existingFeedback) {
      existingFeedback.remove();
    }

    if (isValid && this.options.showSuccessIcons && field.value.trim()) {
      field.classList.add('is-valid');
    } else if (!isValid) {
      field.classList.add('is-invalid');

      const feedback = document.createElement('div');
      feedback.className = 'field-feedback invalid-feedback';
      feedback.textContent = errorMessage;
      feedback.setAttribute('role', 'alert');

      fieldContainer.appendChild(feedback);

      // Update ARIA
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', `${field.id || field.name}-error`);
      feedback.id = `${field.id || field.name}-error`;
    } else {
      field.removeAttribute('aria-invalid');
      field.removeAttribute('aria-describedby');
    }
  }

  reset() {
    this.form.querySelectorAll('.is-valid, .is-invalid').forEach((field) => {
      field.classList.remove('is-valid', 'is-invalid');
      field.removeAttribute('aria-invalid');
      field.removeAttribute('aria-describedby');
    });

    this.form.querySelectorAll('.field-feedback').forEach((feedback) => {
      feedback.remove();
    });
  }
}

// Add CSS for validation feedback
const formValidationStyle = document.createElement('style');
formValidationStyle.textContent = `
  .form-group {
    position: relative;
    margin-bottom: 1.25rem;
  }

  input.is-valid,
  textarea.is-valid,
  select.is-valid {
    border-color: #10b981;
    padding-right: 2.5rem;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2310b981' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1.25rem;
  }

  input.is-invalid,
  textarea.is-invalid,
  select.is-invalid {
    border-color: #ef4444;
    padding-right: 2.5rem;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'%3E%3C/circle%3E%3Cline x1='15' y1='9' x2='9' y2='15'%3E%3C/line%3E%3Cline x1='9' y1='9' x2='15' y2='15'%3E%3C/line%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1.25rem;
  }

  input.is-valid:focus,
  textarea.is-valid:focus,
  select.is-valid:focus {
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
  }

  input.is-invalid:focus,
  textarea.is-invalid:focus,
  select.is-invalid:focus {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .field-feedback {
    font-size: 0.875rem;
    margin-top: 0.375rem;
    display: flex;
    align-items: center;
    gap: 0.375rem;
  }

  .invalid-feedback {
    color: #ef4444;
  }

  .invalid-feedback::before {
    content: "⚠";
    font-size: 1rem;
  }

  .valid-feedback {
    color: #10b981;
  }

  /* Ensure required field indicators are visible */
  .required-indicator,
  .required {
    color: #ef4444;
    margin-left: 0.25rem;
  }
`;
document.head.appendChild(formValidationStyle);

// Global custom validators
window.customValidators = {
  password: (field) => {
    const value = field.value;
    if (value.length < 8) {
      return {
        valid: false,
        message: 'Password must be at least 8 characters',
      };
    }
    if (!/[0-9]/.test(value)) {
      return {
        valid: false,
        message: 'Password must include at least one number',
      };
    }
    if (!/[!@#$%^&*]/.test(value)) {
      return {
        valid: false,
        message: 'Password must include a special character (!@#$%^&*)',
      };
    }
    return { valid: true };
  },
};

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormValidator;
}
