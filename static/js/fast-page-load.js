/**
 * Ultra-fast page load optimization
 * Makes initial data loading non-blocking and shows UI immediately
 */

(function() {
    'use strict';
    
    console.log('⚡ Fast page load optimization enabled');
    
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
            return;
        }
        
        // Store original function
        originalCheckForExistingData = TagManager.checkForExistingData;
        
        // Replace with optimized version
        TagManager.checkForExistingData = async function() {
            console.log('⚡ Optimized checkForExistingData called');
            
            // CRITICAL: Check cache FIRST before any API calls
            const cachedTags = this.loadAvailableTagsFromCache();
            if (cachedTags && cachedTags.length > 0) {
                console.log(`⚡ INSTANT: Loaded ${cachedTags.length} tags from cache - skipping API call`);
                // Render cached tags immediately
                this.state.tags = [...cachedTags];
                this.state.originalTags = [...cachedTags];
                this._updateAvailableTags(cachedTags, null);
                
                // Hide splash immediately
                if (AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                
                // Load fresh data in background (non-blocking)
                setTimeout(async () => {
                    try {
                        const response = await fetch('/api/initial-data');
                        if (response.ok) {
                            const data = await response.json();
                            if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                                console.log(`⚡ Background: Updated with ${data.available_tags.length} fresh tags`);
                                this.state.tags = [...data.available_tags];
                                this.state.originalTags = [...data.available_tags];
                                this._updateAvailableTags(data.available_tags, null);
                            }
                        }
                    } catch (error) {
                        console.log('Background data refresh failed (non-critical):', error.message);
                    }
                }, 100);
                
                return;
            }
            
            // Show UI immediately - don't block on data loading
            AppLoadingSplash.updateProgress(50, 'UI Ready - Loading data in background...');
            
            // Hide splash after 500ms, even if data isn't loaded yet (faster UI)
            setTimeout(() => {
                if (AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    console.log('⚡ Splash hidden - UI is interactive');
                }
                // Also hide action splash if it's showing
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
            }, 500);
            
            // Load data in background (non-blocking)
            try {
                const response = await fetch('/api/initial-data');
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                        console.log(`⚡ Loaded ${data.available_tags.length} tags in background`);
                        
                        // Update state immediately
                        this.state.tags = [...data.available_tags];
                        this.state.originalTags = [...data.available_tags];
                        
                        // Update UI with loaded data IMMEDIATELY (no debounce for initial load)
                        // Use _updateAvailableTags directly to avoid debounce delay
                        this._updateAvailableTags(data.available_tags, null);
                        
                        // Force hide splash immediately - don't wait for tags to render
                        if (this.hideActionSplash) {
                            this.hideActionSplash();
                        }
                        if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                            AppLoadingSplash.stopAutoAdvance();
                            AppLoadingSplash.complete();
                        }
                        
                        // Verify tags rendered (non-blocking check)
                        setTimeout(() => {
                            const container = document.getElementById('availableTags');
                            if (container) {
                                const tagItems = container.querySelectorAll('.tag-item');
                                if (tagItems.length > 0) {
                                    console.log(`⚡ Tags rendered (${tagItems.length} items)`);
                                }
                            }
                        }, 100);
                        
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
                        console.log('⚡ No initial data available - ready for file upload');
                        // FIXED: Don't load test data - keep UI empty for upload
                        this.initializeEmptyState();
                    }
                } else {
                    console.log('⚡ Initial data endpoint error - ready for file upload');
                    // FIXED: Don't load test data - keep UI empty for upload
                    this.initializeEmptyState();
                }
            } catch (error) {
                console.log('⚡ Initial data load error - UI remains interactive:', error.message);
                // Don't load test data on timeout - just leave UI ready for upload
                this.initializeEmptyState();
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

