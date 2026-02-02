/**
 * BarberX Legal Case Management Pro Suite
 * Docket Search Tool - Production Implementation
 */

// Load docket data from Jekyll-generated JSON
let docketIndex = [];
let casesMap = {};

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  await loadDocketData();
  initializeSearchHandlers();
});

async function loadDocketData() {
  try {
    // Load docket entries from all YAML files
    const response = await fetch("/index.json");
    const siteData = await response.json();

    // Build docket index from site data
    if (siteData && siteData.cases) {
      docketIndex = siteData.cases.flatMap((c) => {
        return (c.docket || []).map((entry) => ({
          ...entry,
          caseSlug: c.slug,
          caseDocket: c.docket_number,
          caseTitle: c.title,
          court: c.court,
          status: c.status,
        }));
      });
    }

    console.log(`Loaded ${docketIndex.length} docket entries`);
  } catch (error) {
    console.error("Failed to load docket data:", error);
    showToast("Failed to load docket data. Using offline mode.", "error");
  }
}

function initializeSearchHandlers() {
  const searchInput = document.getElementById("docketSearchInput");
  const searchBtn = document.getElementById("searchBtn");
  const clearBtn = document.getElementById("clearSearch");
  const applyFiltersBtn = document.getElementById("applyFilters");
  const resetFiltersBtn = document.getElementById("resetFilters");

  // Search on button click
  searchBtn.addEventListener("click", performSearch);

  // Search on Enter key
  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") performSearch();
  });

  // Clear search
  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearResults();
  });

  // Apply filters
  applyFiltersBtn.addEventListener("click", performSearch);

  // Reset filters
  resetFiltersBtn.addEventListener("click", resetFilters);
}

function performSearch() {
  const query = document.getElementById("docketSearchInput").value.trim();

  if (!query && !hasActiveFilters()) {
    showToast("Please enter a search term or apply filters", "info");
    return;
  }

  // Get filter values
  const filters = {
    court: document.getElementById("courtFilter").value,
    caseType: document.getElementById("caseTypeFilter").value,
    dateFrom: document.getElementById("dateFromFilter").value,
    dateTo: document.getElementById("dateToFilter").value,
    status: document.getElementById("statusFilter").value,
    partyType: document.getElementById("partyTypeFilter").value,
  };

  // Search docket index
  let results = docketIndex;

  // Apply text search
  if (query) {
    const searchTerm = query.toLowerCase();
    results = results.filter((entry) => {
      return (
        entry.caseDocket?.toLowerCase().includes(searchTerm) ||
        entry.caseTitle?.toLowerCase().includes(searchTerm) ||
        entry.title?.toLowerCase().includes(searchTerm) ||
        entry.type?.toLowerCase().includes(searchTerm)
      );
    });
  }

  // Apply court filter
  if (filters.court) {
    results = results.filter((entry) =>
      entry.caseDocket?.startsWith(filters.court),
    );
  }

  // Apply case type filter
  if (filters.caseType) {
    results = results.filter((entry) =>
      entry.caseDocket?.includes(`-${filters.caseType}-`),
    );
  }

  // Apply date range filters
  if (filters.dateFrom) {
    results = results.filter(
      (entry) => entry.date && entry.date >= filters.dateFrom,
    );
  }

  if (filters.dateTo) {
    results = results.filter(
      (entry) => entry.date && entry.date <= filters.dateTo,
    );
  }

  // Apply status filter
  if (filters.status) {
    results = results.filter(
      (entry) => entry.status?.toLowerCase() === filters.status,
    );
  }

  displayResults(results, query);
}

