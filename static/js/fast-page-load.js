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
            
            // Show UI immediately - don't block on data loading
            AppLoadingSplash.updateProgress(50, 'UI Ready - Loading data in background...');
            
            // Show tag loading splash immediately BEFORE fetching data (for page reloads)
            // This ensures splash appears even if data loads very quickly
            let tagSplashShown = false;
            if (this.showTagLoadingSplash) {
                this.showTagLoadingSplash('Loading tags from session...');
                tagSplashShown = true;
            }
            if (this.showActionSplash) {
                this.showActionSplash('Loading tags...');
            }
            
            // Hide app splash after 500ms, but keep tag loading splash visible
            setTimeout(() => {
                if (AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    console.log('⚡ App splash hidden - UI is interactive');
                }
                // Don't hide tag loading splash here - it will be hidden after tags appear
            }, 500);
            
            // Load data in background (non-blocking)
            try {
                const response = await fetch('/api/initial-data');
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                        console.log(`⚡ Loaded ${data.available_tags.length} tags in background`);
                        
                        // Update tag loading splash message now that data is loaded
                        // (splash is already shown above, just update the message)
                        if (this.showTagLoadingSplash && tagSplashShown) {
                            // Splash already shown, just update message if needed
                            const statusElement = document.getElementById('tagLoadingStatus');
                            if (statusElement) {
                                statusElement.textContent = 'Loading tags...';
                            }
                        } else {
                            // Fallback: show splash if it wasn't shown before
                            if (this.showTagLoadingSplash) {
                                this.showTagLoadingSplash('Loading tags...');
                            }
                            if (this.showActionSplash) {
                                this.showActionSplash('Loading tags...');
                            }
                        }
                        
                        // Update state immediately
                        this.state.tags = [...data.available_tags];
                        this.state.originalTags = [...data.available_tags];
                        
                        // Update UI with loaded data IMMEDIATELY (no debounce for initial load)
                        // Use _updateAvailableTags directly to avoid debounce delay
                        this._updateAvailableTags(data.available_tags, null);
                        
                        // Use _waitForTagsToAppear to properly wait for tags and hide splash
                        // This ensures splash stays visible until tags are actually rendered
                        if (this._waitForTagsToAppear) {
                            this._waitForTagsToAppear();
                        } else {
                            // Fallback: check after a delay if _waitForTagsToAppear is not available
                            setTimeout(() => {
                                const container = document.getElementById('availableTags');
                                if (container) {
                                    const tagItems = container.querySelectorAll('.tag-item');
                                    if (tagItems.length > 0) {
                                        console.log(`⚡ Tags rendered (${tagItems.length} items), hiding splash`);
                                        if (this.hideActionSplash) {
                                            this.hideActionSplash();
                                        }
                                        if (this.hideTagLoadingSplash) {
                                            this.hideTagLoadingSplash();
                                        }
                                        if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                                            AppLoadingSplash.stopAutoAdvance();
                                            AppLoadingSplash.complete();
                                        }
                                    }
                                }
                            }, 500);
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
                            // Update upload notification banner
                            if (window.updateUploadNotificationBanner) {
                                window.updateUploadNotificationBanner();
                            }
                        }
                        
                        console.log('⚡ Background data loading complete');
                    } else {
                        console.log('⚡ No initial data available - ready for file upload');
                        // Hide tag loading splash if no data found
                        if (tagSplashShown) {
                            if (this.hideTagLoadingSplash) {
                                this.hideTagLoadingSplash();
                            }
                            if (this.hideActionSplash) {
                                this.hideActionSplash();
                            }
                        }
                        // FIXED: Don't load test data - keep UI empty for upload
                        this.initializeEmptyState();
                    }
                } else {
                    console.log('⚡ Initial data endpoint error - ready for file upload');
                    // Hide tag loading splash if error occurred
                    if (tagSplashShown) {
                        if (this.hideTagLoadingSplash) {
                            this.hideTagLoadingSplash();
                        }
                        if (this.hideActionSplash) {
                            this.hideActionSplash();
                        }
                    }
                    // FIXED: Don't load test data - keep UI empty for upload
                    this.initializeEmptyState();
                }
            } catch (error) {
                console.log('⚡ Initial data load error - UI remains interactive:', error.message);
                // Hide tag loading splash if error occurred
                if (tagSplashShown) {
                    if (this.hideTagLoadingSplash) {
                        this.hideTagLoadingSplash();
                    }
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                }
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

