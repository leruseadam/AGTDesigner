/**
 * PC Performance Optimizer - Makes PC web experience as fast as Mac
 * Optimizes dropdowns, Excel upload, and checkbox selections
 */

(function() {
    'use strict';
    
    console.log('🚀 PC Performance Optimizer Loading...');
    
    // Performance configuration
    const PC_PERFORMANCE_CONFIG = {
        DROPDOWN_DEBOUNCE_MS: 150,        // Debounce dropdown searches
        CHECKBOX_BATCH_SIZE: 50,          // Process checkboxes in batches
        EXCEL_CHUNK_SIZE: 1000,           // Process Excel in chunks
        VIRTUAL_SCROLL_THRESHOLD: 100,    // Use virtual scrolling for >100 items
        CACHE_DURATION_MS: 300000,        // 5 minutes cache
        MAX_CONCURRENT_REQUESTS: 3         // Limit concurrent API calls
    };
    
    // Global performance state
    const PerformanceState = {
        dropdownCache: new Map(),
        checkboxBatchQueue: [],
        excelProcessingQueue: [],
        activeRequests: 0,
        lastDropdownUpdate: 0,
        lastCheckboxUpdate: 0
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
            if (!this.isWindows()) return fn(); // Only measure on Windows
            
            const start = performance.now();
            const result = fn();
            const end = performance.now();
            console.log(`⚡ ${name}: ${(end - start).toFixed(2)}ms`);
            return result;
        }
    };
    
    // Dropdown Performance Optimizer
    const DropdownOptimizer = {
        init() {
            if (!Utils.isWindows()) return;
            
            console.log('🔧 Initializing Dropdown Optimizer...');
            this.setupDebouncedSearch();
            this.setupVirtualScrolling();
            this.setupDropdownCaching();
        },
        
        setupDebouncedSearch() {
            // Find all dropdown search inputs
            const searchInputs = document.querySelectorAll('input[type="text"], input[type="search"]');
            
            searchInputs.forEach(input => {
                if (input.placeholder && (
                    input.placeholder.toLowerCase().includes('search') ||
                    input.placeholder.toLowerCase().includes('filter')
                )) {
                    this.addDebouncedSearch(input);
                }
            });
        },
        
        addDebouncedSearch(input) {
            const originalHandler = input.oninput;
            
            const debouncedSearch = Utils.debounce((e) => {
                Utils.measurePerformance('Dropdown Search', () => {
                    this.performOptimizedSearch(e.target);
                });
            }, PC_PERFORMANCE_CONFIG.DROPDOWN_DEBOUNCE_MS);
            
            input.addEventListener('input', debouncedSearch);
            
            // Preserve original handler if it exists
            if (originalHandler) {
                input.addEventListener('input', originalHandler);
            }
        },
        
        performOptimizedSearch(input) {
            const searchTerm = input.value.toLowerCase();
            const dropdown = input.closest('.dropdown, .select-container');
            
            if (!dropdown) return;
            
            const options = dropdown.querySelectorAll('option, .dropdown-item, .select-option');
            const cacheKey = `${dropdown.id || 'dropdown'}_${searchTerm}`;
            
            // Check cache first
            if (PerformanceState.dropdownCache.has(cacheKey)) {
                this.applyCachedResults(dropdown, PerformanceState.dropdownCache.get(cacheKey));
                return;
            }
            
            // Perform search with virtual scrolling for large lists
            const results = this.searchOptions(options, searchTerm);
            
            // Cache results
            PerformanceState.dropdownCache.set(cacheKey, results);
            
            // Apply results
            this.applySearchResults(dropdown, options, results);
        },
        
        searchOptions(options, searchTerm) {
            const results = [];
            const maxResults = PC_PERFORMANCE_CONFIG.VIRTUAL_SCROLL_THRESHOLD;
            
            for (let i = 0; i < options.length && results.length < maxResults; i++) {
                const option = options[i];
                const text = option.textContent.toLowerCase();
                
                if (text.includes(searchTerm)) {
                    results.push({
                        element: option,
                        index: i,
                        score: this.calculateRelevanceScore(text, searchTerm)
                    });
                }
            }
            
            // Sort by relevance
            return results.sort((a, b) => b.score - a.score);
        },
        
        calculateRelevanceScore(text, searchTerm) {
            if (text.startsWith(searchTerm)) return 100;
            if (text.includes(searchTerm)) return 50;
            return 25;
        },
        
        applySearchResults(dropdown, allOptions, results) {
            // Hide all options first
            allOptions.forEach(option => {
                option.style.display = 'none';
            });
            
            // Show matching results
            results.forEach(result => {
                result.element.style.display = 'block';
            });
            
            // Update dropdown height for virtual scrolling
            this.updateDropdownHeight(dropdown, results.length);
        },
        
        applyCachedResults(dropdown, results) {
            const allOptions = dropdown.querySelectorAll('option, .dropdown-item, .select-option');
            this.applySearchResults(dropdown, allOptions, results);
        },
        
        updateDropdownHeight(dropdown, visibleCount) {
            const maxHeight = Math.min(visibleCount * 30, 300); // 30px per item, max 300px
            dropdown.style.maxHeight = `${maxHeight}px`;
            dropdown.style.overflowY = visibleCount > 10 ? 'auto' : 'visible';
        },
        
        setupVirtualScrolling() {
            // Implement virtual scrolling for large dropdowns
            const dropdowns = document.querySelectorAll('.dropdown, .select-container');
            
            dropdowns.forEach(dropdown => {
                const options = dropdown.querySelectorAll('option, .dropdown-item, .select-option');
                
                if (options.length > PC_PERFORMANCE_CONFIG.VIRTUAL_SCROLL_THRESHOLD) {
                    this.enableVirtualScrolling(dropdown, options);
                }
            });
        },
        
        enableVirtualScrolling(dropdown, options) {
            const container = dropdown.querySelector('.dropdown-menu, .options-container');
            if (!container) return;
            
            const itemHeight = 30;
            const visibleItems = Math.floor(300 / itemHeight); // 300px max height
            
            // Create virtual scrolling container
            const virtualContainer = document.createElement('div');
            virtualContainer.style.height = `${options.length * itemHeight}px`;
            virtualContainer.style.position = 'relative';
            
            // Move options to virtual container
            options.forEach(option => {
                option.style.position = 'absolute';
                option.style.top = `${Array.from(options).indexOf(option) * itemHeight}px`;
                virtualContainer.appendChild(option);
            });
            
            container.appendChild(virtualContainer);
            
            // Add scroll listener for virtual scrolling
            container.addEventListener('scroll', Utils.throttle(() => {
                this.updateVisibleOptions(container, virtualContainer, options, itemHeight, visibleItems);
            }, 16)); // 60fps
        },
        
        updateVisibleOptions(container, virtualContainer, options, itemHeight, visibleItems) {
            const scrollTop = container.scrollTop;
            const startIndex = Math.floor(scrollTop / itemHeight);
            const endIndex = Math.min(startIndex + visibleItems, options.length);
            
            // Hide all options
            options.forEach(option => {
                option.style.display = 'none';
            });
            
            // Show visible options
            for (let i = startIndex; i < endIndex; i++) {
                if (options[i]) {
                    options[i].style.display = 'block';
                }
            }
        },
        
        setupDropdownCaching() {
            // Clear cache periodically
            setInterval(() => {
                PerformanceState.dropdownCache.clear();
            }, PC_PERFORMANCE_CONFIG.CACHE_DURATION_MS);
        }
    };
    
    // Checkbox Performance Optimizer
    const CheckboxOptimizer = {
        init() {
            if (!Utils.isWindows()) return;
            
            console.log('🔧 Initializing Checkbox Optimizer...');
            this.setupBatchProcessing();
            this.setupEventDelegation();
            this.setupCheckboxCaching();
        },
        
        setupBatchProcessing() {
            // Process checkbox changes in batches to reduce DOM updates
            const processBatch = Utils.throttle(() => {
                if (PerformanceState.checkboxBatchQueue.length === 0) return;
                
                Utils.measurePerformance('Checkbox Batch Processing', () => {
                    this.processCheckboxBatch();
                });
            }, 100); // Process every 100ms
            
            // Store the batch processor
            this.batchProcessor = processBatch;
        },
        
        setupEventDelegation() {
            // Use event delegation for better performance
            document.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox' && e.target.classList.contains('tag-checkbox')) {
                    this.handleCheckboxChange(e);
                }
            });
        },
        
        handleCheckboxChange(e) {
            const checkbox = e.target;
            const change = {
                element: checkbox,
                checked: checkbox.checked,
                value: checkbox.value,
                timestamp: Date.now()
            };
            
            // Add to batch queue
            PerformanceState.checkboxBatchQueue.push(change);
            
            // Trigger batch processing
            if (this.batchProcessor) {
                this.batchProcessor();
            }
        },
        
        processCheckboxBatch() {
            const batch = PerformanceState.checkboxBatchQueue.splice(0, PC_PERFORMANCE_CONFIG.CHECKBOX_BATCH_SIZE);
            
            if (batch.length === 0) return;
            
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
                this.applyCheckboxChanges(container, changes);
            });
            
            // Update UI once for all changes
            this.updateCheckboxUI();
        },
        
        applyCheckboxChanges(container, changes) {
            const selectedTags = new Set(TagManager.state.selectedTags || []);
            
            changes.forEach(change => {
                if (change.checked) {
                    selectedTags.add(change.value);
                } else {
                    selectedTags.delete(change.value);
                }
            });
            
            // Update TagManager state
            TagManager.state.selectedTags = selectedTags;
            
            // Update persistent selections
            TagManager.state.persistentSelectedTags = Array.from(selectedTags);
        },
        
        updateCheckboxUI() {
            // Batch DOM updates
            requestAnimationFrame(() => {
                this.updateTagCounts();
                this.updateSelectedTagsDisplay();
            });
        },
        
        updateTagCounts() {
            const availableCount = document.querySelectorAll('#availableTags .tag-checkbox').length;
            const selectedCount = TagManager.state.selectedTags.size;
            
            // Update count displays
            const availableCountEl = document.querySelector('.available-count, #availableCount');
            const selectedCountEl = document.querySelector('.selected-count, #selectedCount');
            
            if (availableCountEl) availableCountEl.textContent = availableCount;
            if (selectedCountEl) selectedCountEl.textContent = selectedCount;
        },
        
        updateSelectedTagsDisplay() {
            const selectedContainer = document.getElementById('selectedTags');
            if (!selectedContainer) return;
            
            // Clear and rebuild selected tags display
            selectedContainer.innerHTML = '';
            
            TagManager.state.selectedTags.forEach(tagValue => {
                const tagElement = this.createSelectedTagElement(tagValue);
                selectedContainer.appendChild(tagElement);
            });
        },
        
        createSelectedTagElement(tagValue) {
            const div = document.createElement('div');
            div.className = 'tag-item selected-tag';
            div.innerHTML = `
                <input type="checkbox" class="tag-checkbox" value="${tagValue}" checked>
                <span class="tag-text">${tagValue}</span>
            `;
            return div;
        },
        
        setupCheckboxCaching() {
            // Cache checkbox states to avoid re-processing
            const cacheKey = 'checkbox_states';
            
            // Load cached states on init
            try {
                const cached = sessionStorage.getItem(cacheKey);
                if (cached) {
                    const states = JSON.parse(cached);
                    states.forEach(state => {
                        const checkbox = document.querySelector(`input[value="${state.value}"]`);
                        if (checkbox) {
                            checkbox.checked = state.checked;
                        }
                    });
                }
            } catch (e) {
                console.warn('Failed to load checkbox cache:', e);
            }
            
            // Save states periodically
            setInterval(() => {
                this.saveCheckboxStates();
            }, 5000); // Save every 5 seconds
        },
        
        saveCheckboxStates() {
            const states = Array.from(document.querySelectorAll('.tag-checkbox')).map(checkbox => ({
                value: checkbox.value,
                checked: checkbox.checked
            }));
            
            try {
                sessionStorage.setItem('checkbox_states', JSON.stringify(states));
            } catch (e) {
                console.warn('Failed to save checkbox cache:', e);
            }
        }
    };
    
    // Excel Upload Performance Optimizer
    const ExcelOptimizer = {
        init() {
            if (!Utils.isWindows()) return;
            
            console.log('🔧 Initializing Excel Optimizer...');
            this.setupChunkedUpload();
            this.setupProgressTracking();
            this.setupUploadCaching();
        },
        
        setupChunkedUpload() {
            const fileInput = document.querySelector('input[type="file"][accept*="xlsx"], input[type="file"][accept*="xls"]');
            if (!fileInput) return;
            
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileUpload(file);
                }
            });
        },
        
        handleFileUpload(file) {
            Utils.measurePerformance('Excel Upload', () => {
                this.uploadFileChunked(file);
            });
        },
        
        uploadFileChunked(file) {
            const chunkSize = PC_PERFORMANCE_CONFIG.EXCEL_CHUNK_SIZE;
            const totalChunks = Math.ceil(file.size / chunkSize);
            
            console.log(`📊 Uploading ${file.name} in ${totalChunks} chunks`);
            
            // Show progress
            this.showUploadProgress(0, totalChunks);
            
            // Upload chunks sequentially to avoid overwhelming the server
            this.uploadChunksSequentially(file, chunkSize, totalChunks);
        },
        
        uploadChunksSequentially(file, chunkSize, totalChunks) {
            let currentChunk = 0;
            
            const uploadNextChunk = () => {
                if (currentChunk >= totalChunks) {
                    this.completeUpload();
                    return;
                }
                
                const start = currentChunk * chunkSize;
                const end = Math.min(start + chunkSize, file.size);
                const chunk = file.slice(start, end);
                
                this.uploadChunk(chunk, currentChunk, totalChunks)
                    .then(() => {
                        currentChunk++;
                        this.updateUploadProgress(currentChunk, totalChunks);
                        uploadNextChunk();
                    })
                    .catch(error => {
                        console.error('Chunk upload failed:', error);
                        this.handleUploadError(error);
                    });
            };
            
            uploadNextChunk();
        },
        
        uploadChunk(chunk, chunkIndex, totalChunks) {
            return new Promise((resolve, reject) => {
                const formData = new FormData();
                formData.append('chunk', chunk);
                formData.append('chunkIndex', chunkIndex);
                formData.append('totalChunks', totalChunks);
                
                fetch('/upload-chunk', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resolve(data);
                    } else {
                        reject(new Error(data.error));
                    }
                })
                .catch(reject);
            });
        },
        
        showUploadProgress(current, total) {
            // Create or update progress bar
            let progressBar = document.querySelector('.upload-progress');
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'upload-progress';
                progressBar.innerHTML = `
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-text">Uploading...</div>
                `;
                document.body.appendChild(progressBar);
            }
            
            const percentage = (current / total) * 100;
            const fill = progressBar.querySelector('.progress-fill');
            const text = progressBar.querySelector('.progress-text');
            
            if (fill) fill.style.width = `${percentage}%`;
            if (text) text.textContent = `Uploading... ${current}/${total} chunks (${percentage.toFixed(1)}%)`;
        },
        
        updateUploadProgress(current, total) {
            this.showUploadProgress(current, total);
        },
        
        completeUpload() {
            const progressBar = document.querySelector('.upload-progress');
            if (progressBar) {
                progressBar.remove();
            }
            
            // Trigger final processing
            this.finalizeUpload();
        },
        
        finalizeUpload() {
            fetch('/finalize-upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Upload completed successfully');
                    // Refresh data without full page reload
                    this.refreshData();
                } else {
                    console.error('Upload finalization failed:', data.error);
                }
            })
            .catch(error => {
                console.error('Upload finalization error:', error);
            });
        },
        
        refreshData() {
            // Refresh data without full page reload
            if (typeof TagManager !== 'undefined' && TagManager.loadAvailableTags) {
                TagManager.loadAvailableTags();
            }
            
            // Refresh dropdowns
            if (typeof DropdownOptimizer !== 'undefined') {
                DropdownOptimizer.setupDropdownCaching();
            }
        },
        
        handleUploadError(error) {
            console.error('Upload error:', error);
            const progressBar = document.querySelector('.upload-progress');
            if (progressBar) {
                progressBar.innerHTML = `
                    <div class="progress-error">Upload failed: ${error.message}</div>
                `;
            }
        },
        
        setupProgressTracking() {
            // Track upload performance metrics
            this.uploadMetrics = {
                startTime: 0,
                endTime: 0,
                totalSize: 0,
                chunksProcessed: 0
            };
        },
        
        setupUploadCaching() {
            // Cache upload results to avoid re-processing
            const cacheKey = 'upload_cache';
            
            // Clear old cache entries
            try {
                const cached = sessionStorage.getItem(cacheKey);
                if (cached) {
                    const data = JSON.parse(cached);
                    const now = Date.now();
                    if (now - data.timestamp > PC_PERFORMANCE_CONFIG.CACHE_DURATION_MS) {
                        sessionStorage.removeItem(cacheKey);
                    }
                }
            } catch (e) {
                console.warn('Failed to check upload cache:', e);
            }
        }
    };
    
    // Main initialization
    const PCPerformanceOptimizer = {
        init() {
            if (!Utils.isWindows()) {
                console.log('🍎 Mac detected - skipping PC optimizations');
                return;
            }
            
            console.log('🖥️ PC detected - initializing performance optimizations...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.initializeOptimizers();
                });
            } else {
                this.initializeOptimizers();
            }
        },
        
        initializeOptimizers() {
            DropdownOptimizer.init();
            CheckboxOptimizer.init();
            ExcelOptimizer.init();
            
            console.log('✅ PC Performance Optimizer initialized successfully');
            
            // Log performance metrics
            this.logPerformanceMetrics();
        },
        
        logPerformanceMetrics() {
            // Log initial performance metrics
            const metrics = {
                dropdownCacheSize: PerformanceState.dropdownCache.size,
                checkboxBatchQueueSize: PerformanceState.checkboxBatchQueue.length,
                activeRequests: PerformanceState.activeRequests,
                timestamp: Date.now()
            };
            
            console.log('📊 Performance Metrics:', metrics);
        }
    };
    
    // Auto-initialize
    PCPerformanceOptimizer.init();
    
    // Expose for debugging
    window.PCPerformanceOptimizer = PCPerformanceOptimizer;
    window.PerformanceState = PerformanceState;
    
    console.log('🚀 PC Performance Optimizer loaded successfully');
})();
