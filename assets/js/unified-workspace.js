// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * EVIDENT UNIFIED WORKSPACE
 * Multi-tool AI-powered legal intelligence platform
 */

// State Management
const WorkspaceState = {
  currentView: "dashboard",
  currentCase: null,
  aiModel: "gpt-4",
  chatMessages: [],
  evidence: [],
  cases: [],
};

// ========================================
// VIEW MANAGEMENT
// ========================================

function switchView(viewName) {
  // Hide all views
  document.querySelectorAll(".content-view").forEach((view) => {
    view.classList.remove("active");
  });

  // Show selected view
  const targetView = document.getElementById(`${viewName}-view`);
  if (targetView) {
    targetView.classList.add("active");
    WorkspaceState.currentView = viewName;

    // Update title
    const title = document.querySelector(".workspace-title");
    title.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);

    // Update breadcrumb
    const breadcrumbActive = document.querySelector(".breadcrumb-item.active");
    breadcrumbActive.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);
  }

  // Update active nav item
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.remove("active");
  });
  const activeNav = document.querySelector(`[data-view="${viewName}"]`);
  if (activeNav) {
    activeNav.classList.add("active");
  }
}

// ========================================
// NAVIGATION
// ========================================

document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault();
    const view = item.getAttribute("data-view");
    switchView(view);
  });
});

// ========================================
// CHAT INTERFACE
// ========================================

const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const chatMessages = document.getElementById("chatMessages");
const aiModelSelect = document.getElementById("aiModel");

// Auto-resize textarea
chatInput?.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

// Send message
function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Add user message to UI
  addChatMessage("user", message);

  // Clear input
  chatInput.value = "";
  chatInput.style.height = "auto";

  // Show typing indicator
  showTypingIndicator();

  // Send to backend
  fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      model: WorkspaceState.aiModel,
      case_id: WorkspaceState.currentCase,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      hideTypingIndicator();
      addChatMessage("assistant", data.response);
    })
    .catch((error) => {
      hideTypingIndicator();
      addChatMessage("assistant", "Sorry, I encountered an error. Please try again.");
      console.error("Chat error:", error);
    });
}

sendBtn?.addEventListener("click", sendMessage);

chatInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// AI Model selection
aiModelSelect?.addEventListener("change", (e) => {
  WorkspaceState.aiModel = e.target.value;
  console.log("AI Model changed to:", e.target.value);
});

