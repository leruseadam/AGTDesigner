/**
 * Ultra-fast page load optimization v2.1.0
 * Makes initial data loading non-blocking and shows UI immediately
 * UPDATED: 2025-11-19 - Added cache checking and splash screen fixes
 */

(function() {
    'use strict';
    
    console.log('⚡ Fast page load optimization v2.1.0 enabled');
    
    // CRITICAL: Clear cache if no file uploaded
    // Prevents showing stale cached data from previous sessions
    // NOTE: Only clear sessionStorage, keep localStorage for faster reloads
    const fileInfoText = document.getElementById('fileInfoText');
    const hasUploadedFile = fileInfoText && !fileInfoText.textContent.includes('No file uploaded');
    if (!hasUploadedFile) {
        console.log('🗑️ No uploaded file detected - clearing stale sessionStorage cache (keeping localStorage)');
        // Clear all tag-related cache entries from sessionStorage only
        if (window.sessionStorage) {
            const keysToRemove = [];
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                if (key && key.includes('agt_available_tags')) {
                    keysToRemove.push(key);
                }
            }
            keysToRemove.forEach(key => sessionStorage.removeItem(key));
            console.log(`✅ Cleared ${keysToRemove.length} stale sessionStorage cache entries`);
        }
    }
    
    // Store original checkForExistingData function
    let originalCheckForExistingData = null;
    
    // Wait for TagManager to be available
    function waitForTagManager() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.TagManager && TagManager.checkForExistingData) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 10);
            
            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                resolve();
            }, 5000);
        });
    }
    
    // Optimize the page load
    async function optimizePageLoad() {
        await waitForTagManager();
        
        if (!window.TagManager || !TagManager.checkForExistingData) {
            console.warn('⚠️ TagManager not available, skipping optimization');
            // Fallback: Try to load tags directly if TagManager.init exists
            if (window.TagManager && typeof window.TagManager.init === 'function') {
                console.log('⚠️ Attempting fallback tag load via TagManager.init()');
                try {
                    window.TagManager.init();
                } catch (fallbackError) {
                    console.error('⚠️ Fallback tag load failed:', fallbackError);
                }
            }
            return;
        }
        
        // Store original function
        originalCheckForExistingData = TagManager.checkForExistingData;
        
        // Replace with optimized version
        TagManager.checkForExistingData = async function() {
            console.log('⚡ Optimized checkForExistingData called');
            
            // CRITICAL: Try cache FIRST for instant load
            console.log('🔍 Checking for cached tags...');
            const cachedTags = this.loadAvailableTagsFromCache ? this.loadAvailableTagsFromCache() : null;
            
            if (cachedTags && cachedTags.length > 0) {
                console.log(`⚡ INSTANT CACHE HIT: ${cachedTags.length} tags available`);
                // CRITICAL FIX: Preserve selected tags before rendering
                const savedSelectedTags = [...(this.state.persistentSelectedTags || [])];
                
                // Render cached tags IMMEDIATELY
                this.state.tags = [...cachedTags];
                this.state.originalTags = [...cachedTags];
                this.state.hydratedFromCache = true;
                
                // Use requestAnimationFrame for instant render
                requestAnimationFrame(() => {
                    console.log('🎨 Rendering cached tags...');
                    if (this._updateAvailableTags) {
                        this._updateAvailableTags(cachedTags, null);
                    }
                    console.log(`✅ INSTANT RENDER: ${cachedTags.length} tags displayed from cache`);
                    
                    // CRITICAL FIX: Restore selected tags after rendering
                    if (savedSelectedTags.length > 0) {
                        this.state.persistentSelectedTags = [...savedSelectedTags];
                        this.state.selectedTags = new Set(savedSelectedTags);
                        // Restore checkboxes
                        requestAnimationFrame(() => {
                            savedSelectedTags.forEach(tagName => {
                                const checkboxes = document.querySelectorAll(`input[type="checkbox"][value="${CSS.escape(tagName)}"]`);
                                checkboxes.forEach(cb => {
                                    if (!cb.checked) {
                                        cb.checked = true;
                                    }
                                });
                            });
                            // Restore selected tags display
                            if (this.getSelectedTagObjects && this.updateSelectedTags) {
                                const selectedTagObjects = this.getSelectedTagObjects();
                                if (selectedTagObjects.length > 0) {
                                    this.updateSelectedTags(selectedTagObjects);
                                }
                            }
                        });
                    }
                    
                    // Hide splash immediately
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                });
                
                // Load selected tags and filters in background (non-blocking)
                console.log('📡 Background: Fetching selected tags and filters');
                Promise.allSettled([
                    this.fetchAndUpdateSelectedTags ? this.fetchAndUpdateSelectedTags() : Promise.resolve(),
                    this.fetchAndPopulateFilters ? this.fetchAndPopulateFilters() : Promise.resolve()
                ]).then(() => {
                    console.log('✅ Background: Selected tags and filters loaded');
                    // CRITICAL FIX: Ensure selected tags are still preserved after background fetch
                    if (savedSelectedTags.length > 0 && this.state.persistentSelectedTags.length === 0) {
                        this.state.persistentSelectedTags = [...savedSelectedTags];
                        this.state.selectedTags = new Set(savedSelectedTags);
                        if (this.getSelectedTagObjects && this.updateSelectedTags) {
                            const selectedTagObjects = this.getSelectedTagObjects();
                            if (selectedTagObjects.length > 0) {
                                this.updateSelectedTags(selectedTagObjects);
                            }
                        }
                    }
                }).catch(err => {
                    console.warn('⚠️ Background load error (non-critical):', err);
                });
                
                return; // Exit early - we have cached data
            }
            
            // No cache available - show loading UI
            console.log('⏳ No cache found - loading from server...');
            if (typeof AppLoadingSplash !== 'undefined') {
                AppLoadingSplash.updateProgress(50, 'Loading tags...');
            }
            
            // Show loading splash while fetching
            if (this.showActionSplash) {
                this.showActionSplash('Loading tags from server...');
            }
            
            // INSTANT RELOAD FIX: Load data from server with timeout and show UI immediately
            try {
                // CRITICAL FIX: Increased timeout to 10 seconds to prevent premature restarts
                // Use Promise.race to timeout after 10 seconds (was 2 seconds)
                const fetchPromise = fetch('/api/initial-data?fast_load=1&stream=1');
                const timeoutPromise = new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Server timeout')), 10000)
                );
                
                let response;
                try {
                    response = await Promise.race([fetchPromise, timeoutPromise]);
                } catch (timeoutError) {
                    console.warn('⚡ Server fetch timeout, falling back to original checkForExistingData');
                    // CRITICAL FIX: Don't restart - just hide splash and show error
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                    // Only fallback if we have no tags at all
                    if (!hasExistingTags && originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                        await originalCheckForExistingData.call(this);
                    }
                    return;
                }
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('⚡ Initial data response:', data);
                    
                    if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                        console.log(`⚡ Loaded ${data.available_tags.length} tags from server`);
                        
                        // Save to cache for next instant load
                        if (this.saveAvailableTagsToCache) {
                            this.saveAvailableTagsToCache(data.available_tags);
                            console.log(`💾 Cached ${data.available_tags.length} tags for next load`);
                        }
                        
                        // Update state immediately
                        this.state.tags = [...data.available_tags];
                        this.state.originalTags = [...data.available_tags];
                        
                        // Update UI with loaded data IMMEDIATELY (no debounce for initial load)
                        // Use _updateAvailableTags directly to avoid debounce delay
                        this._updateAvailableTags(data.available_tags, null);
                        
                        // Immediately check if tags are visible and hide splash
                        requestAnimationFrame(() => {
                            const container = document.getElementById('availableTags');
                            if (container) {
                                const tagItems = container.querySelectorAll('.tag-item');
                                if (tagItems.length > 0) {
                                    console.log(`⚡ Tags rendered (${tagItems.length} items), hiding splash immediately`);
                                    if (this.hideActionSplash) {
                                        this.hideActionSplash();
                                    }
                                    if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                                        AppLoadingSplash.stopAutoAdvance();
                                        AppLoadingSplash.complete();
                                    }
                                }
                            }
                        });
                        
                        // Also ensure splash is hidden when tags appear (backup)
                        if (this._waitForTagsToAppear) {
                            this._waitForTagsToAppear();
                        }
                        
                        // Restore selected tags (non-blocking)
                        this.fetchAndUpdateSelectedTags().catch(err => {
                            console.warn('Error restoring selected tags:', err);
                        });
                        
                        // Update filters
                        this.updateFilters(data.filters || {
                            vendor: [],
                            brand: [],
                            productType: [],
                            lineage: [],
                            weight: []
                        }, true);
                        
                        // Update file info
                        if (data.filename) {
                            const fileInfoText = document.getElementById('fileInfoText');
                            if (fileInfoText) {
                                fileInfoText.textContent = data.filename;
                            }
                        }
                        
                        console.log('⚡ Background data loading complete');
                    } else {
                        console.warn('⚡ No initial data available:', data);
                        // Fallback to original checkForExistingData if available
                        if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                            console.log('⚡ Falling back to original checkForExistingData');
                            try {
                                await originalCheckForExistingData.call(this);
                            } catch (fallbackError) {
                                console.error('⚡ Fallback failed:', fallbackError);
                                this.initializeEmptyState();
                            }
                        } else {
                            this.initializeEmptyState();
                        }
                    }
                } else {
                    console.error('⚡ Initial data endpoint error:', response.status, response.statusText);
                    // Fallback to original checkForExistingData if available
                    if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                        console.log('⚡ Falling back to original checkForExistingData');
                        try {
                            await originalCheckForExistingData.call(this);
                        } catch (fallbackError) {
                            console.error('⚡ Fallback failed:', fallbackError);
                            this.initializeEmptyState();
                        }
                    } else {
                        this.initializeEmptyState();
                    }
                }
            } catch (error) {
                console.error('⚡ Initial data load error:', error);
                // Fallback to original checkForExistingData if available
                if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                    console.log('⚡ Falling back to original checkForExistingData after error');
                    try {
                        await originalCheckForExistingData.call(this);
                    } catch (fallbackError) {
                        console.error('⚡ Fallback failed:', fallbackError);
                        this.initializeEmptyState();
                    }
                } else {
                    this.initializeEmptyState();
                }
            }
        };
        
        console.log('⚡ Page load optimization active');
    }
    
    // ULTRA-FAST RELOAD: Check cache immediately on script load (before DOM ready)
    // This allows instant tag display even before TagManager is fully initialized
    function earlyCacheCheck() {
        try {
            // Try to find any cached tags immediately
            const storageBackends = [];
            if (window.localStorage) storageBackends.push({ name: 'localStorage', storage: localStorage });
            if (window.sessionStorage) storageBackends.push({ name: 'sessionStorage', storage: sessionStorage });
            
            if (storageBackends.length > 0) {
                // Search for any valid cache keys
                const allKeys = [];
                for (const backend of storageBackends) {
                    for (let i = 0; i < backend.storage.length; i++) {
                        const key = backend.storage.key(i);
                        if (key && key.startsWith('agt_available_tags_')) {
                            allKeys.push({ key, storage: backend.storage });
                        }
                    }
                }
                
                if (allKeys.length > 0) {
                    console.log(`⚡ Early cache check: Found ${allKeys.length} potential cache keys`);
                    // Try to find a valid cache entry
                    for (const { key, storage } of allKeys) {
                        try {
                            const raw = storage.getItem(key);
                            if (raw) {
                                const payload = JSON.parse(raw);
                                if (payload && Array.isArray(payload.tags) && payload.tags.length > 0) {
                                    const age = Date.now() - (payload.timestamp || 0);
                                    const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes
                                    if (age <= CACHE_TTL_MS) {
                                        console.log(`⚡ Early cache HIT: Found ${payload.tags.length} tags in ${storage === localStorage ? 'localStorage' : 'sessionStorage'}`);
                                        // Store in window for TagManager to pick up
                                        window._earlyCacheFound = { key, tags: payload.tags, storage: storage === localStorage ? 'localStorage' : 'sessionStorage' };
                                        break;
                                    }
                                }
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                }
            }
        } catch (error) {
            console.warn('Early cache check failed:', error);
        }
    }
    
    // Run early cache check immediately
    earlyCacheCheck();
    
    // Run optimization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', optimizePageLoad);
    } else {
        optimizePageLoad();
    }
})();

