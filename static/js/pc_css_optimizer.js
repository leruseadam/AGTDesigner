/**
 * PC Performance CSS Optimizations
 * Adds CSS optimizations specifically for PC users
 */

(function() {
    'use strict';
    
    // Check if this is a Windows PC
    const isWindows = navigator.platform.indexOf('Win') > -1 || 
                     navigator.userAgent.indexOf('Windows') > -1;
    
    if (!isWindows) {
        console.log('🍎 Mac detected - skipping PC CSS optimizations');
        return;
    }
    
    console.log('🖥️ PC detected - applying CSS performance optimizations...');
    
    // Create style element
    const style = document.createElement('style');
    style.id = 'pc-performance-styles';
    
    // PC-specific CSS optimizations
    style.textContent = `
        /* PC Performance Optimizations */
        
        /* Hardware acceleration for better performance */
        .tag-item, .tag-checkbox, .dropdown-item, .select-option {
            transform: translateZ(0);
            will-change: transform, opacity;
            backface-visibility: hidden;
        }
        
        /* Optimize checkbox rendering */
        .tag-checkbox {
            transform: translateZ(0);
            -webkit-transform: translateZ(0);
            -moz-transform: translateZ(0);
            -ms-transform: translateZ(0);
            -o-transform: translateZ(0);
        }
        
        /* Smooth transitions for better UX */
        .tag-item {
            transition: all 0.15s ease-out;
            -webkit-transition: all 0.15s ease-out;
            -moz-transition: all 0.15s ease-out;
            -ms-transition: all 0.15s ease-out;
            -o-transition: all 0.15s ease-out;
        }
        
        /* Optimize dropdown performance */
        .dropdown-menu, .select-container {
            contain: layout style paint;
            transform: translateZ(0);
        }
        
        /* Virtual scrolling container */
        .virtual-scroll-container {
            overflow-y: auto;
            overflow-x: hidden;
            contain: strict;
        }
        
        /* Optimize large lists */
        .tag-list, .available-tags, .selected-tags {
            contain: layout style paint;
            transform: translateZ(0);
        }
        
        /* Progress bar optimizations */
        .upload-progress {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            min-width: 300px;
            transform: translateZ(0);
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            border-radius: 4px;
            transition: width 0.3s ease;
            transform: translateZ(0);
        }
        
        .progress-text {
            font-size: 14px;
            text-align: center;
            margin-top: 5px;
        }
        
        .progress-error {
            color: #ff6b6b;
            font-weight: bold;
            text-align: center;
        }
        
        /* Optimize checkbox states */
        .tag-selected {
            background-color: rgba(76, 175, 80, 0.1);
            border-color: #4CAF50;
        }
        
        /* Batch processing indicator */
        .batch-processing {
            opacity: 0.7;
            pointer-events: none;
        }
        
        /* Optimize form elements */
        input[type="text"], input[type="search"], select {
            transform: translateZ(0);
            -webkit-transform: translateZ(0);
            -moz-transform: translateZ(0);
            -ms-transform: translateZ(0);
            -o-transform: translateZ(0);
        }
        
        /* Optimize file upload area */
        .file-upload-area {
            transform: translateZ(0);
            contain: layout style paint;
        }
        
        /* Performance monitoring styles */
        .performance-metrics {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            z-index: 9998;
            display: none;
        }
        
        .performance-metrics.show {
            display: block;
        }
        
        /* Optimize large tables */
        table {
            contain: layout style paint;
        }
        
        /* Optimize modal performance */
        .modal {
            transform: translateZ(0);
            contain: layout style paint;
        }
        
        /* Optimize button performance */
        button, .btn {
            transform: translateZ(0);
            -webkit-transform: translateZ(0);
            -moz-transform: translateZ(0);
            -ms-transform: translateZ(0);
            -o-transform: translateZ(0);
        }
        
        /* Optimize scroll performance */
        .scroll-container {
            -webkit-overflow-scrolling: touch;
            scroll-behavior: smooth;
        }
        
        /* Optimize animation performance */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.2s ease-out;
        }
        
        /* Optimize hover states */
        .tag-item:hover {
            transform: translateZ(0) scale(1.02);
        }
        
        /* Optimize focus states */
        .tag-checkbox:focus {
            outline: 2px solid #4CAF50;
            outline-offset: 2px;
        }
        
        /* Optimize selection states */
        .tag-item.selected {
            background-color: rgba(76, 175, 80, 0.2);
            border-color: #4CAF50;
            transform: translateZ(0) scale(1.05);
        }
        
        /* Optimize loading states */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        /* Optimize error states */
        .error {
            border-color: #ff6b6b;
            background-color: rgba(255, 107, 107, 0.1);
        }
        
        /* Optimize success states */
        .success {
            border-color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.1);
        }
        
        /* Optimize disabled states */
        .disabled {
            opacity: 0.5;
            pointer-events: none;
        }
        
        /* Optimize responsive design for PC */
        @media (min-width: 1200px) {
            .container {
                max-width: 1400px;
            }
        }
        
        /* Optimize for high DPI displays */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
            .tag-checkbox {
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
            }
        }
        
        /* Optimize for Windows high contrast mode */
        @media (prefers-contrast: high) {
            .tag-item {
                border-width: 2px;
            }
            
            .tag-checkbox:checked {
                background-color: Highlight;
            }
        }
        
        /* Optimize for reduced motion preferences */
        @media (prefers-reduced-motion: reduce) {
            .tag-item, .progress-fill {
                transition: none;
            }
            
            .fade-in {
                animation: none;
            }
        }
    `;
    
    // Add styles to document
    document.head.appendChild(style);
    
    // Add performance monitoring toggle
    const performanceToggle = document.createElement('div');
    performanceToggle.className = 'performance-metrics';
    performanceToggle.innerHTML = `
        <div>PC Performance Monitor</div>
        <div id="performance-stats">Loading...</div>
        <button onclick="togglePerformanceMonitor()" style="margin-top: 5px; padding: 2px 5px; font-size: 10px;">Toggle</button>
    `;
    document.body.appendChild(performanceToggle);
    
    // Performance monitoring functions
    window.togglePerformanceMonitor = function() {
        const monitor = document.querySelector('.performance-metrics');
        monitor.classList.toggle('show');
    };
    
    // Update performance stats
    function updatePerformanceStats() {
        const stats = document.getElementById('performance-stats');
        if (!stats) return;
        
        const metrics = {
            memory: performance.memory ? `${Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)}MB` : 'N/A',
            timing: `${Math.round(performance.now())}ms`,
            checkboxQueue: window.PCCheckboxOptimizer ? window.PCCheckboxOptimizer.getPerformanceMetrics().batchQueueSize : 0,
            dropdownCache: window.PerformanceState ? window.PerformanceState.dropdownCache.size : 0
        };
        
        stats.innerHTML = `
            Memory: ${metrics.memory}<br>
            Timing: ${metrics.timing}<br>
            Checkbox Queue: ${metrics.checkboxQueue}<br>
            Dropdown Cache: ${metrics.dropdownCache}
        `;
    }
    
    // Update stats every 2 seconds
    setInterval(updatePerformanceStats, 2000);
    
    console.log('✅ PC CSS Performance Optimizations applied successfully');
})();
