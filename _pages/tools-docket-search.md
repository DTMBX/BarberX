---
layout: page
title: Docket Search
subtitle: Search court dockets across New Jersey Superior Court
description: Advanced docket search with filters, real-time updates, and export capabilities
permalink: /tools/docket-search/
toc: false
---

<div class="tool-page-header">
  <div class="tool-page-header__icon">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
      <circle cx="11" cy="11" r="8"/>
      <path d="M21 21l-4.35-4.35"/>
    </svg>
  </div>
  <h1>Docket Search</h1>
  <p>Search and track court dockets, case filings, and party information across New Jersey Superior Court System</p>
</div>

<div class="search-tool">
  <div class="search-tool__main">
    <!-- Search Input -->
    <div class="search-box">
      <div class="search-box__input-wrapper">
        <svg class="search-box__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input 
          type="text" 
          class="search-box__input" 
          placeholder="Enter docket number, party name, or attorney..."
          id="docketSearchInput"
        />
        <button class="search-box__clear" id="clearSearch" aria-label="Clear search">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <button class="search-box__btn" id="searchBtn">
        Search Dockets
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <!-- Advanced Filters -->
    <details class="filter-panel">
      <summary class="filter-panel__summary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
        </svg>
        <span>Advanced Filters</span>
        <svg class="filter-panel__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </summary>

      <div class="filter-panel__content">
        <div class="filter-grid">
          <div class="filter-group">
            <label for="courtFilter">Court</label>
            <select id="courtFilter" class="filter-select">
              <option value="">All Courts</option>
              <option value="ATL">Atlantic County</option>
              <option value="MER">Mercer County</option>
              <option value="CAM">Camden County</option>
              <option value="ESS">Essex County</option>
              <option value="HUD">Hudson County</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="caseTypeFilter">Case Type</label>
            <select id="caseTypeFilter" class="filter-select">
              <option value="">All Types</option>
              <option value="L">Law Division</option>
              <option value="DC">Special Civil Part</option>
              <option value="F">Family</option>
              <option value="CR">Criminal</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="dateFromFilter">Filed After</label>
            <input type="date" id="dateFromFilter" class="filter-input" />
          </div>

          <div class="filter-group">
            <label for="dateToFilter">Filed Before</label>
            <input type="date" id="dateToFilter" class="filter-input" />
          </div>

          <div class="filter-group">
            <label for="statusFilter">Status</label>
            <select id="statusFilter" class="filter-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="closed">Closed</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="partyTypeFilter">Party Type</label>
            <select id="partyTypeFilter" class="filter-select">
              <option value="">Any Party</option>
              <option value="plaintiff">Plaintiff</option>
              <option value="defendant">Defendant</option>
            </select>
          </div>
        </div>

        <div class="filter-actions">
          <button class="btn-secondary" id="resetFilters">Reset Filters</button>
          <button class="btn-premium" id="applyFilters">Apply Filters</button>
        </div>
      </div>
    </details>

    <!-- Results -->
    <div class="search-results" id="searchResults">
      <div class="search-results__placeholder">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="64" height="64">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <h3>No Search Yet</h3>
        <p>Enter a docket number, party name, or use filters to search court records</p>
      </div>
    </div>

  </div>

  <!-- Sidebar -->
  <aside class="search-tool__sidebar">
    <div class="info-card">
      <h3>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4M12 8h.01"/>
        </svg>
        Search Tips
      </h3>
      <ul>
        <li><strong>Docket Format:</strong> County-Division-Number-Year (e.g., ATL-L-002794-25)</li>
        <li><strong>Party Names:</strong> Last name, First name format works best</li>
        <li><strong>Wildcards:</strong> Use * for partial matches</li>
        <li><strong>Date Ranges:</strong> Narrow results with filing date filters</li>
      </ul>
    </div>

    <div class="info-card info-card--premium">
      <h3>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
        Premium Features
      </h3>
      <ul>
        <li>Save searches and get alerts</li>
        <li>Export results to PDF/CSV</li>
        <li>Bulk docket monitoring</li>
        <li>API access for integrations</li>
      </ul>
      <a href="/contact/" class="btn-premium btn-premium--small">
        Upgrade Now
      </a>
    </div>

    <div class="info-card">
      <h3>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Quick Links
      </h3>
      <ul class="quick-links">
        <li><a href="/cases/">View Active Cases</a></li>
        <li><a href="/tools/deadline-calculator/">Deadline Calculator</a></li>
        <li><a href="/tools/document-analysis/">Document Analysis</a></li>
      </ul>
    </div>

  </aside>
