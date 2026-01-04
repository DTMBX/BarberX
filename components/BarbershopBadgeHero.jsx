import React, { useEffect, useState } from 'react';
import styles from './BarbershopBadgeHero.module.css';

/**
 * BarbershopBadgeHero - React Component
 * 
 * A mobile-first animated barbershop badge hero component with:
 * - Responsive design (360px+)
 * - Subtle spinning barber pole animation
 * - Dark mode support via CSS variables
 * - Accessibility features (ARIA, semantic HTML, prefers-reduced-motion)
 * - Touch-friendly interactions
 * 
 * @param {Object} props - Component props
 * @param {string} props.heading - Main heading (default: "Citizen Accountability")
 * @param {string} props.description - Description text (default: provided)
 * @param {string} props.year - EST year (default: "2024")
 * @param {string} props.tagline - Badge tagline (default: "A CUT ABOVE")
 * @param {Function} props.onCtaClick - CTA button click handler
 * @param {string} props.className - Additional CSS classes
 * 
 * @example
 * <BarbershopBadgeHero 
 *   heading="Welcome to Barber Cam"
 *   onCtaClick={() => alert('CTA clicked!')}
 * />
 */
export const BarbershopBadgeHero = ({
  heading = 'Citizen Accountability',
  description = 'Precision. Patience. Virtue. Honor. A citizen-led accountability platform built on transparency and due process.',
  year = '2024',
  tagline = 'A CUT ABOVE',
  onCtaClick,
  className = '',
}) => {
  // State to track motion preference
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // Detect motion preference on mount and listen for changes
  useEffect(() => {
    // Check initial preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    // Listen for changes
    const handleChange = (e) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  const handleCtaClick = () => {
    if (onCtaClick) {
      onCtaClick();
    } else {
      // Default behavior: log to console
      console.log('CTA clicked');
    }
  };

  return (
    <section
      className={`${styles.barbershopHero} ${className}`}
      aria-labelledby="hero-heading"
    >
      <div className={styles.badgeContainer}>
        
        {/* Barbershop Badge with Spinning Pole */}
        <div
          className={styles.barbershopBadge}
          role="img"
          aria-label="Barber Cam badge: Animated barbershop pole"
        >
          {/* Badge background circle */}
          <div className={styles.badgeBg}></div>

          {/* SVG Barber Pole (spinning element) */}
          <svg
            className={`${styles.barberPole} ${prefersReducedMotion ? styles.noAnimation : ''}`}
            viewBox="0 0 60 140"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
            focusable="false"
          >
            <defs>
              {/* Vertical color gradient for pole */}
              <linearGradient
                id="poleGradient"
                x1="0%"
                y1="0%"
                x2="0%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#ffffff" />
                <stop offset="25%" stopColor="#c41e3a" />
                <stop offset="50%" stopColor="#ffffff" />
                <stop offset="75%" stopColor="#1e40af" />
                <stop offset="100%" stopColor="#ffffff" />
              </linearGradient>

              {/* Spiral pattern for animation effect */}
              <pattern
                id="spiralPattern"
                patternUnits="userSpaceOnUse"
                width="60"
                height="140"
              >
                <rect width="60" height="140" fill="url(#poleGradient)" />
                <line
                  x1="0"
                  y1="0"
                  x2="60"
                  y2="140"
                  stroke="#c41e3a"
                  strokeWidth="6"
                  opacity="0.7"
                />
                <line
                  x1="0"
                  y1="30"
                  x2="60"
                  y2="170"
                  stroke="#1e40af"
                  strokeWidth="6"
                  opacity="0.7"
                />
              </pattern>
            </defs>

            {/* White pole base */}
            <rect
              x="10"
              y="10"
              width="40"
              height="120"
              rx="8"
              fill="#ffffff"
              stroke="none"
            />

            {/* Animated spiral overlay */}
            <rect
              x="10"
              y="10"
              width="40"
              height="120"
              rx="8"
              fill="url(#spiralPattern)"
              opacity="1"
            />

            {/* Subtle border */}
            <rect
              x="10"
              y="10"
              width="40"
              height="120"
              rx="8"
              fill="none"
              stroke="rgba(0,0,0,0.1)"
              strokeWidth="1"
            />
          </svg>

          {/* Badge text overlay */}
          <div className={styles.badgeText}>
            <span className={styles.badgeYear}>EST. {year}</span>
            <span className={styles.badgeTagline}>{tagline}</span>
          </div>
        </div>

        {/* Hero content section */}
        <div className={styles.heroContent} id="main">
          <h1 className={styles.heroHeading} id="hero-heading">
            {heading}
          </h1>
          <p className={styles.heroDescription}>{description}</p>
          <button
            className={styles.heroCta}
            onClick={handleCtaClick}
            aria-label="Explore now - navigate to next section"
          >
            Explore Now
          </button>
        </div>

      </div>
    </section>
  );
};

export default BarbershopBadgeHero;
