// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Interactive Tutorial Tooltips for Evident
 * Provides contextual help throughout the platform
 */

class TooltipManager {
  constructor() {
    this.tooltips = [];
    this.currentStep = 0;
    this.isActive = false;
    this.overlay = null;
    this.init();
  }

  init() {
    const onboardingComplete = localStorage.getItem("onboardingComplete");
    if (!onboardingComplete) {
      this.createTooltipStyles();
      this.loadUserProgress();
    }
  }

  createTooltipStyles() {
    const style = document.createElement("style");
    style.textContent = `
            .tooltip-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                z-index: 9998;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .tooltip-overlay.active {
                opacity: 1;
            }

            .tooltip-highlight {
                position: relative;
                z-index: 9999 !important;
                box-shadow: 0 0 0 4px #667eea, 0 0 0 8px rgba(102, 126, 234, 0.3) !important;
                border-radius: 8px;
            }

            .tooltip-popup {
                position: absolute;
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                max-width: 350px;
                z-index: 10000;
                opacity: 0;
                transform: translateY(-10px);
                transition: all 0.3s ease;
            }

            .tooltip-popup.active {
                opacity: 1;
                transform: translateY(0);
            }

            .tooltip-header {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
            }

            .tooltip-icon {
                font-size: 2rem;
                margin-right: 0.75rem;
            }

            .tooltip-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #2d3748;
                margin: 0;
            }

            .tooltip-content {
                color: #4a5568;
                font-size: 0.95rem;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }

            .tooltip-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .tooltip-progress {
                color: #718096;
                font-size: 0.85rem;
            }

            .tooltip-buttons {
                display: flex;
                gap: 0.5rem;
            }

            .tooltip-btn {
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 6px;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .tooltip-btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .tooltip-btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }

            .tooltip-btn-secondary {
                background: #e2e8f0;
                color: #4a5568;
            }

            .tooltip-btn-secondary:hover {
                background: #cbd5e0;
            }

            @media (max-width: 768px) {
                .tooltip-popup {
                    max-width: 90vw;
                    padding: 1rem;
                }
            }
        `;
    document.head.appendChild(style);
  }

  startTour(page) {
    console.log("[Tooltip] Starting tour for:", page);
    // Tour can be started manually or automatically
  }

  endTour() {
    localStorage.setItem("onboardingComplete", "true");
    console.log("[Tooltip] Tour complete");
  }

  loadUserProgress() {
    const page = this.getCurrentPage();
    const visitCount = parseInt(
      localStorage.getItem("visitCount_" + page) || "0",
    );
    localStorage.setItem("visitCount_" + page, (visitCount + 1).toString());
  }

  getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes("dashboard")) return "dashboard";
    if (path.includes("evidence")) return "evidence-intake";
    if (path.includes("analysis")) return "analysis";
    return "unknown";
  }
}

const tooltipManager = new TooltipManager();
window.tooltipManager = tooltipManager;
