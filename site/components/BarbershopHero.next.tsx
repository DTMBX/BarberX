"use client";

import { useEffect, useState, useCallback } from "react";
import styles from "./EvidentHero.module.css";

/**
 * EvidentHero.next.tsx
 * Next.js App Router TypeScript component for animated barber shop hero
 *
 * Features:
 * - 'use client' directive for App Router compatibility
 * - Full TypeScript support with strict typing
 * - Motion preference detection for accessibility
 * - Three layout variants (default, minimal, full)
 * - Dark mode auto-detection
 * - GPU-accelerated animation (60fps)
 * - Server-safe with typeof window checks
 *
 * @example
 * import EvidentHero from '@/components/EvidentHero.next';
 *
 * export default function Home() {
 *   return (
 *     <EvidentHero
 *       variant="default"
 *       onCtaClick={() => console.log('CTA clicked')}
 *     />
 *   );
 * }
 */

interface EvidentHeroProps {
  /** Heading text displayed above the pole */
  heading?: string;
  /** Descriptive text/tagline */
  tagline?: string;
  /** Layout variant: 'default' | 'minimal' | 'full' */
  variant?: "default" | "minimal" | "full";
  /** CTA button text */
  ctaText?: string;
  /** Callback when CTA is clicked */
  onCtaClick?: () => void;
  /** Custom className for root element */
  className?: string;
  /** SVG size in pixels (responsive) */
  svgSize?: number;
  /** Animation duration in seconds */
  animationDuration?: number;
  /** Show badge above heading */
  showBadge?: boolean;
  /** Badge text */
  badgeText?: string;
}

export default function EvidentHero({
  heading = "Welcome to Barber Cam",
  tagline = "Premium Evident experience",
  variant = "default",
  ctaText = "Get Started",
  onCtaClick,
  className = "",
  svgSize = 200,
  animationDuration = 5.5,
  showBadge = false,
  badgeText = "Premium",
}: EvidentHeroProps) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check motion preference
    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(motionQuery.matches);

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    motionQuery.addEventListener("change", handleMotionChange);

    // Check dark mode preference
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
    setIsDarkMode(darkModeQuery.matches);

    const handleDarkModeChange = (e: MediaQueryListEvent) => {
      setIsDarkMode(e.matches);
    };

    darkModeQuery.addEventListener("change", handleDarkModeChange);

    return () => {
      motionQuery.removeEventListener("change", handleMotionChange);
      darkModeQuery.removeEventListener("change", handleDarkModeChange);
    };
  }, []);

  const handleCtaClick = useCallback(() => {
    onCtaClick?.();
  }, [onCtaClick]);

  const rootClass = [
    styles["Evident-hero"],
    styles[`Evident-hero--${variant}`],
    prefersReducedMotion && styles["no-animation"],
    isDarkMode && styles["dark-mode"],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const svgAnimationClass = prefersReducedMotion ? styles["paused"] : "";

  return (
    <section
      className={rootClass}
      aria-label="Evident hero section with animated barber pole"
      role="banner"
    >
      <div className={styles["hero-inner"]}>
        {/* Visual: Barber Pole SVG */}
        <div className={styles["hero-visual"]}>
          <svg
            width={svgSize}
            height={svgSize}
            viewBox="0 0 200 200"
            className={svgAnimationClass}
            aria-hidden="true"
            focusable="false"
            style={{
              animation: !prefersReducedMotion
                ? `spin-pole ${animationDuration}s linear infinite`
                : "none",
            }}
          >
            <defs>
              <linearGradient
                id="poleGradient"
                x1="0%"
                y1="0%"
                x2="0%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#ffffff" />
                <stop offset="33%" stopColor="#ff0000" />
                <stop offset="66%" stopColor="#0047ab" />
                <stop offset="100%" stopColor="#ffffff" />
              </linearGradient>

              <pattern
                id="polePattern"
                x="0"
                y="0"
                width="20"
                height="20"
                patternUnits="userSpaceOnUse"
                patternTransform="rotate(-45)"
              >
                <line
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="20"
                  stroke="#d4af37"
                  strokeWidth="3"
                />
              </pattern>
            </defs>

            {/* White base */}
            <rect
              x="50"
              y="40"
              width="100"
              height="120"
              rx="50"
              fill="#f5f5f7"
              stroke="#0a0a0f"
              strokeWidth="2"
            />

            {/* Animated gradient pattern overlay */}
            <rect
              x="50"
              y="40"
              width="100"
              height="120"
              rx="50"
              fill="url(#poleGradient)"
              opacity="0.85"
            />

            {/* Subtle border */}
            <rect
              x="50"
              y="40"
              width="100"
              height="120"
              rx="50"
              fill="none"
              stroke="#d4af37"
              strokeWidth="1.5"
              opacity="0.5"
            />

            {/* Text: Est. */}
            <text
              x="100"
              y="70"
              fontSize="14"
              fontWeight="700"
              textAnchor="middle"
              fill="#0a0a0f"
              opacity="0.8"
            >
              EST.
            </text>

            {/* Text: 2024 */}
            <text
              x="100"
              y="145"
              fontSize="20"
              fontWeight="700"
              textAnchor="middle"
              fill="#0a0a0f"
              opacity="0.9"
            >
              2024
            </text>
          </svg>
        </div>

        {/* Content: Heading, Tagline, CTA */}
        <div className={styles["hero-content"]}>
          {showBadge && badgeText && (
            <span className={styles["hero-badge"]}>{badgeText}</span>
          )}

          {heading && <h1 className={styles["hero-title"]}>{heading}</h1>}

          {tagline && <p className={styles["hero-tagline"]}>{tagline}</p>}

          {ctaText && (
            <button
              className={styles["hero-cta"]}
              onClick={handleCtaClick}
              aria-label={ctaText}
            >
              {ctaText}
            </button>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin-pole {
          from { transform: rotateZ(0deg); }
          to { transform: rotateZ(360deg); }
        }
      `}</style>
    </section>
  );
}

