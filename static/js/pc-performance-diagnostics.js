/**
 * PC Performance Diagnostics Tool
 * 
 * Identifies performance bottlenecks on Windows/PC browsers
 * Run in browser console: window.runPCDiagnostics()
 */

class PCPerformanceDiagnostics {
    constructor() {
        this.metrics = {
            fps: [],
            longTasks: [],
            domQueries: 0,
            repaints: 0,
            scrollEvents: 0,
            memoryUsage: []
        };
        this.isMonitoring = false;
    }
    
    /**
     * Run complete diagnostics
     */
    async runDiagnostics() {
        console.log('🔍 Starting PC Performance Diagnostics...\n');
        
        // Platform detection
        this.checkPlatform();
        
        // Browser detection
        this.checkBrowser();
        
        // Check if optimizations are loaded
        this.checkOptimizations();
        
        // Measure current performance
        await this.measurePerformance();
        
        // Check for common issues
        this.checkCommonIssues();
        
        // Generate report
        this.generateReport();
    }
    
    checkPlatform() {
        const ua = navigator.userAgent;
        const isWindows = /Windows|Win32|Win64/.test(ua);
        const isLinux = /Linux/.test(ua);
        const isMac = /Mac/.test(ua);
        
        console.log('📱 Platform Detection:');
        console.log(`  OS: ${isWindows ? 'Windows ✅' : isLinux ? 'Linux' : isMac ? 'Mac' : 'Unknown'}`);
        console.log(`  User Agent: ${ua.substring(0, 80)}...`);
        console.log('');
    }
    
    checkBrowser() {
        const isChrome = /Chrome/.test(navigator.userAgent);
        const isEdge = /Edg/.test(navigator.userAgent);
        const isFirefox = /Firefox/.test(navigator.userAgent);
        
        console.log('🌐 Browser Detection:');
        console.log(`  Chrome: ${isChrome ? '✅' : '❌'}`);
        console.log(`  Edge: ${isEdge ? '✅' : '❌'}`);
        console.log(`  Firefox: ${isFirefox ? '✅' : '❌'}`);
        console.log('');
    }
    
    checkOptimizations() {
        console.log('⚙️ Checking Loaded Optimizations:');
        
        // Check for PC Performance Boost
        const hasPCBoost = typeof window.pcBoost !== 'undefined';
        console.log(`  PC Performance Boost: ${hasPCBoost ? '✅ Loaded' : '❌ Missing'}`);
        
        // Check for Windows Optimizer
        const hasWindowsOptimizer = typeof WindowsPerformanceOptimizer !== 'undefined';
        console.log(`  Windows Optimizer: ${hasWindowsOptimizer ? '✅ Loaded' : '❌ Missing'}`);
        
        // Check for CSS optimization
        const hasOptCSS = document.getElementById('windows-scrollbar-optimization') || 
                         document.querySelector('link[href*="windows-performance.css"]');
        console.log(`  Windows CSS: ${hasOptCSS ? '✅ Loaded' : '❌ Missing'}`);
        
        // Check scroll behavior
        const scrollBehavior = getComputedStyle(document.documentElement).scrollBehavior;
        console.log(`  Scroll Behavior: ${scrollBehavior === 'auto' ? '✅ Auto (fast)' : '⚠️ Smooth (slow)'}`);
        
        console.log('');
    }
    
    async measurePerformance() {
        console.log('📊 Measuring Performance (10 seconds)...');
        console.log('  Please scroll through the page during this time...\n');
        
        const startTime = performance.now();
        let frameCount = 0;
        let lastFrameTime = startTime;
        
        // FPS monitoring
        const measureFPS = () => {
            const now = performance.now();
            frameCount++;
            
            if (now - lastFrameTime >= 1000) {
                const fps = frameCount;
                this.metrics.fps.push(fps);
                frameCount = 0;
                lastFrameTime = now;
            }
            
            if (now - startTime < 10000) {
                requestAnimationFrame(measureFPS);
            }
        };
        
        measureFPS();
        
        // Monitor scroll events
        let scrollCount = 0;
        const scrollHandler = () => scrollCount++;
        window.addEventListener('scroll', scrollHandler, { passive: true });
        
        // Wait for 10 seconds
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        window.removeEventListener('scroll', scrollHandler);
        this.metrics.scrollEvents = scrollCount;
        
        // Calculate average FPS
        const avgFPS = this.metrics.fps.reduce((a, b) => a + b, 0) / this.metrics.fps.length;
        const minFPS = Math.min(...this.metrics.fps);
        
        console.log('✅ Performance Measurement Complete:');
        console.log(`  Average FPS: ${avgFPS.toFixed(1)} fps ${avgFPS >= 55 ? '✅' : avgFPS >= 30 ? '⚠️' : '❌'}`);
        console.log(`  Minimum FPS: ${minFPS} fps ${minFPS >= 30 ? '✅' : '❌'}`);
        console.log(`  Scroll Events: ${this.metrics.scrollEvents} ${this.metrics.scrollEvents < 100 ? '✅ Throttled' : '⚠️ Too many'}`);
        console.log('');
    }
    
