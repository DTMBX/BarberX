// Navigation component logic (locked behavior)
(function () {
  "use strict";

  function getFocusableInNav(nav) {
    return nav.querySelectorAll(
      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
  }

  function initNav() {
    var toggle = document.querySelector(".premium-nav-toggle");
    var nav = document.getElementById("premium-nav-mobile");

    if (!toggle || !nav || nav.dataset.ffNavReady === "1") {
      return;
    }

    nav.dataset.ffNavReady = "1";

    var backdrop = document.querySelector(".premium-nav-overlay");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "premium-nav-overlay";
      document.body.appendChild(backdrop);
    }

    toggle.setAttribute("aria-expanded", "false");

    var keydownHandler = null;

    function openNav() {
      if (nav.classList.contains("is-open")) return;
      nav.classList.add("is-open");
      toggle.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      backdrop.classList.add("is-visible");
      document.body.style.overflow = "hidden";

      var focusable = getFocusableInNav(nav);
      if (focusable && focusable.length) {
        try {
          focusable[0].focus({ preventScroll: true });
        } catch (_err) {
          focusable[0].focus();
        }
      }

      if (!keydownHandler) {
        keydownHandler = function (e) {
          if (e.key === "Escape") {
            closeNav(true);
            return;
          }
          if (e.key !== "Tab") return;
          var nodes = getFocusableInNav(nav);
          if (!nodes || !nodes.length) return;
          var first = nodes[0];
          var last = nodes[nodes.length - 1];
          var active = document.activeElement;
          if (e.shiftKey && active === first) {
            e.preventDefault();
            last.focus();
          } else if (!e.shiftKey && active === last) {
            e.preventDefault();
            first.focus();
          }
        };
      }
      window.addEventListener("keydown", keydownHandler);
    }

    function closeNav(restoreFocus) {
      if (!nav.classList.contains("is-open")) return;
      nav.classList.remove("is-open");
      toggle.classList.remove("is-open");
      backdrop.classList.remove("is-visible");
      toggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
      if (keydownHandler) window.removeEventListener("keydown", keydownHandler);
      if (restoreFocus) {
        try {
          toggle.focus({ preventScroll: true });
        } catch (_err) {
          toggle.focus();
        }
      }
    }

    toggle.addEventListener("click", function () {
      if (nav.classList.contains("is-open")) {
        closeNav(false);
      } else {
        openNav();
      }
    });

    backdrop.addEventListener("click", function () {
      closeNav(false);
    });

    nav.addEventListener("click", function (e) {
      var link = e.target.closest("a");
      if (!link) return;
      if (!nav.classList.contains("is-open")) return;
      closeNav(false);
    });

    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        if (window.innerWidth >= 768) {
          closeNav(false);
        }
      }, 250);
    });

    var closeBtn = document.querySelector(".premium-nav__close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        closeNav(true);
      });
    }
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    if (typeof window !== "undefined") {
      window.FFNav = window.FFNav || {};
      window.FFNav.initNav = initNav;
    }
    initNav();
  });
})();
