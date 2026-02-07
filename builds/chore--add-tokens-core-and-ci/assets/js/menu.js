// Lightweight menu + dropdown keyboard accessibility
document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav toggle
  const mobileToggle = document.getElementById("mobile-nav-toggle");
  const primaryNav = document.getElementById("primary-nav");
  if (mobileToggle && primaryNav) {
    mobileToggle.addEventListener("click", function () {
      const expanded = this.getAttribute("aria-expanded") === "true";
      this.setAttribute("aria-expanded", String(!expanded));
      primaryNav.classList.toggle("hidden");
    });
  }

  // Dropdowns
  document.querySelectorAll("[data-dropdown-button]").forEach((button) => {
    const parent = button.closest("[data-nav-item]");
    const menu = parent && parent.querySelector("[data-dropdown]");
    if (!menu) return;

    button.addEventListener("click", (e) => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      menu.classList.toggle("hidden");
    });

    // close on Escape
    button.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        menu.classList.add("hidden");
        button.setAttribute("aria-expanded", "false");
        button.focus();
      }
    });
  });
});
