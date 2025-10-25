// static/js/web_event_optimizer.js
// Web Event Optimizer for Responsive Checkboxes and Filters

class WebEventOptimizer {
    constructor() {
        this.isProcessing = false;
        this.pendingEvents = new Map();
        this.debounceTimers = new Map();
        this.eventQueue = [];
        this.processingDelay = 50; // ms
        this.useEventDelegation = true;
        
        console.log('🚀 WebEventOptimizer initialized');
    }

    // Initialize optimized event system
    initialize() {
        if (!this.useEventDelegation) return;
        
        console.log('⚡ Initializing optimized web event system');
        this.setupEventDelegation();
        this.setupCheckboxOptimization();
        this.setupFilterOptimization();
        console.log('✅ Web event system optimized');
    }

    // Event delegation for better performance
    setupEventDelegation() {
        const container = document.getElementById('availableTags') || document.body;
        
        // Use event delegation for checkboxes (single listener for all checkboxes)
        container.addEventListener('change', (e) => {
            if (e.target.classList.contains('tag-checkbox')) {
                this.handleCheckboxChange(e);
            }
        }, true); // Use capture phase for better control

        // Use event delegation for filter dropdowns
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('filter-dropdown')) {
                this.handleFilterChange(e);
            }
        }, true);

        console.log('✅ Event delegation system active');
    }

    // Optimized checkbox handling
    handleCheckboxChange(event) {
        event.stopPropagation();
        event.stopImmediatePropagation();

        const checkbox = event.target;
        const isChecked = checkbox.checked;

        // Debounce checkbox changes
        const checkboxId = checkbox.value || checkbox.closest('.tag-item')?.id;
        
        if (this.debounceTimers.has(checkboxId)) {
            clearTimeout(this.debounceTimers.get(checkboxId));
        }

        this.debounceTimers.set(checkboxId, setTimeout(() => {
            this.processCheckboxChange(checkbox, isChecked);
        }, 100)); // 100ms debounce
    }

    processCheckboxChange(checkbox, isChecked) {
        if (this.isProcessing) {
            this.pendingEvents.set('checkbox', { checkbox, isChecked });
            return;
        }

        this.isProcessing = true;

        try {
            const value = checkbox.value;
            
            if (isChecked) {
                TagManager.state.selectedTags.add(value);
            } else {
                TagManager.state.selectedTags.delete(value);
                
                // Remove from persistent selections
                const idx = TagManager.state.persistentSelectedTags.indexOf(value);
                if (idx > -1) TagManager.state.persistentSelectedTags.splice(idx, 1);
                
                // Remove DOM row if in selected list
                const row = checkbox.closest('.tag-item, .tag-row');
                if (row && row.parentElement && row.parentElement.id === 'selectedTags') {
                    requestAnimationFrame(() => {
                        row.remove();
                        TagManager.updateTagCount('selected', TagManager.state.persistentSelectedTags.length);
                    });
                }
            }

            console.log(`⚡ Checkbox ${isChecked ? 'checked' : 'unchecked'}: ${value}`);
            
        } catch (error) {
            console.error('Error processing checkbox change:', error);
        } finally {
            this.isProcessing = false;
            
            // Process pending events
            if (this.pendingEvents.has('checkbox')) {
                const { checkbox, isChecked } = this.pendingEvents.get('checkbox');
                this.pendingEvents.delete('checkbox');
                setTimeout(() => this.processCheckboxChange(checkbox, isChecked), 50);
            }
        }
    }

    // Optimized filter handling
    handleFilterChange(event) {
        event.stopPropagation();
        
        const filterElement = event.target;
        const filterId = filterElement.id;
        const value = filterElement.value;

        console.log(`⚡ Filter changed: ${filterId} = ${value}`);

        // Clear any existing debounce timer
        if (this.debounceTimers.has(filterId)) {
            clearTimeout(this.debounceTimers.get(filterId));
        }

        // Debounce filter changes
        this.debounceTimers.set(filterId, setTimeout(() => {
            this.processFilterChange(filterElement, filterId, value);
        }, 200)); // 200ms debounce for filters
    }

    async processFilterChange(filterElement, filterId, value) {
        if (this.isProcessing) {
            this.pendingEvents.set('filter', { filterElement, filterId, value });
            return;
        }

        this.isProcessing = true;

        try {
            const filterType = this.getFilterTypeFromId(filterId);
            
            // Update table header for product type filter
            if (filterId === 'productTypeFilter' && typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }

            // Special handling for vendor filter
            if (filterId === 'vendorFilter' && value && value.trim() !== '' && value.toLowerCase() !== 'all') {
                console.log('⚡ Vendor filter changed, resetting other filters');
                TagManager.resetAllOtherFilters();
            }

            // Update filter options for cascading behavior
            await TagManager.updateFilterOptions();

            // Apply filters to tag lists
            TagManager.applyFilters();
            TagManager.renderActiveFilters();

            console.log(`✅ Filter ${filterId} processed: ${value}`);

        } catch (error) {
            console.error('Error processing filter change:', error);
        } finally {
            this.isProcessing = false;
            
            // Process pending events
            if (this.pendingEvents.has('filter')) {
                const { filterElement, filterId, value } = this.pendingEvents.get('filter');
                this.pendingEvents.delete('filter');
                setTimeout(() => this.processFilterChange(filterElement, filterId, value), 100);
            }
        }
    }

    getFilterTypeFromId(filterId) {
        const idToType = {
            'vendorFilter': 'vendor',
            'brandFilter': 'brand',
            'productTypeFilter': 'productType',
            'lineageFilter': 'lineage',
            'weightFilter': 'weight',
            'dohFilter': 'doh',
            'highCbdFilter': 'highCbd'
        };
        return idToType[filterId] || filterId;
    }

    // Setup checkbox-specific optimizations
    setupCheckboxOptimization() {
        // Use passive event listeners for better scroll performance
        const container = document.getElementById('availableTags');
        if (container) {
            container.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
        }
    }

    handleScroll() {
        // Lazy load checkbox visibility if needed
        this.updateVisibleCheckboxes();
    }

    updateVisibleCheckboxes() {
        const checkboxes = document.querySelectorAll('.tag-checkbox');
        
        checkboxes.forEach(checkbox => {
            const rect = checkbox.getBoundingClientRect();
            const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
            
            // Add visible class for CSS optimization
            if (isVisible) {
                checkbox.classList.add('visible');
            } else {
                checkbox.classList.remove('visible');
            }
        });
    }

    // Setup filter-specific optimizations
    setupFilterOptimization() {
        // Add filter dropdown class for event delegation
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.classList.add('filter-dropdown');
            }
        });
    }

    // Batch process multiple events efficiently
    processEventQueue() {
        if (this.eventQueue.length === 0) return;

        const batch = this.eventQueue.splice(0, 10); // Process 10 events at a time
        
        batch.forEach(({ type, data }) => {
            if (type === 'checkbox') {
                this.processCheckboxChange(data.checkbox, data.isChecked);
            } else if (type === 'filter') {
                this.processFilterChange(data.filterElement, data.filterId, data.value);
            }
        });

        // Continue processing if more events in queue
        if (this.eventQueue.length > 0) {
            setTimeout(() => this.processEventQueue(), this.processingDelay);
        }
    }

    // Clean up timers and listeners
    cleanup() {
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        this.pendingEvents.clear();
        this.eventQueue = [];
        console.log('🧹 WebEventOptimizer cleaned up');
    }
}

// Initialize global instance
window.webEventOptimizer = new WebEventOptimizer();

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.webEventOptimizer.initialize();
    });
} else {
    window.webEventOptimizer.initialize();
}

console.log('✅ WebEventOptimizer loaded');
