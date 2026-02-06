// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Technologies Evidence Processing Platform
 * Constitutional Analysis Tool - AI-Powered Document Analysis
 */

let analysisResults = null;
let uploadedDocuments = [];

// Initialize when backend is available
document.addEventListener("DOMContentLoaded", async () => {
  const isBackendAvailable = await checkBackendHealth();

  if (isBackendAvailable) {
    document.getElementById("aiFeatures").style.display = "block";
    document.getElementById("offlineNotice").style.display = "none";
  } else {
    document.getElementById("aiFeatures").style.display = "none";
    document.getElementById("offlineNotice").style.display = "block";
  }
});

/**
 * Analyze uploaded document for constitutional violations
 */
async function analyzeDocument(file) {
  showToast("Analyzing document for constitutional violations...", "info");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("analyze_violations", "true");
  formData.append("extract_citations", "true");

  try {
    const response = await fetch(
      `${API_CONFIG.BACKEND_URL}/api/v1/ai/analyze-document`,
      {
        method: "POST",
        body: formData,
      },
    );

    if (!response.ok) throw new Error("Analysis failed");

    const result = await response.json();
    displayAnalysisResults(result);
    analysisResults = result;

    showToast("Analysis complete! Review findings below.", "success");
    return result;
  } catch (error) {
    console.error("Analysis error:", error);
    showToast("Analysis failed. Check backend connection.", "error");
    return null;
  }
}

/**
 * Display AI analysis results
 */
function displayAnalysisResults(analysis) {
  const resultsContainer = document.getElementById("analysisResults");
  if (!resultsContainer) return;

  const violations = analysis.violations_detected || [];
  const keyFacts = analysis.key_facts || [];
  const citations = analysis.legal_citations || [];
  const recommendations = analysis.recommended_actions || [];

  const html = `
    <div class="analysis-results">
      <div class="analysis-header">
        <h3>Analysis Results: ${analysis.filename}</h3>
        <span class="confidence-badge">Confidence: ${Math.round(analysis.confidence_score * 100)}%</span>
      </div>
      
      <div class="analysis-section">
        <h4>📄 Document Type</h4>
        <p class="document-type-badge">${formatDocumentType(analysis.document_type)}</p>
      </div>
      
      <div class="analysis-section">
        <h4>📝 Summary</h4>
        <p>${analysis.summary}</p>
      </div>
      
      ${
        violations.length > 0
          ? `
        <div class="analysis-section violations-section">
          <h4>⚖️ Constitutional Violations Detected (${violations.length})</h4>
          <div class="violations-list">
            ${violations
              .map(
                (v) => `
              <div class="violation-card violation-card-${getSeverity(v.severity)}">
                <div class="violation-header">
                  <span class="violation-type">${formatViolationType(v.type)}</span>
                  <span class="severity-badge severity-badge-${getSeverity(v.severity)}">${v.severity || "Medium"}</span>
                </div>
                <p class="violation-description">${v.description}</p>
                ${v.amendment ? `<p class="violation-amendment">Amendment: ${v.amendment}</p>` : ""}
                ${v.case_law ? `<p class="violation-caselaw">Case Law: ${v.case_law}</p>` : ""}
                ${
                  v.damages_range
                    ? `
                  <div class="damages-estimate">
                    <strong>Estimated Damages:</strong> 
                    $${formatNumber(v.damages_range[0])} - $${formatNumber(v.damages_range[1])}
                  </div>
                `
                    : ""
                }
              </div>
            `,
              )
              .join("")}
          </div>
        </div>
      `
          : '<div class="analysis-section"><p>✅ No constitutional violations detected</p></div>'
      }
      
      ${
        keyFacts.length > 0
          ? `
        <div class="analysis-section">
          <h4>🔑 Key Facts</h4>
          <ul class="facts-list">
            ${keyFacts.map((fact) => `<li>${fact}</li>`).join("")}
          </ul>
        </div>
      `
          : ""
      }
      
      ${
        citations.length > 0
          ? `
        <div class="analysis-section">
          <h4>📚 Legal Citations</h4>
          <ul class="citations-list">
            ${citations.map((cite) => `<li>${cite}</li>`).join("")}
          </ul>
        </div>
      `
          : ""
      }
      
      ${
        recommendations.length > 0
          ? `
        <div class="analysis-section recommendations-section">
          <h4>💡 Recommended Actions</h4>
          <ul class="recommendations-list">
            ${recommendations.map((rec) => `<li>${rec}</li>`).join("")}
          </ul>
        </div>
      `
          : ""
      }
      
      <div class="analysis-actions">
        <button class="btn-premium" onclick="generateComplaint()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          Generate Verified Complaint
        </button>
        <button class="btn-secondary" onclick="exportAnalysis()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
          Export Analysis
        </button>
        <button class="btn-secondary" onclick="askAI()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
          Ask AI Follow-up
        </button>
      </div>
    </div>
  `;

  resultsContainer.innerHTML = html;
  resultsContainer.style.display = "block";

  // Scroll to results
  resultsContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Generate verified complaint from analysis
 */
async function generateComplaint() {
  if (!analysisResults) {
    showToast("No analysis results available", "error");
    return;
  }

  showToast("Generating verified complaint...", "info");

  try {
    const response = await fetch(
      `${API_CONFIG.BACKEND_URL}/api/v1/ai/generate-complaint`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis: analysisResults,
          include_exhibits: true,
          include_damages: true,
          format: "verified_complaint",
        }),
      },
    );

    if (!response.ok) throw new Error("Generation failed");

    const result = await response.json();

    // Download generated complaint
    downloadComplaint(result.content, result.filename);
    showToast("Verified complaint generated successfully!", "success");
  } catch (error) {
    console.error("Generation error:", error);
    showToast("Failed to generate complaint. Try again.", "error");
  }
}

