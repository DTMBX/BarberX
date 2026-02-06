// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Service Worker for Evident Progressive Web App (PWA)
// Enables offline mode, caching, and push notifications

const CACHE_VERSION = "3.0.0";
const CACHE_NAME = `Evident-v${CACHE_VERSION}`;
const RUNTIME_CACHE = "evident-runtime";
const DOCUMENT_CACHE = "evident-documents";
const AI_CACHE = "evident-ai-responses";

// Files to cache immediately on install
const PRECACHE_URLS = [
  "/",
  "/offline.html",
  "/assets/css/evident-core.css",
  "/assets/js/evident-core.js",
  "/manifest.json",
];

// Install event - cache essential files
self.addEventListener("install", (event) => {
  console.log("[ServiceWorker] Installing v" + CACHE_VERSION);

  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("[ServiceWorker] Caching app shell");
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => self.skipWaiting()),
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("[ServiceWorker] Activating v" + CACHE_VERSION);

  const currentCaches = [CACHE_NAME, RUNTIME_CACHE, DOCUMENT_CACHE, AI_CACHE];

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => !currentCaches.includes(cacheName))
            .map((cacheName) => {
              console.log("[ServiceWorker] Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }),
        );
      })
      .then(() => self.clients.claim()),
  );
});

// Fetch event - serve from cache, fall back to network
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }

  // Handle share target
  if (url.pathname === "/api/share-target" && request.method === "POST") {
    event.respondWith(handleShareTarget(request));
    return;
  }

  // Handle file opener
  if (url.pathname === "/open-document") {
    event.respondWith(handleFileOpen(request));
    return;
  }

  // AI chatbot responses - cache with stale-while-revalidate
  if (url.pathname.startsWith("/api/v1/chatbot/")) {
    event.respondWith(staleWhileRevalidate(request, AI_CACHE));
    return;
  }

  // API requests - network first, cache as fallback
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Document files - cache for offline viewing
  if (
    url.pathname.startsWith("/documents/") ||
    url.pathname.match(/\.(pdf|doc|docx|txt)$/)
  ) {
    event.respondWith(documentCache(request));
    return;
  }

  // Evidence files - network only (too large to cache)
  if (
    url.pathname.startsWith("/uploads/") ||
    url.pathname.startsWith("/exports/")
  ) {
    event.respondWith(fetch(request));
    return;
  }

  // Everything else - cache first, network as fallback
  event.respondWith(cacheFirst(request));
});

// Cache-first strategy
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    console.log("[ServiceWorker] Serving from cache:", request.url);
    return cached;
  }

  try {
    const response = await fetch(request);

    // Cache successful responses
    if (response.status === 200) {
      const responseClone = response.clone();
      cache.put(request, responseClone);
    }

    return response;
  } catch (error) {
    console.error("[ServiceWorker] Fetch failed:", error);

    // Return offline page for navigation requests
    if (request.mode === "navigate") {
      const offlinePage = await cache.match("/offline.html");
      if (offlinePage) {
        return offlinePage;
      }
    }

    throw error;
  }
}

// Network-first strategy (for API calls)
async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE);

  try {
    const response = await fetch(request);

    // Cache successful API responses
    if (response.status === 200) {
      const responseClone = response.clone();
      cache.put(request, responseClone);
    }

    return response;
  } catch (error) {
    console.log(
      "[ServiceWorker] Network failed, serving from cache:",
      request.url,
    );

    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }

    // Return error response
    return new Response(
      JSON.stringify({
        error: "Offline",
        message: "You are currently offline. Some features may be unavailable.",
      }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
}

// Stale-while-revalidate (for AI responses)
async function staleWhileRevalidate(request, cacheName = AI_CACHE) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  // Fetch in background regardless
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.status === 200) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch((err) => {
      console.log("[ServiceWorker] Background fetch failed:", err);
      return null;
    });

  // Return cached immediately if available, otherwise wait for network
  if (cached) {
    return cached;
  }

  const networkResponse = await fetchPromise;
  if (networkResponse) {
    return networkResponse;
  }

  // Return offline response
  return new Response(
    JSON.stringify({
      error: "Offline",
      message:
        "AI assistant is unavailable offline. Please try again when connected.",
    }),
    {
      status: 503,
      headers: { "Content-Type": "application/json" },
    },
  );
}

// Document cache strategy (cache for offline viewing)
async function documentCache(request) {
  const cache = await caches.open(DOCUMENT_CACHE);
  const cached = await cache.match(request);

  if (cached) {
    console.log("[ServiceWorker] Serving document from cache:", request.url);
    return cached;
  }

  try {
    const response = await fetch(request);

    // Cache documents for offline viewing
    if (response.status === 200) {
      const contentType = response.headers.get("content-type") || "";
      const isDocument =
        contentType.includes("pdf") ||
        contentType.includes("word") ||
        contentType.includes("text");

      if (isDocument) {
        const responseClone = response.clone();
        cache.put(request, responseClone);
        console.log(
          "[ServiceWorker] Cached document for offline:",
          request.url,
        );
      }
    }

    return response;
  } catch (error) {
    console.error("[ServiceWorker] Document fetch failed:", error);

    return new Response("Document unavailable offline", {
      status: 503,
      headers: { "Content-Type": "text/plain" },
    });
  }
}

