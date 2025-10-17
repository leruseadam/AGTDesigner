/**
 * PC Performance Optimizer
 * Optimizes web application performance specifically for PC browsers
 * Addresses issues with scroll performance, rendering, and general responsiveness
 */

(function() {
    'use strict';

    // Detect if user is on PC (not mobile/tablet)
    const isPC = () => {
        return !/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            && window.innerWidth >= 1024;
    };

    // Performance optimization utilities
    const PCPerformanceOptimizer = {
        
        /**
         * Initialize all PC-specific optimizations
         */
        init() {
            if (!isPC()) {
                console.log('Mobile/tablet detected - skipping PC-specific optimizations');
                return;
            }

            console.log('PC detected - applying performance optimizations');
            
            this.optimizeScrolling();
            this.optimizeRendering();
            this.enableHardwareAcceleration();
            this.optimizeEventListeners();
            this.reduceLayoutThrashing();
            this.optimizeAnimations();
        },

        /**
         * Optimize scrolling performance
         */
        optimizeScrolling() {
            // Add CSS smooth scrolling to all scrollable elements
            const scrollableElements = document.querySelectorAll(
                '.tag-list-container, .modal-body, [style*="overflow"], .table-responsive'
            );

            scrollableElements.forEach(element => {
                // Enable CSS smooth scrolling instead of JavaScript-based scrolling
                element.style.scrollBehavior = 'smooth';
                
                // Optimize scrollbar rendering on Windows
                element.style.scrollbarWidth = 'thin';
                element.style.scrollbarColor = 'rgba(160, 132, 232, 0.5) transparent';
            });

            // Add custom scrollbar styles for Chromium browsers on Windows
            const style = document.createElement('style');
            style.textContent = `
                /* Optimized scrollbars for PC */
                ::-webkit-scrollbar {
                    width: 12px;
                    height: 12px;
                }
                
                ::-webkit-scrollbar-track {
                    background: rgba(0, 0, 0, 0.05);
                    border-radius: 6px;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: rgba(160, 132, 232, 0.5);
                    border-radius: 6px;
                    border: 2px solid transparent;
                    background-clip: padding-box;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: rgba(160, 132, 232, 0.7);
                    background-clip: padding-box;
                }
                
                ::-webkit-scrollbar-thumb:active {
                    background: rgba(160, 132, 232, 0.9);
                    background-clip: padding-box;
                }
            `;
            document.head.appendChild(style);
        },

        /**
         * Enable hardware acceleration for better rendering
         */
        enableHardwareAcceleration() {
            const elementsToAccelerate = document.querySelectorAll(
                '.tag-item, .tag-row, .modal, .dropdown-menu, .card, .glass-card'
            );

            elementsToAccelerate.forEach(element => {
                // Use CSS transforms to trigger GPU acceleration
                if (!element.style.transform) {
                    element.style.transform = 'translateZ(0)';
                }
                element.style.backfaceVisibility = 'hidden';
                element.style.perspective = '1000px';
            });
        },

        /**
         * Optimize rendering performance
         */
        optimizeRendering() {
            // Use requestAnimationFrame for DOM updates
            let rafId = null;
            const updates = [];

            window.scheduleDOMUpdate = (callback) => {
                updates.push(callback);
                
                if (!rafId) {
                    rafId = requestAnimationFrame(() => {
                        // Batch all DOM updates together
                        updates.forEach(cb => cb());
                        updates.length = 0;
                        rafId = null;
                    });
                }
            };

            // Optimize DOM queries - cache frequently accessed elements
            window.cachedElements = window.cachedElements || {};
            
            const originalQuerySelector = document.querySelector.bind(document);
            const originalQuerySelectorAll = document.querySelectorAll.bind(document);
            
            // Cache querySelector results for better performance
            document.querySelector = function(selector) {
                const cacheKey = `qs_${selector}`;
                if (window.cachedElements[cacheKey]) {
                    return window.cachedElements[cacheKey];
                }
                const result = originalQuerySelector(selector);
                if (result && !selector.includes('[')) { // Don't cache attribute selectors
                    window.cachedElements[cacheKey] = result;
                }
                return result;
            };
        },

        /**
         * Optimize event listeners with proper throttling and debouncing
         */
        optimizeEventListeners() {
            // Remove any existing wheel event listeners that prevent default
            const containers = document.querySelectorAll('.tag-list-container');
            containers.forEach(container => {
                // Clone and replace to remove all event listeners
                const clone = container.cloneNode(true);
                if (container.parentNode) {
                    container.parentNode.replaceChild(clone, container);
                }
            });

            // Add passive event listeners for better scroll performance
            const passiveEvents = ['scroll', 'wheel', 'touchstart', 'touchmove', 'touchend'];
            const originalAddEventListener = EventTarget.prototype.addEventListener;
            
            EventTarget.prototype.addEventListener = function(type, listener, options) {
                if (passiveEvents.includes(type)) {
                    // Force passive for scroll-related events
                    if (typeof options === 'object') {
                        options.passive = true;
                    } else {
                        options = { passive: true };
                    }
                }
                return originalAddEventListener.call(this, type, listener, options);
            };
        },

        /**
         * Reduce layout thrashing by batching reads and writes
         */
        reduceLayoutThrashing() {
            // Create a queue for layout reads and writes
            const readQueue = [];
            const writeQueue = [];
            let scheduled = false;

            const flush = () => {
                // First, perform all reads
                readQueue.forEach(fn => fn());
                readQueue.length = 0;

                // Then, perform all writes
                writeQueue.forEach(fn => fn());
                writeQueue.length = 0;

                scheduled = false;
            };

            window.readDOM = (fn) => {
                readQueue.push(fn);
                if (!scheduled) {
                    scheduled = true;
                    requestAnimationFrame(flush);
                }
            };

            window.writeDOM = (fn) => {
                writeQueue.push(fn);
                if (!scheduled) {
                    scheduled = true;
                    requestAnimationFrame(flush);
                }
            };
        },

        /**
         * Optimize animations and transitions
         */
        optimizeAnimations() {
            // Remove will-change when not animating
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        const element = mutation.target;
                        
                        // Remove will-change after animation completes
                        if (element.style.willChange && element.style.willChange !== 'auto') {
                            setTimeout(() => {
                                if (!element.matches(':hover, :active, :focus')) {
                                    element.style.willChange = 'auto';
                                }
                            }, 300);
                        }
                    }
                });
            });

            // Observe elements that might animate
            const animatingElements = document.querySelectorAll(
                '.tag-item, .tag-row, .modal, .dropdown-menu, .btn'
            );

            animatingElements.forEach(element => {
                observer.observe(element, { attributes: true, attributeFilter: ['class'] });
            });

            // Add hover listeners to apply will-change only when needed
            const hoverElements = document.querySelectorAll('.tag-item, .tag-row, .btn');
            hoverElements.forEach(element => {
                element.addEventListener('mouseenter', () => {
                    element.style.willChange = 'transform, opacity';
                }, { passive: true });

                element.addEventListener('mouseleave', () => {
                    setTimeout(() => {
                        element.style.willChange = 'auto';
                    }, 300);
                }, { passive: true });
            });
        },

        /**
         * Monitor and log performance metrics
         */
        monitorPerformance() {
            if (window.PerformanceObserver) {
                // Monitor long tasks
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {
                            console.warn(`Long task detected: ${entry.duration.toFixed(2)}ms`);
                        }
                    }
                });

                try {
                    observer.observe({ entryTypes: ['longtask'] });
                } catch (e) {
                    // longtask not supported in all browsers
                }
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            PCPerformanceOptimizer.init();
            PCPerformanceOptimizer.monitorPerformance();
        });
    } else {
        // DOM already loaded
        PCPerformanceOptimizer.init();
        PCPerformanceOptimizer.monitorPerformance();
    }

    // Make available globally
    window.PCPerformanceOptimizer = PCPerformanceOptimizer;

    console.log('PC Performance Optimizer loaded');
})();