</div>

<div class="info-notice">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
    <path d="M12 8v4"/>
  </svg>
  <div>
    <strong>Local Data Search</strong>
    <p>Searching across all docket entries in the Evident case database. For official NJ Courts records, visit <a href="https://portal.njcourts.gov/" target="_blank" rel="noopener">NJ Courts Portal</a>.</p>
  </div>
</div>

<script src="/assets/js/api-config.js"></script>
<script src="/assets/js/docket-search.js"></script>

<style>
.tool-page-header {
  text-align: center;
  padding: 2rem 0 3rem;
  max-width: 720px;
  margin: 0 auto;
}

.tool-page-header__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #d4a574 0%, #c49364 100%);
  border-radius: 20px;
  color: #0a0a0f;
  margin-bottom: 1.5rem;
}

.tool-page-header h1 {
  font-size: clamp(2rem, 4vw, 2.75rem);
  margin-bottom: 1rem;
}

.tool-page-header p {
  font-size: 1.125rem;
  color: rgb(255 255 255 / 60%);
  line-height: 1.6;
}

.search-tool {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin: 2rem 0;
}

@media (min-width: 1024px) {
  .search-tool {
    grid-template-columns: 1fr 320px;
  }
}

/* Search Box */
.search-box {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (min-width: 640px) {
  .search-box {
    flex-direction: row;
  }
}

.search-box__input-wrapper {
  position: relative;
  flex: 1;
}

.search-box__icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgb(156 163 175);
  pointer-events: none;
}

.search-box__input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgb(255 255 255 / 5%);
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 12px;
  color: #f5f5f7;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.search-box__input::placeholder {
  color: rgb(156 163 175);
}

.search-box__input:focus {
  border-color: #d4a574;
  box-shadow: 0 0 0 3px rgb(212 165 116 / 20%);
}

.search-box__clear {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgb(156 163 175);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.search-box__input:not(:placeholder-shown) ~ .search-box__clear {
  opacity: 1;
}

.search-box__clear:hover {
  background: rgb(255 255 255 / 10%);
  color: #f5f5f7;
}

.search-box__btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #d4a574 0%, #c49364 100%);
  border: none;
  border-radius: 12px;
  color: #0a0a0f;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-box__btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgb(212 165 116 / 35%);
}

/* Filter Panel */
.filter-panel {
  background: linear-gradient(135deg, rgb(255 255 255 / 5%) 0%, rgb(255 255 255 / 2%) 100%);
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 16px;
  margin-bottom: 2rem;
  overflow: hidden;
}

.filter-panel__summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  cursor: pointer;
  user-select: none;
  list-style: none;
  font-weight: 500;
  color: #f5f5f7;
}

.filter-panel__summary::-webkit-details-marker {
  display: none;
}

.filter-panel__chevron {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.filter-panel[open] .filter-panel__chevron {
  transform: rotate(180deg);
}

.filter-panel__content {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid rgb(255 255 255 / 8%);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1.25rem 0;
}

.filter-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(255 255 255 / 70%);
  margin-bottom: 0.5rem;
}

.filter-select,
.filter-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background: rgb(255 255 255 / 5%);
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 8px;
  color: #f5f5f7;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.2s ease;
}

.filter-select:focus,
.filter-input:focus {
  border-color: #d4a574;
  box-shadow: 0 0 0 2px rgb(212 165 116 / 15%);
}

.filter-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* Search Results */
.search-results {
  min-height: 400px;
  background: rgb(255 255 255 / 3%);
  border: 1px solid rgb(255 255 255 / 8%);
  border-radius: 16px;
  padding: 3rem 2rem;
}

.search-results__placeholder {
  text-align: center;
  color: rgb(255 255 255 / 40%);
}

.search-results__placeholder svg {
  margin: 0 auto 1.5rem;
  opacity: 0.5;
}

.search-results__placeholder h3 {
  font-size: 1.25rem;
  color: rgb(255 255 255 / 50%);
  margin-bottom: 0.5rem;
}