    checkCommonIssues() {
        console.log('🔧 Checking Common Performance Issues:');
        
        // Check for heavy elements
        const heavyElements = {
            'Large tables': document.querySelectorAll('table tbody tr').length,
            'List items': document.querySelectorAll('li, .tag-item').length,
            'Modals': document.querySelectorAll('.modal').length,
            'Images': document.querySelectorAll('img').length,
            'Iframes': document.querySelectorAll('iframe').length
        };
        
        Object.entries(heavyElements).forEach(([name, count]) => {
            const warning = count > 1000 ? '⚠️ Very High' : count > 500 ? '⚠️ High' : count > 100 ? '⚡ Medium' : '✅ Low';
            console.log(`  ${name}: ${count} ${warning}`);
        });
        
        // Check for expensive CSS
        const expensiveCSSIssues = [];
        
        // Check for box-shadows during scroll
        document.querySelectorAll('*').forEach(el => {
            const style = getComputedStyle(el);
            if (style.boxShadow !== 'none' && style.boxShadow.includes('rgba')) {
                expensiveCSSIssues.push('Heavy box-shadows detected');
            }
        });
        
        if (expensiveCSSIssues.length > 0) {
            console.log(`  ⚠️ Found ${expensiveCSSIssues.length} expensive CSS effects`);
        } else {
            console.log('  ✅ No expensive CSS effects detected');
        }
        
        // Check for will-change abuse
        const willChangeElements = document.querySelectorAll('[style*="will-change"]');
        if (willChangeElements.length > 10) {
            console.log(`  ⚠️ Too many will-change properties: ${willChangeElements.length}`);
        } else {
            console.log(`  ✅ will-change usage: ${willChangeElements.length} elements`);
        }
        
        console.log('');
    }
    
    generateReport() {
        const avgFPS = this.metrics.fps.reduce((a, b) => a + b, 0) / this.metrics.fps.length;
        
        console.log('📋 DIAGNOSTIC REPORT SUMMARY');
        console.log('═══════════════════════════════════════');
        
        if (avgFPS >= 55) {
            console.log('✅ EXCELLENT: Performance is optimal');
            console.log('   No action needed.');
        } else if (avgFPS >= 40) {
            console.log('⚡ GOOD: Performance is acceptable');
            console.log('   Minor optimizations may help.');
        } else if (avgFPS >= 25) {
            console.log('⚠️ FAIR: Performance needs improvement');
            console.log('   Recommended actions:');
            console.log('   1. Clear browser cache (Ctrl+Shift+Delete)');
            console.log('   2. Close unnecessary browser tabs');
            console.log('   3. Disable browser extensions temporarily');
            console.log('   4. Update graphics drivers');
        } else {
            console.log('❌ POOR: Significant performance issues detected');
            console.log('   Immediate actions needed:');
            console.log('   1. Verify optimization scripts are loaded (see above)');
            console.log('   2. Try a different browser (Chrome/Edge recommended)');
            console.log('   3. Check if hardware acceleration is enabled');
            console.log('   4. Reduce number of products displayed');
        }
        
        console.log('═══════════════════════════════════════');
        console.log('\n💡 Tips:');
        console.log('  - For best performance, use Chrome or Edge on Windows');
        console.log('  - Keep your browser updated to the latest version');
        console.log('  - Enable hardware acceleration in browser settings');
        console.log('  - Close other programs to free up system resources');
        console.log('\n📊 To monitor FPS continuously: window.monitorFPS()');
    }
    
    /**
     * Monitor FPS continuously
     */
    monitorFPS() {
        if (this.isMonitoring) {
            console.log('⚠️ FPS monitoring already active');
            return;
        }
        
        this.isMonitoring = true;
        console.log('🎬 Starting continuous FPS monitoring...');
        console.log('   Watch the console for FPS updates');
        console.log('   Run window.stopFPSMonitoring() to stop\n');
        
        let frameCount = 0;
        let lastTime = performance.now();
        
        const countFPS = () => {
            if (!this.isMonitoring) return;
            
            frameCount++;
            const now = performance.now();
            
            if (now - lastTime >= 1000) {
                const fps = frameCount;
                const status = fps >= 55 ? '✅' : fps >= 30 ? '⚠️' : '❌';
                console.log(`${status} FPS: ${fps}`);
                
                if (fps < 30) {
                    console.warn('⚠️ Low FPS detected! Performance is degraded.');
                }
                
                frameCount = 0;
                lastTime = now;
            }
            
            requestAnimationFrame(countFPS);
        };
        
        requestAnimationFrame(countFPS);
    }
    
    stopFPSMonitoring() {
        this.isMonitoring = false;
        console.log('⏸️ FPS monitoring stopped');
    }
}

// Global instance
window.pcDiagnostics = new PCPerformanceDiagnostics();

// Convenience functions
window.runPCDiagnostics = () => window.pcDiagnostics.runDiagnostics();
window.monitorFPS = () => window.pcDiagnostics.monitorFPS();
window.stopFPSMonitoring = () => window.pcDiagnostics.stopFPSMonitoring();

// Auto-run on PC if query parameter is present
if (window.location.search.includes('diagnose=true')) {
    console.log('🔍 Auto-running diagnostics (diagnose=true detected)...\n');
    setTimeout(() => window.runPCDiagnostics(), 2000);
}

console.log('✅ PC Performance Diagnostics loaded');
console.log('   Run: window.runPCDiagnostics() to start');
console.log('   Or add ?diagnose=true to URL to auto-run');

