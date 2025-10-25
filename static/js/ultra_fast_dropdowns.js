// static/js/ultra_fast_dropdowns.js
// Ultra-Fast Dropdown Performance Optimizer for PC Filter Dropdowns

class UltraFastDropdownManager {
    constructor() {
        this.cache = new Map();
        this.debounceTimers = new Map();
        this.virtualScrollThreshold = 100;
        this.maxVisibleOptions = 50;
        this.cacheDuration = 300000; // 5 minutes
        this.isUpdating = false;
        this.pendingUpdates = new Map();
        
        console.log('🚀 UltraFastDropdownManager initialized');
    }

    // Main optimization function - replaces the slow updateFilters method
    updateFilters(filters, preserveExistingValues = true) {
        if (!filters || this.isUpdating) {
            console.log('🚫 Skipping filter update - no filters or update in progress');
            return;
        }

        this.isUpdating = true;
        const startTime = performance.now();
        
        console.log('⚡ Ultra-fast filter update started:', Object.keys(filters).length, 'filters');

        // Store original filter options to preserve order
        if (!window.TagManager.state.originalFilterOptions.vendor) {
            window.TagManager.state.originalFilterOptions = { ...filters };
        }

        // Map of filter types to their HTML IDs
        const filterFieldMap = {
            vendor: 'vendorFilter',
            brand: 'brandFilter',
            productType: 'productTypeFilter',
            lineage: 'lineageFilter',
            weight: 'weightFilter',
            doh: 'dohFilter',
            highCbd: 'highCbdFilter'
        };

        // Process all dropdowns in parallel using requestAnimationFrame
        const updatePromises = Object.entries(filterFieldMap).map(([filterType, filterId]) => 
            this.updateSingleDropdown(filterType, filterId, filters[filterType] || [], preserveExistingValues)
        );

        Promise.all(updatePromises).then(() => {
            const endTime = performance.now();
            console.log(`✅ Ultra-fast filter update completed in ${(endTime - startTime).toFixed(2)}ms`);
            this.isUpdating = false;
            
            // Process any pending updates
            this.processPendingUpdates();
        }).catch(error => {
            console.error('❌ Error in ultra-fast filter update:', error);
            this.isUpdating = false;
        });
    }

