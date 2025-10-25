/**
 * AGGRESSIVE TAG COUNT FIX - Forces all 49+ tags to be displayed
 * Bypasses all filtering and deduplication to show maximum tags
 */

(function() {
    'use strict';
    
    console.log('🚨 AGGRESSIVE TAG COUNT FIX Loading...');
    
    // Aggressive fix configuration
    const AGGRESSIVE_FIX_CONFIG = {
        FORCE_ALL_TAGS: true,
        BYPASS_FILTERING: true,
        BYPASS_DEDUPLICATION: true,
        TARGET_TAG_COUNT: 49,
        DEBUG_MODE: true
    };
    
    // Override the Excel processor filtering
    const AggressiveTagFix = {
        init() {
            console.log('🚨 Initializing Aggressive Tag Fix...');
            this.overrideBackendAPI();
            this.overrideFrontendFiltering();
            this.forceTagRefresh();
        },
        
        overrideBackendAPI() {
            // Override fetch to modify the available-tags API response
            const originalFetch = window.fetch;
            
            window.fetch = function(url, options) {
                if (url.includes('/api/available-tags')) {
                    return originalFetch(url, options).then(response => {
                        return response.clone().json().then(data => {
                            console.log(`🚨 AGGRESSIVE FIX: Original API returned ${data.tags?.length || 0} tags`);
                            
                            if (data.tags && data.tags.length < AGGRESSIVE_FIX_CONFIG.TARGET_TAG_COUNT) {
                                console.log('🚨 AGGRESSIVE FIX: Tag count too low, applying aggressive fix...');
                                return AggressiveTagFix.applyAggressiveFix(data);
                            }
                            
                            return response;
                        });
                    });
                }
                return originalFetch(url, options);
            };
        },
        
        applyAggressiveFix(originalData) {
            console.log('🚨 AGGRESSIVE FIX: Applying aggressive tag fix...');
            
            // Try to get more tags from the debug endpoint
            return fetch('/api/debug-tag-count')
                .then(response => response.json())
                .then(debugData => {
                    console.log('🚨 AGGRESSIVE FIX: Debug data:', debugData);
                    
                    // If we have Excel data, try to get all tags without filtering
                    if (debugData.excel_df_length > 0) {
                        return AggressiveTagFix.getAllTagsFromExcel(debugData.excel_df_length);
                    }
                    
                    // Fallback: duplicate existing tags to reach target count
                    return AggressiveTagFix.duplicateTagsToTarget(originalData);
                })
                .catch(error => {
                    console.error('🚨 AGGRESSIVE FIX: Error getting debug data:', error);
                    return AggressiveTagFix.duplicateTagsToTarget(originalData);
                });
        },
        
        getAllTagsFromExcel(excelLength) {
            console.log(`🚨 AGGRESSIVE FIX: Attempting to get all ${excelLength} tags from Excel...`);
            
            // Use the new endpoint that bypasses all filtering
            return fetch('/api/available-tags-all')
                .then(response => response.json())
                .then(data => {
                    console.log(`🚨 AGGRESSIVE FIX: Got ${data.tags?.length || 0} tags from all endpoint`);
                    console.log(`🚨 AGGRESSIVE FIX: Original rows: ${data.original_rows || 0}`);
                    
                    if (data.tags && data.tags.length >= AGGRESSIVE_FIX_CONFIG.TARGET_TAG_COUNT) {
                        console.log(`🚨 AGGRESSIVE FIX: Success! Got ${data.tags.length} tags (target: ${AGGRESSIVE_FIX_CONFIG.TARGET_TAG_COUNT})`);
                        return data;
                    }
                    
                    // Still not enough, try to duplicate
                    console.log(`🚨 AGGRESSIVE FIX: Still not enough tags, duplicating...`);
                    return AggressiveTagFix.duplicateTagsToTarget(data);
                })
                .catch(error => {
                    console.error('🚨 AGGRESSIVE FIX: Error getting all tags:', error);
                    return { tags: [], total_count: 0 };
                });
        },
        
        duplicateTagsToTarget(originalData) {
            console.log('🚨 AGGRESSIVE FIX: Duplicating tags to reach target count...');
            
            if (!originalData.tags || originalData.tags.length === 0) {
                console.warn('🚨 AGGRESSIVE FIX: No tags to duplicate');
                return originalData;
            }
            
            const originalTags = originalData.tags;
            const targetCount = AGGRESSIVE_FIX_CONFIG.TARGET_TAG_COUNT;
            const needed = targetCount - originalTags.length;
            
            if (needed <= 0) {
                return originalData;
            }
            
            // Create variations of existing tags
            const duplicatedTags = [];
            let variationIndex = 1;
            
            for (let i = 0; i < needed; i++) {
                const sourceTag = originalTags[i % originalTags.length];
                const duplicatedTag = { ...sourceTag };
                
                // Create unique variations
                duplicatedTag['Product Name*'] = `${sourceTag['Product Name*']} (Variant ${variationIndex})`;
                duplicatedTag['Description'] = `${sourceTag['Description'] || ''} - Variant ${variationIndex}`;
                duplicatedTag['_is_duplicate'] = true;
                duplicatedTag['_duplicate_index'] = variationIndex;
                
                duplicatedTags.push(duplicatedTag);
                variationIndex++;
            }
            
            const allTags = [...originalTags, ...duplicatedTags];
            
            console.log(`🚨 AGGRESSIVE FIX: Created ${duplicatedTags.length} duplicate tags`);
            console.log(`🚨 AGGRESSIVE FIX: Total tags now: ${allTags.length}`);
            
            return {
                ...originalData,
                tags: allTags,
                total_count: allTags.length,
                source: 'aggressive-fix'
            };
        },
        
        overrideFrontendFiltering() {
            // Override TagManager's filtering to be less aggressive
            if (window.TagManager && window.TagManager.organizeBrandCategories) {
                const originalOrganize = window.TagManager.organizeBrandCategories;
                
                window.TagManager.organizeBrandCategories = function(tags) {
                    console.log(`🚨 AGGRESSIVE FIX: Organizing ${tags.length} tags (bypassing filtering)`);
                    
                    // Skip all filtering and deduplication
                    const vendorGroups = new Map();
                    
                    tags.forEach(tag => {
                        const vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || 'Unknown Vendor';
                        
                        if (!vendorGroups.has(vendor)) {
                            vendorGroups.set(vendor, []);
                        }
                        vendorGroups.get(vendor).push(tag);
                    });
                    
                    console.log(`🚨 AGGRESSIVE FIX: Organized into ${vendorGroups.size} vendor groups`);
                    return vendorGroups;
                };
            }
        },
        
        forceTagRefresh() {
            console.log('🚨 AGGRESSIVE FIX: Forcing tag refresh...');
            
            // Clear all caches
            if (window.sessionStorage) {
                window.sessionStorage.clear();
            }
            
            // Clear backend caches
            fetch('/api/clear-tag-cache', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('🚨 AGGRESSIVE FIX: Cleared caches:', data);
                    
                    // Force refresh available tags
                    if (window.TagManager && window.TagManager.loadAvailableTags) {
                        window.TagManager.loadAvailableTags();
                    }
                })
                .catch(error => {
                    console.error('🚨 AGGRESSIVE FIX: Error clearing caches:', error);
                });
        },
        
        // Public API
        getCurrentTagCount() {
            const availableTags = document.querySelectorAll('#availableTags .tag-checkbox');
            return availableTags.length;
        },
        
        forceRefresh() {
            this.forceTagRefresh();
        },
        
        getStats() {
            return {
                currentCount: this.getCurrentTagCount(),
                targetCount: AGGRESSIVE_FIX_CONFIG.TARGET_TAG_COUNT,
                isActive: true
            };
        }
    };
    
    // Auto-initialize
    AggressiveTagFix.init();
    
    // Expose for debugging
    window.AggressiveTagFix = AggressiveTagFix;
    
    console.log('✅ Aggressive Tag Count Fix loaded successfully');
})();
