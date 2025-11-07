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
            
            // Hide splash after 1 second, even if data isn't loaded yet
            setTimeout(() => {
                if (AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    console.log('⚡ Splash hidden - UI is interactive');
                }
            }, 1000);
            
            // Load data in background (non-blocking)
            try {
                // Add shorter timeout for faster failure
                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('Quick timeout')), 3000); // 3 second timeout
                });
                
                const response = await Promise.race([
                    fetch('/api/initial-data'),
                    timeoutPromise
                ]);
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                        console.log(`⚡ Loaded ${data.available_tags.length} tags in background`);
                        
                        // Update UI with loaded data
                        this.debouncedUpdateAvailableTags(data.available_tags, null);
                        
                        // Restore selected tags
                        await this.fetchAndUpdateSelectedTags();
                        
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
                console.log('⚡ Quick timeout or error - UI remains interactive:', error.message);
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