/**
 * Download generated complaint as DOCX
 */
function downloadComplaint(content, filename) {
  const blob = new Blob([content], {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "verified-complaint.docx";
  a.click();
  window.URL.revokeObjectURL(url);
}

/**
 * Export analysis as PDF
 */
async function exportAnalysis() {
  if (!analysisResults) {
    showToast("No analysis to export", "error");
    return;
  }

  try {
    const response = await fetch(
      `${API_CONFIG.BACKEND_URL}/api/v1/documents/export-analysis`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis: analysisResults, format: "pdf" }),
      },
    );

    if (!response.ok) throw new Error("Export failed");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analysis-${analysisResults.filename}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);

    showToast("Analysis exported successfully!", "success");
  } catch (error) {
    console.error("Export error:", error);
    showToast("Export failed. Generating text version...", "warning");
    exportAnalysisAsText();
  }
}

/**
 * Export as plain text (fallback)
 */
function exportAnalysisAsText() {
  const text = JSON.stringify(analysisResults, null, 2);
  const blob = new Blob([text], { type: "text/plain" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `analysis-${analysisResults.filename}.txt`;
  a.click();
  window.URL.revokeObjectURL(url);
}

/**
 * Interactive AI conversation
 */
async function askAI() {
  const question = prompt("Ask AI about this document:");
  if (!question) return;

  showToast("AI is thinking...", "info");

  try {
    const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: question,
        document_context: [analysisResults],
        conversation_id: null,
      }),
    });

    if (!response.ok) throw new Error("AI chat failed");

    const result = await response.json();
    alert(`AI Response:\n\n${result.message}`);
  } catch (error) {
    console.error("AI chat error:", error);
    showToast("AI conversation failed", "error");
  }
}

// Utility functions
function formatDocumentType(type) {
  return (type || "unknown")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

function formatViolationType(type) {
  const typeMap = {
    "4th_excessive_force": "4th Amendment - Excessive Force",
    "4th_unlawful_search": "4th Amendment - Unlawful Search",
    "4th_unlawful_seizure": "4th Amendment - Unlawful Seizure",
    "5th_miranda": "5th Amendment - Miranda Violation",
    "5th_self_incrimination": "5th Amendment - Self-Incrimination",
    "6th_right_to_counsel": "6th Amendment - Right to Counsel",
    "14th_due_process": "14th Amendment - Due Process",
    "14th_equal_protection": "14th Amendment - Equal Protection",
  };
  return typeMap[type] || type;
}

function getSeverity(severity) {
  const s = (severity || "medium").toLowerCase();
  if (s.includes("high") || s.includes("severe")) return "high";
  if (s.includes("low") || s.includes("minor")) return "low";
  return "medium";
}

function formatNumber(num) {
  return new Intl.NumberFormat("en-US").format(num);
}
