// Service Worker for PWA - Offline Support & Caching
const CACHE_NAME = "evident-premium-v3.0.0";
const STATIC_CACHE = "evident-static-v3";
const DYNAMIC_CACHE = "evident-dynamic-v3";

// Assets to cache immediately
const STATIC_ASSETS = [
  "/",
  "/assets/css/evident-core.css",
  "/assets/js/evident-core.js",
  "/manifest.json",
  "/offline.html",
];

// Install event - cache static assets
self.addEventListener("install", (event) => {
  console.log("[SW] Installing service worker...");
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("[SW] Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((err) => console.error("[SW] Cache failed:", err)),
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("[SW] Activating service worker...");
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
          .map((name) => caches.delete(name)),
      );
    }),
  );
  return self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API requests - network first, cache fallback
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone response before caching
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // If network fails, try cache
          return caches.match(request);
        }),
    );
    return;
  }

  // Static assets - cache first, network fallback
  event.respondWith(
    caches
      .match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(request).then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
      .catch(() => {
        // Offline fallback page
        if (request.destination === "document") {
          return caches.match("/offline.html");
        }
      }),
  );
});

// Background sync for offline uploads
self.addEventListener("sync", (event) => {
  console.log("[SW] Background sync:", event.tag);

  if (event.tag === "sync-evidence") {
    event.waitUntil(syncEvidenceUploads());
  }
});

// Push notifications
self.addEventListener("push", (event) => {
  console.log("[SW] Push notification received");

  const data = event.data ? event.data.json() : {};
  const title = data.title || "Evident Notification";
  const options = {
    body: data.body || "You have a new notification",
    icon: "/assets/images/logo-192.png",
    badge: "/assets/images/badge-72.png",
    vibrate: [200, 100, 200],
    data: data.url || "/",
    actions: [
      { action: "open", title: "Open" },
      { action: "close", title: "Dismiss" },
    ],
    requireInteraction: data.priority === "high",
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click handler
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "open" || !event.action) {
    const urlToOpen = event.notification.data || "/";

    event.waitUntil(
      clients
        .matchAll({ type: "window", includeUncontrolled: true })
        .then((windowClients) => {
          // Check if there's already a window open
          for (let client of windowClients) {
            if (client.url === urlToOpen && "focus" in client) {
              return client.focus();
            }
          }
          // Open new window if none exists
          if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
          }
        }),
    );
  }
});

// Helper: Sync offline evidence uploads
async function syncEvidenceUploads() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();

    const pendingUploads = requests.filter(
      (req) =>
        req.url.includes("/api/evidence/intake") && req.method === "POST",
    );

    for (let request of pendingUploads) {
      try {
        await fetch(request);
        await cache.delete(request);
        console.log("[SW] Synced offline upload");
      } catch (err) {
        console.error("[SW] Upload sync failed:", err);
      }
    }
  } catch (err) {
    console.error("[SW] Sync failed:", err);
  }
}

// Message handler for cache updates
self.addEventListener("message", (event) => {
  if (event.data.action === "skipWaiting") {
    self.skipWaiting();
  }

  if (event.data.action === "clearCache") {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(cacheNames.map((name) => caches.delete(name)));
      }),
    );
  }
});
