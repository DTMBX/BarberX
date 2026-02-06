// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Evident Mobile Bottom Navigation
 * =================================
 * Touch-friendly navigation for mobile PWA experience
 * Includes haptic feedback, gesture support, and install prompts
 */

class EvidentMobileNav {
  constructor(options = {}) {
    this.options = {
      container: options.container || document.body,
      activeClass: "nav-active",
      hapticFeedback: options.hapticFeedback !== false,
      showInstallPrompt: options.showInstallPrompt !== false,
      ...options,
    };

    this.deferredPrompt = null;
    this.isStandalone = window.matchMedia("(display-mode: standalone)").matches;

    this.init();
  }

  init() {
    this.createNavigation();
    this.bindEvents();
    this.checkInstallPrompt();
    this.setupGestures();
  }

  createNavigation() {
    // Only show on mobile
    if (window.innerWidth > 768) return;

    const nav = document.createElement("nav");
    nav.className = "evident-mobile-nav";
    nav.innerHTML = `
      <div class="mobile-nav-items">
        <a href="/workspace" class="mobile-nav-item" data-nav="workspace">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="9"/>
            <rect x="14" y="3" width="7" height="5"/>
            <rect x="14" y="12" width="7" height="9"/>
            <rect x="3" y="16" width="7" height="5"/>
          </svg>
          <span>Workspace</span>
        </a>
        
        <a href="/cases" class="mobile-nav-item" data-nav="cases">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>Cases</span>
        </a>
        
        <button class="mobile-nav-item mobile-nav-fab" data-nav="upload" aria-label="Upload Document">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </button>
        
        <a href="/chat" class="mobile-nav-item" data-nav="chat">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span>AI Chat</span>
          <span class="nav-badge" id="chatBadge" style="display:none">1</span>
        </a>
        
        <button class="mobile-nav-item" data-nav="menu" aria-label="Menu">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
          <span>More</span>
        </button>
      </div>
      
      <div class="mobile-nav-menu" id="mobileNavMenu">
        <div class="mobile-nav-menu-header">
          <span class="brand">Barber<span class="x">X</span></span>
          <button class="close-menu" aria-label="Close menu">&times;</button>
        </div>
        <div class="mobile-nav-menu-items">
          <a href="/settings" class="menu-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            Settings
          </a>
          <a href="/subscription" class="menu-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            Subscription
          </a>
          <a href="/help" class="menu-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Help & Support
          </a>
          <button class="menu-item install-btn" id="installBtn" style="display:none">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Install App
          </button>
          <a href="/auth/logout" class="menu-item menu-item-danger">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sign Out
          </a>
        </div>
      </div>
      
      <div class="mobile-nav-overlay" id="mobileNavOverlay"></div>
    `;

    this.injectStyles();
    this.options.container.appendChild(nav);
    this.nav = nav;
    this.highlightCurrentPage();
  }