    async updateSingleDropdown(filterType, filterId, fieldValues, preserveExistingValues) {
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                const filterElement = document.getElementById(filterId);
                
                if (!filterElement) {
                    console.warn(`Filter element not found: ${filterId}`);
                    resolve();
                    return;
                }

                // Get current value before updating
                const currentValue = filterElement.value;

                // Optimize options processing
                const optimizedOptions = this.optimizeOptions(fieldValues, filterType);
                
                // Generate optimized HTML
                const optimizedHTML = this.generateOptimizedHTML(
                    optimizedOptions, 
                    currentValue, 
                    preserveExistingValues,
                    filterType
                );

                // Use efficient DOM update
                this.efficientDOMUpdate(filterElement, optimizedHTML, currentValue, preserveExistingValues);
                
                console.log(`⚡ Updated ${filterId} with ${optimizedOptions.length} options`);
                resolve();
            });
        });
    }

    optimizeOptions(fieldValues, filterType) {
        if (!fieldValues || fieldValues.length === 0) return [];

        // Use Set for O(1) deduplication
        const uniqueValues = new Set();
        fieldValues.forEach(value => {
            if (value && value.trim() !== '') {
                uniqueValues.add(value.trim());
            }
        });

        // Convert to array and sort efficiently
        const sortedValues = Array.from(uniqueValues).sort((a, b) => {
            if (filterType === 'lineage') {
                return this.sortLineageOptions(a, b);
            }
            return a.localeCompare(b);
        });

        return sortedValues;
    }

    sortLineageOptions(a, b) {
        const lineageOrder = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA'];
        const aIndex = lineageOrder.indexOf(a.toUpperCase());
        const bIndex = lineageOrder.indexOf(b.toUpperCase());
        
        if (aIndex !== -1 && bIndex !== -1) {
            return aIndex - bIndex;
        }
        return a.localeCompare(b);
    }

    generateOptimizedHTML(options, currentValue, preserveExistingValues, filterType) {
        if (options.length === 0) {
            return '<option value="">All</option>';
        }

        const htmlParts = ['<option value="">All</option>'];

        // Add current value if preserving and not in options
        if (preserveExistingValues && currentValue && !options.includes(currentValue)) {
            htmlParts.push(`<option value="${currentValue}" style="color: #666;">${currentValue}</option>`);
        }

        // Use virtual scrolling for large lists
        if (options.length > this.virtualScrollThreshold) {
            return this.generateVirtualScrollHTML(options, htmlParts);
        } else {
            return this.generateStandardHTML(options, htmlParts);
        }
    }

    generateVirtualScrollHTML(options, htmlParts) {
        // Add first batch of options
        const visibleOptions = options.slice(0, this.maxVisibleOptions);
        visibleOptions.forEach(option => {
            htmlParts.push(this.formatOption(option));
        });

        // Add "Load More" option if there are more items
        if (options.length > this.maxVisibleOptions) {
            htmlParts.push(`<option value="__load_more__" style="color: #007bff; font-style: italic;">... Load More (${options.length - this.maxVisibleOptions} more)</option>`);
        }

        return htmlParts.join('');
    }

    generateStandardHTML(options, htmlParts) {
        options.forEach(option => {
            htmlParts.push(this.formatOption(option));
        });
        return htmlParts.join('');
    }

    formatOption(option) {
        if (option === 'rso/co2 tankers') {
            return '<option value="rso/co2 tankers" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>';
        }
        return `<option value="${option}">${option}</option>`;
    }

    efficientDOMUpdate(element, html, currentValue, preserveExistingValues) {
        // Use DocumentFragment for efficient DOM manipulation
        const fragment = document.createDocumentFragment();
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Clear existing options efficiently
        element.innerHTML = '';
        
        // Add new options
        while (tempDiv.firstChild) {
            element.appendChild(tempDiv.firstChild);
        }

        // Restore value efficiently
        if (preserveExistingValues && currentValue) {
            if (element.querySelector(`option[value="${currentValue}"]`)) {
                element.value = currentValue;
            } else if (currentValue !== '') {
                // Add current value back if not found
                const option = document.createElement('option');
                option.value = currentValue;
                option.textContent = currentValue;
                option.style.color = '#666';
                element.appendChild(option);
                element.value = currentValue;
            }
        } else if (currentValue && element.querySelector(`option[value="${currentValue}"]`)) {
            element.value = currentValue;
        } else {
            element.value = '';
        }
    }

    // Debounced filter fetching to prevent excessive API calls
    debouncedFetchFilters(forceRefresh = false) {
        const cacheKey = 'filter_options_cache';
        const cacheTimestamp = 'filter_options_timestamp';
        const CACHE_DURATION = 30000; // 30 seconds

        // Check cache first
        if (!forceRefresh && window.TagManager.state.filterOptionsCache) {
            const cacheAge = Date.now() - window.TagManager.state.filterOptionsCache.timestamp;
            if (cacheAge < CACHE_DURATION) {
                console.log('⚡ Using cached filter options for ultra-fast performance');
                this.updateFilters(window.TagManager.state.filterOptionsCache.data, true);
                return Promise.resolve();
            }
        }

        // Clear any existing timer
        if (this.debounceTimers.has('fetchFilters')) {
            clearTimeout(this.debounceTimers.get('fetchFilters'));
        }

        return new Promise((resolve, reject) => {
            this.debounceTimers.set('fetchFilters', setTimeout(async () => {
                try {
                    const isWindows = /Windows|Win32|Win64/.test(navigator.userAgent);
                    const isWebClient = isWindows || window.location.hostname !== 'localhost';
                    
                    const apiUrl = isWebClient 
                        ? `/api/web/filter-options?refresh=${forceRefresh}&t=${Date.now()}&platform=windows&ultra_fast=true`
                        : `/api/filter-options?refresh=${forceRefresh}&t=${Date.now()}&platform=windows&ultra_fast=true`;
                    
                    console.log(`⚡ Fetching filter options${isWebClient ? ' (Web-optimized)' : ''}...`);
                    
                    const response = await fetch(apiUrl, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (!response.ok) {
                        throw new Error('Failed to fetch filter options');
                    }
                    
                    const filterOptions = await response.json();
                    console.log('⚡ Fetched filter options:', Object.keys(filterOptions).length, 'filter types');
                    
                    // Cache the results
                    window.TagManager.state.filterOptionsCache = {
                        data: filterOptions,
                        timestamp: Date.now()
                    };
                    
                    // Use ultra-fast update
                    this.updateFilters(filterOptions, true);
                    resolve(filterOptions);
                    
                } catch (error) {
                    console.error('❌ Error fetching filter options:', error);
                    reject(error);
                }
            }, 100)); // Short debounce for responsiveness
        });
    }

    processPendingUpdates() {
        if (this.pendingUpdates.size > 0) {
            console.log(`🔄 Processing ${this.pendingUpdates.size} pending updates`);
            this.pendingUpdates.forEach((update, key) => {
                this.updateFilters(update.filters, update.preserveValues);
            });
            this.pendingUpdates.clear();
        }
    }

    // Handle virtual scroll "Load More" functionality
    handleLoadMore(filterId, allOptions, currentVisibleCount) {
        const filterElement = document.getElementById(filterId);
        if (!filterElement) return;

        const nextBatch = allOptions.slice(currentVisibleCount, currentVisibleCount + this.maxVisibleOptions);
        const remainingCount = allOptions.length - (currentVisibleCount + nextBatch.length);

        // Remove "Load More" option
        const loadMoreOption = filterElement.querySelector('option[value="__load_more__"]');
        if (loadMoreOption) {
            loadMoreOption.remove();
        }

        // Add next batch of options
        nextBatch.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            filterElement.appendChild(optionElement);
        });

        // Add new "Load More" option if there are more items
        if (remainingCount > 0) {
            const loadMoreElement = document.createElement('option');
            loadMoreElement.value = '__load_more__';
            loadMoreElement.textContent = `... Load More (${remainingCount} more)`;
            loadMoreElement.style.color = '#007bff';
            loadMoreElement.style.fontStyle = 'italic';
            filterElement.appendChild(loadMoreElement);
        }
    }
}

// Initialize the ultra-fast dropdown manager
window.ultraFastDropdownManager = new UltraFastDropdownManager();

// Override the original updateFilters method with ultra-fast version
if (window.TagManager) {
    window.TagManager.updateFilters = window.ultraFastDropdownManager.updateFilters.bind(window.ultraFastDropdownManager);
    window.TagManager.fetchAndPopulateFilters = window.ultraFastDropdownManager.debouncedFetchFilters.bind(window.ultraFastDropdownManager);
}

console.log('✅ UltraFastDropdownManager loaded and integrated');
