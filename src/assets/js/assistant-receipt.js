/**
 * Evident Assistant Receipt System
 * ==================================
 * Every AI-initiated action produces a visible receipt in the UI.
 * No silent execution. This is legal software — traceability is mandatory.
 *
 * Usage:
 *   import { AssistantReceipt } from './assistant-receipt.js';
 *   const receipt = new AssistantReceipt(containerElement);
 *   receipt.show(actionResult);
 */

/**
 * @typedef {Object} ActionResult
 * @property {string} status - "success" | "denied" | "validation_error" | "error"
 * @property {string} audit_reference - UUID linking to audit log entry
 * @property {Object} [result] - Handler result (on success)
 * @property {string[]} [errors] - Validation errors
 * @property {string} [error] - Error message
 */

const STATUS_LABELS = {
  success: 'Completed',
  denied: 'Denied',
  validation_error: 'Invalid Input',
  error: 'Failed',
};

const STATUS_ICONS = {
  success: '\u2705',
  denied: '\u26D4',
  validation_error: '\u26A0\uFE0F',
  error: '\u274C',
};

export class AssistantReceipt {
  /**
   * @param {HTMLElement} container - DOM element to render receipts into.
   */
  constructor(container) {
    if (!container || !(container instanceof HTMLElement)) {
      throw new Error('AssistantReceipt requires a valid DOM container');
    }
    this._container = container;
    this._container.setAttribute('role', 'log');
    this._container.setAttribute('aria-label', 'Assistant action receipts');
    this._container.setAttribute('aria-live', 'polite');
  }

  /**
   * Display a receipt for an executed assistant action.
   *
   * @param {Object} params
   * @param {string} params.capabilityId - The capability that was executed.
   * @param {string} params.caseId - Affected case identifier (if any).
   * @param {ActionResult} params.result - The action result from the server.
   */
  show({ capabilityId, caseId, result }) {
    const receipt = document.createElement('article');
    receipt.classList.add('assistant-receipt');
    receipt.setAttribute('role', 'article');
    receipt.setAttribute('aria-label', `Action receipt: ${capabilityId}`);

    const status = result.status || 'error';
    receipt.dataset.status = status;

    const timestamp = new Date().toISOString();

    receipt.innerHTML = /* html */ `
      <header class="receipt-header">
        <span class="receipt-icon" aria-hidden="true">${STATUS_ICONS[status] || '\u2753'}</span>
        <span class="receipt-status">${STATUS_LABELS[status] || status}</span>
        <time class="receipt-timestamp" datetime="${timestamp}">
          ${new Date().toLocaleString()}
        </time>
      </header>
      <dl class="receipt-details">
        <div class="receipt-row">
          <dt>Capability</dt>
          <dd><code>${this._escape(capabilityId)}</code></dd>
        </div>
        ${caseId ? `
        <div class="receipt-row">
          <dt>Case</dt>
          <dd><code>${this._escape(caseId)}</code></dd>
        </div>
        ` : ''}
        <div class="receipt-row">
          <dt>Audit Reference</dt>
          <dd>
            <a href="/admin/audit/${this._escape(result.audit_reference || '')}"
               class="receipt-audit-link">
              ${this._escape((result.audit_reference || '').slice(0, 12))}…
            </a>
          </dd>
        </div>
        ${status === 'validation_error' && result.errors ? `
        <div class="receipt-row receipt-errors">
          <dt>Errors</dt>
          <dd>
            <ul>
              ${result.errors.map(e => `<li>${this._escape(e)}</li>`).join('')}
            </ul>
          </dd>
        </div>
        ` : ''}
        ${status === 'denied' || status === 'error' ? `
        <div class="receipt-row receipt-error">
          <dt>Detail</dt>
          <dd>${this._escape(result.error || 'No additional detail')}</dd>
        </div>
        ` : ''}
      </dl>
    `;

    // Prepend newest receipt at top
    this._container.prepend(receipt);

    // Announce to screen readers
    receipt.focus({ preventScroll: true });

    return receipt;
  }

  /**
   * Clear all displayed receipts.
   */
  clear() {
    this._container.innerHTML = '';
  }

  /**
   * Escape HTML to prevent XSS.
   * @param {string} str
   * @returns {string}
   */
  _escape(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}

/**
 * Execute an assistant action and display the receipt.
 *
 * @param {Object} params
 * @param {string} params.capabilityId
 * @param {string} [params.caseId]
 * @param {Object} params.args
 * @param {AssistantReceipt} params.receiptUI
 * @returns {Promise<Object>} The action result
 */
export async function executeAndReceipt({ capabilityId, caseId, args, receiptUI }) {
  const requestId = crypto.randomUUID();

  const response = await fetch('/assistant/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      capability_id: capabilityId,
      case_id: caseId || null,
      args: args || {},
      request_id: requestId,
    }),
  });

  const result = await response.json();

  receiptUI.show({
    capabilityId,
    caseId,
    result,
  });

  return result;
}
