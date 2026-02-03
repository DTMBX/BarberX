/**
 * Evident Technologies - Premium Features
 * Mobile app experience with PWA support
 */

(function () {
  "use strict";

  // ============================================
  // App Configuration
  // ============================================
  const CONFIG = {
    APP_NAME: "Evident",
    VERSION: "1.0.0",
    DEBUG: false,
  };

  // ============================================
  // Service Worker Registration
  // ============================================
  async function registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      try {
        const registration = await navigator.serviceWorker.register(
          "/assets/js/service-worker.js",
          {
            scope: "/",
          },
        );

        if (CONFIG.DEBUG) {
          console.log("[App] Service Worker registered:", registration.scope);
        }

        // Check for updates
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          newWorker.addEventListener("statechange", () => {
            if (
              newWorker.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              showToast(
                "Update available! Refresh to get the latest version.",
                "info",
              );
            }
          });
        });
      } catch (error) {
        console.error("[App] Service Worker registration failed:", error);
      }
    }
  }

  // ============================================
  // PWA Install Prompt
  // ============================================
  let deferredPrompt;

  function setupInstallPrompt() {
    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      deferredPrompt = e;

      // Check if user has dismissed before
      if (!localStorage.getItem("pwa-install-dismissed")) {
        setTimeout(() => showInstallBanner(), 3000);
      }
    });

    window.addEventListener("appinstalled", () => {
      hideInstallBanner();
      showToast("App installed successfully! 🎉", "success");
      deferredPrompt = null;
    });
  }

  function showInstallBanner() {
    const banner = document.getElementById("install-banner");
    if (banner && deferredPrompt) {
      banner.classList.add("visible");
    }
  }

  function hideInstallBanner() {
    const banner = document.getElementById("install-banner");
    if (banner) {
      banner.classList.remove("visible");
    }
  }

  async function installApp() {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (CONFIG.DEBUG) {
      console.log("[App] Install prompt outcome:", outcome);
    }

    if (outcome === "dismissed") {
      localStorage.setItem("pwa-install-dismissed", "true");
    }

    hideInstallBanner();
    deferredPrompt = null;
  }

  // ============================================
  // Toast Notifications
  // ============================================
  function showToast(message, type = "info", duration = 4000) {
    const container =
      document.getElementById("toast-container") || createToastContainer();

    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;

    const icons = {
      success: "✓",
      error: "✕",
      info: "ℹ",
      warning: "⚠",
    };

    toast.innerHTML = `
      <span class="toast__icon">${icons[type] || icons.info}</span>
      <span class="toast__message">${message}</span>
      <button class="toast__close" aria-label="Close">✕</button>
    `;

    container.appendChild(toast);

    // Close button
    toast
      .querySelector(".toast__close")
      .addEventListener("click", () => removeToast(toast));

    // Auto-dismiss
    setTimeout(() => removeToast(toast), duration);

    return toast;
  }

  function createToastContainer() {
    const container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
    return container;
  }

  function removeToast(toast) {
    toast.classList.add("toast-out");
    setTimeout(() => toast.remove(), 200);
  }

  // ============================================
  // Bottom Navigation
  // ============================================
  function createBottomNav() {
    const nav = document.createElement("nav");
    nav.className = "bottom-nav";
    nav.setAttribute("aria-label", "Main navigation");

    const currentPath = window.location.pathname;

    const navItems = [
      { href: "/", icon: "🏠", label: "Home", paths: ["/", "/index.html"] },
      {
        href: "/cases/",
        icon: "📁",
        label: "Cases",
        paths: ["/cases/", "/cases"],
      },
      { href: "/opra/", icon: "📋", label: "OPRA", paths: ["/opra/", "/opra"] },
      {
        href: "/essays/",
        icon: "📝",
        label: "Essays",
        paths: ["/essays/", "/essays"],
      },
    ];

    nav.innerHTML = `
      <ul class="bottom-nav__items">
        ${navItems
          .map((item) => {
            const isActive = item.paths.some(
              (p) => currentPath === p || currentPath.startsWith(p + "/"),
            );
            return `
            <li>
              <a href="${item.href}" class="bottom-nav__item${isActive ? " active" : ""}" aria-current="${isActive ? "page" : "false"}">
                <span class="bottom-nav__icon">${item.icon}</span>
                <span class="bottom-nav__label">${item.label}</span>
              </a>
            </li>
          `;
          })
          .join("")}
      </ul>
    `;

    document.body.appendChild(nav);
  }

  // ============================================
  // Floating Action Button
  // ============================================
  function createFAB() {
    const fab = document.createElement("button");
    fab.className = "fab haptic-tap";
    fab.setAttribute("aria-label", "Quick actions");
    fab.setAttribute("aria-expanded", "false");
    fab.innerHTML = `
      <span class="fab__icon">⚡</span>
      <div class="fab__menu">
        <a href="/cases/" class="fab__menu-item">
          <span>📁</span>
          <span>Browse Cases</span>
        </a>
        <a href="/opra/" class="fab__menu-item">
          <span>📋</span>
          <span>OPRA Records</span>
        </a>
        <a href="#top" class="fab__menu-item" data-action="scroll-top">
          <span>⬆️</span>
          <span>Back to Top</span>
        </a>
      </div>
    `;

    fab.addEventListener("click", (e) => {
      if (e.target.closest(".fab__menu-item")) return;
      fab.classList.toggle("active");
      fab.setAttribute("aria-expanded", fab.classList.contains("active"));
    });

    // Handle scroll to top
    fab
      .querySelector('[data-action="scroll-top"]')
      .addEventListener("click", (e) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
        fab.classList.remove("active");
      });

    // Close on outside click
    document.addEventListener("click", (e) => {
      if (!fab.contains(e.target)) {
        fab.classList.remove("active");
        fab.setAttribute("aria-expanded", "false");
      }
    });

    document.body.appendChild(fab);
  }

  // ============================================
  // Install Banner Component
  // ============================================
  function createInstallBanner() {
    const banner = document.createElement("div");
    banner.id = "install-banner";
    banner.className = "install-banner";
    banner.innerHTML = `
      <div class="install-banner__content">
        <div class="install-banner__icon">⚖️</div>
        <div class="install-banner__text">
          <div class="install-banner__title">Install Evident</div>
          <div class="install-banner__desc">Add to home screen for quick access</div>
        </div>
      </div>
      <div class="install-banner__actions">
        <button class="install-banner__btn install-banner__btn--secondary" data-action="dismiss">Not Now</button>
        <button class="install-banner__btn install-banner__btn--primary" data-action="install">Install</button>
      </div>
    `;

    banner
      .querySelector('[data-action="install"]')
      .addEventListener("click", installApp);
    banner
      .querySelector('[data-action="dismiss"]')
      .addEventListener("click", () => {
        hideInstallBanner();
        localStorage.setItem("pwa-install-dismissed", "true");
      });

    document.body.appendChild(banner);
  }

  // ============================================
  // Search & Filter Functionality
  // ============================================
  function initSearch() {
    const searchInput = document.querySelector(".search-bar");
    const searchClear = document.querySelector(".search-clear");
    const cards = document.querySelectorAll("[data-searchable]");

    if (!searchInput || cards.length === 0) return;

    searchInput.addEventListener(
      "input",
      debounce((e) => {
        const query = e.target.value.toLowerCase().trim();
        filterCards(cards, query);
      }, 200),
    );

    if (searchClear) {
      searchClear.addEventListener("click", () => {
        searchInput.value = "";
        filterCards(cards, "");
        searchInput.focus();
      });
    }
  }

  function filterCards(cards, query) {
    let visibleCount = 0;

    cards.forEach((card) => {
      const searchText =
        card.dataset.searchable?.toLowerCase() ||
        card.textContent.toLowerCase();
      const matches = !query || searchText.includes(query);

      card.style.display = matches ? "" : "none";
      if (matches) visibleCount++;
    });

    // Show empty state if no results
    updateEmptyState(visibleCount === 0 && query);
  }

  function updateEmptyState(show) {
    let emptyState = document.querySelector(".search-empty-state");

    if (show && !emptyState) {
      emptyState = document.createElement("div");
      emptyState.className = "empty-state search-empty-state";
      emptyState.innerHTML = `
        <div class="empty-state__icon">🔍</div>
        <h3 class="empty-state__title">No results found</h3>
        <p class="empty-state__desc">Try adjusting your search or filters</p>
      `;
      document.querySelector(".cases-grid, .opra-grid")?.after(emptyState);
    } else if (!show && emptyState) {
      emptyState.remove();
    }
  }

  // ============================================
  // Filter Pills
  // ============================================
  function initFilterPills() {
    const pills = document.querySelectorAll(".filter-pill");
    const cards = document.querySelectorAll("[data-status]");

    if (pills.length === 0 || cards.length === 0) return;

    pills.forEach((pill) => {
      pill.addEventListener("click", () => {
        // Update active state
        pills.forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");

        // Filter cards
        const status = pill.dataset.filter;
        cards.forEach((card) => {
          const matches = status === "all" || card.dataset.status === status;
          card.style.display = matches ? "" : "none";
        });
      });
    });
  }

  // ============================================
  // Staggered Animations
  // ============================================
  function animateOnScroll() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry, index) => {
          if (entry.isIntersecting) {
            entry.target.style.animationDelay = `${index * 0.05}s`;
            entry.target.classList.add("stagger-item");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 },
    );

    document.querySelectorAll(".case-card, .opra-card").forEach((el) => {
      observer.observe(el);
    });
  }

  // ============================================
  // Pull to Refresh (simulated)
  // ============================================
  function initPullToRefresh() {
    if (!("ontouchstart" in window)) return;

    let startY = 0;
    let pulling = false;

    const indicator = document.createElement("div");
    indicator.className = "pull-indicator";
    indicator.innerHTML = '<div class="pull-indicator__spinner"></div>';
    document.body.appendChild(indicator);

    document.addEventListener(
      "touchstart",
      (e) => {
        if (window.scrollY === 0) {
          startY = e.touches[0].clientY;
          pulling = true;
        }
      },
      { passive: true },
    );

    document.addEventListener(
      "touchmove",
      (e) => {
        if (!pulling) return;

        const y = e.touches[0].clientY;
        const diff = y - startY;

        if (diff > 60 && window.scrollY === 0) {
          indicator.classList.add("visible");
        }
      },
      { passive: true },
    );

    document.addEventListener("touchend", () => {
      if (indicator.classList.contains("visible")) {
        // Trigger refresh
        setTimeout(() => {
          window.location.reload();
        }, 500);
      }
      pulling = false;
    });
  }

  // ============================================
  // Theme Toggle (Future Feature)
  // ============================================
  function initThemeToggle() {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.dataset.theme = savedTheme;
  }

  // ============================================
  // Utility Functions
  // ============================================
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ============================================
  // Offline Detection
  // ============================================
  function initOfflineDetection() {
    window.addEventListener("online", () => {
      showToast("Back online! ✓", "success");
    });

    window.addEventListener("offline", () => {
      showToast("You're offline. Some features may be limited.", "warning");
    });
  }

  // ============================================
  // Page Visibility API
  // ============================================
  function initVisibilityHandler() {
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        // Could refresh data here when app becomes visible
        if (CONFIG.DEBUG) {
          console.log("[App] Page became visible");
        }
      }
    });
  }

  // ============================================
  // Keyboard Shortcuts
  // ============================================
  function initKeyboardShortcuts() {
    const shortcuts = {
      "g h": () => (window.location.href = "/"), // Go Home
      "g c": () => (window.location.href = "/cases/"), // Go Cases
      "g o": () => (window.location.href = "/opra/"), // Go OPRA
      "g e": () => (window.location.href = "/essays/"), // Go Essays
      "/": () => document.querySelector(".search-bar")?.focus(), // Focus search
      Escape: () => {
        document.querySelector(".search-bar")?.blur();
        document.querySelector(".fab")?.classList.remove("active");
        document.querySelector(".bottom-sheet")?.classList.remove("active");
        document.querySelector(".modal-overlay")?.classList.remove("active");
      },
      "?": () => showShortcutsModal(), // Show shortcuts
      t: () => window.scrollTo({ top: 0, behavior: "smooth" }), // Top
    };

    let keySequence = "";
    let keyTimer;

    document.addEventListener("keydown", (e) => {
      // Don't trigger in input fields
      if (e.target.matches("input, textarea, select, [contenteditable]")) {
        if (e.key === "Escape") {
          e.target.blur();
        }
        return;
      }

      // Handle Escape directly
      if (e.key === "Escape") {
        shortcuts["Escape"]();
        return;
      }

      // Handle single-key shortcuts
      if (e.key === "/" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        shortcuts["/"]();
        return;
      }

      if (e.key === "?" && e.shiftKey) {
        e.preventDefault();
        shortcuts["?"]();
        return;
      }

      if (e.key === "t" && !e.ctrlKey && !e.metaKey) {
        shortcuts["t"]();
        return;
      }

      // Handle key sequences (like 'g h')
      clearTimeout(keyTimer);
      keySequence += e.key + " ";
      keySequence = keySequence.slice(-4); // Keep last 4 chars

      const matchedShortcut = Object.keys(shortcuts).find(
        (s) => keySequence.trim() === s,
      );

      if (matchedShortcut) {
        e.preventDefault();
        shortcuts[matchedShortcut]();
        keySequence = "";
      }

      keyTimer = setTimeout(() => (keySequence = ""), 500);
    });
  }

  function showShortcutsModal() {
    let modal = document.querySelector(".shortcuts-modal");

    if (!modal) {
      modal = document.createElement("div");
      modal.className = "shortcuts-modal";
      modal.innerHTML = `
        <div class="shortcuts-modal__content">
          <div class="shortcuts-modal__header">
            <h2 class="shortcuts-modal__title">⌨️ Keyboard Shortcuts</h2>
            <button class="bottom-sheet__close" aria-label="Close">✕</button>
          </div>
          
          <div class="shortcut-group">
            <h3 class="shortcut-group__title">Navigation</h3>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Go to Home</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">g</span>
                <span class="shortcut-key">h</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Go to Cases</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">g</span>
                <span class="shortcut-key">c</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Go to OPRA</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">g</span>
                <span class="shortcut-key">o</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Go to Essays</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">g</span>
                <span class="shortcut-key">e</span>
              </div>
            </div>
          </div>
          
          <div class="shortcut-group">
            <h3 class="shortcut-group__title">Actions</h3>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Focus Search</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">/</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Scroll to Top</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">t</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Close / Cancel</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">Esc</span>
              </div>
            </div>
            <div class="shortcut-item">
              <span class="shortcut-item__desc">Show Shortcuts</span>
              <div class="shortcut-item__keys">
                <span class="shortcut-key">?</span>
              </div>
            </div>
          </div>
        </div>
      `;

      modal
        .querySelector(".bottom-sheet__close")
        .addEventListener("click", () => {
          modal.classList.remove("open");
        });

      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          modal.classList.remove("open");
        }
      });

      document.body.appendChild(modal);
    }

    modal.classList.add("open");
  }

  // ============================================
  // Swipe Gestures (Mobile)
  // ============================================
  function initSwipeGestures() {
    if (!("ontouchstart" in window)) return;

    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    document.addEventListener(
      "touchstart",
      (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
      },
      { passive: true },
    );

    document.addEventListener(
      "touchend",
      (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
      },
      { passive: true },
    );

    function handleSwipe() {
      const deltaX = touchEndX - touchStartX;
      const deltaY = touchEndY - touchStartY;
      const minSwipeDistance = 100;

      // Horizontal swipe
      if (
        Math.abs(deltaX) > Math.abs(deltaY) &&
        Math.abs(deltaX) > minSwipeDistance
      ) {
        if (deltaX > 0) {
          // Swipe right - go back
          if (window.history.length > 1) {
            // Could trigger back navigation
          }
        } else {
          // Swipe left - could open menu
        }
      }
    }
  }

  // ============================================
  // Initialize App
  // ============================================
  function init() {
    // Core features
    registerServiceWorker();
    setupInstallPrompt();
    createBottomNav();
    createFAB();
    createInstallBanner();

    // Interactive features
    initSearch();
    initFilterPills();
    animateOnScroll();
    initPullToRefresh();
    initThemeToggle();
    initKeyboardShortcuts();
    initSwipeGestures();

    // System features
    initOfflineDetection();
    initVisibilityHandler();

    // Add page transition class
    document.body.classList.add("page-enter");

    if (CONFIG.DEBUG) {
      console.log(`[${CONFIG.APP_NAME}] v${CONFIG.VERSION} initialized`);
    }
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose API for external use
  window.EvidentApp = {
    showToast,
    installApp,
    showShortcutsModal,
    VERSION: CONFIG.VERSION,
  };
})();
