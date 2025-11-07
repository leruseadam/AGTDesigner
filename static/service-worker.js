/**
 * Service Worker for aggressive caching of static assets
 * This significantly speeds up page loads by caching CSS, JS, and images
 * 
 * DEVELOPMENT MODE: Set DEV_MODE = true to disable caching
 * CACHE BUST: Increment version numbers to force cache refresh
 */

// 🔧 DEVELOPMENT MODE: Set to true to disable all caching
const DEV_MODE = false;

// Version numbers - increment to force cache refresh
const CACHE_VERSION = 'v3';
const CACHE_NAME = `labelmaker-${CACHE_VERSION}`;
const STATIC_CACHE_NAME = `labelmaker-static-${CACHE_VERSION}`;
const API_CACHE_NAME = `labelmaker-api-${CACHE_VERSION}`;

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/styles.css',
    '/static/js/main.js',
    '/static/js/performance.js',
    '/static/js/fast-page-load.js',
    '/static/js/enhanced-ui.js',
    '/static/js/unified-font-sizing.js',
    '/static/js/generation-splash.js',
    '/static/js/tags_table.js',
    '/static/js/drag-and-drop-manager.js',
    '/static/js/lineage-editor-enhanced.js',
    '/static/js/lineage-editor.js',
    // Add Bootstrap and other CDN assets if needed
];

// API endpoints to cache with short TTL
const API_CACHE_URLS = [
    '/api/initial-data',
    '/api/available-tags',
    '/api/filter-options'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS.map(url => {
                    // Add cache-busting parameter
                    return new Request(url, { cache: 'reload' });
                })).catch(err => {
                    console.warn('[Service Worker] Failed to cache some assets:', err);
                    // Continue anyway
                });
            })
            .then(() => {
                console.log('[Service Worker] Skip waiting');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            // Remove old caches
                            return cacheName.startsWith('labelmaker-') && 
                                   cacheName !== STATIC_CACHE_NAME &&
                                   cacheName !== API_CACHE_NAME;
                        })
                        .map((cacheName) => {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[Service Worker] Claiming clients');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // 🔧 DEVELOPMENT MODE: Skip all caching
    if (DEV_MODE) {
        console.log('[Service Worker] DEV_MODE: Bypassing cache for:', url.pathname);
        return; // Use network for everything
    }
    
    // Skip non-GET requests (POST, PUT, DELETE, etc.)
    // This ensures lineage updates and other mutations are never cached
    if (request.method !== 'GET') {
        console.log('[Service Worker] Skipping non-GET request:', request.method, url.pathname);
        return;
    }
    
    // Skip WebSocket upgrades
    if (request.headers.get('upgrade') === 'websocket') {
        return;
    }
    
    // Handle static assets - cache first, network fallback
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request)
                .then((response) => {
                    if (response) {
                        console.log('[Service Worker] Serving from cache:', url.pathname);
                        return response;
                    }
                    
                    console.log('[Service Worker] Fetching from network:', url.pathname);
                    return fetch(request)
                        .then((response) => {
                            // Cache the new response
                            if (response && response.status === 200) {
                                const responseClone = response.clone();
                                caches.open(STATIC_CACHE_NAME)
                                    .then((cache) => {
                                        cache.put(request, responseClone);
                                    });
                            }
                            return response;
                        });
                })
        );
        return;
    }
    
    // Handle API requests - network first, limited caching
    if (url.pathname.startsWith('/api/')) {
        // Never cache mutation endpoints (update, save, delete, etc.)
        const isMutationEndpoint = url.pathname.includes('update') || 
                                   url.pathname.includes('save') || 
                                   url.pathname.includes('delete') ||
                                   url.pathname.includes('upload');
        
        if (isMutationEndpoint) {
            console.log('[Service Worker] Not caching mutation endpoint:', url.pathname);
            event.respondWith(fetch(request));
            return;
        }
        
        // For read-only endpoints, use network-first with cache fallback
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cache successful API responses (read-only endpoints only)
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(API_CACHE_NAME)
                            .then((cache) => {
                                cache.put(request, responseClone);
                                
                                // Set expiry for API cache (2 minutes - shorter for faster updates)
                                setTimeout(() => {
                                    cache.delete(request);
                                }, 2 * 60 * 1000);
                            });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, try cache
                    console.log('[Service Worker] Network failed, trying cache for:', url.pathname);
                    return caches.match(request);
                })
        );
        return;
    }
    
    // Handle HTML pages - network first, cache fallback
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cache the HTML page
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, try cache
                    console.log('[Service Worker] Network failed, trying cache for:', url.pathname);
                    return caches.match(request);
                })
        );
        return;
    }
    
    // For everything else, just try network
    event.respondWith(fetch(request));
});

// Handle messages from the main thread
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        console.log('[Service Worker] Skip waiting requested');
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        console.log('[Service Worker] Clearing all caches');
        event.waitUntil(
            caches.keys()
                .then((cacheNames) => {
                    return Promise.all(
                        cacheNames.map((cacheName) => caches.delete(cacheName))
                    );
                })
                .then(() => {
                    console.log('[Service Worker] All caches cleared');
                    return self.clients.matchAll();
                })
                .then((clients) => {
                    clients.forEach((client) => {
                        client.postMessage({
                            type: 'CACHE_CLEARED'
                        });
                    });
                })
        );
    }
});

console.log('[Service Worker] Loaded');

