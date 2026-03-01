/**
 * Performance Optimization Utilities
 * Lazy loading, resource hints, and Web Vitals tracking
 * Browser-compatible version (no build step required)
 */

// Web Vitals tracking (gracefully degrades if library not loaded)
export function trackWebVitals() {
  console.log('📊 Initializing Web Vitals tracking...');
  
  function sendToAnalytics({ name, delta, value, id }) {
    console.log(`📊 ${name}:`, {
      value: Math.round(value),
      delta: Math.round(delta),
      id,
    });

    // Send to Google Analytics if available
    if (window.gtag) {
      window.gtag('event', name, {
        event_category: 'Web Vitals',
        value: Math.round(value),
        event_label: id,
        non_interaction: true,
      });
    }
  }

  // Basic performance metrics using Performance API
  if ('performance' in window) {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
          console.log('📊 Load Time:', Math.round(perfData.loadEventEnd - perfData.fetchStart), 'ms');
          console.log('📊 DOM Content Loaded:', Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart), 'ms');
        }
      }, 0);
    });
  }
}

// Initialize Lazy Loading (native browser support)
export function initLazyLoad() {
  const lazyImages = document.querySelectorAll('img[loading="lazy"], .lazy');
  
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading support
    lazyImages.forEach(img => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
      }
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
      }
    });
    console.log('🚀 Native lazy loading enabled');
  } else {
    // Fallback to Intersection Observer
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) img.src = img.dataset.src;
          if (img.dataset.srcset) img.srcset = img.dataset.srcset;
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
    console.log('🚀 Lazy loading initialized (IntersectionObserver)');
  }
}

// Prefetch visible links (native implementation)
export function initQuicklink() {
  if (!('IntersectionObserver' in window)) {
    console.log('⚡ IntersectionObserver not supported. Prefetching skipped.');
    return;
  }

  const linkObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const link = entry.target;
        const href = link.href;
        
        // Prefetch the link
        if (href && !link.dataset.prefetched) {
          const linkTag = document.createElement('link');
          linkTag.rel = 'prefetch';
          linkTag.href = href;
          document.head.appendChild(linkTag);
          link.dataset.prefetched = 'true';
        }
      }
    });
  });

  // Observe all internal links
  document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]').forEach(link => {
    linkObserver.observe(link);
  });

  console.log('⚡ Link prefetching initialized');
}

// Resource Hints
export function addResourceHints() {
  const hints = [
    { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
    { rel: 'dns-prefetch', href: '//www.googletagmanager.com' },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com', crossorigin: true },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
  ];

  hints.forEach((hint) => {
    const link = document.createElement('link');
    link.rel = hint.rel;
    link.href = hint.href;
    if (hint.crossorigin) link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });

  console.log('🔗 Resource hints added');
}

// Defer Non-Critical CSS
export function deferNonCriticalCSS() {
  const stylesheets = document.querySelectorAll('link[rel="stylesheet"][data-defer]');
  
  stylesheets.forEach((link) => {
    link.media = 'print';
    link.onload = function () {
      this.media = 'all';
      this.onload = null;
    };
  });

  console.log('📄 Non-critical CSS deferred');
}

// Font Loading Optimization
export function optimizeFontLoading() {
  if ('fonts' in document) {
    Promise.all([
      document.fonts.load('1em Inter'),
      document.fonts.load('700 1em Inter'),
    ]).then(() => {
      document.documentElement.classList.add('fonts-loaded');
      console.log('🔤 Fonts loaded');
    }).catch(() => {
      console.log('🔤 Font loading failed, using fallbacks');
    });
  }
}

// Service Worker Registration
export async function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('✅ Service Worker registered:', registration);
      return registration;
    } catch (error) {
      console.log('⚠️ Service Worker registration skipped');
    }
  }
}

// Image Format Detection
export function supportsWebP() {
  const canvas = document.createElement('canvas');
  if (canvas.getContext && canvas.getContext('2d')) {
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
}

export function supportsAVIF() {
  return new Promise((resolve) => {
    const image = new Image();
    image.onload = () => resolve(true);
    image.onerror = () => resolve(false);
    image.src =
      'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgANogQEAwgMg8f8D///8WfhwB8+ErK42A=';
  });
}

// Detect Network Connection
export function getNetworkType() {
  if ('connection' in navigator) {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    return connection.effectiveType;
  }
  return 'unknown';
}

// Adaptive Loading
export function shouldLoadHighQuality() {
  const networkType = getNetworkType();
  const saveData = navigator.connection?.saveData;
  
  if (saveData) return false;
  if (networkType === 'slow-2g' || networkType === '2g') return false;
  
  return true;
}

// Initialize all performance optimizations
export function initPerformance() {
  console.log('⚡ Initializing performance optimizations...');

  // Add resource hints
  addResourceHints();

  // Initialize lazy loading
  initLazyLoad();

  // Defer non-critical CSS
  deferNonCriticalCSS();

  // Optimize font loading
  optimizeFontLoading();

  // Track performance metrics
  trackWebVitals();

  // Initialize prefetching for high-quality connections
  if (shouldLoadHighQuality()) {
    initQuicklink();
  }

  // Register service worker (optional, won't error if sw.js doesn't exist)
  registerServiceWorker();

  console.log('✅ Performance optimizations initialized');
}

export default {
  initLazyLoad,
  initQuicklink,
  trackWebVitals,
  addResourceHints,
  deferNonCriticalCSS,
  optimizeFontLoading,
  registerServiceWorker,
  supportsWebP,
  supportsAVIF,
  getNetworkType,
  shouldLoadHighQuality,
  initPerformance,
};
