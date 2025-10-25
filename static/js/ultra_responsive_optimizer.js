// static/js/ultra_responsive_optimizer.js
// Ultra-Responsive Optimizer for Maximum Web Performance

class UltraResponsiveOptimizer {
    constructor() {
        this.isActive = true;
        this.performanceMode = 'ultra';
        this.debounceTimers = new Map();
        this.throttleTimers = new Map();
        this.requestQueue = [];
        this.isProcessingQueue = false;
        this.frameScheduler = null;
        this.lastFrameTime = 0;
        this.targetFPS = 60;
        this.frameTime = 1000 / this.targetFPS;
        
        // Performance monitoring
        this.performanceMetrics = {
            frameCount: 0,
            lastFPS: 0,
            averageFrameTime: 0,
            droppedFrames: 0
        };
        
        console.log('🚀 UltraResponsiveOptimizer initialized');
        this.initialize();
    }

    initialize() {
        this.setupFrameScheduler();
        this.setupPerformanceMonitoring();
        this.optimizeDOM();
        this.setupEventOptimization();
        console.log('✅ Ultra-responsive optimization active');
    }

    // Ultra-fast frame scheduler
    setupFrameScheduler() {
        const processFrame = (currentTime) => {
            if (!this.isActive) return;
            
            const deltaTime = currentTime - this.lastFrameTime;
            
            if (deltaTime >= this.frameTime) {
                this.processRequestQueue();
                this.updatePerformanceMetrics(deltaTime);
                this.lastFrameTime = currentTime;
            }
            
            this.frameScheduler = requestAnimationFrame(processFrame);
        };
        
        this.frameScheduler = requestAnimationFrame(processFrame);
    }

    // Process queued operations efficiently
    processRequestQueue() {
        if (this.isProcessingQueue || this.requestQueue.length === 0) return;
        
        this.isProcessingQueue = true;
        const startTime = performance.now();
        
        // Process up to 5 operations per frame
        const batchSize = Math.min(5, this.requestQueue.length);
        const batch = this.requestQueue.splice(0, batchSize);
        
        batch.forEach(operation => {
            try {
                operation();
            } catch (error) {
                console.error('Queue operation error:', error);
            }
        });
        
        this.isProcessingQueue = false;
        
        // If queue is still full, schedule next batch
        if (this.requestQueue.length > 0) {
            requestAnimationFrame(() => this.processRequestQueue());
        }
    }

    // Add operation to processing queue
    queueOperation(operation, priority = 'normal') {
        if (!this.isActive) return;
        
        if (priority === 'high') {
            this.requestQueue.unshift(operation);
        } else {
            this.requestQueue.push(operation);
        }
    }

    // Ultra-fast debouncing
    debounce(key, func, delay = 16) { // 16ms = 60fps
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);
        
