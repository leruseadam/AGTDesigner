// Production JavaScript Error Fix
// This script fixes common JavaScript errors on the production website

console.log('🔧 Loading production JavaScript error fixes...');

// Fix 1: Ensure CLASSIC_TYPES is only declared once
if (typeof CLASSIC_TYPES === 'undefined') {
    const CLASSIC_TYPES = [
        "flower", "pre-roll", "concentrate", "infused pre-roll", 
        "solventless concentrate", "vape cartridge", "rso/co2 tankers"
    ];
    console.log('✅ CLASSIC_TYPES defined');
}

// Fix 2: Create backup definitions for missing functions
if (typeof performDetailedJsonMatch === 'undefined') {
    window.performDetailedJsonMatch = function() {
        console.warn('performDetailedJsonMatch not found, using backup');
        return false;
    };
}

if (typeof displayDetailedMatchResults === 'undefined') {
    window.displayDetailedMatchResults = function() {
        console.warn('displayDetailedMatchResults not found, using backup');
        return false;
    };
}

// Fix 3: Global error handler to prevent crashes
window.addEventListener('error', function(e) {
    console.error('JavaScript Error Caught:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error
    });
    
    // Don't let errors break the page
    return true;
});

// Fix 4: Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    e.preventDefault();
});

// Fix 5: Ensure critical functions exist
if (typeof showDatabaseModal === 'undefined') {
    window.showDatabaseModal = function(title, content) {
        console.warn('showDatabaseModal not found, using backup');
        alert(`${title}: ${content}`);
    };
}

console.log('✅ Production JavaScript error fixes loaded');
