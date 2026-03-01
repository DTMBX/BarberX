/**
 * Workbox Service Worker Configuration
 * Caches assets for offline support and faster repeat visits
 */

export default {
  globDirectory: '_site/',
  globPatterns: [
    '**/*.{html,css,js,json,webp,avif,jpg,png,svg,woff2,woff}',
  ],
  swDest: '_site/sw.js',
  
  // Runtime caching strategies
  runtimeCaching: [
    {
      // Cache images with Cache First strategy
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'images-cache',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
        },
      },
    },
    {
      // Cache CSS/JS with Stale While Revalidate
      urlPattern: /\.(?:css|js)$/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'static-resources',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 7 * 24 * 60 * 60, // 7 days
        },
      },
    },
    {
      // Cache fonts with Cache First
      urlPattern: /\.(?:woff|woff2|ttf|otf)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'fonts-cache',
        expiration: {
          maxEntries: 20,
          maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
        },
      },
    },
    {
      // Cache HTML pages with Network First
      urlPattern: /\.html$/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'pages-cache',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 24 * 60 * 60, // 1 day
        },
      },
    },
    {
      // Cache Google Fonts CSS
      urlPattern: /^https:\/\/fonts\.googleapis\.com/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'google-fonts-stylesheets',
      },
    },
    {
      // Cache Google Fonts files
      urlPattern: /^https:\/\/fonts\.gstatic\.com/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'google-fonts-webfonts',
        expiration: {
          maxEntries: 30,
          maxAgeSeconds: 365 * 24 * 60 * 60,
        },
      },
    },
  ],

  // Skip waiting and claim clients immediately
  skipWaiting: true,
  clientsClaim: true,

  // Ignore specific files
  ignoreURLParametersMatching: [/^utm_/, /^fbclid$/],
  
  // Don't cache admin or form submission pages
  navigateFallback: '/offline.html',
  navigateFallbackDenylist: [/^\/_/, /\/[^/?]+\.[^/]+$/],
};
