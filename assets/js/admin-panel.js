// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Evident Admin Panel
// Supports: overview stats, audit log viewer
// User management is handled by server-rendered Flask routes at /admin/users

let currentLogs = [];

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  loadOverviewData();
});

function setupTabs() {
  document.querySelectorAll('.tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      const targetTab = tab.dataset.tab;

      document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(targetTab).classList.add('active');

      loadTabData(targetTab);
    });
  });
}

async function loadTabData(tab) {
  switch (tab) {
    case 'overview':
      await loadOverviewData();
      break;
    case 'logs':
      await loadAuditLogs();
      break;
  }
}

// ============================================================================
// OVERVIEW TAB
// ============================================================================

async function loadOverviewData() {
  showLoading();
  try {
    const response = await fetch('/admin/api/stats');
    const data = await response.json();

    const totalUsersEl = document.getElementById('totalUsers');
    const activeUsersEl = document.getElementById('activeUsers');
    const verifiedUsersEl = document.getElementById('verifiedUsers');

    if (totalUsersEl) totalUsersEl.textContent = data.total_users ?? 0;
    if (activeUsersEl) activeUsersEl.textContent = data.active_users ?? 0;
    if (verifiedUsersEl) verifiedUsersEl.textContent = data.verified_users ?? 0;
  } catch (error) {
    showToast('Error loading overview data', 'error');
    console.error(error);
  } finally {
    hideLoading();
  }
}

// ============================================================================
// AUDIT LOGS TAB
// ============================================================================

async function loadAuditLogs() {
  showLoading();
  try {
    const action = document.getElementById('logFilter')?.value || '';
    const url = action
      ? `/admin/api/audit-logs?action=${encodeURIComponent(action)}&limit=200`
      : '/admin/api/audit-logs?limit=200';

    const response = await fetch(url);
    const data = await response.json();

    currentLogs = data.logs || [];
    renderAuditLogs(currentLogs);
  } catch (error) {
    showToast('Error loading audit logs', 'error');
    console.error(error);
  } finally {
    hideLoading();
  }
}

function renderAuditLogs(logs) {
  const tbody = document.getElementById('logsTable');
  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; padding: 2rem; color: #64748b;">
          No audit logs found
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = logs
    .map(
      (log) => `
      <tr>
        <td style="font-weight: 600;">${escapeHtml(log.action)}</td>
        <td>${log.user_id ?? 'N/A'}</td>
        <td>${escapeHtml(log.resource_type ?? 'N/A')} ${log.resource_id ? '#' + log.resource_id : ''}</td>
        <td>${escapeHtml(log.ip_address ?? 'N/A')}</td>
        <td>${formatDate(log.created_at)}</td>
      </tr>`
    )
    .join('');
}

function filterLogs() {
  loadAuditLogs();
}

function refreshLogs() {
  loadAuditLogs();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showLoading() {
  document.getElementById('loadingOverlay')?.classList.add('active');
}

function hideLoading() {
  document.getElementById('loadingOverlay')?.classList.remove('active');
}

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast toast-${type} active`;
  setTimeout(() => toast.classList.remove('active'), 4000);
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
