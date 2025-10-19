/**
 * Windows PC Performance Optimization
 * 
 * This module optimizes the application for better performance on Windows/PC browsers
 * which tend to have slower rendering than Mac Safari.
 * 
 * Key optimizations:
 * 1. Reduce CSS transitions/transforms
 * 2. Implement virtual scrolling for large lists
 * 3. Throttle scroll events aggressively
 * 4. Batch DOM updates
 * 5. Reduce querySelectorAll calls
 * 6. Optimize table rendering
 */

class WindowsPerformanceOptimizer {
    constructor() {
        this.isWindows = this.detectWindows();
        this.isChrome = /Chrome/.test(navigator.userAgent);
        this.isEdge = /Edg/.test(navigator.userAgent);
        this.cachedElements = new Map();
        this.scrollThrottleDelay = this.isWindows ? 100 : 50; // Longer throttle on Windows
        this.init();
    }

    detectWindows() {
        return /Windows|Win32|Win64/.test(navigator.userAgent);
    }

    init() {
        if (this.isWindows) {
            console.log('🪟 Windows detected - applying performance optimizations');
            this.applyWindowsOptimizations();
        }
    }

    applyWindowsOptimizations() {
        // Apply all optimizations
        this.optimizeScrollbars();
        this.reduceTransitions();
        this.implementVirtualScrolling();
        this.optimizeTableRendering();
        this.batchDOMOperations();
        this.cacheSelectors();
        this.optimizeAnimations();
        this.addWindowsCSS();
    }

    /**
     * Optimize scrollbar performance on Windows
     */
    optimizeScrollbars() {
        const style = document.createElement('style');
        style.id = 'windows-scrollbar-optimization';
        style.textContent = `
            /* Windows scrollbar optimization */
            * {
                /* Use browser's native scrollbar rendering */
                scrollbar-width: auto;
                scrollbar-gutter: stable;
            }
            
            /* DISABLE smooth scrolling on Windows - it's slower */
            html {
                scroll-behavior: auto !important;
            }
            
            /* Optimize scrollable containers */
            .scrollable-container,
            #availableTags,
            #selectedTags,
            .tag-list-container,
            .modal-body {
                /* Disable GPU compositing that causes lag on Windows */
                transform: none !important;
                will-change: auto !important;
                
                /* Use native scrolling - faster on Windows */
                overflow-y: auto;
                overflow-x: hidden;
                -webkit-overflow-scrolling: auto;
                
                /* Prevent unnecessary repaints */
                backface-visibility: hidden;
                -webkit-backface-visibility: hidden;
                
                /* Use CSS containment for better performance */
                contain: layout style paint;
                
                /* Optimize rendering */
                -webkit-font-smoothing: subpixel-antialiased;
                -moz-osx-font-smoothing: auto;
            }
            
            /* Remove heavy box shadows during scroll */
            .scrolling,
            .scrolling * {
                box-shadow: none !important;
                transition: none !important;
            }
            
            /* Simplify custom scrollbars on Windows */
            ::-webkit-scrollbar {
                width: 12px;
                height: 12px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.1);
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 0, 0, 0.5);
            }
        `;
        document.head.appendChild(style);

        // Disable custom smooth scrolling event handlers on Windows
        this.disableCustomScrollBehavior();
        
        // Throttle scroll events aggressively on Windows
        this.throttleScrollEvents();
    }

    /**
     * Disable custom smooth scrolling that interferes with native scrolling
     */
    disableCustomScrollBehavior() {
        // Remove wheel event listeners that prevent default scrolling
        document.querySelectorAll('.tag-list-container, .scrollable-container').forEach(container => {
            const clone = container.cloneNode(true);
            container.parentNode.replaceChild(clone, container);
        });
        
        console.log('🪟 Disabled custom smooth scrolling for better Windows performance');
    }

    /**
     * Throttle scroll events to reduce CPU usage
     */
    throttleScrollEvents() {
        let scrolling = false;
        let scrollTimeout;

        const scrollHandler = this.throttle(() => {
            document.body.classList.remove('scrolling');
            scrolling = false;
        }, this.scrollThrottleDelay);

        window.addEventListener('scroll', () => {
            if (!scrolling) {
                document.body.classList.add('scrolling');
                scrolling = true;
            }
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(scrollHandler, this.scrollThrottleDelay);
        }, { passive: true });

        // Also handle container scrolls
        document.addEventListener('scroll', (e) => {
            if (e.target.classList.contains('scrollable-container')) {
                e.target.classList.add('scrolling');
                clearTimeout(e.target.scrollTimeout);
                e.target.scrollTimeout = setTimeout(() => {
                    e.target.classList.remove('scrolling');
                }, this.scrollThrottleDelay);
            }
        }, { passive: true, capture: true });
    }

