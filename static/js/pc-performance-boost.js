/**
 * Enhanced PC Performance Boost
 * 
 * This script provides additional aggressive optimizations for Windows/PC browsers
 * to improve scrolling, UI responsiveness, and general performance.
 * 
 * Key improvements:
 * 1. Debounced scroll event handlers (reduce CPU usage)
 * 2. RequestAnimationFrame-based rendering
 * 3. Virtual scrolling for large lists
 * 4. Intersection Observer for lazy rendering
 * 5. Reduced DOM queries with caching
 * 6. Optimized event delegation
 * 7. GPU compositing optimization
 */

class PCPerformanceBoost {
    constructor() {
        this.isPC = this.detectPC();
        this.observers = new Map();
        this.renderQueue = [];
        this.rafId = null;
        this.elementCache = new Map();
        this.scrollEndTimers = new Map();
        
        // Performance thresholds
        this.SCROLL_THROTTLE = 16; // ~60fps
        this.RESIZE_DEBOUNCE = 150;
        this.DOM_BATCH_SIZE = 20;
        
        if (this.isPC) {
            console.log('🚀 PC Performance Boost: Activating enhanced optimizations');
            this.init();
        }
    }
    
    detectPC() {
        const ua = navigator.userAgent;
        return /Windows|Win32|Win64|Linux|CrOS/.test(ua) || 
               (!/Mac/.test(ua) && !/iPhone|iPad|iPod/.test(ua));
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.applyOptimizations());
        } else {
            this.applyOptimizations();
        }
    }
    
    applyOptimizations() {
        // Core optimizations
        this.optimizeScrollPerformance();
        this.optimizeResizeHandlers();
        this.optimizeDOMOperations();
        this.implementVirtualScrolling();
        this.optimizeEventHandlers();
        this.reduceRepaints();
        this.optimizeAnimations();
        this.setupIntersectionObserver();
        this.optimizeTableRendering();
        this.disableExpensiveEffects();
        
        console.log('✅ PC Performance Boost: All optimizations applied');
    }
    
    /**
     * Optimize scroll performance with passive listeners and throttling
     */
    optimizeScrollPerformance() {
        // Remove existing scroll listeners that might be causing issues
        const scrollableElements = [
            window,
            ...document.querySelectorAll('.tag-list-container, #availableTags, #selectedTags, .modal-body')
        ];
        
        scrollableElements.forEach(element => {
            // Create optimized scroll handler
            const scrollHandler = this.throttle(() => {
                requestAnimationFrame(() => {
                    // Only update if element is visible
                    if (element === window || this.isElementVisible(element)) {
                        element.classList?.remove('scrolling');
                    }
                });
            }, this.SCROLL_THROTTLE);
            
            // Passive listener for better performance
            element.addEventListener('scroll', (e) => {
                element.classList?.add('scrolling');
                scrollHandler();
            }, { passive: true, capture: false });
        });
        
        // Disable smooth scroll behavior globally on PC
        document.documentElement.style.scrollBehavior = 'auto';
        document.body.style.scrollBehavior = 'auto';
        
        console.log('✅ Optimized scroll performance');
    }
    
    /**
     * Optimize resize handlers with debouncing
     */
    optimizeResizeHandlers() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            document.body.classList.add('resizing');
            
            resizeTimeout = setTimeout(() => {
                requestAnimationFrame(() => {
                    document.body.classList.remove('resizing');
                    this.elementCache.clear(); // Clear cache on resize
                });
            }, this.RESIZE_DEBOUNCE);
        }, { passive: true });
        
        // Add CSS for resizing state
        this.addStyle(`
            body.resizing * {
                transition: none !important;
                animation: none !important;
            }
        `, 'pc-resize-optimization');
        
        console.log('✅ Optimized resize handlers');
    }
    
    /**
     * Batch DOM operations for better performance
     */
    optimizeDOMOperations() {
        // Override common DOM manipulation methods with batched versions
        window.batchedUpdates = (callback) => {
            this.renderQueue.push(callback);
            
            if (!this.rafId) {
                this.rafId = requestAnimationFrame(() => {
                    const queue = [...this.renderQueue];
                    this.renderQueue = [];
                    this.rafId = null;
                    
                    // Execute all queued operations
                    queue.forEach(cb => {
                        try {
                            cb();
                        } catch (error) {
                            console.error('Batched operation failed:', error);
                        }
                    });
                });
            }
        };
        
        console.log('✅ Enabled batched DOM operations');
    }
    
    /**
     * Implement virtual scrolling for large lists
     */
    implementVirtualScrolling() {
        const largeContainers = document.querySelectorAll('#availableTags, #selectedTags');
        
        largeContainers.forEach(container => {
            if (!container) return;
            
            const items = container.querySelectorAll('.tag-item, .tag-row');
            if (items.length < 50) return; // Only virtualize if many items
            
            // Set up virtual scrolling
            const ITEM_HEIGHT = 60;
            const BUFFER = 5;
            
            const updateVisibleItems = this.throttle(() => {
                if (!this.isElementVisible(container)) return;
                
                const scrollTop = container.scrollTop;
                const containerHeight = container.clientHeight;
                
                const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER);
                const endIndex = Math.min(
                    items.length,
                    Math.ceil((scrollTop + containerHeight) / ITEM_HEIGHT) + BUFFER
                );
                
                requestAnimationFrame(() => {
                    items.forEach((item, index) => {
                        if (index >= startIndex && index < endIndex) {
                            item.style.display = '';
                            item.style.contentVisibility = 'visible';
                        } else {
                            item.style.contentVisibility = 'hidden';
                        }
                    });
                });
            }, this.SCROLL_THROTTLE);
            
            container.addEventListener('scroll', updateVisibleItems, { passive: true });
            updateVisibleItems(); // Initial render
        });
        
        console.log('✅ Implemented virtual scrolling');
    }
    
    /**
     * Optimize event handlers with delegation
     */
    optimizeEventHandlers() {
        // Use event delegation instead of individual listeners
        document.body.addEventListener('click', (e) => {
            const target = e.target;
            
            // Handle button clicks
            if (target.closest('.btn, button')) {
                const button = target.closest('.btn, button');
                
                // Prevent double-clicks
                if (button.classList.contains('btn-processing')) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
                
                button.classList.add('btn-processing');
                setTimeout(() => button.classList.remove('btn-processing'), 300);
            }
            
            // Handle tag clicks
            if (target.closest('.tag-item, .tag-row')) {
                requestAnimationFrame(() => {
                    // Tag selection logic handled by existing TagManager
                });
            }
        }, { passive: false });
        
        console.log('✅ Optimized event handlers');
    }
    
    /**
     * Reduce repaints and reflows
     */
    reduceRepaints() {
        this.addStyle(`
            /* Reduce repaints during interactions */
            * {
                /* Disable will-change to reduce memory usage on PC */
                will-change: auto !important;
            }
            
            /* Use containment for better paint performance */
            .tag-item, .tag-row, .card, .modal-content {
                contain: layout style paint;
            }
            
            /* Disable expensive effects during scroll */
            body.scrolling *, body.resizing * {
                pointer-events: none !important;
                box-shadow: none !important;
                text-shadow: none !important;
                filter: none !important;
            }
            
            /* Optimize dropdown/select performance */
            select, option {
                contain: layout style;
            }
            
            /* Prevent button processing double-clicks */
            .btn-processing {
                pointer-events: none !important;
                opacity: 0.7 !important;
            }
        `, 'pc-repaint-optimization');
        
        console.log('✅ Reduced repaints and reflows');
    }
    
    /**
     * Optimize animations for PC
     */
    optimizeAnimations() {
        this.addStyle(`
            /* Aggressive animation reduction for PC */
            @media (pointer: fine) {
                * {
                    animation-duration: 0.15s !important;
                    transition-duration: 0.15s !important;
                }
                
                /* Instant transitions for scroll and resize */
                body.scrolling *, body.resizing * {
                    animation-duration: 0s !important;
                    transition-duration: 0s !important;
                }
                
                /* Disable complex keyframe animations */
                @keyframes trippyTieDye {
                    0%, 100% { 
                        transform: none !important;
                        filter: none !important;
                    }
                }
                
                /* Simplify hover effects */
                .btn:hover, .card:hover, .tag-item:hover {
                    transform: none !important;
                }
                
                /* Faster modal animations */
                .modal.fade .modal-dialog {
                    transition: opacity 0.1s ease !important;
                }
            }
        `, 'pc-animation-optimization');
        
        console.log('✅ Optimized animations');
    }
    
    /**
     * Setup Intersection Observer for lazy rendering
     */
    setupIntersectionObserver() {
        const observerOptions = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.contentVisibility = 'visible';
                } else {
                    entry.target.style.contentVisibility = 'auto';
                }
            });
        }, observerOptions);
        
        // Observe heavy elements
        const heavyElements = document.querySelectorAll('.card, .vendor-section, .brand-section, .weight-section');
        heavyElements.forEach(el => observer.observe(el));
        
        this.observers.set('intersection', observer);
        
        console.log('✅ Setup Intersection Observer');
    }
    
    /**
     * Optimize table rendering
     */
    optimizeTableRendering() {
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            table.style.tableLayout = 'fixed';
            table.style.contain = 'layout style paint';
            
            // Use content-visibility for table rows
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                row.style.contain = 'layout style';
            });
        });
        
        console.log('✅ Optimized table rendering');
    }
    
    /**
     * Disable expensive visual effects on PC
     */
    disableExpensiveEffects() {
        this.addStyle(`
            /* Disable expensive effects */
            .blur, [style*="blur"] {
                filter: none !important;
                backdrop-filter: none !important;
            }
            
            /* Simplify shadows */
            .shadow, .shadow-sm, .shadow-lg,
            .card, .modal-content, .dropdown-menu {
                box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            }
            
            /* Disable gradients on PC */
            .gradient, .bg-gradient {
                background-image: none !important;
            }
            
            /* Simplify borders */
            * {
                border-radius: min(0.25rem, 4px) !important;
            }
            
            /* Optimize input rendering */
            input, select, textarea {
                appearance: auto !important;
                -webkit-appearance: auto !important;
            }
        `, 'pc-effects-optimization');
        
        console.log('✅ Disabled expensive effects');
    }
    
    /**
     * Check if element is visible in viewport
     */
    isElementVisible(element) {
        if (element === window) return true;
        if (!element || !element.getBoundingClientRect) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top < window.innerHeight &&
            rect.bottom > 0 &&
            rect.left < window.innerWidth &&
            rect.right > 0
        );
    }
    
    /**
     * Get cached element or query and cache it
     */
    getCachedElement(selector) {
        if (this.elementCache.has(selector)) {
            const cached = this.elementCache.get(selector);
            if (document.contains(cached)) {
                return cached;
            }
            this.elementCache.delete(selector);
        }
        
        const element = document.querySelector(selector);
        if (element) {
            this.elementCache.set(selector, element);
        }
        return element;
    }
    
    /**
     * Add optimized styles
     */
    addStyle(css, id) {
        const existing = document.getElementById(id);
        if (existing) existing.remove();
        
        const style = document.createElement('style');
        style.id = id;
        style.textContent = css;
        document.head.appendChild(style);
    }
    
    /**
     * Throttle function
     */
    throttle(func, limit) {
        let lastCall = 0;
        return function(...args) {
            const now = Date.now();
            if (now - lastCall >= limit) {
                lastCall = now;
                return func.apply(this, args);
            }
        };
    }
    
    /**
     * Debounce function
     */
    debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }
    
    /**
     * Monitor and log performance metrics
     */
    monitorPerformance() {
        if (!this.isPC) return;
        
        // Monitor FPS
        let frameCount = 0;
        let lastTime = performance.now();
        let lowFPSCount = 0;
        
        const measureFPS = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime >= lastTime + 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                
                if (fps < 30) {
                    lowFPSCount++;
                    if (lowFPSCount >= 3) {
                        console.warn(`⚠️ Low FPS detected: ${fps} fps - Consider further optimization`);
                        lowFPSCount = 0;
                    }
                } else {
                    lowFPSCount = 0;
                }
                
                frameCount = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(measureFPS);
        };
        
        requestAnimationFrame(measureFPS);
    }
    
    /**
     * Clean up and destroy
     */
    destroy() {
        // Cancel any pending RAF
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
        }
        
        // Disconnect observers
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        
        // Clear caches
        this.elementCache.clear();
        this.renderQueue = [];
        
        console.log('🛑 PC Performance Boost: Deactivated');
    }
}

// Initialize on load
let pcBoost;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        pcBoost = new PCPerformanceBoost();
        pcBoost.monitorPerformance();
    });
} else {
    pcBoost = new PCPerformanceBoost();
    pcBoost.monitorPerformance();
}

// Export for global access
window.PCPerformanceBoost = PCPerformanceBoost;
window.pcBoost = pcBoost;

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PCPerformanceBoost;
}

