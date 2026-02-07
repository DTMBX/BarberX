// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * PERFORMANCE MONITORING
 *
 * Tracks Core Web Vitals and performance metrics.
 * Default OFF in production unless explicitly enabled.
 *
 * Enable conditions (any one):
 * - ?debug=performance
 * - localhost
 * - <html data-performance-monitor="true">
 *
 * Notes:
 * - Safe no-op unless enabled.
 * - Uses PerformanceObserver only when supported.
 */

(function () {
  "use strict";

  // -------------
  // Enable gate (default OFF)
  // -------------
  function isEnabled() {
    try {
      const params = new URLSearchParams(window.location.search);
      if (params.get("debug") === "performance") return true;
    } catch (_) {}

    if (window.location.hostname === "localhost") return true;

    const html = document.documentElement;
    if (html && html.getAttribute("data-performance-monitor") === "true") return true;

    return false;
  }

  if (!isEnabled()) return;

  const metrics = {
    fcp: null, // First Contentful Paint
    lcp: null, // Largest Contentful Paint
    fid: null, // First Input Delay
    cls: null, // Cumulative Layout Shift
    ttfb: null, // Time to First Byte
  };

  function reportMetric(metric, value, rating) {
    metrics[metric] = { value, rating };
    // Keep logging simple and non-spammy
    console.log(`${metric.toUpperCase()}: ${value} - ${rating}`);
  }

  function getRating(metric, value) {
    const thresholds = {
      fcp: { good: 1800, poor: 3000 },
      lcp: { good: 2500, poor: 4000 },
      fid: { good: 100, poor: 300 },
      cls: { good: 0.1, poor: 0.25 },
      ttfb: { good: 800, poor: 1800 },
    };

    const threshold = thresholds[metric];
    if (!threshold) return "unknown";

    if (value <= threshold.good) return "good";
    if (value <= threshold.poor) return "needs-improvement";
    return "poor";
  }

  function measureTTFB() {
    if (!window.performance || !performance.timing) return;
    const ttfb = performance.timing.responseStart - performance.timing.requestStart;
    reportMetric("ttfb", ttfb, getRating("ttfb", ttfb));
  }

  function measureFCP() {
    if (!window.PerformanceObserver) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.name === "first-contentful-paint") {
            const value = Math.round(entry.startTime);
            reportMetric("fcp", value, getRating("fcp", value));
            observer.disconnect();
          }
        }
      });
      observer.observe({ entryTypes: ["paint"] });
    } catch (_) {}
  }

  function measureLCP() {
    if (!window.PerformanceObserver) return;

    let observer;
    try {
      observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        const value = Math.round(
          lastEntry.renderTime || lastEntry.loadTime || lastEntry.startTime || 0
        );
        reportMetric("lcp", value, getRating("lcp", value));
      });

      observer.observe({ entryTypes: ["largest-contentful-paint"] });
    } catch (_) {
      return;
    }

    // Stop observing when page is hidden to avoid lingering observer
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden" && observer) {
        observer.disconnect();
        observer = null;
      }
    });
  }

  function measureFID() {
    if (!window.PerformanceObserver) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const value = Math.round(entry.processingStart - entry.startTime);
          reportMetric("fid", value, getRating("fid", value));
          observer.disconnect();
        }
      });
      observer.observe({ entryTypes: ["first-input"] });
    } catch (_) {}
  }

  function measureCLS() {
    if (!window.PerformanceObserver) return;

    let clsValue = 0;
    let observer;

    try {
      observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) clsValue += entry.value;
        }
      });

      observer.observe({ entryTypes: ["layout-shift"] });
    } catch (_) {
      return;
    }

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") {
        reportMetric("cls", Number(clsValue.toFixed(3)), getRating("cls", clsValue));
        if (observer) observer.disconnect();
        observer = null;
      }
    });
  }

  function measurePageLoad() {
    window.addEventListener("load", () => {
      if (!window.performance || !performance.timing) return;
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      console.log(`Page Load Time: ${loadTime}ms`);

      setTimeout(() => {
        console.group("Performance Summary");
        console.table(metrics);
        console.groupEnd();
      }, 1500);
    });
  }

  function logResourceTiming() {
    // Only do this when explicitly requested (debug flag)
    const params = new URLSearchParams(window.location.search);
    const logResources = params.get("debug") === "performance";

    if (!logResources) return;
    if (!window.performance || !performance.getEntriesByType) return;

    const resources = performance.getEntriesByType("resource");
    const slow = resources.filter((r) => r.duration > 500);

    if (slow.length) {
      console.group("Slow Resources (>500ms)");
      slow.forEach((r) => console.log(`${r.name}: ${Math.round(r.duration)}ms`));
      console.groupEnd();
    }
  }

  function init() {
    console.log("Performance Monitoring Enabled (debug/localhost/data attribute).");
    measureTTFB();
    measureFCP();
    measureLCP();
    measureFID();
    measureCLS();
    measurePageLoad();

    window.addEventListener("load", () => setTimeout(logResourceTiming, 1000));
  }

  init();

  // Export (debug convenience)
  window.performanceMetrics = {
    get: () => metrics,
    report: () => console.table(metrics),
  };
})();
