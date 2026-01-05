// Debug script for advanced features
console.log('Debug script loaded');

// Test if functions exist
function testAdvancedFeatures() {
    console.log('Testing advanced features...');
    
    const functions = [
        'openDatabaseAnalytics',
        'openProductSimilarity', 
        'openDatabaseHealth',
        'openAdvancedSearch',
        'openDatabaseBackup',
        'openTrendAnalysis',
        'openVendorAnalytics',
        'openDatabaseOptimization',
        'showDatabaseModal'
    ];
    
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ ${funcName} exists`);
        } else {
            console.log(`❌ ${funcName} is not defined`);
        }
    });
    
    // Test if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        console.log('✅ Bootstrap is loaded');
        // Bootstrap 5.x doesn't expose VERSION consistently, so just confirm it's loaded
        const version = bootstrap.Tooltip?.VERSION || bootstrap.Modal?.VERSION || '5.1.3 (estimated)';
        console.log('Bootstrap version:', version);
    } else {
        console.log('❌ Bootstrap is not loaded');
    }
    
    // Test API endpoints
    const endpoints = [
        '/api/database-stats',
        '/api/database-vendor-stats',
        '/api/database-analytics'
        // DISABLED: '/api/available-tags' - this was interfering with tag selection
    ];

    endpoints.forEach(endpoint => {
        fetch(endpoint)
            .then(response => {
                if (response.ok) {
                    console.log(`✅ ${endpoint} - OK`);
                } else {
                    console.log(`❌ ${endpoint} - ${response.status}`);
                }
            })
            .catch(error => {
                console.log(`❌ ${endpoint} - Error: ${error.message}`);
            });
    });
}

// CRITICAL FIX: Wait for all inline scripts to load before running tests
// The advanced feature functions are defined in inline scripts that load AFTER this deferred script
// So we need to wait for window.load event, not just DOMContentLoaded
if (document.readyState === 'complete') {
    // Page already loaded, wait a bit for inline scripts to execute
    setTimeout(testAdvancedFeatures, 100);
} else {
    // Wait for full page load including all inline scripts
    window.addEventListener('load', () => {
        // Small delay to ensure inline scripts have executed
        setTimeout(testAdvancedFeatures, 100);
    });
}

// Add click handlers to test buttons
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('[onclick*="openDatabase"]');
    buttons.forEach(button => {
        console.log('Found button:', button.textContent.trim());
        button.addEventListener('click', function(e) {
            console.log('Button clicked:', this.textContent.trim());
        });
    });
}); 