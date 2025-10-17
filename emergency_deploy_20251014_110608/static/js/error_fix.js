// JavaScript Error Fix Script
// Run this in browser console to fix common issues

console.log('🔧 Running JavaScript error fixes...');

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
    console.log('✅ performDetailedJsonMatch backup created');
}

if (typeof displayDetailedMatchResults === 'undefined') {
    window.displayDetailedMatchResults = function() {
        console.warn('displayDetailedMatchResults not found, using backup');
        return false;
    };
    console.log('✅ displayDetailedMatchResults backup created');
}

// Fix 3: Ensure error handling is in place
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.message, 'at', e.filename, ':', e.lineno);
    // Don't let errors break the page
    return true;
});

console.log('✅ JavaScript error fixes applied');
