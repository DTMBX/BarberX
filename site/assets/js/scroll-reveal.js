/**
 * Evident Scroll Reveal Animation System
 * Smooth, performance-optimized scroll-triggered animations
 */

class ScrollReveal {
  constructor(options = {}) {
    this.options = {
      threshold: 0.15,
      rootMargin: "0px 0px -100px 0px",
      animationClass: "reveal",
      ...options,
    };

    this.observer = null;
    this.init();
  }

  init() {
    // Check for IntersectionObserver support
    if (!("IntersectionObserver" in window)) {
      this.fallback();
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => this.handleIntersect(entries),
      {
        threshold: this.options.threshold,
        rootMargin: this.options.rootMargin,
      },
    );

    this.observeElements();
  }

  observeElements() {
    const elements = document.querySelectorAll(".reveal, [data-reveal]");
    elements.forEach((el) => {
      el.classList.add("reveal-hidden");
      this.observer.observe(el);
    });
  }

  handleIntersect(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("reveal-visible");
        entry.target.classList.remove("reveal-hidden");

        // Unobserve after revealing (one-time animation)
        this.observer.unobserve(entry.target);
      }
    });
  }

  fallback() {
    // For browsers without IntersectionObserver, show all elements
    const elements = document.querySelectorAll(".reveal, [data-reveal]");
    elements.forEach((el) => el.classList.add("reveal-visible"));
  }
}

// Auto-initialize on DOMContentLoaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => new ScrollReveal());
} else {
  new ScrollReveal();
}