  injectStyles() {
    if (document.getElementById("evident-mobile-nav-styles")) return;

    const styles = document.createElement("style");
    styles.id = "evident-mobile-nav-styles";
    styles.textContent = `
      .Evident-mobile-nav {
        display: none;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
      }
      
      @media (max-width: 768px) {
        .Evident-mobile-nav {
          display: block;
        }
        
        body {
          padding-bottom: calc(70px + env(safe-area-inset-bottom, 0px));
        }
      }
      
      .mobile-nav-items {
        display: flex;
        align-items: center;
        justify-content: space-around;
        background: linear-gradient(to top, #0a2540, #16213e);
        border-top: 1px solid rgba(255,255,255,0.1);
        padding: 8px 4px;
        padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
      }
      
      .mobile-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        padding: 8px 12px;
        color: rgba(255,255,255,0.6);
        text-decoration: none;
        font-size: 11px;
        font-weight: 500;
        border: none;
        background: none;
        cursor: pointer;
        transition: all 0.2s;
        position: relative;
        -webkit-tap-highlight-color: transparent;
      }
      
      .mobile-nav-item:active {
        transform: scale(0.95);
      }
      
      .mobile-nav-item.nav-active {
        color: #c41e3a;
      }
      
      .mobile-nav-item .nav-icon {
        width: 24px;
        height: 24px;
      }
      
      .mobile-nav-fab {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #c41e3a, #d4af37);
        border-radius: 50%;
        margin-top: -28px;
        box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4);
        color: white !important;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .mobile-nav-fab .nav-icon {
        width: 28px;
        height: 28px;
      }
      
      .mobile-nav-fab:active {
        transform: scale(0.9);
        box-shadow: 0 2px 8px rgba(196, 30, 58, 0.3);
      }
      
      .nav-badge {
        position: absolute;
        top: 2px;
        right: 6px;
        background: #c41e3a;
        color: white;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 10px;
        min-width: 18px;
        text-align: center;
      }
      
      /* Menu overlay */
      .mobile-nav-overlay {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9998;
        opacity: 0;
        transition: opacity 0.3s;
      }
      
      .mobile-nav-overlay.active {
        display: block;
        opacity: 1;
      }
      
      /* Slide-up menu */
      .mobile-nav-menu {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #0a2540;
        border-radius: 20px 20px 0 0;
        transform: translateY(100%);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 10000;
        max-height: 70vh;
        overflow-y: auto;
        padding-bottom: env(safe-area-inset-bottom, 0px);
      }
      
      .mobile-nav-menu.active {
        transform: translateY(0);
      }
      
      .mobile-nav-menu-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      
      .mobile-nav-menu-header .brand {
        font-size: 20px;
        font-weight: 700;
        color: white;
      }
      
      .mobile-nav-menu-header .brand .x {
        color: #c41e3a;
      }
      
      .mobile-nav-menu-header .close-menu {
        background: none;
        border: none;
        color: rgba(255,255,255,0.6);
        font-size: 28px;
        cursor: pointer;
        padding: 4px 8px;
      }
      
      .mobile-nav-menu-items {
        padding: 12px 0;
      }
      
      .menu-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px 20px;
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        font-size: 16px;
        border: none;
        background: none;
        width: 100%;
        cursor: pointer;
        transition: background 0.2s;
      }
      
      .menu-item:hover,
      .menu-item:active {
        background: rgba(255,255,255,0.05);
      }
      
      .menu-item svg {
        width: 22px;
        height: 22px;
        opacity: 0.7;
      }
      
      .menu-item-danger {
        color: #ef4444;
      }
      
      .install-btn {
        background: rgba(196, 30, 58, 0.1);
        margin: 8px 16px;
        border-radius: 8px;
        color: #c41e3a;
      }
      
      /* Gesture indicator */
      .gesture-indicator {
        width: 40px;
        height: 4px;
        background: rgba(255,255,255,0.3);
        border-radius: 2px;
        margin: 8px auto;
      }
    `;

    document.head.appendChild(styles);
  }

