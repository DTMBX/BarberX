// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Evident Admin Panel - Full Management System
// Handles all CRUD operations for users, analyses, and system management

let currentUsers = [];
let currentAnalyses = [];
let currentLogs = [];

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  // Setup tab navigation
  setupTabs();

  // Load initial data
  loadOverviewData();
});

function setupTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetTab = tab.dataset.tab;

      // Update tab states
      document
        .querySelectorAll(".tab")
        .forEach((t) => t.classList.remove("active"));
      document
        .querySelectorAll(".tab-content")
        .forEach((c) => c.classList.remove("active"));

      tab.classList.add("active");
      document.getElementById(targetTab).classList.add("active");

      // Load tab data
      loadTabData(targetTab);
    });
  });
}

async function loadTabData(tab) {
  switch (tab) {
    case "overview":
      await loadOverviewData();
      break;
    case "users":
      await loadUsers();
      break;
    case "analyses":
      await loadAnalyses();
      break;
    case "settings":
      await loadSettings();
      break;
    case "system":
      await loadSystemInfo();
      break;
    case "logs":
      await loadAuditLogs();
      break;
  }
}

// ========================================
// OVERVIEW TAB
// ========================================

async function loadOverviewData() {
  showLoading();
  try {
    const response = await fetch("/admin/stats");
    const data = await response.json();

    // Update stats
    document.getElementById("totalUsers").textContent = data.total_users || 0;
    document.getElementById("activeUsers").textContent = data.active_users || 0;
    document.getElementById("totalAnalyses").textContent =
      data.total_analyses || 0;
    document.getElementById("successRate").textContent =
      Math.round(data.success_rate || 0) + "%";

    // Create charts
    createSubscriptionChart(data.subscription_breakdown);
    createActivityChart(data.daily_activity);
  } catch (error) {
    showToast("Error loading overview data", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function createSubscriptionChart(breakdown) {
  const ctx = document.getElementById("subscriptionChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Free", "Professional", "Enterprise"],
      datasets: [
        {
          data: [
            breakdown?.free || 0,
            breakdown?.professional || 0,
            breakdown?.enterprise || 0,
          ],
          backgroundColor: ["#e2e8f0", "#3b82f6", "#8b5cf6"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

function createActivityChart(daily_activity) {
  const ctx = document.getElementById("activityChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Analyses",
          data: daily_activity || [0, 0, 0, 0, 0, 0, 0],
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
}

// ========================================
// USERS TAB
// ========================================

async function loadUsers() {
  showLoading();
  try {
    const response = await fetch("/admin/users");
    const data = await response.json();

    currentUsers = data.users || [];
    renderUsers(currentUsers);
  } catch (error) {
    showToast("Error loading users", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function renderUsers(users) {
  const tbody = document.getElementById("usersTable");

  if (users.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: #64748b;">
                    No users found
                </td>
            </tr>
        `;
    return;
  }

  tbody.innerHTML = users
    .map(
      (user) => `
        <tr data-user-id="${user.id}">
            <td style="font-weight: 600;">${escapeHtml(user.full_name || "N/A")}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>
                <span class="badge badge-${user.subscription_tier}">
                    ${user.subscription_tier}
                </span>
            </td>
            <td>${user.role}</td>
            <td>${user.analyses_count || 0}</td>
            <td>${(user.storage_used_mb || 0).toFixed(2)} MB</td>
            <td>
                <span class="badge ${user.is_active ? "badge-active" : "badge-inactive"}">
                    ${user.is_active ? "Active" : "Inactive"}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                        ✎ Edit
                    </button>
                    <button class="btn btn-sm ${user.is_active ? "btn-warning" : "btn-success"}" 
                            onclick="toggleUserStatus(${user.id})">
                        ${user.is_active ? "⏸ Disable" : "▶ Enable"}
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="confirmDeleteUser(${user.id}, '${escapeHtml(user.email)}')">
                        🗑 Delete
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join("");
}

function filterUsers() {
  const searchTerm = document.getElementById("userSearch").value.toLowerCase();
  const filtered = currentUsers.filter(
    (user) =>
      (user.full_name && user.full_name.toLowerCase().includes(searchTerm)) ||
      (user.email && user.email.toLowerCase().includes(searchTerm)) ||
      (user.organization &&
        user.organization.toLowerCase().includes(searchTerm)),
  );
  renderUsers(filtered);
}

function refreshUsers() {
  loadUsers();
}

// Edit User
function editUser(userId) {
  const user = currentUsers.find((u) => u.id === userId);
  if (!user) return;

  document.getElementById("editUserId").value = user.id;
  document.getElementById("editFullName").value = user.full_name || "";
  document.getElementById("editEmail").value = user.email;
  document.getElementById("editOrganization").value = user.organization || "";
  document.getElementById("editTier").value = user.subscription_tier;
  document.getElementById("editRole").value = user.role;

  document.getElementById("editUserModal").classList.add("active");
}

function closeEditModal() {
  document.getElementById("editUserModal").classList.remove("active");
}

document
  .getElementById("editUserForm")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const userId = document.getElementById("editUserId").value;
    const data = {
      full_name: document.getElementById("editFullName").value,
      organization: document.getElementById("editOrganization").value,
      subscription_tier: document.getElementById("editTier").value,
      role: document.getElementById("editRole").value,
    };

    showLoading();
    try {
      const response = await fetch(`/admin/users/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        showToast("User updated successfully", "success");
        closeEditModal();
        await loadUsers();
      } else {
        const error = await response.json();
        showToast(error.error || "Failed to update user", "error");
      }
    } catch (error) {
      showToast("Error updating user", "error");
      console.error(error);
    } finally {
      hideLoading();
    }
  });

// Toggle User Status
async function toggleUserStatus(userId) {
  showLoading();
  try {
    const response = await fetch(`/admin/users/${userId}/toggle-status`, {
      method: "POST",
    });

    if (response.ok) {
      const result = await response.json();
      showToast(result.message, "success");
      await loadUsers();
    } else {
      const error = await response.json();
      showToast(error.error || "Failed to toggle status", "error");
    }
  } catch (error) {
    showToast("Error toggling user status", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

// Delete User
function confirmDeleteUser(userId, email) {
  if (
    confirm(
      `Are you sure you want to delete user "${email}"? This action cannot be undone.`,
    )
  ) {
    deleteUser(userId);
  }
}

async function deleteUser(userId) {
  showLoading();
  try {
    const response = await fetch(`/admin/users/${userId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      showToast("User deleted successfully", "success");
      await loadUsers();
    } else {
      const error = await response.json();
      showToast(error.error || "Failed to delete user", "error");
    }
  } catch (error) {
    showToast("Error deleting user", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

// ========================================
// ANALYSES TAB
// ========================================

async function loadAnalyses() {
  showLoading();
  try {
    const status = document.getElementById("analysisFilter")?.value || "";
    const url = status
      ? `/admin/analyses?status=${status}&limit=100`
      : "/admin/analyses?limit=100";

    const response = await fetch(url);
    const data = await response.json();

    currentAnalyses = data.analyses || [];
    renderAnalyses(currentAnalyses);
  } catch (error) {
    showToast("Error loading analyses", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function renderAnalyses(analyses) {
  const tbody = document.getElementById("analysesTable");

  if (analyses.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #64748b;">
                    No analyses found
                </td>
            </tr>
        `;
    return;
  }

  tbody.innerHTML = analyses
    .map(
      (analysis) => `
        <tr>
            <td style="font-weight: 600; max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                ${escapeHtml(analysis.filename || "Unknown")}
            </td>
            <td>${analysis.user_id || "N/A"}</td>
            <td>
                <span class="badge badge-${getStatusClass(analysis.status)}">
                    ${analysis.status}
                </span>
            </td>
            <td>${formatBytes(analysis.file_size || 0)}</td>
            <td>${formatDate(analysis.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="viewAnalysis('${analysis.id}')">
                        👁 View
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="confirmDeleteAnalysis('${analysis.id}', '${escapeHtml(analysis.filename)}')">
                        🗑 Delete
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join("");
}

function filterAnalyses() {
  loadAnalyses();
}

function refreshAnalyses() {
  loadAnalyses();
}

function viewAnalysis(analysisId) {
  window.location.href = `/analysis/${analysisId}`;
}

function confirmDeleteAnalysis(analysisId, filename) {
  if (
    confirm(
      `Are you sure you want to delete analysis "${filename}"? This action cannot be undone.`,
    )
  ) {
    deleteAnalysis(analysisId);
  }
}

async function deleteAnalysis(analysisId) {
  showLoading();
  try {
    const response = await fetch(`/admin/analyses/${analysisId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      showToast("Analysis deleted successfully", "success");
      await loadAnalyses();
    } else {
      const error = await response.json();
      showToast(error.error || "Failed to delete analysis", "error");
    }
  } catch (error) {
    showToast("Error deleting analysis", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

// ========================================
// SETTINGS TAB
// ========================================

async function loadSettings() {
  showLoading();
  try {
    const response = await fetch("/admin/settings");
    const data = await response.json();

    renderSettings(data.settings);
  } catch (error) {
    showToast("Error loading settings", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function renderSettings(settingsByCategory) {
  const container = document.getElementById("settingsCategories");

  if (!settingsByCategory || Object.keys(settingsByCategory).length === 0) {
    container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <p style="font-size: 1.25rem; margin-bottom: 1rem;">No settings found</p>
                <button class="btn btn-primary" onclick="initializeSettings()">Initialize Default Settings</button>
            </div>
        `;
    return;
  }

  const categories = {
    general: { icon: "🌐", title: "General Settings" },
    security: { icon: "🔒", title: "Security Settings" },
    features: { icon: "✨", title: "Feature Flags" },
    limits: { icon: "📊", title: "Tier Limits" },
    email: { icon: "📧", title: "Email Configuration" },
    branding: { icon: "🎨", title: "Branding & Customization" },
  };

  let html = "";

  for (const [category, settings] of Object.entries(settingsByCategory)) {
    const catInfo = categories[category] || { icon: "⚙️", title: category };

    html += `
            <div style="margin-bottom: 2rem;">
                <h3 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>${catInfo.icon}</span>
                    <span>${catInfo.title}</span>
                    <span style="font-size: 0.875rem; color: #64748b; font-weight: normal;">(${settings.length})</span>
                </h3>
                <div style="display: grid; gap: 1rem;">
        `;

    for (const setting of settings) {
      const isEditable = setting.is_editable;
      const inputType =
        setting.value_type === "bool"
          ? "checkbox"
          : setting.value_type === "int" || setting.value_type === "float"
            ? "number"
            : "text";
      const inputValue =
        setting.value_type === "bool"
          ? setting.value.toLowerCase() === "true"
          : setting.value;

      html += `
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">${escapeHtml(setting.key)}</div>
                            <div style="font-size: 0.875rem; color: #64748b;">${escapeHtml(setting.description || "No description")}</div>
                        </div>
                        ${
                          isEditable
                            ? `
                            <div style="display: flex; gap: 0.5rem;">
                                <button class="btn btn-sm btn-primary" onclick="editSetting(${setting.id})">✏️ Edit</button>
                                <button class="btn btn-sm btn-danger" onclick="deleteSetting(${setting.id}, '${escapeHtml(setting.key)}')">🗑️</button>
                            </div>
                        `
                            : '<span style="color: #94a3b8; font-size: 0.75rem;">Read-only</span>'
                        }
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        ${
                          setting.value_type === "bool"
                            ? `
                            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: ${isEditable ? "pointer" : "not-allowed"};">
                                <input type="checkbox" id="setting_${setting.id}" 
                                       ${inputValue ? "checked" : ""} 
                                       ${!isEditable ? "disabled" : ""}
                                       onchange="quickUpdateSetting(${setting.id}, this.checked)"
                                       style="width: 20px; height: 20px; cursor: ${isEditable ? "pointer" : "not-allowed"};">
                                <span style="font-weight: 500; color: #475569;">${inputValue ? "Enabled" : "Disabled"}</span>
                            </label>
                        `
                            : `
                            <input type="${inputType}" 
                                   id="setting_${setting.id}" 
                                   value="${escapeHtml(inputValue)}"
                                   ${!isEditable ? "readonly" : ""}
                                   style="flex: 1; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 4px; background: ${isEditable ? "white" : "#f1f5f9"};"
                                   ${isEditable ? `onblur="quickUpdateSetting(${setting.id}, this.value)"` : ""}>
                        `
                        }
                        <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">${setting.value_type}</span>
                    </div>
                </div>
            `;
    }

    html += `
                </div>
            </div>
        `;
  }

  container.innerHTML = html;
}

async function quickUpdateSetting(settingId, value) {
  try {
    const response = await fetch(`/admin/settings/${settingId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: value }),
    });

    if (response.ok) {
      showToast("Setting updated successfully", "success");
    } else {
      const error = await response.json();
      showToast(error.error || "Failed to update setting", "error");
      await loadSettings(); // Reload to reset value
    }
  } catch (error) {
    showToast("Error updating setting", "error");
    console.error(error);
    await loadSettings();
  }
}

async function deleteSetting(settingId, key) {
  if (!confirm(`Are you sure you want to delete the setting "${key}"?`)) {
    return;
  }

  showLoading();
  try {
    const response = await fetch(`/admin/settings/${settingId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      showToast("Setting deleted successfully", "success");
      await loadSettings();
    } else {
      const error = await response.json();
      showToast(error.error || "Failed to delete setting", "error");
    }
  } catch (error) {
    showToast("Error deleting setting", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

async function initializeSettings() {
  if (
    !confirm(
      "This will create all default settings. Existing settings will not be modified. Continue?",
    )
  ) {
    return;
  }

  showLoading();
  try {
    const response = await fetch("/admin/settings/initialize", {
      method: "POST",
    });

    const data = await response.json();

    if (response.ok) {
      showToast(
        `Settings initialized: ${data.created} created, ${data.skipped} skipped`,
        "success",
      );
      await loadSettings();
    } else {
      showToast(data.error || "Failed to initialize settings", "error");
    }
  } catch (error) {
    showToast("Error initializing settings", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function refreshSettings() {
  loadSettings();
}

// Form submission for new setting
document
  .getElementById("newSettingForm")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      key: document.getElementById("newSettingKey").value,
      value: document.getElementById("newSettingValue").value,
      value_type: document.getElementById("newSettingType").value,
      category: document.getElementById("newSettingCategory").value,
      description: document.getElementById("newSettingDescription").value,
    };

    showLoading();
    try {
      const response = await fetch("/admin/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        showToast("Setting created successfully", "success");
        document.getElementById("newSettingForm").reset();
        await loadSettings();
      } else {
        const error = await response.json();
        showToast(error.error || "Failed to create setting", "error");
      }
    } catch (error) {
      showToast("Error creating setting", "error");
      console.error(error);
    } finally {
      hideLoading();
    }
  });

// ========================================
// SYSTEM TAB
// ========================================

async function loadSystemInfo() {
  showLoading();
  try {
    const response = await fetch("/admin/system-info");
    const data = await response.json();

    document.getElementById("dbSize").textContent =
      data.database_size_mb.toFixed(2) + " MB";
    document.getElementById("uploadStorage").textContent =
      data.upload_storage_gb.toFixed(2) + " GB";
    document.getElementById("cpuUsage").textContent =
      data.cpu_percent.toFixed(1) + "%";
    document.getElementById("memoryUsage").textContent =
      data.memory_percent.toFixed(1) + "%";

    // Render detailed system info
    const infoHtml = `
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; justify-content: space-between; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-weight: 600;">Python Version:</span>
                    <span>${data.python_version.split(" ")[0]}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-weight: 600;">Flask Version:</span>
                    <span>${data.flask_version}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-weight: 600;">Memory Usage:</span>
                    <span>${data.memory_used_gb.toFixed(2)} GB / ${data.memory_total_gb.toFixed(2)} GB (${data.memory_percent.toFixed(1)}%)</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-weight: 600;">Disk Usage:</span>
                    <span>${data.disk_used_gb.toFixed(2)} GB / ${data.disk_total_gb.toFixed(2)} GB (${data.disk_percent.toFixed(1)}%)</span>
                </div>
            </div>
        `;

    document.getElementById("systemHealthInfo").innerHTML = infoHtml;
  } catch (error) {
    showToast("Error loading system info", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function refreshSystemInfo() {
  loadSystemInfo();
}

// ========================================
// AUDIT LOGS TAB
// ========================================

async function loadAuditLogs() {
  showLoading();
  try {
    const action = document.getElementById("logFilter")?.value || "";
    const url = action
      ? `/admin/audit-logs?action=${action}&limit=200`
      : "/admin/audit-logs?limit=200";

    const response = await fetch(url);
    const data = await response.json();

    currentLogs = data.logs || [];
    renderAuditLogs(currentLogs);
  } catch (error) {
    showToast("Error loading audit logs", "error");
    console.error(error);
  } finally {
    hideLoading();
  }
}

function renderAuditLogs(logs) {
  const tbody = document.getElementById("logsTable");

  if (logs.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: #64748b;">
                    No audit logs found
                </td>
            </tr>
        `;
    return;
  }

  tbody.innerHTML = logs
    .map(
      (log) => `
        <tr>
            <td style="font-weight: 600;">${escapeHtml(log.action)}</td>
            <td>${log.user_id || "N/A"}</td>
            <td>${escapeHtml(log.resource_type || "N/A")} ${log.resource_id ? "#" + log.resource_id : ""}</td>
            <td>${escapeHtml(log.ip_address || "N/A")}</td>
            <td>${formatDate(log.created_at)}</td>
        </tr>
    `,
    )
    .join("");
}

function filterLogs() {
  loadAuditLogs();
}

function refreshLogs() {
  loadAuditLogs();
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

function showLoading() {
  document.getElementById("loadingOverlay").classList.add("active");
}

function hideLoading() {
  document.getElementById("loadingOverlay").classList.remove("active");
}

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast toast-${type} active`;

  setTimeout(() => {
    toast.classList.remove("active");
  }, 4000);
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

function getStatusClass(status) {
  const statusMap = {
    completed: "active",
    analyzing: "professional",
    failed: "inactive",
    uploaded: "free",
  };
  return statusMap[status] || "free";
}

// Close modal when clicking outside
document.getElementById("editUserModal")?.addEventListener("click", (e) => {
  if (e.target.id === "editUserModal") {
    closeEditModal();
  }
});
