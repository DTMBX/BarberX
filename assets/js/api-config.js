// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Technologies Evidence Processing Platform
 * API Configuration
 */

const API_CONFIG = {
  // Backend API base URL
  BACKEND_URL: "http://localhost:8000",

  // API endpoints
  ENDPOINTS: {
    // Document Upload
    UPLOAD_DOCUMENTS: "/api/v1/documents/upload",
    BATCH_UPLOAD: "/api/v1/batch/upload",

    // BWC/Video Upload
    BWC_UPLOAD: "/api/v1/bwc/upload",

    // Docket Search (local Jekyll data)
    DOCKET_DATA: "/assets/data/docket-index.json",
    CASES_MAP: "/assets/data/cases-map.json",

    // Document Analysis
    OCR_PROCESS: "/api/v1/documents/ocr",
    CONSTITUTIONAL_SCAN: "/api/v1/documents/constitutional-scan",
    CLASSIFY_DOCUMENT: "/api/v1/documents/classify",

    // Transcription
    TRANSCRIBE: "/api/v1/transcription/create",
    TRANSCRIPTION_STATUS: "/api/v1/transcription/status",
  },

  // File upload limits
  LIMITS: {
    MAX_FILE_SIZE_MB: 500,
    MAX_FILES_PER_BATCH: 50,
    ALLOWED_DOCUMENT_TYPES: [
      ".pdf",
      ".doc",
      ".docx",
      ".txt",
      ".jpg",
      ".jpeg",
      ".png",
    ],
    ALLOWED_VIDEO_TYPES: [".mp4", ".mov", ".avi", ".mkv"],
  },

  // UI settings
  UI: {
    DEBOUNCE_DELAY: 300, // ms
    TOAST_DURATION: 3000, // ms
  },
};

// Utility: Check if backend is available
async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_CONFIG.BACKEND_URL}/health`, {
      method: "HEAD",
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Utility: Format file size
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

// Utility: Show toast notification
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    padding: 1rem 1.5rem;
    background: ${type === "error" ? "#ef4444" : type === "success" ? "#10b981" : "#3b82f6"};
    color: white;
    border-radius: 8px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    z-index: 10000;
    animation: slideIn 0.3s ease;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, API_CONFIG.UI.TOAST_DURATION);
}

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    API_CONFIG,
    checkBackendHealth,
    formatFileSize,
    showToast,
  };
}
