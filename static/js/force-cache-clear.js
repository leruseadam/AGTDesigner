/**
 * Force cache clear on page load if service worker is outdated
 * This ensures users always get the latest code
 */

(function() {
    'use strict';
    
    // Check if service worker is supported
    if ('serviceWorker' in navigator) {
        // Check for cache version mismatch
        const EXPECTED_CACHE_VERSION = 'labelmaker-v2';
        
        caches.keys().then(cacheNames => {
            const hasOldCache = cacheNames.some(name => 
                name.startsWith('labelmaker-') && name !== EXPECTED_CACHE_VERSION
            );
            
            if (hasOldCache) {
                console.log('🔄 Old cache detected - clearing all caches...');
                
                // Clear all caches
                return Promise.all(
                    cacheNames.map(cacheName => {
                        console.log('Deleting cache:', cacheName);
                        return caches.delete(cacheName);
                    })
                ).then(() => {
                    console.log('✅ All caches cleared');
                    
                    // Unregister all service workers
                    return navigator.serviceWorker.getRegistrations();
                }).then(registrations => {
                    return Promise.all(
                        registrations.map(registration => {
                            console.log('Unregistering service worker...');
                            return registration.unregister();
                        })
                    );
                }).then(() => {
                    console.log('✅ Service workers unregistered');
                    console.log('🔄 Please refresh the page to get the latest version');
                    
                    // Show user-friendly message
                    const message = document.createElement('div');
                    message.style.cssText = `
                        position: fixed;
                        top: 20px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: #4CAF50;
                        color: white;
                        padding: 15px 30px;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                        z-index: 999999;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        font-size: 16px;
                        text-align: center;
                        max-width: 500px;
                    `;
                    message.innerHTML = `
                        <strong>✨ Update Available</strong><br>
                        <span style="font-size: 14px;">Refreshing to load the latest version...</span>
                    `;
                    document.body.appendChild(message);
                    
                    // Auto-refresh after 1 second
                    if (window.safeReload) {
                        window.safeReload(1000);
                    } else {
                        setTimeout(() => {
                            if (!window._reloadInProgress) {
                                window._reloadInProgress = true;
                                window.location.reload(true);
                            }
                        }, 1000);
                    }
                });
            } else {
                console.log('✅ Cache version is up to date');
            }
        }).catch(error => {
            console.error('Error checking caches:', error);
        });
    }
})();