function addChatMessage(role, content) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${role}`;

  const avatarDiv = document.createElement("div");
  avatarDiv.className = "message-avatar";
  avatarDiv.innerHTML =
    role === "assistant" ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.innerHTML = formatMessageContent(content);

  messageDiv.appendChild(avatarDiv);
  messageDiv.appendChild(contentDiv);

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Store in state
  WorkspaceState.chatMessages.push({ role, content });
}

function formatMessageContent(content) {
  // Convert markdown-style formatting to HTML
  return content
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>");
}

function showTypingIndicator() {
  const indicator = document.createElement("div");
  indicator.className = "chat-message assistant typing-indicator";
  indicator.id = "typingIndicator";
  indicator.innerHTML = `
    <div class="message-avatar">
      <i class="fas fa-robot"></i>
    </div>
    <div class="message-content">
      <span class="typing-dots">
        <span>.</span><span>.</span><span>.</span>
      </span>
    </div>
  `;
  chatMessages.appendChild(indicator);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) {
    indicator.remove();
  }
}

// ========================================
// COMMAND PALETTE
// ========================================

const commandPalette = document.getElementById("commandPalette");
const commandInput = document.getElementById("commandInput");

// Keyboard shortcut (Ctrl/Cmd + K)
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    toggleCommandPalette();
  }

  if (e.key === "Escape" && commandPalette.getAttribute("aria-hidden") === "false") {
    closeCommandPalette();
  }
});

document.querySelectorAll('[data-action="command"]').forEach((btn) => {
  btn.addEventListener("click", toggleCommandPalette);
});

function toggleCommandPalette() {
  const isHidden = commandPalette.getAttribute("aria-hidden") === "true";
  if (isHidden) {
    openCommandPalette();
  } else {
    closeCommandPalette();
  }
}

function openCommandPalette() {
  commandPalette.setAttribute("aria-hidden", "false");
  commandInput.focus();
}

function closeCommandPalette() {
  commandPalette.setAttribute("aria-hidden", "true");
  commandInput.value = "";
}

// Click outside to close
commandPalette?.addEventListener("click", (e) => {
  if (e.target === commandPalette) {
    closeCommandPalette();
  }
});

// ========================================
// QUICK ACTIONS
// ========================================

document.querySelectorAll('[data-action="new-case"]').forEach((btn) => {
  btn.addEventListener("click", () => {
    // Open new case modal
    console.log("Create new case");
  });
});

document.querySelectorAll('[data-action="upload"]').forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById("uploadModal").style.display = "flex";
  });
});

// Quick start cards
document.querySelectorAll(".quick-start-card").forEach((card) => {
  card.addEventListener("click", () => {
    const action = card.getAttribute("data-action");
    handleQuickAction(action);
  });
});

function handleQuickAction(action) {
  switch (action) {
    case "new-case":
      console.log("New case");
      break;
    case "upload-evidence":
      document.getElementById("uploadModal").style.display = "flex";
      break;
    case "analyze-case":
      switchView("analysis");
      break;
    case "ask-ai":
      switchView("chat");
      setTimeout(() => chatInput.focus(), 100);
      break;
  }
}

// ========================================
// FILE UPLOAD
// ========================================

const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const uploadModal = document.getElementById("uploadModal");

uploadZone?.addEventListener("click", () => {
  fileInput.click();
});

uploadZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("drag-over");
});

uploadZone?.addEventListener("dragleave", () => {
  uploadZone.classList.remove("drag-over");
});

uploadZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  handleFiles(e.dataTransfer.files);
});

fileInput?.addEventListener("change", (e) => {
  handleFiles(e.target.files);
});

function handleFiles(files) {
  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append("files[]", file);
  });

  if (WorkspaceState.currentCase) {
    formData.append("case_id", WorkspaceState.currentCase);
  }

  // Show progress
  const progressEl = document.getElementById("uploadProgress");
  progressEl.style.display = "block";

  fetch("/api/evidence/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Upload success:", data);
      progressEl.style.display = "none";
      uploadModal.style.display = "none";
      // Refresh evidence list
      loadEvidence();
    })
    .catch((error) => {
      console.error("Upload error:", error);
      progressEl.style.display = "none";
      alert("Upload failed. Please try again.");
    });
}

// Modal close buttons
document.querySelectorAll(".modal-close").forEach((btn) => {
  btn.addEventListener("click", () => {
    btn.closest(".modal").style.display = "none";
  });
});

// ========================================
// ANALYSIS TOOLS
// ========================================

document.querySelectorAll(".tool-btn[data-tool]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const tool = btn.getAttribute("data-tool");
    runAnalysis(tool);
  });
});

function runAnalysis(tool) {
  const caseId = document.getElementById("caseSelector")?.value;
  if (!caseId) {
    alert("Please select a case first");
    return;
  }

  const resultsEl = document.getElementById("analysisResults");
  resultsEl.innerHTML = '<div class="loading">Analyzing...</div>';

  fetch("/api/analysis/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      case_id: caseId,
      analysis_type: tool,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      displayAnalysisResults(data);
    })
    .catch((error) => {
      console.error("Analysis error:", error);
      resultsEl.innerHTML = '<div class="error">Analysis failed. Please try again.</div>';
    });
}

function displayAnalysisResults(data) {
  const resultsEl = document.getElementById("analysisResults");
  resultsEl.innerHTML = `
    <div class="analysis-result">
      <h3>${data.title}</h3>
      <div class="result-content">${data.content}</div>
    </div>
  `;
}

// ========================================
// CASE MANAGEMENT
// ========================================

function loadCases() {
  fetch("/api/cases")
    .then((response) => response.json())
    .then((data) => {
      WorkspaceState.cases = data.cases;
      populateCaseSelector();
    })
    .catch((error) => console.error("Error loading cases:", error));
}

function populateCaseSelector() {
  const selector = document.getElementById("caseSelector");
  if (!selector) return;

  selector.innerHTML = '<option value="">Choose a case...</option>';
  WorkspaceState.cases.forEach((c) => {
    const option = document.createElement("option");
    option.value = c.id;
    option.textContent = c.name;
    selector.appendChild(option);
  });
}

// ========================================
// EVIDENCE MANAGEMENT
// ========================================

function loadEvidence() {
  fetch("/api/evidence")
    .then((response) => response.json())
    .then((data) => {
      WorkspaceState.evidence = data.evidence;
      displayEvidence();
    })
    .catch((error) => console.error("Error loading evidence:", error));
}

function displayEvidence() {
  const grid = document.getElementById("evidenceGrid");
  if (!grid) return;

  if (WorkspaceState.evidence.length === 0) {
    grid.innerHTML =
      '<div class="empty-state"><i class="fas fa-folder-open"></i><p>No evidence files yet</p></div>';
    return;
  }

  grid.innerHTML = WorkspaceState.evidence
    .map(
      (item) => `
    <div class="evidence-item" data-id="${item.id}">
      <div class="evidence-icon">
        <i class="fas fa-${getEvidenceIcon(item.type)}"></i>
      </div>
      <div class="evidence-name">${item.name}</div>
      <div class="evidence-meta">${item.size} • ${item.date}</div>
    </div>
  `
    )
    .join("");
}

function getEvidenceIcon(type) {
  const icons = {
    document: "file-alt",
    video: "video",
    audio: "microphone",
    image: "image",
  };
  return icons[type] || "file";
}

// ========================================
// INITIALIZATION
// ========================================
// SMART METER USAGE TRACKING
// ========================================

async function loadUsageQuota() {
  try {
    const response = await fetch("/api/usage/quota");
    const data = await response.json();

    // Update period info
    if (data.period) {
      const start = new Date(data.period.start).toLocaleDateString();
      const end = new Date(data.period.end).toLocaleDateString();
      document.getElementById("billingPeriod").textContent = `${start} - ${end}`;
      document.getElementById("daysRemaining").textContent = data.period.days_remaining;
    }

    // Update each quota meter
    updateQuotaMeter("tokens", data.quotas.ai_tokens);
    updateQuotaMeter("requests", data.quotas.ai_requests);
    updateQuotaMeter("storage", data.quotas.storage);
    updateQuotaMeter("files", data.quotas.files);
    updateQuotaMeter("analyses", data.quotas.analyses);
    updateQuotaMeter("cost", data.quotas.cost);
  } catch (error) {
    console.error("Error loading usage quota:", error);
  }
}

function updateQuotaMeter(type, quota) {
  const percent = quota.percent || 0;
  const used = quota.used || 0;
  const limit = quota.limit || 0;

  // Update percentage display
  const percentEl = document.getElementById(`${type}Percent`);
  if (percentEl) {
    percentEl.textContent = `${Math.round(percent)}%`;

    // Color code based on usage
    if (percent >= 95) {
      percentEl.style.color = "#ff6b6b";
    } else if (percent >= 80) {
      percentEl.style.color = "#ffd43b";
    } else {
      percentEl.style.color = "var(--text-secondary)";
    }
  }

  // Update progress bar
  const barEl = document.getElementById(`${type}Bar`);
  if (barEl) {
    barEl.style.width = `${Math.min(100, percent)}%`;

    // Change color if near limit
    if (percent >= 95) {
      barEl.style.background = "linear-gradient(90deg, #ff6b6b, #ff9e9e)";
    } else if (percent >= 80) {
      barEl.style.background = "linear-gradient(90deg, #ffd43b, #ffe066)";
    }
  }

  // Update used/limit text
  const usedEl = document.getElementById(`${type}Used`);
  const limitEl = document.getElementById(`${type}Limit`);

  if (type === "storage") {
    if (usedEl) usedEl.textContent = `${quota.used_mb.toFixed(2)} MB`;
    if (limitEl)
      limitEl.textContent = limit === -1 ? "Unlimited" : `${quota.limit_mb.toFixed(2)} MB`;
  } else if (type === "cost") {
    if (usedEl) usedEl.textContent = `$${quota.used_usd.toFixed(2)}`;
    if (limitEl)
      limitEl.textContent = limit === -1 ? "Unlimited" : `$${quota.limit_usd.toFixed(2)}`;
  } else if (type === "tokens") {
    if (usedEl) usedEl.textContent = formatNumber(used);
    if (limitEl) limitEl.textContent = limit === -1 ? "Unlimited" : formatNumber(limit);
  } else {
    if (usedEl) usedEl.textContent = used;
    if (limitEl) limitEl.textContent = limit === -1 ? "Unlimited" : limit;
  }
}

async function loadRecentEvents() {
  try {
    const response = await fetch("/api/usage/events?days=1&limit=20");
    const data = await response.json();

    const container = document.getElementById("recentEvents");
    if (!container) return;

    if (data.events.length === 0) {
      container.innerHTML =
        '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No recent events</p>';
      return;
    }

    container.innerHTML = data.events
      .map((event) => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const icon = getEventIcon(event.event_type);
        const color = event.status === "success" ? "#51cf66" : "#ff6b6b";

        return `
        <div style="display: flex; align-items: center; padding: 0.75rem; border-bottom: 1px solid var(--border-color); gap: 1rem;">
          <div style="color: ${color}; font-size: 1.25rem; width: 32px; text-align: center;">
            <i class="fas fa-${icon}"></i>
          </div>
          <div style="flex: 1;">
            <div style="font-weight: 500; color: var(--text-primary);">${formatEventType(event.event_type)}</div>
            <div style="font-size: 0.8125rem; color: var(--text-secondary);">
              ${event.resource_name || event.endpoint || ""}
              ${event.tokens_input + event.tokens_output > 0 ? ` • ${formatNumber(event.tokens_input + event.tokens_output)} tokens` : ""}
              ${event.cost_usd > 0 ? ` • $${event.cost_usd.toFixed(4)}` : ""}
            </div>
          </div>
          <div style="font-size: 0.8125rem; color: var(--text-secondary); white-space: nowrap;">
            ${time}
          </div>
        </div>
      `;
      })
      .join("");
  } catch (error) {
    console.error("Error loading recent events:", error);
  }
}

function getEventIcon(eventType) {
  const icons = {
    ai_request: "robot",
    file_upload: "file-upload",
    analysis: "chart-line",
    workflow: "project-diagram",
    api_call: "code",
    chat_message: "comments",
  };
  return icons[eventType] || "circle";
}

function formatEventType(eventType) {
  return eventType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
}

// Track usage client-side
async function trackUsage(eventType, eventCategory = "feature", metadata = {}) {
  try {
    await fetch("/api/usage/track", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event_type: eventType,
        event_category: eventCategory,
        ...metadata,
      }),
    });
  } catch (error) {
    console.error("Error tracking usage:", error);
  }
}

// ========================================
// PAGE INITIALIZATION
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("Evident Unified Workspace initialized");

  // Load initial data
  loadCases();
  loadEvidence();

  // Load usage metrics
  loadUsageQuota();
  loadRecentEvents();

  // Refresh usage every 30 seconds
  setInterval(() => {
    loadUsageQuota();
    loadRecentEvents();
  }, 30000);

  // Set default view
  switchView("dashboard");

  // Track page view
  trackUsage("page_view", "navigation", { page: "workspace" });
});
