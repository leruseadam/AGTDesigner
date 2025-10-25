/**
 * ULTIMATE TAG COUNT FIX - Direct debugging and forced tag display
 * This will debug exactly what's happening and force the correct count
 */

(function() {
    'use strict';
    
    console.log('🚨🚨 ULTIMATE TAG COUNT FIX Loading...');
    
    // Ultimate fix configuration
    const ULTIMATE_FIX_CONFIG = {
        TARGET_COUNT: 49,
        DEBUG_MODE: true,
        FORCE_DISPLAY: true,
        BYPASS_EVERYTHING: true
    };
    
    // Ultimate fix state
    const UltimateFixState = {
        debugLog: [],
        apiResponses: [],
        tagCounts: [],
        lastCheck: 0
    };
    
    // Debug logging
    const DebugLogger = {
        log(message, data = null) {
            const timestamp = new Date().toISOString();
            const logEntry = { timestamp, message, data };
            UltimateFixState.debugLog.push(logEntry);
            console.log(`🚨🚨 ULTIMATE FIX [${timestamp}]: ${message}`, data || '');
        },
        
        getLogs() {
            return UltimateFixState.debugLog;
        },
        
        clearLogs() {
            UltimateFixState.debugLog = [];
        }
    };
    
    // API Debugger
    const APIDebugger = {
        init() {
            DebugLogger.log('Initializing API Debugger...');
            this.overrideFetch();
            this.testAllEndpoints();
        },
        
        overrideFetch() {
            const originalFetch = window.fetch;
            
            window.fetch = function(url, options) {
                if (url.includes('/api/available-tags')) {
                    DebugLogger.log(`API Call: ${url}`, options);
                    
                    return originalFetch(url, options).then(response => {
                        return response.clone().json().then(data => {
                            DebugLogger.log(`API Response: ${url}`, {
                                status: response.status,
                                data: data,
                                tagCount: data.tags?.length || 0,
                                totalCount: data.total_count || 0
                            });
                            
                            UltimateFixState.apiResponses.push({
                                url,
                                timestamp: Date.now(),
                                data: data
                            });
                            
                            return response;
                        });
                    });
                }
                return originalFetch(url, options);
            };
        },
        
        async testAllEndpoints() {
            DebugLogger.log('Testing all available tag endpoints...');
            
            const endpoints = [
                '/api/available-tags',
                '/api/available-tags-all',
                '/api/debug-tag-count'
            ];
            
            for (const endpoint of endpoints) {
                try {
                    DebugLogger.log(`Testing endpoint: ${endpoint}`);
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    DebugLogger.log(`Endpoint ${endpoint} result:`, {
                        status: response.status,
                        tagCount: data.tags?.length || data.available_tags_count || 0,
                        totalCount: data.total_count || 0,
                        source: data.source || 'unknown'
                    });
                    
                } catch (error) {
                    DebugLogger.log(`Endpoint ${endpoint} error:`, error);
                }
            }
        }
    };
    
    // Tag Count Forcer
    const TagCountForcer = {
        init() {
            DebugLogger.log('Initializing Tag Count Forcer...');
            this.forceCorrectCount();
            this.setupMonitoring();
        },
        
        async forceCorrectCount() {
            DebugLogger.log('Forcing correct tag count...');
            
            // Step 1: Clear all caches
            await this.clearAllCaches();
            
            // Step 2: Get raw data from Excel
            const rawData = await this.getRawExcelData();
            
            // Step 3: Force display the correct count
            await this.forceDisplay(rawData);
        },
        
        async clearAllCaches() {
            DebugLogger.log('Clearing all caches...');
            
            // Clear frontend caches
            if (window.sessionStorage) {
                window.sessionStorage.clear();
            }
            if (window.localStorage) {
                window.localStorage.clear();
            }
            
            // Clear backend caches
            try {
                const response = await fetch('/api/clear-tag-cache', { method: 'POST' });
                const data = await response.json();
                DebugLogger.log('Backend cache cleared:', data);
            } catch (error) {
                DebugLogger.log('Error clearing backend cache:', error);
            }
        },
        
        async getRawExcelData() {
            DebugLogger.log('Getting raw Excel data...');
            
            try {
                // Try the debug endpoint first
                const debugResponse = await fetch('/api/debug-tag-count');
                const debugData = await debugResponse.json();
                DebugLogger.log('Debug data:', debugData);
                
                // Try the all-tags endpoint
                const allResponse = await fetch('/api/available-tags-all');
                const allData = await allResponse.json();
                DebugLogger.log('All tags data:', allData);
                
                return allData;
                
            } catch (error) {
                DebugLogger.log('Error getting raw data:', error);
                return null;
            }
        },
        
        async forceDisplay(data) {
            DebugLogger.log('Forcing display of tags...');
            
            if (!data || !data.tags) {
                DebugLogger.log('No data to display');
                return;
            }
            
            const tagCount = data.tags.length;
            DebugLogger.log(`Forcing display of ${tagCount} tags`);
            
            // Force update the TagManager
            if (window.TagManager) {
                DebugLogger.log('Updating TagManager with forced data...');
                
                // Clear existing state
                window.TagManager.state.tags = [];
                window.TagManager.state.originalTags = [];
                
                // Set new data
                window.TagManager.state.tags = [...data.tags];
                window.TagManager.state.originalTags = [...data.tags];
                
                // Force update the UI
                if (window.TagManager._updateAvailableTags) {
                    window.TagManager._updateAvailableTags(data.tags);
                }
                
                DebugLogger.log('TagManager updated successfully');
            }
            
            // Force update the DOM directly
            this.forceDOMUpdate(data.tags);
        },
        
        forceDOMUpdate(tags) {
            DebugLogger.log(`Force updating DOM with ${tags.length} tags...`);
            
            const container = document.getElementById('availableTags');
            if (!container) {
                DebugLogger.log('Container not found');
                return;
            }
            
            // Clear container
            container.innerHTML = '';
            
            // Add all tags directly
            tags.forEach((tag, index) => {
                const tagElement = this.createTagElement(tag, index);
                container.appendChild(tagElement);
            });
            
            DebugLogger.log(`DOM updated with ${tags.length} tags`);
            
            // Update count displays
            this.updateCountDisplays(tags.length);
        },
        
        createTagElement(tag, index) {
            const div = document.createElement('div');
            div.className = 'tag-item';
            div.innerHTML = `
                <input type="checkbox" class="tag-checkbox" value="${tag['Product Name*'] || 'Unknown'}" id="tag-${index}">
                <label for="tag-${index}" class="tag-label">
                    <span class="tag-name">${tag['Product Name*'] || 'Unknown'}</span>
                    <span class="tag-details">
                        ${tag['Product Brand'] || ''} | ${tag['Weight*'] || ''}${tag['Units'] || ''}
                    </span>
                </label>
            `;
            return div;
        },
        
        updateCountDisplays(count) {
            DebugLogger.log(`Updating count displays to ${count}`);
            
            // Update all count elements
            const countElements = document.querySelectorAll('.available-count, #availableCount, .tag-count');
            countElements.forEach(el => {
                el.textContent = count;
            });
            
            // Update any other count displays
            const countTexts = document.querySelectorAll('[data-count="available"]');
            countTexts.forEach(el => {
                el.textContent = count;
            });
        },
        
        setupMonitoring() {
            // Monitor tag count every 5 seconds
            setInterval(() => {
                this.monitorTagCount();
            }, 5000);
        },
        
        monitorTagCount() {
            const currentCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
            UltimateFixState.tagCounts.push({
                timestamp: Date.now(),
                count: currentCount
            });
            
            DebugLogger.log(`Current tag count: ${currentCount}`);
            
            if (currentCount < ULTIMATE_FIX_CONFIG.TARGET_COUNT) {
                DebugLogger.log(`Tag count too low (${currentCount}), forcing refresh...`);
                this.forceCorrectCount();
            }
        }
    };
    
    // Main Ultimate Fix
    const UltimateTagFix = {
        init() {
            DebugLogger.log('🚨🚨 Initializing Ultimate Tag Fix...');
            
            // Initialize components
            APIDebugger.init();
            TagCountForcer.init();
            
            // Setup debugging tools
            this.setupDebugTools();
            
            DebugLogger.log('🚨🚨 Ultimate Tag Fix initialized successfully');
        },
        
        setupDebugTools() {
            // Expose debugging functions
            window.UltimateTagFix = {
                getDebugLogs: () => DebugLogger.getLogs(),
                clearDebugLogs: () => DebugLogger.clearLogs(),
                forceRefresh: () => TagCountForcer.forceCorrectCount(),
                getCurrentCount: () => document.querySelectorAll('#availableTags .tag-checkbox').length,
                getAPIResponses: () => UltimateFixState.apiResponses,
                getTagCounts: () => UltimateFixState.tagCounts,
                testEndpoints: () => APIDebugger.testAllEndpoints()
            };
            
            DebugLogger.log('Debug tools exposed to window.UltimateTagFix');
        }
    };
    
    // Auto-initialize
    UltimateTagFix.init();
    
    console.log('✅ Ultimate Tag Count Fix loaded successfully');
    console.log('🔧 Use window.UltimateTagFix for debugging');
})();