        this.debounceTimers.set(key, timer);
    }

    // Ultra-fast throttling
    throttle(key, func, delay = 16) {
        if (this.throttleTimers.has(key)) {
            return;
        }
        
        func();
        
        const timer = setTimeout(() => {
            this.throttleTimers.delete(key);
        }, delay);
        
        this.throttleTimers.set(key, timer);
    }

    // Optimize DOM operations
    optimizeDOM() {
        // Use passive event listeners for better scroll performance
        const passiveEvents = ['scroll', 'touchstart', 'touchmove', 'wheel'];
        
        passiveEvents.forEach(eventType => {
            document.addEventListener(eventType, () => {}, { passive: true });
        });

        // Optimize CSS for better performance
        this.injectPerformanceCSS();
    }

    injectPerformanceCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* Ultra-responsive CSS optimizations */
            * {
                will-change: auto;
            }
            
            .tag-checkbox, .filter-dropdown {
                transform: translateZ(0);
                backface-visibility: hidden;
            }
            
            .tag-item {
                contain: layout style paint;
            }
            
            /* Optimize animations */
            .tag-item:hover {
                transform: translateZ(0);
                transition: transform 0.1s ease-out;
            }
            
            /* Reduce repaints */
            .availableTags, .selectedTags {
                contain: layout;
            }
        `;
        document.head.appendChild(style);
    }

    // Setup event optimization
    setupEventOptimization() {
        // Optimize checkbox events
        this.optimizeCheckboxEvents();
        
        // Optimize filter events
        this.optimizeFilterEvents();
        
        // Optimize scroll events
        this.optimizeScrollEvents();
    }

    optimizeCheckboxEvents() {
        // Use event delegation for all checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('tag-checkbox')) {
                this.throttle('checkbox-change', () => {
                    this.handleCheckboxChange(e);
                }, 8); // 8ms throttle for 120fps feel
            }
        }, { passive: true });
    }

    optimizeFilterEvents() {
        // Use event delegation for all filters
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('filter-dropdown')) {
                this.debounce('filter-change', () => {
                    this.handleFilterChange(e);
                }, 50); // 50ms debounce for filters
            }
        }, { passive: true });
    }

    optimizeScrollEvents() {
        let scrollTimeout;
        
        document.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                this.updateVisibleElements();
            }, 16); // 16ms = 60fps
        }, { passive: true });
    }

    handleCheckboxChange(event) {
        const checkbox = event.target;
        const isChecked = checkbox.checked;
        
        // Immediate visual feedback
        checkbox.style.transform = isChecked ? 'scale(1.1)' : 'scale(1)';
        
        // Queue the actual processing
        this.queueOperation(() => {
            this.processCheckboxChange(checkbox, isChecked);
        });
    }

    handleFilterChange(event) {
        const filterElement = event.target;
        const filterId = filterElement.id;
        const value = filterElement.value;
        
        // Immediate visual feedback
        filterElement.style.borderColor = '#007bff';
        
        // Queue the actual processing
        this.queueOperation(() => {
            this.processFilterChange(filterElement, filterId, value);
        });
    }

    processCheckboxChange(checkbox, isChecked) {
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
                    row.style.opacity = '0';
                    setTimeout(() => {
                        row.remove();
                        TagManager.updateTagCount('selected', TagManager.state.persistentSelectedTags.length);
                    }, 150);
                }
            }
            
            // Reset visual state
            checkbox.style.transform = '';
            
        } catch (error) {
            console.error('Error processing checkbox change:', error);
        }
    }

    async processFilterChange(filterElement, filterId, value) {
        try {
            const filterType = this.getFilterTypeFromId(filterId);
            
            // Update table header for product type filter
            if (filterId === 'productTypeFilter' && typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }

            // Special handling for vendor filter
            if (filterId === 'vendorFilter' && value && value.trim() !== '' && value.toLowerCase() !== 'all') {
                TagManager.resetAllOtherFilters();
            }

            // Update filter options for cascading behavior
            await TagManager.updateFilterOptions();

            // Apply filters to tag lists
            TagManager.applyFilters();
            TagManager.renderActiveFilters();

            // Reset visual state
            filterElement.style.borderColor = '';
            
        } catch (error) {
            console.error('Error processing filter change:', error);
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

    updateVisibleElements() {
        // Only update visible elements for better performance
        const visibleCheckboxes = document.querySelectorAll('.tag-checkbox.visible');
        
        visibleCheckboxes.forEach(checkbox => {
            const rect = checkbox.getBoundingClientRect();
            const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
            
            if (isVisible) {
                checkbox.classList.add('visible');
            } else {
                checkbox.classList.remove('visible');
            }
        });
    }

    // Performance monitoring
    setupPerformanceMonitoring() {
        setInterval(() => {
            this.logPerformanceMetrics();
        }, 5000); // Log every 5 seconds
    }

    updatePerformanceMetrics(deltaTime) {
        this.performanceMetrics.frameCount++;
        this.performanceMetrics.averageFrameTime = 
            (this.performanceMetrics.averageFrameTime + deltaTime) / 2;
        
        if (deltaTime > this.frameTime * 1.5) {
            this.performanceMetrics.droppedFrames++;
        }
    }

    logPerformanceMetrics() {
        const fps = this.performanceMetrics.frameCount / 5; // 5 second intervals
        this.performanceMetrics.lastFPS = fps;
        
        if (fps < 30) {
            console.warn(`⚠️ Low FPS detected: ${fps.toFixed(1)}`);
            this.optimizePerformance();
        }
        
        this.performanceMetrics.frameCount = 0;
        this.performanceMetrics.droppedFrames = 0;
    }

    optimizePerformance() {
        // Clear old timers
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.throttleTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        this.throttleTimers.clear();
        
        // Clear request queue
        this.requestQueue = [];
        
        // Force garbage collection if available
        if (window.gc) {
            window.gc();
        }
        
        console.log('🔧 Performance optimization applied');
    }

    // Cleanup
    destroy() {
        this.isActive = false;
        
        if (this.frameScheduler) {
            cancelAnimationFrame(this.frameScheduler);
        }
        
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.throttleTimers.forEach(timer => clearTimeout(timer));
        
        this.debounceTimers.clear();
        this.throttleTimers.clear();
        this.requestQueue = [];
        
        console.log('🧹 UltraResponsiveOptimizer destroyed');
    }
}

// Initialize global optimizer
window.ultraResponsiveOptimizer = new UltraResponsiveOptimizer();

// Override TagManager methods for ultra-responsiveness
if (window.TagManager) {
    // Override updateFilters with ultra-responsive version
    const originalUpdateFilters = TagManager.updateFilters;
    TagManager.updateFilters = function(filters, preserveExistingValues = true) {
        window.ultraResponsiveOptimizer.queueOperation(() => {
            originalUpdateFilters.call(this, filters, preserveExistingValues);
        }, 'high');
    };
    
    // Override applyFilters with ultra-responsive version
    const originalApplyFilters = TagManager.applyFilters;
    TagManager.applyFilters = function() {
        window.ultraResponsiveOptimizer.queueOperation(() => {
            originalApplyFilters.call(this);
        });
    };
}

console.log('✅ UltraResponsiveOptimizer loaded and integrated');