// Handle share target (receive shared documents)
async function handleShareTarget(request) {
  try {
    const formData = await request.formData();
    const title = formData.get("title") || "Shared Document";
    const text = formData.get("text") || "";
    const url = formData.get("url") || "";
    const files = formData.getAll("documents");

    // Store shared data for the app to process
    const shareData = {
      title,
      text,
      url,
      fileCount: files.length,
      timestamp: Date.now(),
    };

    // Store in IndexedDB for the app to retrieve
    await storeSharedData(shareData, files);

    // Redirect to workspace with share flag
    return Response.redirect("/workspace?shared=true", 303);
  } catch (error) {
    console.error("[ServiceWorker] Share target error:", error);
    return Response.redirect("/workspace?share_error=true", 303);
  }
}

// Handle file open (PWA file handler)
async function handleFileOpen(request) {
  try {
    const url = new URL(request.url);
    const fileUrl = url.searchParams.get("file");

    if (fileUrl) {
      // Redirect to workspace with file parameter
      return Response.redirect(
        `/workspace?open=${encodeURIComponent(fileUrl)}`,
        303,
      );
    }

    return Response.redirect("/workspace", 303);
  } catch (error) {
    console.error("[ServiceWorker] File open error:", error);
    return Response.redirect("/workspace", 303);
  }
}

// Store shared data in IndexedDB
async function storeSharedData(metadata, files) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("evident-shared", 1);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("shares")) {
        db.createObjectStore("shares", { keyPath: "timestamp" });
      }
    };

    request.onsuccess = async (event) => {
      const db = event.target.result;
      const tx = db.transaction("shares", "readwrite");
      const store = tx.objectStore("shares");

      // Store file contents as ArrayBuffers
      const fileData = await Promise.all(
        files.map(async (file) => ({
          name: file.name,
          type: file.type,
          size: file.size,
          data: await file.arrayBuffer(),
        })),
      );

      store.put({ ...metadata, files: fileData });

      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    };

    request.onerror = () => reject(request.error);
  });
}

// Push notification handler
self.addEventListener("push", (event) => {
  console.log("[ServiceWorker] Push received:", event);

  let data = {
    title: "Evident Notification",
    body: "You have a new update",
    icon: "/assets/icons/icon-192x192.png",
    badge: "/assets/icons/badge-72x72.png",
    tag: "evident-notification",
    requireInteraction: false,
  };

  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    tag: data.tag,
    requireInteraction: data.requireInteraction,
    data: {
      url: data.url || "/",
      timestamp: Date.now(),
    },
    actions: [
      { action: "open", title: "Open", icon: "/assets/icons/open.png" },
      { action: "dismiss", title: "Dismiss", icon: "/assets/icons/close.png" },
    ],
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

// Notification click handler
self.addEventListener("notificationclick", (event) => {
  console.log("[ServiceWorker] Notification clicked:", event);

  event.notification.close();

  if (event.action === "dismiss") {
    return;
  }

  const urlToOpen = event.notification.data?.url || "/";

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

        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      }),
  );
});

// Background sync (for offline evidence uploads)
self.addEventListener("sync", (event) => {
  console.log("[ServiceWorker] Background sync:", event.tag);

  if (event.tag === "sync-evidence-uploads") {
    event.waitUntil(syncEvidenceUploads());
  }
});

async function syncEvidenceUploads() {
  // Get pending uploads from IndexedDB
  // Upload when connection is restored
  console.log("[ServiceWorker] Syncing evidence uploads...");

  try {
    // Implementation would fetch from IndexedDB and retry failed uploads
    // This is a placeholder for the actual sync logic
    return Promise.resolve();
  } catch (error) {
    console.error("[ServiceWorker] Sync failed:", error);
    throw error;
  }
}

// Periodic background sync (for checking new evidence analysis)
self.addEventListener("periodicsync", (event) => {
  console.log("[ServiceWorker] Periodic sync:", event.tag);

  if (event.tag === "check-analysis-updates") {
    event.waitUntil(checkForUpdates());
  }
});

async function checkForUpdates() {
  try {
    const response = await fetch("/api/evidence/updates");
    const data = await response.json();

    if (data.hasUpdates) {
      // Show notification about new analysis results
      await self.registration.showNotification("Analysis Complete", {
        body: `${data.count} evidence file(s) have been analyzed`,
        icon: "/assets/icons/icon-192x192.png",
        tag: "analysis-complete",
        data: { url: "/command-center" },
      });
    }
  } catch (error) {
    console.error("[ServiceWorker] Update check failed:", error);
  }
}

// Message handler (for communication with main app)
self.addEventListener("message", (event) => {
  console.log("[ServiceWorker] Message received:", event.data);

  if (event.data.action === "skipWaiting") {
    self.skipWaiting();
  }

  if (event.data.action === "clearCache") {
    event.waitUntil(
      caches.delete(CACHE_NAME).then(() => {
        return caches.delete(RUNTIME_CACHE);
      }),
    );
  }
});

console.log("[ServiceWorker] Loaded successfully");
