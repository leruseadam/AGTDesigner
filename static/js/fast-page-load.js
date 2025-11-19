/**
 * Ultra-fast page load optimization v2.1.0
 * Makes initial data loading non-blocking and shows UI immediately
 * UPDATED: 2025-11-19 - Added cache checking and splash screen fixes
 */

(function() {
    'use strict';
    
    console.log('⚡ Fast page load optimization v2.1.0 enabled');
    
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
            
            // Load data from server
            try {
                const response = await fetch('/api/initial-data?fast_load=1');
                
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
    
    // Run optimization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', optimizePageLoad);
    } else {
        optimizePageLoad();
    }
})();