.search-results__placeholder p {
  font-size: 0.95rem;
}

/* Sidebar Info Cards */
.info-card {
  background: linear-gradient(135deg, rgb(255 255 255 / 5%) 0%, rgb(255 255 255 / 2%) 100%);
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-card--premium {
  background: linear-gradient(135deg, rgb(212 165 116 / 10%) 0%, rgb(212 165 116 / 3%) 100%);
  border-color: rgb(212 165 116 / 20%);
}

.info-card h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #f5f5f7;
  margin-bottom: 1rem;
}

.info-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.9rem;
  color: rgb(255 255 255 / 60%);
}

.info-card ul li {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgb(255 255 255 / 5%);
}

.info-card ul li:last-child {
  border-bottom: none;
}

.info-card .btn-premium {
  width: 100%;
  margin-top: 1rem;
  justify-content: center;
}

.quick-links a {
  color: #d4a574;
  text-decoration: none;
  transition: color 0.2s ease;
}

.quick-links a:hover {
  color: #e8c9a8;
}

/* Info Notice */
.info-notice {
  display: flex;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: rgb(16 185 129 / 10%);
  border: 1px solid rgb(16 185 129 / 25%);
  border-radius: 12px;
  margin: 2rem 0;
  color: rgb(167 243 208);
}

.info-notice svg {
  flex-shrink: 0;
}

.info-notice strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.info-notice p {
  font-size: 0.875rem;
  margin: 0;
}

.info-notice a {
  color: #6ee7b7;
  text-decoration: underline;
}

/* Search Results List */
.search-results__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgb(255 255 255 / 10%);
}

.search-results__header h3 {
  font-size: 1.125rem;
  color: #f5f5f7;
  margin: 0;
}

.search-results__actions {
  display: flex;
  gap: 0.5rem;
}

.result-card {
  background: linear-gradient(135deg, rgb(255 255 255 / 5%) 0%, rgb(255 255 255 / 2%) 100%);
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.result-card:hover {
  border-color: rgb(212 165 116 / 30%);
  background: linear-gradient(135deg, rgb(255 255 255 / 8%) 0%, rgb(255 255 255 / 3%) 100%);
}

.result-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.result-card h4 {
  font-size: 1.125rem;
  margin: 0;
}

.result-card h4 a {
  color: #d4a574;
  text-decoration: none;
  transition: color 0.2s ease;
}

.result-card h4 a:hover {
  color: #e8c9a8;
}

.result-card__title {
  font-size: 0.95rem;
  color: rgb(255 255 255 / 70%);
  margin: 0 0 0.5rem 0;
}

.result-card__meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgb(255 255 255 / 50%);
  margin-bottom: 1rem;
}

.result-card__entries {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgb(255 255 255 / 8%);
}

.docket-entry {
  display: grid;
  grid-template-columns: 110px 120px 1fr;
  gap: 1rem;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  border-bottom: 1px solid rgb(255 255 255 / 5%);
}

.docket-entry:last-child {
  border-bottom: none;
}

.docket-entry__date {
  color: rgb(255 255 255 / 50%);
}

.docket-entry__type {
  color: #d4a574;
  font-weight: 500;
}

.docket-entry__title {
  color: rgb(255 255 255 / 70%);
  text-decoration: none;
  transition: color 0.2s ease;
}

.docket-entry__title:hover {
  color: #f5f5f7;
}

.view-all-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #d4a574;
  font-size: 0.9rem;
  text-decoration: none;
  transition: color 0.2s ease;
}

.view-all-link:hover {
  color: #e8c9a8;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge--success {
  background: rgb(16 185 129 / 20%);
  color: #6ee7b7;
}

.badge--warning {
  background: rgb(251 191 36 / 20%);
  color: #fcd34d;
}

.badge--neutral {
  background: rgb(107 114 128 / 20%);
  color: rgb(209 213 219);
}

.badge--info {
  background: rgb(59 130 246 / 20%);
  color: #93c5fd;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: 1px solid rgb(255 255 255 / 20%);
  border-radius: 8px;
  color: rgb(255 255 255 / 70%);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgb(255 255 255 / 5%);
  border-color: rgb(255 255 255 / 35%);
  color: #f5f5f7;
}
</style>

<!-- Search functionality handled by docket-search.js -->
