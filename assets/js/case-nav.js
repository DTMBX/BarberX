// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * CASE NAV ENHANCEMENT
 *
 * Provides quick-jump navigation within case pages
 * and smooth scroll behavior for docket sections.
 */

(function () {
  "use strict";

  // Feature detection
  if (!document.querySelector) return;

  /**
   * Initialize case page enhancements
   */
  function init() {
    setupSmoothScrolling();
    setupQuickJumpNav();
    setupDocketAnchors();
  }

  /**
   * Setup smooth scrolling for anchor links
   */
  function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const target = document.querySelector(this.getAttribute("href"));
        if (!target) return;

        e.preventDefault();
        const headerOffset = 100;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition =
          elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        });

        // Update URL without scrolling
        history.pushState(null, "", this.getAttribute("href"));
      });
    });
  }

  /**
   * Create quick-jump navigation for long case pages
   */
  function setupQuickJumpNav() {
    const caseRecord = document.querySelector(".case-record");
    if (!caseRecord) return;

    const sections = caseRecord.querySelectorAll(
      ".case-section[id], section[id]",
    );
    if (sections.length < 3) return; // Only show for pages with multiple sections

    const nav = document.createElement("nav");
    nav.className = "case-quick-nav";
    nav.setAttribute("aria-label", "Jump to section");

    const navInner = document.createElement("div");
    navInner.className = "case-quick-nav-inner";

    const label = document.createElement("span");
    label.className = "case-quick-nav-label";
    label.textContent = "Jump to:";
    navInner.appendChild(label);

    const list = document.createElement("ul");
    list.className = "case-quick-nav-list";

    sections.forEach((section) => {
      const heading = section.querySelector("h2, h3");
      if (!heading) return;

      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = "#" + section.id;
      link.className = "case-quick-nav-link";
      link.textContent = heading.textContent.trim();

      item.appendChild(link);
      list.appendChild(item);
    });

    navInner.appendChild(list);
    nav.appendChild(navInner);

    // Insert after case header
    const header = caseRecord.querySelector(".case-header, .case-caption");
    if (header && header.nextSibling) {
      header.parentNode.insertBefore(nav, header.nextSibling);
    }

    // Handle scroll to highlight current section
    let ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          updateActiveNavLink(nav, sections);
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  /**
   * Update active link based on scroll position
   */
  function updateActiveNavLink(nav, sections) {
    const scrollPos = window.scrollY + 150;

    let current = null;
    sections.forEach((section) => {
      if (section.offsetTop <= scrollPos) {
        current = section;
      }
    });

    nav.querySelectorAll(".case-quick-nav__link").forEach((link) => {
      link.classList.remove("is-active");
      if (current && link.getAttribute("href") === "#" + current.id) {
        link.classList.add("is-active");
      }
    });
  }

  /**
   * Add anchor links to docket entries for direct linking
   */
  function setupDocketAnchors() {
    document
      .querySelectorAll(".docket-card[data-id], .docket-entry[data-id]")
      .forEach((entry) => {
        const id = entry.dataset.id;
        if (!id) return;

        entry.id = "docket-" + id;

        // Check if navigated to via hash
        if (window.location.hash === "#docket-" + id) {
          entry.classList.add("is-highlighted");
          setTimeout(() => {
            entry.scrollIntoView({ behavior: "smooth", block: "center" });
          }, 100);
        }
      });
  }

  // Initialize on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
