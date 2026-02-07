// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

import React from "react";
import "./EvidentJusticeHero.css";

/**
 * EvidentJusticeHero - Animated Scales of Justice for Login/Hero Section
 * Clean, modern, and smooth. Symbolizes balance and fairness.
 */
export default function EvidentJusticeHero({ className = "" }) {
  return (
    <div className={`evident-justice-hero ${className}`} aria-label="Animated Scales of Justice">
      <svg
        className="justice-svg"
        width="120"
        height="120"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Base */}
        <rect x="55" y="90" width="10" height="20" rx="3" fill="#2d3748" />
        {/* Central pillar */}
        <rect x="58" y="30" width="4" height="60" rx="2" fill="#4f8ef7" />
        {/* Crossbar */}
        <rect x="40" y="40" width="40" height="4" rx="2" fill="#4f8ef7" />
        {/* Left chain */}
        <line x1="44" y1="44" x2="34" y2="70" stroke="#2d3748" strokeWidth="2" />
        {/* Right chain */}
        <line x1="76" y1="44" x2="86" y2="70" stroke="#2d3748" strokeWidth="2" />
        {/* Left pan */}
        <ellipse className="justice-pan left" cx="34" cy="74" rx="10" ry="4" fill="#e2e8f0" />
        {/* Right pan */}
        <ellipse className="justice-pan right" cx="86" cy="74" rx="10" ry="4" fill="#e2e8f0" />
        {/* Top circle */}
        <circle cx="60" cy="30" r="6" fill="#4f8ef7" />
      </svg>
    </div>
  );
}