function displayResults(results, query) {
  const resultsContainer = document.getElementById("searchResults");

  if (results.length === 0) {
    resultsContainer.innerHTML = `
      <div class="search-results__placeholder">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="64" height="64">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <h3>No Results Found</h3>
        <p>No docket entries match your search criteria. Try different keywords or filters.</p>
      </div>
    `;
    return;
  }

  // Group results by case
  const resultsByCase = {};
  results.forEach((entry) => {
    if (!resultsByCase[entry.caseSlug]) {
      resultsByCase[entry.caseSlug] = {
        slug: entry.caseSlug,
        docket: entry.caseDocket,
        title: entry.caseTitle,
        court: entry.court,
        status: entry.status,
        entries: [],
      };
    }
    resultsByCase[entry.caseSlug].entries.push(entry);
  });

  // Sort entries by date (newest first)
  Object.values(resultsByCase).forEach((caseData) => {
    caseData.entries.sort((a, b) => (b.date || "").localeCompare(a.date || ""));
  });

  // Render results
  const html = `
    <div class="search-results__header">
      <h3>Found ${results.length} docket entries in ${Object.keys(resultsByCase).length} case(s)</h3>
      <div class="search-results__actions">
        <button class="btn-secondary btn-secondary--small" onclick="exportResults('csv')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
          Export CSV
        </button>
      </div>
    </div>
    
    <div class="search-results__list">
      ${Object.values(resultsByCase)
        .map(
          (caseData) => `
        <div class="result-card">
          <div class="result-card__header">
            <h4>
              <a href="/cases/${caseData.slug}/">${caseData.docket}</a>
            </h4>
            <span class="badge badge--${getStatusColor(caseData.status)}">${caseData.status || "Active"}</span>
          </div>
          <p class="result-card__title">${caseData.title || "Untitled Case"}</p>
          <div class="result-card__meta">
            <span>${caseData.court || "Court Unspecified"}</span>
            <span>•</span>
            <span>${caseData.entries.length} filing(s)</span>
          </div>
          
          <div class="result-card__entries">
            ${caseData.entries
              .slice(0, 5)
              .map(
                (entry) => `
              <div class="docket-entry">
                <span class="docket-entry__date">${formatDate(entry.date)}</span>
                <span class="docket-entry__type">${entry.type || "Document"}</span>
                <a href="${entry.file}" class="docket-entry__title" target="_blank">
                  ${entry.title || "Untitled Document"}
                </a>
              </div>
            `,
              )
              .join("")}
            ${
              caseData.entries.length > 5
                ? `
              <a href="/cases/${caseData.slug}/#docket" class="view-all-link">
                View all ${caseData.entries.length} entries →
              </a>
            `
                : ""
            }
          </div>
        </div>
      `,
        )
        .join("")}
    </div>
  `;

  resultsContainer.innerHTML = html;
}

function clearResults() {
  const resultsContainer = document.getElementById("searchResults");
  resultsContainer.innerHTML = `
    <div class="search-results__placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="64" height="64">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      <h3>No Search Yet</h3>
      <p>Enter a docket number, party name, or use filters to search court records</p>
    </div>
  `;
}

function resetFilters() {
  document.getElementById("courtFilter").value = "";
  document.getElementById("caseTypeFilter").value = "";
  document.getElementById("dateFromFilter").value = "";
  document.getElementById("dateToFilter").value = "";
  document.getElementById("statusFilter").value = "";
  document.getElementById("partyTypeFilter").value = "";
  showToast("Filters reset", "info");
}

function hasActiveFilters() {
  return (
    document.getElementById("courtFilter").value ||
    document.getElementById("caseTypeFilter").value ||
    document.getElementById("dateFromFilter").value ||
    document.getElementById("dateToFilter").value ||
    document.getElementById("statusFilter").value ||
    document.getElementById("partyTypeFilter").value
  );
}

function formatDate(dateStr) {
  if (!dateStr) return "Date Unknown";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getStatusColor(status) {
  const statusLower = (status || "").toLowerCase();
  if (statusLower.includes("active")) return "success";
  if (statusLower.includes("closed")) return "neutral";
  if (statusLower.includes("pending")) return "warning";
  return "info";
}

function exportResults(format) {
  showToast("Export feature coming soon in premium version", "info");
}
