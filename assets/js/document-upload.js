// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Technologies Evidence Processing Platform
 * Document Upload Tool - Production Implementation
 */

let uploadQueue = [];
let isBackendAvailable = false;

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  isBackendAvailable = await checkBackendHealth();
  console.log("Backend available:", isBackendAvailable);

  initializeUploadHandlers();
});

function initializeUploadHandlers() {
  const uploadZone = document.getElementById("uploadZone");
  const fileInput = document.getElementById("fileInput");

  if (!uploadZone || !fileInput) return;

  // Click to select files
  uploadZone.addEventListener("click", () => fileInput.click());

  // Drag and drop handlers
  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("upload-zone-active");
  });

  uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("upload-zone-active");
  });

  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("upload-zone-active");
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  });

  // File input change
  fileInput.addEventListener("change", (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  });
}

async function handleFiles(files) {
  if (files.length === 0) return;

  // Validate files
  const validFiles = [];
  const invalidFiles = [];

  files.forEach((file) => {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    const isValid = API_CONFIG.LIMITS.ALLOWED_DOCUMENT_TYPES.includes(ext);
    const sizeOk =
      file.size <= API_CONFIG.LIMITS.MAX_FILE_SIZE_MB * 1024 * 1024;

    if (!isValid) {
      invalidFiles.push({ file, reason: `Invalid file type: ${ext}` });
    } else if (!sizeOk) {
      invalidFiles.push({
        file,
        reason: `File too large (max ${API_CONFIG.LIMITS.MAX_FILE_SIZE_MB}MB)`,
      });
    } else {
      validFiles.push(file);
    }
  });

  // Show validation errors
  if (invalidFiles.length > 0) {
    const errors = invalidFiles
      .map((f) => `${f.file.name}: ${f.reason}`)
      .join("\n");
    showToast(`${invalidFiles.length} file(s) rejected:\n${errors}`, "error");
  }

  if (validFiles.length === 0) return;

  // Show upload UI
  showUploadProgress(validFiles);

  // Upload files
  if (isBackendAvailable) {
    await uploadToBackend(validFiles);
  } else {
    await uploadToGitInbox(validFiles);
  }
}

