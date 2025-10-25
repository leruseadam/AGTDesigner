// Ultra-Aggressive PC Performance Optimizer
// Consolidates all checkbox and filter handling for maximum speed on PC

class UltraAggressivePCOptimizer {
    constructor() {
        this.isPC = this.detectPC();
        this.isActive = false;
        this.checkboxCache = new Map();
        this.filterCache = new Map();
        this.debounceTimers = new Map();
        this.batchOperations = [];
        this.batchTimer = null;
        
        if (this.isPC) {
            this.init();
            console.log('🚀 Ultra-Aggressive PC Optimizer initialized');
        }
    }

    detectPC() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.includes('windows') || 
               userAgent.includes('win32') || 
               userAgent.includes('win64');
    }

    init() {
        this.isActive = true;
        
        // Disable all existing optimizers to prevent conflicts
        this.disableExistingOptimizers();
        
        // Apply ultra-aggressive CSS optimizations
        this.applyUltraAggressiveCSS();
        
        // Setup consolidated event handling
        this.setupConsolidatedEvents();
        
        // Enable hardware acceleration
        this.enableHardwareAcceleration();
        
        // Setup batch processing
        this.setupBatchProcessing();
        
        console.log('🔥 Ultra-Aggressive PC optimizations active');
    }

    disableExistingOptimizers() {
        // Disable conflicting optimizers
        if (window.webEventOptimizer) {
            window.webEventOptimizer.isActive = false;
        }
        if (window.ultraResponsiveOptimizer) {
            window.ultraResponsiveOptimizer.isActive = false;
        }
        if (window.pcFilterOptimizer) {
            window.pcFilterOptimizer.isActive = false;
        }
        
        console.log('🛑 Disabled conflicting optimizers');
    }

    applyUltraAggressiveCSS() {
        const style = document.createElement('style');
        style.id = 'ultra-aggressive-pc-css';
        style.textContent = `
            /* Ultra-Aggressive PC Performance CSS */
            .pc-ultra-aggressive * {
                transition: none !important;
                animation: none !important;
                transform: none !important;
                will-change: auto !important;
                backface-visibility: visible !important;
                perspective: none !important;
            }
            
            .pc-ultra-aggressive .tag-checkbox,
            .pc-ultra-aggressive .form-select,
            .pc-ultra-aggressive .compact-filter {
                transition: none !important;
                animation: none !important;
                transform: none !important;
                will-change: auto !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                box-shadow: none !important;
                border-radius: 2px !important;
                background: rgba(45, 34, 58, 0.95) !important;
                border: 1px solid rgba(160, 132, 232, 0.5) !important;
            }
            
            .pc-ultra-aggressive .tag-checkbox:hover,
            .pc-ultra-aggressive .form-select:hover,
            .pc-ultra-aggressive .compact-filter:hover {
                transform: none !important;
                box-shadow: none !important;
                background: rgba(45, 34, 58, 0.95) !important;
            }
            
            .pc-ultra-aggressive .tag-checkbox:focus,
            .pc-ultra-aggressive .form-select:focus,
            .pc-ultra-aggressive .compact-filter:focus {
                transform: none !important;
                box-shadow: none !important;
                outline: 1px solid rgba(160, 132, 232, 0.7) !important;
            }
            
            .pc-ultra-aggressive .tag-item,
            .pc-ultra-aggressive .tag-row {
                transition: none !important;
                animation: none !important;
                transform: none !important;
                will-change: auto !important;
            }
            
            .pc-ultra-aggressive .tag-item:hover,
            .pc-ultra-aggressive .tag-row:hover {
                transform: none !important;
                background: rgba(160, 132, 232, 0.1) !important;
            }
            
            /* Force hardware acceleration only for critical elements */
            .pc-ultra-aggressive .tag-checkbox {
                transform: translateZ(0) !important;
                backface-visibility: hidden !important;
            }
            
            /* Disable all expensive effects */
            .pc-ultra-aggressive * {
                text-shadow: none !important;
                filter: none !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }
        `;
        document.head.appendChild(style);
        
        // Add class to body
        document.body.classList.add('pc-ultra-aggressive');
        
        console.log('🎨 Ultra-aggressive CSS applied');
    }

    setupConsolidatedEvents() {
        // Remove all existing event listeners
        this.removeAllEventListeners();
        
        // Setup single consolidated event delegation
        document.addEventListener('change', this.handleConsolidatedChange.bind(this), true);
        document.addEventListener('click', this.handleConsolidatedClick.bind(this), true);
        
        console.log('🎯 Consolidated event handling setup');
    }

    removeAllEventListeners() {
        // Clone nodes to remove all event listeners
        const checkboxes = document.querySelectorAll('.tag-checkbox');
        checkboxes.forEach(checkbox => {
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);
        });
        
        const filters = document.querySelectorAll('.form-select, .compact-filter');
        filters.forEach(filter => {
            const newFilter = filter.cloneNode(true);
            filter.parentNode.replaceChild(newFilter, filter);
        });
        
        console.log('🧹 Removed all existing event listeners');
    }

    handleConsolidatedChange(event) {
        if (!this.isActive) return;
        
        const target = event.target;
        
        // Handle checkboxes
        if (target.classList.contains('tag-checkbox')) {
            this.handleCheckboxChangeUltraFast(target, event);
            return;
        }
        
        // Handle filters
        if (target.classList.contains('form-select') || target.classList.contains('compact-filter')) {
            this.handleFilterChangeUltraFast(target, event);
            return;
        }
    }

    handleConsolidatedClick(event) {
        if (!this.isActive) return;
        
        const target = event.target;
        
        // Handle tag item clicks
        if (target.closest('.tag-item') && !target.classList.contains('tag-checkbox')) {
            const checkbox = target.closest('.tag-item').querySelector('.tag-checkbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                this.handleCheckboxChangeUltraFast(checkbox, event);
            }
        }
    }

    handleCheckboxChangeUltraFast(checkbox, event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        
        const checkboxId = checkbox.value;
        const isChecked = checkbox.checked;
        
        // Immediate visual feedback without expensive operations
        checkbox.style.opacity = isChecked ? '1' : '0.7';
        
        // Batch the actual processing
        this.batchOperations.push({
            type: 'checkbox',
            id: checkboxId,
            checked: isChecked,
            element: checkbox
        });
        
        this.scheduleBatchProcessing();
    }

    handleFilterChangeUltraFast(filter, event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        
        const filterId = filter.id;
        const value = filter.value;
        
        // Immediate visual feedback
        filter.style.opacity = '0.8';
        
        // Batch the actual processing
        this.batchOperations.push({
            type: 'filter',
            id: filterId,
            value: value,
            element: filter
        });
        
        this.scheduleBatchProcessing();
    }

    scheduleBatchProcessing() {
        if (this.batchTimer) {
            clearTimeout(this.batchTimer);
        }
        
        // Process batches every 16ms (60fps) for ultra-smooth performance
        this.batchTimer = setTimeout(() => {
            this.processBatch();
        }, 16);
    }

    processBatch() {
        if (this.batchOperations.length === 0) return;
        
        const startTime = performance.now();
        
        // Process all operations in the batch
        this.batchOperations.forEach(operation => {
            if (operation.type === 'checkbox') {
                this.processCheckboxOperation(operation);
            } else if (operation.type === 'filter') {
                this.processFilterOperation(operation);
            }
        });
        
        // Clear the batch
        this.batchOperations = [];
        
        const endTime = performance.now();
        console.log(`⚡ Batch processed in ${(endTime - startTime).toFixed(2)}ms`);
    }

    processCheckboxOperation(operation) {
        const { id, checked, element } = operation;
        
        // Restore opacity
        element.style.opacity = '1';
        
        // Update state immediately
        if (window.TagManager && window.TagManager.state) {
            if (checked) {
                window.TagManager.state.selectedTags.add(id);
                if (!window.TagManager.state.persistentSelectedTags.includes(id)) {
                    window.TagManager.state.persistentSelectedTags.push(id);
                }
            } else {
                window.TagManager.state.selectedTags.delete(id);
                const index = window.TagManager.state.persistentSelectedTags.indexOf(id);
                if (index > -1) {
                    window.TagManager.state.persistentSelectedTags.splice(index, 1);
                }
            }
        }
        
        // Update UI immediately without expensive operations
        this.updateCheckboxUI(element, checked);
    }

    processFilterOperation(operation) {
        const { id, value, element } = operation;
        
        // Restore opacity
        element.style.opacity = '1';
        
        // Update filters immediately
        if (window.TagManager && window.TagManager.updateFilters) {
            // Use ultra-fast filter update
            const filters = this.getCurrentFilters();
            filters[id.replace('Filter', '')] = value;
            
            // Debounce the actual filter update
            if (this.debounceTimers.has('filters')) {
                clearTimeout(this.debounceTimers.get('filters'));
            }
            
            this.debounceTimers.set('filters', setTimeout(() => {
                window.TagManager.updateFilters(filters);
            }, 100));
        }
    }

    updateCheckboxUI(checkbox, checked) {
        // Minimal UI update for performance
        const tagItem = checkbox.closest('.tag-item, .tag-row');
        if (tagItem) {
            if (checked) {
                tagItem.classList.add('selected');
            } else {
                tagItem.classList.remove('selected');
            }
        }
        
        // Update select-all checkboxes
        this.updateSelectAllCheckboxes();
    }

    updateSelectAllCheckboxes() {
        // Ultra-fast select-all checkbox updates
        const sections = document.querySelectorAll('.vendor-section, .brand-section, .product-type-section, .weight-section');
        
        sections.forEach(section => {
            const selectAllCheckbox = section.querySelector('.select-all-checkbox');
            if (!selectAllCheckbox) return;
            
            const tagCheckboxes = section.querySelectorAll('.tag-checkbox');
            const checkedCount = Array.from(tagCheckboxes).filter(cb => cb.checked).length;
            
            if (checkedCount === 0) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            } else if (checkedCount === tagCheckboxes.length) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            } else {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = true;
            }
        });
    }

    getCurrentFilters() {
        const filters = {};
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        
        filterIds.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                const key = filterId.replace('Filter', '');
                filters[key] = element.value || '';
            }
        });
        
        return filters;
    }

    enableHardwareAcceleration() {
        // Force hardware acceleration for critical elements
        const criticalElements = document.querySelectorAll('.tag-checkbox, .form-select, .compact-filter');
        
        criticalElements.forEach(element => {
            element.style.transform = 'translateZ(0)';
            element.style.backfaceVisibility = 'hidden';
            element.style.willChange = 'transform';
        });
        
        console.log('🚀 Hardware acceleration enabled');
    }

    setupBatchProcessing() {
        // Use requestAnimationFrame for ultra-smooth processing
        let lastTime = 0;
        
        const processFrame = (currentTime) => {
            if (currentTime - lastTime >= 16) { // 60fps
                if (this.batchOperations.length > 0) {
                    this.processBatch();
                }
                lastTime = currentTime;
            }
            
            if (this.isActive) {
                requestAnimationFrame(processFrame);
            }
        };
        
        requestAnimationFrame(processFrame);
        
        console.log('🎬 Batch processing setup');
    }

    // Public methods
    enable() {
        this.isActive = true;
        document.body.classList.add('pc-ultra-aggressive');
        console.log('🔥 Ultra-Aggressive PC Optimizer enabled');
    }

    disable() {
        this.isActive = false;
        document.body.classList.remove('pc-ultra-aggressive');
        console.log('🛑 Ultra-Aggressive PC Optimizer disabled');
    }

    getPerformanceStats() {
        return {
            isPC: this.isPC,
            isActive: this.isActive,
            batchOperations: this.batchOperations.length,
            cacheSize: this.checkboxCache.size + this.filterCache.size,
            optimizations: [
                'ultra-aggressive CSS',
                'consolidated event handling',
                'batch processing',
                'hardware acceleration',
                'conflict prevention',
                'minimal DOM operations'
            ]
        };
    }
}

// Initialize Ultra-Aggressive PC Optimizer
window.ultraAggressivePCOptimizer = new UltraAggressivePCOptimizer();

// Export for global access
window.UltraAggressivePCOptimizer = UltraAggressivePCOptimizer;
