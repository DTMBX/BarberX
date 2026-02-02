/**
 * Evident Core JavaScript
 * Handles mobile navigation and UI interactions
 */

document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu toggle
  const menuToggle = document.querySelector(".mobile-menu-toggle");
  const mobileNav = document.querySelector(".mobile-nav");

  if (menuToggle && mobileNav) {
    menuToggle.addEventListener("click", function () {
      const isOpen = mobileNav.classList.toggle("is-open");
      menuToggle.setAttribute("aria-expanded", isOpen);

      // Animate hamburger
      const lines = menuToggle.querySelectorAll(".hamburger-line");
      if (isOpen) {
        lines[0].style.transform = "rotate(45deg) translate(5px, 5px)";
        lines[1].style.opacity = "0";
        lines[2].style.transform = "rotate(-45deg) translate(5px, -5px)";
      } else {
        lines[0].style.transform = "";
        lines[1].style.opacity = "";
        lines[2].style.transform = "";
      }
    });
  }

  // Close mobile menu on link click
  const mobileLinks = document.querySelectorAll(".mobile-nav-link");
  mobileLinks.forEach((link) => {
    link.addEventListener("click", function () {
      if (mobileNav) {
        mobileNav.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (targetId === "#") return;

      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const headerHeight =
          document.querySelector(".site-header")?.offsetHeight || 0;
        const targetPosition =
          target.getBoundingClientRect().top +
          window.pageYOffset -
          headerHeight -
          20;

        window.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        });
      }
    });
  });

  // Header scroll behavior
  const header = document.querySelector(".site-header");
  if (header) {
    let lastScroll = 0;

    window.addEventListener(
      "scroll",
      function () {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
          header.style.boxShadow = "var(--shadow-md)";
        } else {
          header.style.boxShadow = "";
        }

        lastScroll = currentScroll;
      },
      { passive: true },
    );
  }
});
