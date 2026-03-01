/**
 * TillerPro™ Quote Validation System
 * Ensures accuracy and legal compliance before quote generation
 *
 * @version 2.0.0
 * @author Tillerstead LLC
 */

class QuoteValidator {
  constructor(config) {
    this.config = config || window.TillerProConfig;
    this.errors = [];
    this.warnings = [];
    this.validationRules = this.config?.quote?.validation || {};
  }

  /**
   * Validate entire quote before generation
   * @param {Object} quoteData - Quote data to validate
   * @returns {Object} { valid: boolean, errors: [], warnings: [] }
   */
  validate(quoteData) {
    this.errors = [];
    this.warnings = [];

    // Run all validation checks
    this.validateCustomerInfo(quoteData.customer);
    this.validateProjectDetails(quoteData.project);
    this.validateMaterials(quoteData.materials);
    this.validateLabor(quoteData.labor);
    this.validatePricing(quoteData.totals);
    this.validateTimeline(quoteData.timeline);
    this.validateRequiredAcknowledgments(quoteData.acknowledgments);

    return {
      valid: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
      canProceed: this.errors.length === 0
    };
  }

  /**
   * Validate customer information
   */
  validateCustomerInfo(customer) {
    if (!customer) {
      this.addError('Customer information is required');
      return;
    }

    // Required fields
    if (this.validationRules.requireCustomerName && !customer.name?.trim()) {
      this.addError('Customer name is required');
    }

    if (this.validationRules.requireCustomerEmail) {
      if (!customer.email?.trim()) {
        this.addError('Customer email is required');
      } else if (!this.isValidEmail(customer.email)) {
        this.addError('Customer email is invalid');
      }
    }

    if (this.validationRules.requireCustomerPhone) {
      if (!customer.phone?.trim()) {
        this.addError('Customer phone number is required');
      } else if (!this.isValidPhone(customer.phone)) {
        this.addWarning('Customer phone number format may be invalid');
      }
    }

    // Address validation
    if (!customer.address?.trim()) {
      this.addWarning('Customer address not provided - recommended for accurate quote');
    }
  }

  /**
   * Validate project details
   */
  validateProjectDetails(project) {
    if (!project) {
      this.addError('Project details are required');
      return;
    }

    if (this.validationRules.requireProjectDescription && !project.description?.trim()) {
      this.addWarning('Project description recommended for clarity');
    }

    if (!project.type || !['bathroom', 'kitchen', 'floor', 'shower', 'other'].includes(project.type)) {
      this.addWarning('Project type not specified - may affect accuracy');
    }

    if (!project.location?.trim()) {
      this.addWarning('Project location not specified');
    }
  }

  /**
   * Validate materials calculations
   */
  validateMaterials(materials) {
    if (!materials?.items || materials.items.length === 0) {
      this.addError('No materials calculated - complete at least one calculator first');
      return;
    }

    // Check minimum materials calculated
    const minMaterials = this.validationRules.minimumMaterialsCalculated || 1;
    if (materials.items.length < minMaterials) {
      this.addWarning(`Only ${materials.items.length} material type(s) calculated. Recommend calculating all required materials.`);
    }

    // Validate material quantities
    materials.items.forEach(item => {
      if (!item.quantity || item.quantity <= 0) {
        this.addError(`Invalid quantity for ${item.description}: ${item.quantity}`);
      }

      if (item.quantity > this.validationRules.maxMaterialQuantity) {
        this.addWarning(`Unusually high quantity for ${item.description}: ${item.quantity}. Please verify.`);
      }

      if (!item.unitPrice || item.unitPrice <= 0) {
        this.addError(`Invalid unit price for ${item.description}: $${item.unitPrice}`);
      }

      if (!item.total || item.total <= 0) {
        this.addError(`Invalid total for ${item.description}: $${item.total}`);
      }
    });

    // Validate materials subtotal
    const calculatedSubtotal = materials.items.reduce((sum, item) => sum + (item.total || 0), 0);
    const reportedSubtotal = materials.subtotal || 0;

    if (Math.abs(calculatedSubtotal - reportedSubtotal) > 0.01) {
      this.addError(`Materials subtotal mismatch: calculated $${calculatedSubtotal.toFixed(2)}, reported $${reportedSubtotal.toFixed(2)}`);
    }

    // Check for essential materials
    const hasTile = materials.items.some(item => item.category?.toLowerCase().includes('tile'));
    const hasGrout = materials.items.some(item => item.category?.toLowerCase().includes('grout'));
    const hasMortar = materials.items.some(item => item.category?.toLowerCase().includes('mortar'));

    if (!hasTile) {
      this.addWarning('No tile calculated - verify if this is intentional');
    }
    if (!hasGrout && hasTile) {
      this.addWarning('Tile calculated but no grout - may be incomplete');
    }
    if (!hasMortar && hasTile) {
      this.addWarning('Tile calculated but no mortar - may be incomplete');
    }
  }

