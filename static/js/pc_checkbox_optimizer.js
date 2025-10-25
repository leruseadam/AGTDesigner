/**
 * PC Checkbox Performance Optimizer
 * Optimizes checkbox selections for PC users with batch processing
 */

(function() {
    'use strict';
    
    console.log('🔧 PC Checkbox Optimizer Loading...');
    
    // Configuration
    const CHECKBOX_CONFIG = {
        BATCH_SIZE: 50,
        BATCH_DELAY: 100,  // ms
        DEBOUNCE_DELAY: 150,  // ms
        MAX_CONCURRENT_UPDATES: 3
    };
    
    // State management
    const CheckboxState = {
        batchQueue: [],
        isProcessing: false,
        lastUpdate: 0,
        pendingUpdates: 0
    };
    
    // Utility functions
    const Utils = {
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        throttle(func, limit) {
            let inThrottle;
            return function executedFunction(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        isWindows() {
            return navigator.platform.indexOf('Win') > -1 || 
                   navigator.userAgent.indexOf('Windows') > -1;
        },
        
        measurePerformance(name, fn) {
            if (!this.isWindows()) return fn();
            
            const start = performance.now();
            const result = fn();
            const end = performance.now();
            console.log(`⚡ ${name}: ${(end - start).toFixed(2)}ms`);
            return result;
        }
    };
    
    // PC Checkbox Optimizer
    const PCCheckboxOptimizer = {
        init() {
            if (!Utils.isWindows()) {
                console.log('🍎 Mac detected - skipping PC checkbox optimizations');
                return;
            }
            
            console.log('🖥️ PC detected - initializing checkbox optimizations...');
            
            this.setupBatchProcessor();
            this.setupEventDelegation();
            this.setupPerformanceMonitoring();
            
            // Wait for TagManager to be available
            this.waitForTagManager();
        },
        
        waitForTagManager() {
            const checkTagManager = () => {
                if (typeof window.TagManager !== 'undefined') {
                    this.integrateWithTagManager();
                } else {
                    setTimeout(checkTagManager, 100);
                }
            };
            checkTagManager();
        },
        
        integrateWithTagManager() {
            console.log('🔗 Integrating with TagManager...');
            
            // Override TagManager's checkbox handling with optimized version
            if (window.TagManager && window.TagManager.createTagElement) {
                const originalCreateTagElement = window.TagManager.createTagElement;
                
                window.TagManager.createTagElement = function(tag, isForSelectedTags = false) {
                    const element = originalCreateTagElement.call(this, tag, isForSelectedTags);
                    
                    // Add PC optimizations to the created element
                    PCCheckboxOptimizer.optimizeTagElement(element);
                    
                    return element;
                };
            }
            
            console.log('✅ TagManager integration complete');
        },
        
        optimizeTagElement(element) {
            const checkbox = element.querySelector('.tag-checkbox');
            if (!checkbox) return;
            
            // Add PC-specific attributes
            checkbox.setAttribute('data-pc-optimized', 'true');
            checkbox.setAttribute('data-batch-id', Date.now() + Math.random());
            
            // Remove individual event listeners (we'll use delegation)
            checkbox.removeEventListener('change', checkbox._originalChangeHandler);
        },
        
        setupBatchProcessor() {
            // Process checkbox changes in batches
            this.batchProcessor = Utils.throttle(() => {
                if (CheckboxState.batchQueue.length === 0) return;
                
                Utils.measurePerformance('Checkbox Batch Processing', () => {
                    this.processBatch();
                });
            }, CHECKBOX_CONFIG.BATCH_DELAY);
            
            console.log('✅ Batch processor initialized');
        },
        
        setupEventDelegation() {
            // Use event delegation for better performance
            document.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox' && 
                    e.target.classList.contains('tag-checkbox') &&
                    e.target.hasAttribute('data-pc-optimized')) {
                    
                    this.handleCheckboxChange(e);
                }
            });
            
            console.log('✅ Event delegation setup complete');
        },
        
        handleCheckboxChange(e) {
            const checkbox = e.target;
            const change = {
                element: checkbox,
                checked: checkbox.checked,
                value: checkbox.value,
                timestamp: Date.now(),
                batchId: checkbox.getAttribute('data-batch-id')
            };
            
            // Add to batch queue
            CheckboxState.batchQueue.push(change);
            
            // Trigger batch processing
            if (this.batchProcessor) {
                this.batchProcessor();
            }
            
            // Immediate visual feedback
            this.updateVisualState(checkbox);
        },
        
        processBatch() {
            if (CheckboxState.isProcessing) return;
            
            const batch = CheckboxState.batchQueue.splice(0, CHECKBOX_CONFIG.BATCH_SIZE);
            if (batch.length === 0) return;
            
            CheckboxState.isProcessing = true;
            
            try {
                // Group changes by container
                const changesByContainer = new Map();
                
                batch.forEach(change => {
                    const container = change.element.closest('#availableTags, #selectedTags');
                    if (!container) return;
                    
                    if (!changesByContainer.has(container)) {
                        changesByContainer.set(container, []);
                    }
                    changesByContainer.get(container).push(change);
                });
                
                // Process each container's changes
                changesByContainer.forEach((changes, container) => {
                    this.applyContainerChanges(container, changes);
                });
                
                // Update UI once for all changes
                this.updateUIAfterBatch();
                
            } finally {
                CheckboxState.isProcessing = false;
            }
        },
        
        applyContainerChanges(container, changes) {
            const containerId = container.id;
            
            if (containerId === 'availableTags') {
                this.handleAvailableTagsChanges(changes);
            } else if (containerId === 'selectedTags') {
                this.handleSelectedTagsChanges(changes);
            }
        },
        
        handleAvailableTagsChanges(changes) {
            // Update TagManager state
            if (window.TagManager && window.TagManager.state) {
                const selectedTags = new Set(window.TagManager.state.selectedTags || []);
                
                changes.forEach(change => {
                    if (change.checked) {
                        selectedTags.add(change.value);
                    } else {
                        selectedTags.delete(change.value);
                    }
                });
                
                window.TagManager.state.selectedTags = selectedTags;
                window.TagManager.state.persistentSelectedTags = Array.from(selectedTags);
            }
        },
        
        handleSelectedTagsChanges(changes) {
            // Handle changes in selected tags container
            changes.forEach(change => {
                if (!change.checked) {
                    // Remove from selected tags
                    this.removeFromSelectedTags(change.value);
                }
            });
        },
        
        removeFromSelectedTags(tagValue) {
            // Remove from TagManager state
            if (window.TagManager && window.TagManager.state) {
                const selectedTags = window.TagManager.state.selectedTags;
                if (selectedTags) {
                    selectedTags.delete(tagValue);
                }
                
                const persistentTags = window.TagManager.state.persistentSelectedTags;
                if (persistentTags) {
                    const index = persistentTags.indexOf(tagValue);
                    if (index > -1) {
                        persistentTags.splice(index, 1);
                    }
                }
            }
            
            // Remove DOM element
            const tagElement = document.querySelector(`input[value="${tagValue}"]`);
            if (tagElement) {
                const row = tagElement.closest('.tag-item, .tag-row');
                if (row && row.parentElement) {
                    row.remove();
                }
            }
        },
        
        updateUIAfterBatch() {
            // Batch DOM updates
            requestAnimationFrame(() => {
                this.updateTagCounts();
                this.updateSelectedTagsDisplay();
            });
        },
        
        updateTagCounts() {
            const availableCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
            const selectedCount = window.TagManager?.state?.selectedTags?.size || 0;
            
            // Update count displays
            const availableCountEl = document.querySelector('.available-count, #availableCount');
            const selectedCountEl = document.querySelector('.selected-count, #selectedCount');
            
            if (availableCountEl) {
                availableCountEl.textContent = availableCount;
            }
            if (selectedCountEl) {
                selectedCountEl.textContent = selectedCount;
            }
        },
        
        updateSelectedTagsDisplay() {
            const selectedContainer = document.getElementById('selectedTags');
            if (!selectedContainer || !window.TagManager?.state?.selectedTags) return;
            
            // Get current selected tags
            const currentSelected = new Set();
            selectedContainer.querySelectorAll('.tag-checkbox').forEach(checkbox => {
                if (checkbox.checked) {
                    currentSelected.add(checkbox.value);
                }
            });
            
            // Add missing tags
            window.TagManager.state.selectedTags.forEach(tagValue => {
                if (!currentSelected.has(tagValue)) {
                    const tagElement = this.createSelectedTagElement(tagValue);
                    selectedContainer.appendChild(tagElement);
                }
            });
        },
        
        createSelectedTagElement(tagValue) {
            const div = document.createElement('div');
            div.className = 'tag-item selected-tag';
            div.innerHTML = `
                <input type="checkbox" class="tag-checkbox" value="${tagValue}" checked data-pc-optimized="true">
                <span class="tag-text">${tagValue}</span>
            `;
            return div;
        },
        
        updateVisualState(checkbox) {
            // Immediate visual feedback
            const tagElement = checkbox.closest('.tag-item');
            if (tagElement) {
                if (checkbox.checked) {
                    tagElement.classList.add('tag-selected');
                } else {
                    tagElement.classList.remove('tag-selected');
                }
            }
        },
        
        setupPerformanceMonitoring() {
            // Monitor performance metrics
            setInterval(() => {
                if (CheckboxState.batchQueue.length > 0) {
                    console.log(`📊 Checkbox queue: ${CheckboxState.batchQueue.length} pending`);
                }
            }, 5000);
            
            console.log('✅ Performance monitoring setup complete');
        },
        
        // Public API
        getPerformanceMetrics() {
            return {
                batchQueueSize: CheckboxState.batchQueue.length,
                isProcessing: CheckboxState.isProcessing,
                pendingUpdates: CheckboxState.pendingUpdates,
                lastUpdate: CheckboxState.lastUpdate
            };
        },
        
        clearBatchQueue() {
            CheckboxState.batchQueue = [];
            console.log('✅ Batch queue cleared');
        }
    };
    
    // Auto-initialize
    PCCheckboxOptimizer.init();
    
    // Expose for debugging
    window.PCCheckboxOptimizer = PCCheckboxOptimizer;
    
    console.log('✅ PC Checkbox Optimizer loaded successfully');
})();