    /**
     * Reduce CSS transitions for better Windows performance
     */
    reduceTransitions() {
        const style = document.createElement('style');
        style.id = 'windows-transition-optimization';
        style.textContent = `
            /* Reduce transition durations on Windows */
            .tag-item,
            .tag-row,
            .btn,
            .card,
            .modal {
                transition-duration: 0.1s !important;
            }
            
            /* Disable expensive transforms during interactions */
            .tag-item:hover,
            .btn:hover {
                transform: none !important;
            }
            
            /* Simplify animations */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Disable will-change on Windows for better performance */
            * {
                will-change: auto !important;
            }
            
            /* Reduce animation complexity */
            .spinner,
            .loading-spinner {
                animation-duration: 1s !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Implement virtual scrolling for large lists
     */
    implementVirtualScrolling() {
        const containers = ['availableTags', 'selectedTags'];
        
        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (!container) return;

            // Create virtual scroll wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'virtual-scroll-wrapper';
            wrapper.style.cssText = `
                height: 500px;
                overflow-y: auto;
                position: relative;
            `;

            // Only render visible items + buffer
            this.setupVirtualScroll(container, wrapper);
        });
    }

    /**
     * Setup virtual scrolling for a container
     */
    setupVirtualScroll(container, wrapper) {
        const ITEM_HEIGHT = 60; // Approximate height of each tag item
        const BUFFER_SIZE = 10; // Number of items to render above/below viewport

        let allItems = [];
        let visibleStart = 0;
        let visibleEnd = 0;

        const updateVisibleItems = this.throttle(() => {
            const scrollTop = wrapper.scrollTop;
            const viewportHeight = wrapper.clientHeight;

            visibleStart = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_SIZE);
            visibleEnd = Math.min(
                allItems.length,
                Math.ceil((scrollTop + viewportHeight) / ITEM_HEIGHT) + BUFFER_SIZE
            );

            this.renderVisibleItems(container, allItems, visibleStart, visibleEnd);
        }, 50);

        wrapper.addEventListener('scroll', updateVisibleItems, { passive: true });
    }

    /**
     * Render only visible items in the viewport
     */
    renderVisibleItems(container, items, start, end) {
        // Use DocumentFragment for better performance
        const fragment = document.createDocumentFragment();
        
        for (let i = start; i < end; i++) {
            if (items[i]) {
                fragment.appendChild(items[i]);
            }
        }

        requestAnimationFrame(() => {
            container.innerHTML = '';
            container.appendChild(fragment);
        });
    }

    /**
     * Optimize table rendering
     */
    optimizeTableRendering() {
        // Override table creation to use DocumentFragment
        const originalCreateElement = document.createElement;
        
        window.createOptimizedTable = (rows) => {
            const fragment = document.createDocumentFragment();
            const tbody = document.createElement('tbody');
            
            // Batch create rows
            rows.forEach(rowData => {
                const tr = document.createElement('tr');
                tr.className = 'tag-row';
                tr.innerHTML = rowData;
                tbody.appendChild(tr);
            });
            
            fragment.appendChild(tbody);
            return fragment;
        };
    }

    /**
     * Batch DOM operations to reduce reflows
     */
    batchDOMOperations() {
        // Create a queue for DOM operations
        let domQueue = [];
        let rafPending = false;

        window.batchDOM = (operation) => {
            domQueue.push(operation);
            
            if (!rafPending) {
                rafPending = true;
                requestAnimationFrame(() => {
                    // Execute all queued operations in one batch
                    domQueue.forEach(op => {
                        try {
                            op();
                        } catch (e) {
                            console.error('Batched DOM operation failed:', e);
                        }
                    });
                    
                    domQueue = [];
                    rafPending = false;
                });
            }
        };
    }

    /**
     * Cache commonly used selectors
     */
    cacheSelectors() {
        // Common selectors
        const commonSelectors = [
            '#availableTags',
            '#selectedTags',
            '#productTypeFilter',
            '#vendorFilter',
            '#searchInput',
            '.tag-list-container',
            '.modal-body'
        ];

        commonSelectors.forEach(selector => {
            try {
                const element = document.querySelector(selector);
                if (element) {
                    this.cachedElements.set(selector, element);
                }
            } catch (e) {
                // Selector not found, skip
            }
        });

        // Create a cached selector function
        window.getCachedElement = (selector) => {
            if (this.cachedElements.has(selector)) {
                return this.cachedElements.get(selector);
            }
            
            const element = document.querySelector(selector);
            if (element) {
                this.cachedElements.set(selector, element);
            }
            return element;
        };
    }

    /**
     * Optimize animations for Windows
     */
    optimizeAnimations() {
        // Detect if user prefers reduced motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion || this.isWindows) {
            const style = document.createElement('style');
            style.id = 'reduced-animations';
            style.textContent = `
                /* Reduce all animations */
                * {
                    animation-duration: 0.01s !important;
                    transition-duration: 0.01s !important;
                }
                
                /* Disable complex animations */
                @keyframes trippyTieDye {
                    0%, 100% { transform: none; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Add Windows-specific CSS optimizations
     */
    addWindowsCSS() {
        const style = document.createElement('style');
        style.id = 'windows-css-optimization';
        style.textContent = `
            /* Windows-specific CSS optimizations */
            
            /* Use GPU acceleration wisely on Windows */
            .card,
            .modal-content,
            .btn {
                transform: translate3d(0, 0, 0);
            }
            
            /* Optimize font rendering for Windows */
            body {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;
            }
            
            /* Reduce paint areas */
            .tag-item,
            .tag-row {
                contain: layout style paint;
            }
            
            /* Optimize scrollable areas */
            .scrollable-container {
                /* Use containment for better performance */
                contain: layout style paint;
                content-visibility: auto;
            }
            
            /* Reduce expensive effects */
            .shadow,
            .card {
                box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            }
            
            /* Optimize table rendering */
            table {
                table-layout: fixed;
                width: 100%;
            }
            
            /* Optimize dropdown rendering */
            select.form-select {
                appearance: auto;
                -webkit-appearance: auto;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Throttle utility function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Debounce utility function
     */
    debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Monitor performance and log issues
     */
    monitorPerformance() {
        if (!this.isWindows) return;

        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {
                            console.warn(`⚠️ Long task detected: ${entry.duration.toFixed(2)}ms`);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                // PerformanceObserver not supported
            }
        }

        // Monitor frame rate
        let lastTime = performance.now();
        let frames = 0;
        
        const checkFPS = () => {
            frames++;
            const currentTime = performance.now();
            
            if (currentTime >= lastTime + 1000) {
                const fps = Math.round((frames * 1000) / (currentTime - lastTime));
                
                if (fps < 30) {
                    console.warn(`⚠️ Low FPS detected: ${fps} fps`);
                }
                
                frames = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(checkFPS);
        };
        
        requestAnimationFrame(checkFPS);
    }

    /**
     * Optimize specific UI components
     */
    optimizeUIComponents() {
        // Optimize tag lists
        const tagLists = document.querySelectorAll('#availableTags, #selectedTags');
        tagLists.forEach(list => {
            list.style.contain = 'layout style paint';
            list.style.contentVisibility = 'auto';
        });

        // Optimize dropdowns
        const dropdowns = document.querySelectorAll('.form-select');
        dropdowns.forEach(dropdown => {
            // Use native rendering on Windows
            dropdown.style.appearance = 'auto';
        });

        // Optimize modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', () => {
                document.body.classList.add('modal-opening');
            });
            
            modal.addEventListener('shown.bs.modal', () => {
                document.body.classList.remove('modal-opening');
            });
        });
        
        // Optimize input events
        this.optimizeInputEvents();
        
        // Optimize click events
        this.optimizeClickEvents();
    }

    /**
     * Optimize input events with debouncing
     */
    optimizeInputEvents() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
        inputs.forEach(input => {
            // Remove existing input listeners and add debounced version
            const originalHandler = input.oninput;
            if (originalHandler) {
                input.oninput = this.debounce(originalHandler, 150);
            }
        });
        
        console.log('🪟 Optimized input events with debouncing');
    }

    /**
     * Optimize click events to prevent double-clicks
     */
    optimizeClickEvents() {
        const buttons = document.querySelectorAll('button, .btn, [role="button"]');
        buttons.forEach(button => {
            let lastClick = 0;
            button.addEventListener('click', (e) => {
                const now = Date.now();
                if (now - lastClick < 300) {
                    // Prevent rapid clicks
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }
                lastClick = now;
            }, { capture: true });
        });
        
        console.log('🪟 Optimized click events to prevent double-clicks');
    }

    /**
     * Clean up cached elements periodically
     */
    cleanupCache() {
        setInterval(() => {
            // Verify cached elements still exist in DOM
            for (const [selector, element] of this.cachedElements.entries()) {
                if (!document.contains(element)) {
                    this.cachedElements.delete(selector);
                }
            }
        }, 30000); // Every 30 seconds
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.windowsOptimizer = new WindowsPerformanceOptimizer();
        window.windowsOptimizer.monitorPerformance();
        window.windowsOptimizer.optimizeUIComponents();
        window.windowsOptimizer.cleanupCache();
    });
} else {
    window.windowsOptimizer = new WindowsPerformanceOptimizer();
    window.windowsOptimizer.monitorPerformance();
    window.windowsOptimizer.optimizeUIComponents();
    window.windowsOptimizer.cleanupCache();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WindowsPerformanceOptimizer;
}

