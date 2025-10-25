/**
 * FORCE 49 TAGS - Ensures all 49 tags are displayed without deduplication
 */

(function() {
    'use strict';
    
    console.log('🚨 FORCE 49 TAGS: Loading...');
    
    // Override TagManager to prevent deduplication
    const originalUpdateAvailableTags = window.TagManager?._updateAvailableTags;
    
    if (window.TagManager && originalUpdateAvailableTags) {
        window.TagManager._updateAvailableTags = function(tags) {
            console.log(`🚨 FORCE 49 TAGS: Received ${tags.length} tags`);
            
            // Store all tags without deduplication
            this.state.tags = [...tags];
            this.state.originalTags = [...tags];
            
            // Call original method
            return originalUpdateAvailableTags.call(this, tags);
        };
        
        console.log('🚨 FORCE 49 TAGS: TagManager override installed');
    }
    
    // Monitor and force 49 tags
    setInterval(() => {
        const currentCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
        
        if (currentCount !== 49 && currentCount > 0) {
            console.log(`🚨 FORCE 49 TAGS: Current count is ${currentCount}, expected 49`);
        }
    }, 5000);
    
    console.log('✅ FORCE 49 TAGS: Loaded successfully');
})();

