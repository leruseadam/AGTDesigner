// PC Filter Dropdown Performance Optimizer
// Dramatically improves filter dropdown performance on PC by simplifying rendering

class PCFilterOptimizer {
    constructor() {
        this.isPC = this.detectPC();
        this.isUltraFast = false;
        this.cache = new Map();
        this.debounceTimer = null;
        
        if (this.isPC) {
            this.initPCOptimizations();
            console.log('🪟 PC Filter Optimizer initialized');
        }
    }

    detectPC() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.includes('windows') || 
               userAgent.includes('win32') || 
               userAgent.includes('win64');
    }

    initPCOptimizations() {
        // Add PC-specific CSS class
        document.body.classList.add('pc-client');
        
        // Disable expensive CSS effects
        this.disableExpensiveEffects();
        
        // Optimize dropdown rendering
        this.optimizeDropdownRendering();
        
        // Enable ultra-fast mode if requested
        if (window.location.search.includes('ultra_fast=true')) {
            this.enableUltraFastMode();
        }
    }

    disableExpensiveEffects() {
        // Create style element to override expensive effects
        const style = document.createElement('style');
        style.textContent = `
            .pc-client .filter-bar,
            .pc-client .sticky-filter-bar {
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                transition: none !important;
                animation: none !important;
            }
            
            .pc-client .filter-bar select,
            .pc-client .form-select,
            .pc-client .compact-filter {
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                transition: none !important;
                animation: none !important;
                will-change: auto !important;
                transform: none !important;
            }
            
            .pc-client .filter-bar option {
                text-shadow: none !important;
                transition: none !important;
            }
        `;
        document.head.appendChild(style);
    }

    optimizeDropdownRendering() {
        // Use requestAnimationFrame for smooth updates
        const originalUpdateFilters = window.TagManager?.updateFilters;
        if (originalUpdateFilters) {
            window.TagManager.updateFilters = this.debouncedUpdateFilters.bind(this);
        }

        // Optimize dropdown change events
        this.optimizeDropdownEvents();
    }

    debouncedUpdateFilters(filters, preserveExistingValues = true) {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.debounceTimer = setTimeout(() => {
            this.performUltraFastUpdate(filters, preserveExistingValues);
        }, 16); // ~60fps
    }

    performUltraFastUpdate(filters, preserveExistingValues = true) {
        if (!filters) return;

        const startTime = performance.now();
        console.log('⚡ PC Ultra-fast filter update started');

        // Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();
        
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

        // Process all dropdowns in parallel
        const updatePromises = Object.entries(filterFieldMap).map(([filterType, filterId]) => 
            this.updateSingleDropdownUltraFast(filterType, filterId, filters[filterType] || [], preserveExistingValues)
        );

        Promise.all(updatePromises).then(() => {
            const endTime = performance.now();
            console.log(`✅ PC Ultra-fast filter update completed in ${(endTime - startTime).toFixed(2)}ms`);
        }).catch(error => {
            console.error('❌ Error in PC ultra-fast filter update:', error);
        });
    }

    async updateSingleDropdownUltraFast(filterType, filterId, fieldValues, preserveExistingValues) {
        const selectElement = document.getElementById(filterId);
        if (!selectElement) return;

        // Cache check
        const cacheKey = `${filterId}_${fieldValues.length}`;
        if (this.cache.has(cacheKey) && preserveExistingValues) {
            const cachedOptions = this.cache.get(cacheKey);
            this.applyCachedOptions(selectElement, cachedOptions);
            return;
        }

        // Store current value
        const currentValue = preserveExistingValues ? selectElement.value : '';
        
        // Clear existing options
        selectElement.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'All';
        selectElement.appendChild(defaultOption);
        
        // Batch create options
        const options = fieldValues.map(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            return option;
        });
        
        // Append all options at once
        options.forEach(option => selectElement.appendChild(option));
        
        // Restore current value
        if (preserveExistingValues && currentValue) {
            selectElement.value = currentValue;
        }
        
        // Cache the options
        this.cache.set(cacheKey, options);
    }

    applyCachedOptions(selectElement, cachedOptions) {
        // Fast path for cached options
        selectElement.innerHTML = '';
        
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'All';
        selectElement.appendChild(defaultOption);
        
        cachedOptions.forEach(option => {
            selectElement.appendChild(option.cloneNode(true));
        });
    }

    optimizeDropdownEvents() {
        // Use event delegation for better performance
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('form-select') || 
                e.target.classList.contains('compact-filter') ||
                e.target.id.includes('Filter')) {
                
                // Debounce filter changes
                if (this.debounceTimer) {
                    clearTimeout(this.debounceTimer);
                }
                
                this.debounceTimer = setTimeout(() => {
                    this.handleFilterChange(e.target);
                }, 50);
            }
        });
    }

    handleFilterChange(selectElement) {
        // Minimal processing for PC performance
        const filterId = selectElement.id;
        const value = selectElement.value;
        
        console.log(`🪟 PC Filter change: ${filterId} = ${value}`);
        
        // Trigger minimal update
        if (window.TagManager && window.TagManager.updateTags) {
            // Use ultra-fast mode for tag updates
            window.TagManager.updateTags();
        }
    }

    enableUltraFastMode() {
        this.isUltraFast = true;
        document.body.classList.add('pc-ultra-fast');
        
        // Further simplify styling
        const ultraFastStyle = document.createElement('style');
        ultraFastStyle.textContent = `
            .pc-ultra-fast .filter-bar,
            .pc-ultra-fast .sticky-filter-bar {
                background: rgba(45, 34, 58, 0.98) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: 1px solid rgba(160, 132, 232, 0.4) !important;
                border-radius: 4px !important;
                box-shadow: none !important;
                transition: none !important;
            }
            
            .pc-ultra-fast .filter-bar select,
            .pc-ultra-fast .form-select,
            .pc-ultra-fast .compact-filter {
                background: rgba(45, 34, 58, 0.95) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: 1px solid rgba(160, 132, 232, 0.5) !important;
                border-radius: 2px !important;
                transition: none !important;
                will-change: auto !important;
                transform: none !important;
            }
            
            .pc-ultra-fast .filter-bar option {
                background: #2d223a !important;
                color: #fff !important;
                text-shadow: none !important;
                transition: none !important;
            }
        `;
        document.head.appendChild(ultraFastStyle);
        
        console.log('🚀 PC Ultra-fast mode enabled');
    }

    // Public method to enable ultra-fast mode
    enableUltraFast() {
        if (this.isPC) {
            this.enableUltraFastMode();
        }
    }

    // Public method to get performance stats
    getPerformanceStats() {
        return {
            isPC: this.isPC,
            isUltraFast: this.isUltraFast,
            cacheSize: this.cache.size,
            optimizations: [
                'backdrop-filter disabled',
                'transitions disabled',
                'animations disabled',
                'debounced updates',
                'cached options',
                'event delegation'
            ]
        };
    }
}

// Initialize PC Filter Optimizer
window.pcFilterOptimizer = new PCFilterOptimizer();

// Export for global access
window.PCFilterOptimizer = PCFilterOptimizer;
