// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

(() => {
  const header = document.querySelector("[data-header]");
  if (!header) return;

  const toggle = header.querySelector("[data-nav-toggle]");
  const nav = document.getElementById("premium-nav-mobile");
  const overlay = document.querySelector("[data-nav-overlay]");
  if (!toggle || !nav || !overlay) return;

  function setOpen(open) {
    header.classList.toggle("nav-open", open);
    nav.setAttribute("aria-hidden", open ? "false" : "true");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    overlay.classList.toggle("is-active", open);
    document.body.classList.toggle("no-scroll", open);
    if (open) {
      nav.focus();
    }
  }

  toggle.addEventListener("click", () => {
    setOpen(!header.classList.contains("nav-open"));
  });

  overlay.addEventListener("click", () => setOpen(false));

  nav.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setOpen(false);
  });

  nav.querySelectorAll("a,button").forEach((el) => {
    el.addEventListener("click", () => {
      if (window.innerWidth < 1024) setOpen(false);
    });
  });

  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle("is-scrolled", y > 8);
    if (header.classList.contains("nav-open")) {
      header.classList.remove("is-hidden");
      lastY = y;
      return;
    }
    const goingDown = y > lastY;
    const past = y > 140;
    header.classList.toggle("is-hidden", goingDown && past);
    lastY = y;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
