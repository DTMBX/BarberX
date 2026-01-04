/**
 * BarbershopHero - Premium React Component
 * Mobile-first, performance-optimized barber pole animation
 * 
 * Features:
 * - GPU-accelerated CSS animation (5.5s cycle)
 * - Responsive mobile-first design
 * - WCAG AA accessibility
 * - Respects prefers-reduced-motion
 * - Zero external dependencies (pure React + CSS)
 */

import React, { useEffect, useRef } from 'react';
import './BarbershopHero.css';

/**
 * BarbershopHero Component
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Main heading
 * @param {string} props.subtitle - Secondary heading
 * @param {string} props.year - EST year (default: '2024')
 * @param {string} props.tagline - Brand tagline (default: 'A CUT ABOVE')
 * @param {string} props.variant - Layout variant: 'default' | 'minimal' | 'full'
 * @param {boolean} props.showAnimation - Enable/disable animation (default: true)
 * @param {Function} props.onAnimationToggle - Callback for motion preference changes
 * @param {React.ReactNode} props.children - Custom content below pole
 * @param {string} props.className - Additional CSS classes
 */
const BarbershopHero = ({
  title = 'Professional Barbershop',
  subtitle = 'Precision. Patience. Virtue. Honor.',
  year = '2024',
  tagline = 'A CUT ABOVE',
  variant = 'default',
  showAnimation = true,
  onAnimationToggle,
  children,
  className = '',
}) => {
  const poleRef = useRef(null);
  const containerRef = useRef(null);

  /**
   * Handle system motion preference changes
   * Respects user accessibility settings
   */
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleMotionPreference = (e) => {
      const shouldReduceMotion = e.matches;
      if (onAnimationToggle) {
        onAnimationToggle(!shouldReduceMotion);
      }
      
      // Update aria-label for accessibility
      if (containerRef.current) {
        containerRef.current.setAttribute(
          'aria-label',
          shouldReduceMotion ? 'Barber pole (animation disabled)' : 'Barber pole with spinning animation'
        );
      }
    };

    mediaQuery.addEventListener('change', handleMotionPreference);
    
    // Check initial preference
    handleMotionPreference(mediaQuery);

    return () => mediaQuery.removeEventListener('change', handleMotionPreference);
  }, [onAnimationToggle]);

  /**
   * Render barber pole SVG
   * Uses inline SVG for performance (no HTTP request)
   */
  const renderBarberPole = () => (
    <svg
      ref={poleRef}
      className="barber-pole-svg"
      viewBox="0 0 80 200"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Spinning barber pole"
    >
      <defs>
        <linearGradient
          id="poleGradient"
          x1="0%"
          y1="0%"
          x2="0%"
          y2="100%"
        >
          <stop offset="0%" stopColor="#fff" stopOpacity="1" />
          <stop offset="25%" stopColor="#c41e3a" stopOpacity="1" />
          <stop offset="50%" stopColor="#fff" stopOpacity="1" />
          <stop offset="75%" stopColor="#1e40af" stopOpacity="1" />
          <stop offset="100%" stopColor="#fff" stopOpacity="1" />
        </linearGradient>
        <pattern
          id="spiralPattern"
          patternUnits="userSpaceOnUse"
          width="80"
          height="200"
          patternTransform="rotate(0)"
        >
          <rect width="80" height="200" fill="url(#poleGradient)" />
          <line
            x1="0"
            y1="0"
            x2="80"
            y2="200"
            stroke="#c41e3a"
            strokeWidth="8"
            opacity="0.8"
          />
          <line
            x1="0"
            y1="40"
            x2="80"
            y2="240"
            stroke="#1e40af"
            strokeWidth="8"
            opacity="0.8"
          />
        </pattern>
      </defs>
      {/* Base white pole */}
      <rect
        rx="20"
        ry="20"
        width="80"
        height="200"
        fill="#fff"
        stroke="none"
      />
      {/* Animated spiral pattern */}
      <rect
        className={`pole-spin ${showAnimation ? 'animate' : 'static'}`}
        rx="20"
        ry="20"
        width="80"
        height="200"
        fill="url(#spiralPattern)"
        opacity="1"
      />
      {/* Subtle edge definition */}
      <rect
        rx="20"
        ry="20"
        width="80"
        height="200"
        fill="none"
        stroke="rgba(0,0,0,0.05)"
        strokeWidth="1"
      />
    </svg>
  );

  /**
   * Render visual content (pole + text)
   */
  const renderVisualContent = () => (
    <div className="visual-content">
      <div className="barber-pole-container">
        {renderBarberPole()}
      </div>
      <div className="visual-text">
        <span className="est">EST. {year}</span>
        <h2 className="tagline">{tagline}</h2>
      </div>
      {children && <div className="hero-custom-content">{children}</div>}
    </div>
  );

  /**
   * Default layout: text + visual side by side (desktop) or stacked (mobile)
   */
  if (variant === 'default') {
    return (
      <section
        ref={containerRef}
        className={`hero hero-default ${className}`}
        aria-label="Premium barbershop hero section"
      >
        <div className="hero-bg">
          <div className="stripe stripe-1" />
          <div className="stripe stripe-2" />
          <div className="stripe stripe-3" />
        </div>

        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-dot" />
              <span>Precision Crafted</span>
            </div>
            <h1 className="hero-title">{title}</h1>
            {subtitle && <p className="hero-lead">{subtitle}</p>}
          </div>

          <div className="hero-visual">
            <div className="visual-frame">
              <div className="frame-corner tl" />
              <div className="frame-corner tr" />
              <div className="frame-corner bl" />
              <div className="frame-corner br" />
              {renderVisualContent()}
            </div>
          </div>
        </div>

        <div className="scroll-indicator">
          <span>Scroll</span>
          <div className="scroll-line" />
        </div>
      </section>
    );
  }

  /**
   * Minimal layout: centered pole only
   */
  if (variant === 'minimal') {
    return (
      <section
        ref={containerRef}
        className={`hero hero-minimal ${className}`}
        aria-label="Barber shop hero"
      >
        <div className="hero-minimal-content">
          {title && <h1 className="hero-title">{title}</h1>}
          <div className="visual-frame hero-minimal-frame">
            {renderVisualContent()}
          </div>
        </div>
      </section>
    );
  }

  /**
   * Full layout: everything, maximum visual impact
   */
  return (
    <section
      ref={containerRef}
      className={`hero hero-full ${className}`}
      aria-label="Premium barbershop experience"
    >
      <div className="hero-bg">
        <div className="stripe stripe-1" />
        <div className="stripe stripe-2" />
        <div className="stripe stripe-3" />
      </div>

      <div className="container">
        <div className="hero-content">
          <h1 className="hero-title">{title}</h1>
          {subtitle && <p className="hero-lead">{subtitle}</p>}
        </div>

        <div className="hero-visual">
          <div className="visual-frame">
            <div className="frame-corner tl" />
            <div className="frame-corner tr" />
            <div className="frame-corner bl" />
            <div className="frame-corner br" />
            {renderVisualContent()}
          </div>
        </div>
      </div>

      <div className="scroll-indicator">
        <span>Scroll</span>
        <div className="scroll-line" />
      </div>
    </section>
  );
};

export default BarbershopHero;
