/**
 * Tag Count Fix - Resolves mismatch between available tags and expected matches
 * Fixes aggressive filtering and deduplication issues
 */

(function() {
    'use strict';
    
    console.log('🔧 Tag Count Fix Loading...');
    
    // Tag count fix configuration
    const TAG_FIX_CONFIG = {
        DEBUG_MODE: true,
        LOG_FILTERING: true,
        PRESERVE_ALL_TAGS: true,
        MIN_TAG_COUNT: 30  // Minimum expected tag count
    };
    
    // Tag count fix state
    const TagFixState = {
        originalTagCount: 0,
        filteredTagCount: 0,
        filteredOutTags: [],
        deduplicationIssues: [],
        lastFixTime: 0
    };
    
    // Utility functions
    const Utils = {
        logTagFix(message, data = null) {
            if (TAG_FIX_CONFIG.DEBUG_MODE) {
                console.log(`🔧 TAG FIX: ${message}`, data || '');
            }
        },
        
        logFiltering(tag, reason) {
            if (TAG_FIX_CONFIG.LOG_FILTERING) {
                console.log(`🚫 FILTERED OUT: ${tag} - Reason: ${reason}`);
            }
        },
        
        isTagValid(tag) {
            // More lenient validation - only filter out obvious invalid tags
            const productName = tag['Product Name*'] || tag.ProductName || tag.Description || '';
            const productType = tag['Product Type*'] || tag.ProductType || '';
            const weight = tag['Weight*'] || tag.Weight || '';
            
            // Only filter out truly invalid tags
            if (!productName || productName.trim() === '') {
                return false;
            }
            
            // Don't filter out samples unless explicitly marked as trade samples
            if (productName.toLowerCase().includes('sample') && 
                !productName.toLowerCase().includes('trade sample')) {
                return true; // Keep regular samples
            }
            
            // Don't filter out based on weight unless it's clearly invalid
            if (weight === '-1g' || weight === '0g' || weight === '') {
                return true; // Keep even if weight is missing
            }
            
            return true;
        },
        
        createUniqueKey(tag) {
            // Create a more specific unique key to avoid over-deduplication
            const productName = tag['Product Name*'] || tag.ProductName || tag.Description || '';
            const vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || '';
            const brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || '';
            const weight = tag['Weight*'] || tag.Weight || tag['WeightUnits'] || '';
            const productType = tag['Product Type*'] || tag.ProductType || '';
            
            // Include more fields to make the key more specific
            return `${productName}|${vendor}|${brand}|${weight}|${productType}`;
        }
    };
    
    // Tag Filtering Fix
    const TagFilteringFix = {
        init() {
            console.log('🔍 Initializing Tag Filtering Fix...');
            this.overrideTagFiltering();
            this.setupTagCountMonitoring();
        },
        
        overrideTagFiltering() {
            // Override TagManager's organizeBrandCategories to be less aggressive
            if (window.TagManager && window.TagManager.organizeBrandCategories) {
                const originalOrganize = window.TagManager.organizeBrandCategories;
                
                window.TagManager.organizeBrandCategories = function(tags) {
                    Utils.logTagFix(`Organizing ${tags.length} tags`);
                    
                    // Store original count
                    TagFixState.originalTagCount = tags.length;
                    
                    // Apply less aggressive filtering
                    const filteredTags = this.filterTagsLessAggressively(tags);
                    
                    // Store filtered count
                    TagFixState.filteredTagCount = filteredTags.length;
                    
                    Utils.logTagFix(`Filtered tags: ${TagFixState.originalTagCount} → ${TagFixState.filteredTagCount}`);
                    
                    // Call original function with filtered tags
                    return originalOrganize.call(this, filteredTags);
                };
            }
        },
        
        filterTagsLessAggressively(tags) {
            const seenKeys = new Set();
            const filteredTags = [];
            let duplicatesRemoved = 0;
            
            for (const tag of tags) {
                // Apply more lenient validation
                if (!Utils.isTagValid(tag)) {
                    Utils.logFiltering(tag['Product Name*'] || 'Unknown', 'Failed validation');
                    continue;
                }
                
                // Create unique key
                const uniqueKey = Utils.createUniqueKey(tag);
                
                // Only remove if it's a true duplicate (same key)
                if (seenKeys.has(uniqueKey)) {
                    duplicatesRemoved++;
                    Utils.logTagFix(`Removing duplicate: ${tag['Product Name*'] || 'Unknown'}`);
                    continue;
                }
                
                seenKeys.add(uniqueKey);
                filteredTags.push(tag);
            }
            
            Utils.logTagFix(`Deduplication: Removed ${duplicatesRemoved} true duplicates`);
            return filteredTags;
        },
        
        setupTagCountMonitoring() {
            // Monitor tag counts and alert if there's a significant drop
            setInterval(() => {
                this.checkTagCounts();
            }, 10000); // Check every 10 seconds
        },
        
        checkTagCounts() {
            const availableTags = document.querySelectorAll('#availableTags .tag-checkbox');
            const currentCount = availableTags.length;
            
            if (currentCount < TAG_FIX_CONFIG.MIN_TAG_COUNT) {
                console.warn(`⚠️ Low tag count detected: ${currentCount} (expected: ${TAG_FIX_CONFIG.MIN_TAG_COUNT}+)`);
                this.attemptTagCountFix();
            }
        },
        
        attemptTagCountFix() {
            console.log('🔧 Attempting to fix low tag count...');
            
            // Clear cache to force refresh
            if (window.sessionStorage) {
                window.sessionStorage.removeItem('available_tags_cache');
            }
            
            // Trigger tag refresh
            if (window.TagManager && window.TagManager.loadAvailableTags) {
                window.TagManager.loadAvailableTags();
            }
        }
    };
    
    // Backend Tag Count Fix
    const BackendTagCountFix = {
        init() {
            console.log('🔍 Initializing Backend Tag Count Fix...');
            this.overrideAvailableTagsAPI();
            this.setupCacheBusting();
        },
        
        overrideAvailableTagsAPI() {
            // Override fetch to add debugging for available-tags API
            const originalFetch = window.fetch;
            
            window.fetch = function(url, options) {
                if (url.includes('/api/available-tags')) {
                    return originalFetch(url, options).then(response => {
                        return response.clone().json().then(data => {
                            Utils.logTagFix(`API Response: ${data.total_count || data.tags?.length || 0} tags`);
                            
                            // Check if count is too low
                            const tagCount = data.total_count || data.tags?.length || 0;
                            if (tagCount < TAG_FIX_CONFIG.MIN_TAG_COUNT) {
                                console.warn(`⚠️ Low tag count from API: ${tagCount}`);
                                BackendTagCountFix.handleLowTagCount(data);
                            }
                            
                            return response;
                        });
                    });
                }
                return originalFetch(url, options);
            };
        },
        
        handleLowTagCount(data) {
            console.log('🔧 Handling low tag count from API...');
            
            // Add cache busting parameter
            const cacheBustUrl = `/api/available-tags?cache_bust=${Date.now()}`;
            
            fetch(cacheBustUrl)
                .then(response => response.json())
                .then(freshData => {
                    const freshCount = freshData.total_count || freshData.tags?.length || 0;
                    Utils.logTagFix(`Fresh API Response: ${freshCount} tags`);
                    
                    if (freshCount > data.total_count) {
                        console.log(`✅ Fresh data has more tags: ${freshCount} vs ${data.total_count}`);
                        // Update the UI with fresh data
                        if (window.TagManager && window.TagManager._updateAvailableTags) {
                            window.TagManager._updateAvailableTags(freshData.tags);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching fresh tag data:', error);
                });
        },
        
        setupCacheBusting() {
            // Add cache busting to tag-related requests
            const originalFetch = window.fetch;
            
            window.fetch = function(url, options) {
                if (url.includes('/api/available-tags') && !url.includes('cache_bust')) {
                    const separator = url.includes('?') ? '&' : '?';
                    url = `${url}${separator}cache_bust=${Date.now()}`;
                }
                return originalFetch(url, options);
            };
        }
    };
    
    // Tag Count Display Fix
    const TagCountDisplayFix = {
        init() {
            console.log('🔍 Initializing Tag Count Display Fix...');
            this.overrideCountDisplays();
            this.setupCountMonitoring();
        },
        
        overrideCountDisplays() {
            // Override count update functions to be more accurate
            if (window.TagManager && window.TagManager.updateTagCount) {
                const originalUpdateCount = window.TagManager.updateTagCount;
                
                window.TagManager.updateTagCount = function(type, count) {
                    Utils.logTagFix(`Updating ${type} count to: ${count}`);
                    
                    // Ensure count is reasonable
                    if (type === 'available' && count < TAG_FIX_CONFIG.MIN_TAG_COUNT) {
                        console.warn(`⚠️ Available tag count seems low: ${count}`);
                        // Try to get a more accurate count
                        const actualCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
                        if (actualCount > count) {
                            count = actualCount;
                            Utils.logTagFix(`Corrected available count to: ${count}`);
                        }
                    }
                    
                    return originalUpdateCount.call(this, type, count);
                };
            }
        },
        
        setupCountMonitoring() {
            // Monitor count displays and fix if needed
            setInterval(() => {
                this.monitorCountDisplays();
            }, 5000);
        },
        
        monitorCountDisplays() {
            const availableCountEl = document.querySelector('.available-count, #availableCount');
            const actualCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
            
            if (availableCountEl) {
                const displayedCount = parseInt(availableCountEl.textContent) || 0;
                
                if (Math.abs(displayedCount - actualCount) > 5) {
                    console.warn(`⚠️ Count mismatch: Displayed ${displayedCount}, Actual ${actualCount}`);
                    availableCountEl.textContent = actualCount;
                    Utils.logTagFix(`Fixed count display: ${displayedCount} → ${actualCount}`);
                }
            }
        }
    };
    
    // Main Tag Count Fix
    const TagCountFix = {
        init() {
            console.log('🖥️ Initializing Tag Count Fix...');
            
            // Initialize components
            TagFilteringFix.init();
            BackendTagCountFix.init();
            TagCountDisplayFix.init();
            
            // Setup global monitoring
            this.setupGlobalMonitoring();
            
            console.log('✅ Tag Count Fix initialized successfully');
        },
        
        setupGlobalMonitoring() {
            // Monitor for tag count issues globally
            setInterval(() => {
                this.performGlobalCheck();
            }, 15000);
        },
        
        performGlobalCheck() {
            const availableTags = document.querySelectorAll('#availableTags .tag-checkbox');
            const currentCount = availableTags.length;
            
            Utils.logTagFix(`Global check: ${currentCount} available tags`);
            
            if (currentCount < TAG_FIX_CONFIG.MIN_TAG_COUNT) {
                console.warn(`⚠️ Global check: Low tag count detected: ${currentCount}`);
                this.triggerTagRefresh();
            }
        },
        
        triggerTagRefresh() {
            console.log('🔄 Triggering tag refresh...');
            
            // Clear all caches
            if (window.sessionStorage) {
                window.sessionStorage.clear();
            }
            
            // Force refresh available tags
            if (window.TagManager && window.TagManager.loadAvailableTags) {
                window.TagManager.loadAvailableTags();
            }
        },
        
        // Public API
        getTagCounts() {
            return {
                available: document.querySelectorAll('#availableTags .tag-checkbox').length,
                selected: window.TagManager?.state?.selectedTags?.size || 0,
                original: TagFixState.originalTagCount,
                filtered: TagFixState.filteredTagCount
            };
        },
        
        forceRefresh() {
            this.triggerTagRefresh();
        },
        
        getFilteringStats() {
            return {
                filteredOut: TagFixState.filteredOutTags.length,
                deduplicationIssues: TagFixState.deduplicationIssues.length,
                lastFixTime: TagFixState.lastFixTime
            };
        }
    };
    
    // Auto-initialize
    TagCountFix.init();
    
    // Expose for debugging
    window.TagCountFix = TagCountFix;
    window.TagFixState = TagFixState;
    
    console.log('✅ Tag Count Fix loaded successfully');
})();