async function uploadToBackend(files) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("auto_transcribe", "false");
  formData.append("case_id", ""); // Optional: link to case

  try {
    const response = await fetch(
      `${API_CONFIG.BACKEND_URL}${API_CONFIG.ENDPOINTS.UPLOAD_DOCUMENTS}`,
      {
        method: "POST",
        body: formData,
      },
    );

    if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`);

    const result = await response.json();

    showToast(
      `Successfully uploaded ${result.uploaded || files.length} file(s)`,
      "success",
    );
    displayUploadResults(result);
  } catch (error) {
    console.error("Upload error:", error);
    showToast("Upload failed. Falling back to Git inbox method.", "error");
    await uploadToGitInbox(files);
  }
}

async function uploadToGitInbox(files) {
  // Since we can't directly write to filesystem from browser,
  // provide instructions for manual upload

  const instructions = `
    <div class="upload-instructions">
      <h3>Manual Upload Instructions</h3>
      <p>To upload these ${files.length} file(s), please follow these steps:</p>
      <ol>
        <li>Save your selected files to: <code>_inbox/</code></li>
        <li>Open PowerShell in the repository root</li>
        <li>Run: <code>.\\tools\\upload_pdfs.ps1</code></li>
        <li>The script will commit and push your files</li>
        <li>GitHub Actions will process them automatically</li>
      </ol>
      
      <div class="file-list">
        <h4>Files to upload:</h4>
        <ul>
          ${files.map((f) => `<li>${f.name} (${formatFileSize(f.size)})</li>`).join("")}
        </ul>
      </div>
      
      <div class="actions">
        <button class="btn-premium" onclick="downloadUploadScript()">
          Download PowerShell Script
        </button>
        <a href="/docs/batch-upload-guide/" class="btn-secondary">
          View Full Guide
        </a>
      </div>
    </div>
  `;

  const resultsContainer =
    document.getElementById("uploadResults") || createResultsContainer();
  resultsContainer.innerHTML = instructions;
  resultsContainer.style.display = "block";
}

function showUploadProgress(files) {
  const uploadZone = document.getElementById("uploadZone");

  const progressHTML = `
    <div class="upload-progress">
      <svg class="upload-progress-spinner" viewBox="0 0 24 24" width="48" height="48">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" 
          stroke-dasharray="63" stroke-dashoffset="16" 
          style="animation: spin 1s linear infinite; transform-origin: center;">
        </circle>
      </svg>
      <h3>Processing ${files.length} file(s)...</h3>
      <div class="file-list">
        ${files
          .map(
            (f) => `
          <div class="file-item">
            <span>${f.name}</span>
            <span>${formatFileSize(f.size)}</span>
          </div>
        `,
          )
          .join("")}
      </div>
    </div>
  `;

  uploadZone.insertAdjacentHTML(
    "afterend",
    `<div id="uploadResults">${progressHTML}</div>`,
  );
}

function displayUploadResults(result) {
  const resultsContainer = document.getElementById("uploadResults");
  if (!resultsContainer) return;

  const html = `
    <div class="upload-results">
      <div class="upload-results-summary">
        <h3>Upload Complete</h3>
        <p>${result.uploaded} file(s) uploaded successfully</p>
        ${result.failed > 0 ? `<p class="error">${result.failed} file(s) failed</p>` : ""}
      </div>
      
      <div class="upload-results-files">
        ${(result.results || [])
          .map(
            (file) => `
          <div class="result-file ${file.status === "error" ? "result-file-error" : "result-file-success"}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              ${
                file.status === "error"
                  ? '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
                  : '<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>'
              }
            </svg>
            <div>
              <strong>${file.filename}</strong>
              <small>${file.message || formatFileSize(file.file_size)}</small>
            </div>
          </div>
        `,
          )
          .join("")}
      </div>
      
      <button class="btn-premium" onclick="location.reload()">Upload More Files</button>
    </div>
  `;

  resultsContainer.innerHTML = html;
}

function createResultsContainer() {
  const container = document.createElement("div");
  container.id = "uploadResults";
  document
    .getElementById("uploadZone")
    .insertAdjacentElement("afterend", container);
  return container;
}

function downloadUploadScript() {
  showToast("PowerShell script is located at: tools/upload_pdfs.ps1", "info");
}

// Add CSS for upload UI
const style = document.createElement("style");
style.textContent = `
  .upload-zone--active {
    border-color: rgb(212 165 116 / 70%) !important;
    background: linear-gradient(135deg, rgb(212 165 116 / 12%) 0%, transparent 100%) !important;
  }
  
  #uploadResults {
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, rgb(255 255 255 / 5%) 0%, rgb(255 255 255 / 2%) 100%);
    border: 1px solid rgb(255 255 255 / 12%);
    border-radius: 16px;
  }
  
  .upload-progress {
    text-align: center;
    padding: 2rem;
  }
  
  .upload-progress__spinner {
    color: #d4a574;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .file-list {
    margin: 1rem 0;
  }
  
  .file-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    background: rgb(255 255 255 / 5%);
    border-radius: 8px;
    margin: 0.5rem 0;
  }
  
  .upload-instructions code {
    background: rgb(255 255 255 / 10%);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
  }
  
  .upload-instructions ol {
    text-align: left;
    max-width: 600px;
    margin: 1.5rem auto;
  }
  
  .actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
  }
  
  .result-file {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: rgb(16 185 129 / 10%);
    border-left: 3px solid #10b981;
    border-radius: 8px;
    margin: 0.5rem 0;
  }
  
  .result-file--error {
    background: rgb(239 68 68 / 10%);
    border-left-color: #ef4444;
  }
`;
document.head.appendChild(style);