  /**
   * Validate labor calculations
   */
  validateLabor(labor) {
    if (this.validationRules.requireLaborEstimate) {
      if (!labor || !labor.hours || labor.hours <= 0) {
        this.addError('Labor estimate is required - complete Labor Estimator calculator');
        return;
      }
    }

    if (labor.hours > this.validationRules.maxLaborHours) {
      this.addWarning(`Labor hours (${labor.hours}) exceeds ${this.validationRules.maxLaborHours}. Please verify estimate is accurate.`);
    }

    if (labor.hours < 1) {
      this.addWarning('Labor estimate less than 1 hour seems low - verify calculation');
    }

    if (!labor.rate || labor.rate <= 0) {
      this.addError(`Invalid labor rate: $${labor.rate}/hour`);
    }

    if (!labor.total || labor.total <= 0) {
      this.addError(`Invalid labor total: $${labor.total}`);
    }

    // Verify labor calculation
    const calculatedTotal = (labor.hours || 0) * (labor.rate || 0);
    if (Math.abs(calculatedTotal - labor.total) > 0.01) {
      this.addError(`Labor total mismatch: ${labor.hours} hrs × $${labor.rate}/hr = $${calculatedTotal.toFixed(2)}, but reported $${labor.total.toFixed(2)}`);
    }
  }

  /**
   * Validate pricing and totals
   */
  validatePricing(totals) {
    if (!totals) {
      this.addError('Quote totals missing');
      return;
    }

    // Check minimum/maximum quote values
    if (totals.grandTotal < this.validationRules.minQuoteValue) {
      this.addWarning(`Quote total ($${totals.grandTotal.toFixed(2)}) is below minimum ($${this.validationRules.minQuoteValue}). Verify this is accurate.`);
    }

    if (totals.grandTotal > this.validationRules.maxQuoteValue) {
      this.addWarning(`Quote total ($${totals.grandTotal.toFixed(2)}) exceeds $${this.validationRules.maxQuoteValue}. Recommend management review before sending.`);
    }

    // Validate totals calculation
    const calculatedSubtotal = (totals.materials || 0) + (totals.labor || 0) + (totals.fees || 0);
    if (Math.abs(calculatedSubtotal - totals.subtotal) > 0.01) {
      this.addError(`Subtotal mismatch: $${calculatedSubtotal.toFixed(2)} vs $${totals.subtotal.toFixed(2)}`);
    }

    // Validate tax calculation
    const expectedTax = totals.subtotal * (totals.taxRate || 0);
    if (Math.abs(expectedTax - totals.tax) > 0.01) {
      this.addError(`Tax calculation error: expected $${expectedTax.toFixed(2)}, got $${totals.tax.toFixed(2)}`);
    }

    // Validate grand total
    const calculatedGrandTotal = totals.subtotal + totals.tax;
    if (Math.abs(calculatedGrandTotal - totals.grandTotal) > 0.01) {
      this.addError(`Grand total mismatch: $${calculatedGrandTotal.toFixed(2)} vs $${totals.grandTotal.toFixed(2)}`);
    }

    // Check for negative values
    if (totals.materials < 0 || totals.labor < 0 || totals.tax < 0 || totals.grandTotal < 0) {
      this.addError('Quote contains negative values - this is invalid');
    }

    // Check for zero values
    if (totals.materials === 0) {
      this.addWarning('Materials cost is $0 - verify this is intentional');
    }
    if (totals.labor === 0) {
      this.addWarning('Labor cost is $0 - verify this is intentional');
    }
  }

  /**
   * Validate timeline
   */
  validateTimeline(timeline) {
    if (!timeline) {
      this.addWarning('Timeline not specified');
      return;
    }

    if (timeline.estimatedStart) {
      const startDate = new Date(timeline.estimatedStart);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (startDate < today) {
        this.addWarning('Start date is in the past');
      }
    }

    if (timeline.estimatedCompletion && timeline.estimatedStart) {
      const start = new Date(timeline.estimatedStart);
      const end = new Date(timeline.estimatedCompletion);

      if (end <= start) {
        this.addError('Completion date must be after start date');
      }

      const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
      if (diffDays > 365) {
        this.addWarning(`Project duration (${diffDays} days) exceeds 1 year - verify timeline`);
      }
    }
  }

  /**
   * Validate required acknowledgments
   */
  validateRequiredAcknowledgments(acknowledgments) {
    const required = this.config?.quote?.requiredAcknowledgments || [];

    if (required.length === 0) return;

    if (!acknowledgments || !Array.isArray(acknowledgments)) {
      this.addError('Customer must acknowledge all required terms before proceeding');
      return;
    }

    required.forEach((ack, index) => {
      if (!acknowledgments[index]) {
        this.addError(`Customer must acknowledge: "${ack.substring(0, 50)}..."`);
      }
    });
  }

  /**
   * Helper: Validate email format
   */
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Helper: Validate phone format
   */
  isValidPhone(phone) {
    // Remove all non-digit characters
    const digits = phone.replace(/\D/g, '');
    // US phone numbers should be 10 or 11 digits (with country code)
    return digits.length === 10 || digits.length === 11;
  }

  /**
   * Add error
   */
  addError(message) {
    this.errors.push({
      type: 'error',
      message: message,
      severity: 'high'
    });
  }

  /**
   * Add warning
   */
  addWarning(message) {
    this.warnings.push({
      type: 'warning',
      message: message,
      severity: 'medium'
    });
  }

  /**
   * Get validation summary
   */
  getSummary() {
    return {
      totalIssues: this.errors.length + this.warnings.length,
      errors: this.errors.length,
      warnings: this.warnings.length,
      canProceed: this.errors.length === 0,
      message: this.errors.length === 0
        ? 'Quote passed all validation checks'
        : `Found ${this.errors.length} error(s) and ${this.warnings.length} warning(s)`
    };
  }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuoteValidator;
}

// Expose globally for browser
if (typeof window !== 'undefined') {
  window.QuoteValidator = QuoteValidator;
}

console.log('[QuoteValidator] Loaded');