  bindEvents() {
    if (!this.nav) return;

    // Navigation item clicks
    this.nav.querySelectorAll(".mobile-nav-item").forEach((item) => {
      item.addEventListener("click", (e) => this.handleNavClick(e, item));
    });

    // Menu close button
    const closeBtn = this.nav.querySelector(".close-menu");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.closeMenu());
    }

    // Overlay click to close
    const overlay = document.getElementById("mobileNavOverlay");
    if (overlay) {
      overlay.addEventListener("click", () => this.closeMenu());
    }

    // Install button
    const installBtn = document.getElementById("installBtn");
    if (installBtn) {
      installBtn.addEventListener("click", () => this.promptInstall());
    }

    // Resize handler
    window.addEventListener("resize", () => {
      if (window.innerWidth > 768) {
        this.closeMenu();
      }
    });
  }

  handleNavClick(e, item) {
    const navType = item.dataset.nav;

    // Haptic feedback
    if (this.options.hapticFeedback && navigator.vibrate) {
      navigator.vibrate(10);
    }

    switch (navType) {
      case "menu":
        e.preventDefault();
        this.toggleMenu();
        break;

      case "upload":
        e.preventDefault();
        this.triggerUpload();
        break;

      default:
        // Let link navigate normally
        break;
    }
  }

  toggleMenu() {
    const menu = document.getElementById("mobileNavMenu");
    const overlay = document.getElementById("mobileNavOverlay");

    if (menu && overlay) {
      menu.classList.toggle("active");
      overlay.classList.toggle("active");

      // Prevent body scroll when menu is open
      document.body.style.overflow = menu.classList.contains("active")
        ? "hidden"
        : "";
    }
  }

  closeMenu() {
    const menu = document.getElementById("mobileNavMenu");
    const overlay = document.getElementById("mobileNavOverlay");

    if (menu && overlay) {
      menu.classList.remove("active");
      overlay.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  triggerUpload() {
    // Check if there's already an upload input
    let input = document.getElementById("mobileUploadInput");
    if (!input) {
      input = document.createElement("input");
      input.type = "file";
      input.id = "mobileUploadInput";
      input.accept = ".pdf,.doc,.docx,.txt,application/pdf,application/msword";
      input.multiple = true;
      input.style.display = "none";
      document.body.appendChild(input);

      input.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
          // Navigate to workspace with files
          window.location.href = "/workspace?action=upload";
          // Store files in sessionStorage for the workspace to pick up
          // (actual implementation would handle file upload)
        }
      });
    }

    input.click();
  }

  highlightCurrentPage() {
    if (!this.nav) return;

    const path = window.location.pathname;

    this.nav.querySelectorAll(".mobile-nav-item[href]").forEach((item) => {
      const href = item.getAttribute("href");
      if (href && path.startsWith(href)) {
        item.classList.add("nav-active");
      } else {
        item.classList.remove("nav-active");
      }
    });
  }

  checkInstallPrompt() {
    if (this.isStandalone) return;

    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      this.deferredPrompt = e;

      // Show install button
      const installBtn = document.getElementById("installBtn");
      if (installBtn) {
        installBtn.style.display = "flex";
      }
    });

    window.addEventListener("appinstalled", () => {
      this.deferredPrompt = null;
      const installBtn = document.getElementById("installBtn");
      if (installBtn) {
        installBtn.style.display = "none";
      }
    });
  }

  async promptInstall() {
    if (!this.deferredPrompt) return;

    this.deferredPrompt.prompt();
    const { outcome } = await this.deferredPrompt.userChoice;

    if (outcome === "accepted") {
      console.log("[Evident] PWA installed");
    }

    this.deferredPrompt = null;
    this.closeMenu();
  }

  setupGestures() {
    if (!this.nav) return;

    let touchStartY = 0;
    let touchEndY = 0;

    const menu = document.getElementById("mobileNavMenu");
    if (!menu) return;

    menu.addEventListener(
      "touchstart",
      (e) => {
        touchStartY = e.touches[0].clientY;
      },
      { passive: true },
    );

    menu.addEventListener(
      "touchmove",
      (e) => {
        touchEndY = e.touches[0].clientY;
      },
      { passive: true },
    );

    menu.addEventListener("touchend", () => {
      const swipeDistance = touchEndY - touchStartY;

      // Swipe down to close
      if (swipeDistance > 100) {
        this.closeMenu();
      }
    });
  }

  // Public API
  updateBadge(navItem, count) {
    const badge = this.nav?.querySelector(`[data-nav="${navItem}"] .nav-badge`);
    if (badge) {
      if (count > 0) {
        badge.textContent = count > 99 ? "99+" : count;
        badge.style.display = "block";
      } else {
        badge.style.display = "none";
      }
    }
  }

  destroy() {
    if (this.nav) {
      this.nav.remove();
    }
  }
}

// Auto-initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.EvidentMobileNav = new EvidentMobileNav();
});

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = EvidentMobileNav;
}
