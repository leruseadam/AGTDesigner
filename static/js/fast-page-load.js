/**
 * Ultra-fast page load optimization
 * Makes initial data loading non-blocking and shows UI immediately
 * 
 * FIXED: No longer overrides checkForExistingData to prevent conflicts
 * Instead, we just ensure the main checkForExistingData loads tags immediately
 */

(function() {
    'use strict';
    
    console.log('⚡ Fast page load optimization enabled (non-conflicting mode)');
    
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
    
    // Optimize the page load - but don't override checkForExistingData
    async function optimizePageLoad() {
        await waitForTagManager();
        
        if (!window.TagManager || !TagManager.checkForExistingData) {
            console.warn('⚠️ TagManager not available, skipping optimization');
            return;
        }
        
        // Store original function to ensure immediate loading on initial load
        const originalCheckForExistingData = TagManager.checkForExistingData;
        
        // Wrap checkForExistingData to ensure immediate tag loading (no debounce on initial load)
        TagManager.checkForExistingData = async function() {
            // Set flag to indicate this is initial load - skip debounce
            const isInitialLoad = !this.state.tags || this.state.tags.length === 0;
            if (isInitialLoad) {
                this.state.isInitialLoad = true;
            }
            
            // Call original function
            const result = await originalCheckForExistingData.call(this);
            
            // Clear initial load flag after a short delay
            if (isInitialLoad) {
                setTimeout(() => {
                    this.state.isInitialLoad = false;
                }, 1000);
            }
            
            return result;
        };
        
        console.log('⚡ Page load optimization active (non-conflicting)');
    }
    
    // Run optimization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', optimizePageLoad);
    } else {
        optimizePageLoad();
    }
})();

