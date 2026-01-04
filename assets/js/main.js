// Respect prefers‑reduced‑motion – already handled in CSS,
// but we keep a small helper for any future interactive bits.

document.addEventListener('DOMContentLoaded', () => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReduced.matches) {
        console.log('User prefers reduced motion – additional JS animations disabled.');
        // Insert any extra cleanup here if you later add JS‑driven animations.
    }

    // Example: log CTA clicks (replace with real analytics if desired)
    const cta = document.querySelector('.hero-cta');
    if (cta) {
        cta.addEventListener('click', () => console.log('CTA clicked'));
    }
});