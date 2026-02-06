// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * DOCKET NAVIGATOR
 *
 * Interactive JavaScript for browsing case docket entries.
 * Features:
 * - Real-time filtering by document type, date range
 * - Full-text search across titles and notes
 * - Grid/List view toggle
 * - Keyboard navigation support
 * - URL state persistence
 *
 * @requires docket data in window.DOCKET_DATA or data-docket attribute
 */

(function () {
  "use strict";

  // Feature detection
  if (!document.querySelector || !window.addEventListener) return;

  /**
   * DocketNavigator Class
   */
  class DocketNavigator {
    constructor(container) {
      this.container = container;
      this.data = [];
      this.filtered = [];
      this.filters = {
        search: "",
        type: "all",
        year: "all",
        sort: "date-desc",
      };
      this.view = "grid";

      this.init();
    }

    /**
     * Initialize the navigator
     */
    init() {
      this.loadData();
      this.cacheElements();
      this.bindEvents();
      this.restoreState();
      this.render();
    }

    /**
     * Load docket data from various sources
     */
    loadData() {
      // Try data attribute first
      const dataAttr = this.container.dataset.docket;
      if (dataAttr) {
        try {
          this.data = JSON.parse(dataAttr);
          return;
        } catch (e) {
          console.warn("Failed to parse docket data attribute:", e);
        }
      }

      // Try global variable
      if (window.DOCKET_DATA && Array.isArray(window.DOCKET_DATA)) {
        this.data = window.DOCKET_DATA;
        return;
      }

      // Try fetching from embedded script
      const scriptEl = this.container.querySelector(
        'script[type="application/json"]',
      );
      if (scriptEl) {
        try {
          this.data = JSON.parse(scriptEl.textContent);
          return;
        } catch (e) {
          console.warn("Failed to parse embedded docket JSON:", e);
        }
      }

      console.warn("No docket data found");
      this.data = [];
    }

    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
      this.searchInput = this.container.querySelector(".docket-search-input");
      this.typeFilter = this.container.querySelector('[data-filter="type"]');
      this.yearFilter = this.container.querySelector('[data-filter="year"]');
      this.sortSelect = this.container.querySelector('[data-filter="sort"]');
      this.gridContainer = this.container.querySelector(
        ".docket-nav-grid, .docket-nav-list",
      );
      this.viewToggle = this.container.querySelector(".docket-view-toggle");
      this.clearBtn = this.container.querySelector(".docket-clear-filters");
      this.statTotal = this.container.querySelector('[data-stat="total"]');
      this.statFiltered = this.container.querySelector(
        '[data-stat="filtered"]',
      );
      this.chips = this.container.querySelectorAll(".docket-chip[data-type]");
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
      // Search input
      if (this.searchInput) {
        this.searchInput.addEventListener(
          "input",
          this.debounce(() => {
            this.filters.search = this.searchInput.value.trim().toLowerCase();
            this.applyFilters();
          }, 200),
        );

        this.searchInput.addEventListener("keydown", (e) => {
          if (e.key === "Escape") {
            this.searchInput.value = "";
            this.filters.search = "";
            this.applyFilters();
          }
        });
      }

      // Type filter chips
      this.chips.forEach((chip) => {
        chip.addEventListener("click", () => {
          const type = chip.dataset.type;
          this.filters.type = this.filters.type === type ? "all" : type;
          this.updateChipStates();
          this.applyFilters();
        });
      });

      // Year filter dropdown
      if (this.yearFilter) {
        this.yearFilter.addEventListener("change", () => {
          this.filters.year = this.yearFilter.value;
          this.applyFilters();
        });
      }

      // Sort dropdown
      if (this.sortSelect) {
        this.sortSelect.addEventListener("change", () => {
          this.filters.sort = this.sortSelect.value;
          this.applyFilters();
        });
      }

      // View toggle
      if (this.viewToggle) {
        this.viewToggle.querySelectorAll(".docket-view-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            this.view = btn.dataset.view || "grid";
            this.updateViewToggle();
            this.render();
            this.saveState();
          });
        });
      }

      // Clear filters
      if (this.clearBtn) {
        this.clearBtn.addEventListener("click", () => {
          this.resetFilters();
        });
      }

      // Keyboard navigation for cards
      this.container.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          const card = e.target.closest(".docket-card");
          if (card) {
            const link = card.querySelector(".docket-card-action[href]");
            if (link) {
              e.preventDefault();
              link.click();
            }
          }
        }
      });
    }

    /**
     * Apply all active filters
     */
    applyFilters() {
      this.filtered = this.data.filter((item) => {
        // Search filter
        if (this.filters.search) {
          const searchable = [
            item.title || "",
            item.notes || "",
            item.type || "",
          ]
            .join(" ")
            .toLowerCase();
          if (!searchable.includes(this.filters.search)) {
            return false;
          }
        }

        // Type filter
        if (this.filters.type !== "all") {
          if (
            (item.type || "").toLowerCase() !== this.filters.type.toLowerCase()
          ) {
            return false;
          }
        }

        // Year filter
        if (this.filters.year !== "all") {
          const itemYear = new Date(item.date).getFullYear().toString();
          if (itemYear !== this.filters.year) {
            return false;
          }
        }

        return true;
      });

      // Sort results
      this.sortResults();

      // Update UI
      this.render();
      this.updateStats();
      this.saveState();
    }

    /**
     * Sort filtered results
     */
    sortResults() {
      switch (this.filters.sort) {
        case "date-asc":
          this.filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
          break;
        case "date-desc":
        default:
          this.filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
          break;
        case "title":
          this.filtered.sort((a, b) =>
            (a.title || "").localeCompare(b.title || ""),
          );
          break;
        case "type":
          this.filtered.sort((a, b) =>
            (a.type || "").localeCompare(b.type || ""),
          );
          break;
      }
    }

    /**
     * Render filtered results
     */
    render() {
      if (!this.gridContainer) return;

      if (this.filtered.length === 0) {
        this.gridContainer.innerHTML = this.renderEmpty();
        return;
      }

      const html = this.view === "list" ? this.renderList() : this.renderGrid();

      this.gridContainer.innerHTML = html;

      // Update container class for view
      this.gridContainer.className =
        this.view === "list" ? "docket-nav-list" : "docket-nav-grid";
    }

    /**
     * Render grid view
     */
    renderGrid() {
      return this.filtered
        .map(
          (item) => `
        <article class="docket-card" tabindex="0">
          <span class="docket-card-type docket-card-type-${(item.type || "other").toLowerCase()}">${this.escapeHtml(item.type || "Document")}</span>
          <time class="docket-card-date" datetime="${this.escapeHtml(item.date)}">${this.formatDate(item.date)}</time>
          <h3 class="docket-card-title">${this.escapeHtml(item.title || "Untitled Document")}</h3>
          ${item.notes ? `<p class="docket-card-notes">${this.escapeHtml(item.notes)}</p>` : ""}
          <div class="docket-card-actions">
            ${
              item.file
                ? `
              <a href="${this.escapeHtml(item.file)}" class="docket-card-action" target="_blank" rel="noopener">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                View PDF
              </a>
            `
                : ""
            }
            <button class="docket-card-action" data-action="copy" data-id="${this.escapeHtml(item.id || "")}">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              Copy Link
            </button>
          </div>
        </article>
      `,
        )
        .join("");
    }

    /**
     * Render list view
     */
    renderList() {
      return this.filtered
        .map(
          (item) => `
        <article class="docket-list-item" tabindex="0">
          <time class="docket-list-date" datetime="${this.escapeHtml(item.date)}">${this.formatDate(item.date)}</time>
          <h3 class="docket-list-title">${this.escapeHtml(item.title || "Untitled Document")}</h3>
          <span class="docket-list-type">${this.escapeHtml(item.type || "Document")}</span>
          ${
            item.file
              ? `
            <a href="${this.escapeHtml(item.file)}" class="docket-card-action" target="_blank" rel="noopener" aria-label="View PDF">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </a>
          `
              : ""
          }
        </article>
      `,
        )
        .join("");
    }

    /**
     * Render empty state
     */
    renderEmpty() {
      const hasFilters =
        this.filters.search ||
        this.filters.type !== "all" ||
        this.filters.year !== "all";

      return `
        <div class="docket-empty">
          <svg class="docket-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <h3 class="docket-empty-title">${hasFilters ? "No matching documents" : "No documents available"}</h3>
          <p class="docket-empty-text">
            ${
              hasFilters
                ? "Try adjusting your search or filters to find what you're looking for."
                : "Docket entries will appear here once documents are filed."
            }
          </p>
          ${hasFilters ? `<button class="btn btn-ghost btn-sm" onclick="this.closest('.docket-navigator').dispatchEvent(new CustomEvent('reset-filters'))">Clear Filters</button>` : ""}
        </div>
      `;
    }

    /**
     * Update filter chip states
     */
    updateChipStates() {
      this.chips.forEach((chip) => {
        const isActive = chip.dataset.type === this.filters.type;
        chip.setAttribute("aria-pressed", isActive);
        chip.classList.toggle("active", isActive);
      });
    }

    /**
     * Update view toggle states
     */
    updateViewToggle() {
      if (!this.viewToggle) return;

      this.viewToggle.querySelectorAll(".docket-view-btn").forEach((btn) => {
        const isActive = (btn.dataset.view || "grid") === this.view;
        btn.setAttribute("aria-pressed", isActive);
        btn.classList.toggle("active", isActive);
      });
    }

    /**
     * Update stats display
     */
    updateStats() {
      if (this.statTotal) {
        this.statTotal.textContent = this.data.length;
      }
      if (this.statFiltered) {
        this.statFiltered.textContent = this.filtered.length;
      }
    }

    /**
     * Reset all filters
     */
    resetFilters() {
      this.filters = {
        search: "",
        type: "all",
        year: "all",
        sort: "date-desc",
      };

      if (this.searchInput) this.searchInput.value = "";
      if (this.yearFilter) this.yearFilter.value = "all";
      if (this.sortSelect) this.sortSelect.value = "date-desc";

      this.updateChipStates();
      this.applyFilters();
    }

    /**
     * Save filter state to URL
     */
    saveState() {
      if (!history.replaceState) return;

      const params = new URLSearchParams();
      if (this.filters.search) params.set("q", this.filters.search);
      if (this.filters.type !== "all") params.set("type", this.filters.type);
      if (this.filters.year !== "all") params.set("year", this.filters.year);
      if (this.filters.sort !== "date-desc")
        params.set("sort", this.filters.sort);
      if (this.view !== "grid") params.set("view", this.view);

      const newUrl = params.toString()
        ? `${location.pathname}?${params}${location.hash}`
        : `${location.pathname}${location.hash}`;

      history.replaceState(null, "", newUrl);
    }

    /**
     * Restore filter state from URL
     */
    restoreState() {
      const params = new URLSearchParams(location.search);

      if (params.has("q")) {
        this.filters.search = params.get("q");
        if (this.searchInput) this.searchInput.value = this.filters.search;
      }

      if (params.has("type")) {
        this.filters.type = params.get("type");
        this.updateChipStates();
      }

      if (params.has("year")) {
        this.filters.year = params.get("year");
        if (this.yearFilter) this.yearFilter.value = this.filters.year;
      }

      if (params.has("sort")) {
        this.filters.sort = params.get("sort");
        if (this.sortSelect) this.sortSelect.value = this.filters.sort;
      }

      if (params.has("view")) {
        this.view = params.get("view");
        this.updateViewToggle();
      }

      // Initial filter application
      this.filtered = [...this.data];
      this.applyFilters();
    }

    /**
     * Utility: Format date
     */
    formatDate(dateStr) {
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      } catch {
        return dateStr;
      }
    }

    /**
     * Utility: Escape HTML
     */
    escapeHtml(str) {
      if (!str) return "";
      const div = document.createElement("div");
      div.textContent = str;
      return div.innerHTML;
    }

    /**
     * Utility: Debounce function
     */
    debounce(fn, delay) {
      let timeout;
      return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
      };
    }
  }

  /**
   * Auto-initialize on DOM ready
   */
  function init() {
    document.querySelectorAll(".docket-navigator").forEach((container) => {
      if (!container._docketNav) {
        container._docketNav = new DocketNavigator(container);
      }
    });
  }

  // Initialize
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose for manual initialization
  window.DocketNavigator = DocketNavigator;
})();
