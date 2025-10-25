// Fix for double refresh issue
// This script prevents multiple refresh calls from happening simultaneously

(function() {
    let refreshInProgress = false;
    let refreshTimeout = null;
    
    // Store the original reload function
    const originalReload = window.location.reload;
    
    // Override window.location.reload to prevent double refreshes
    window.location.reload = function(forceReload) {
        if (refreshInProgress) {
            console.log('🚫 Double refresh prevented - refresh already in progress');
            return;
        }
        
        refreshInProgress = true;
        console.log('✅ Refresh initiated');
        
        // Clear any existing timeout
        if (refreshTimeout) {
            clearTimeout(refreshTimeout);
        }
        
        // Call the original reload function
        originalReload.call(this, forceReload);
        
        // Reset the flag after a delay (in case reload doesn't actually happen)
        refreshTimeout = setTimeout(() => {
            refreshInProgress = false;
            console.log('🔄 Refresh flag reset');
        }, 5000);
    };
    
    // Also override any direct calls to refreshPage
    if (window.refreshPage) {
        const originalRefreshPage = window.refreshPage;
        window.refreshPage = function() {
            if (refreshInProgress) {
                console.log('🚫 Double refreshPage prevented');
                return;
            }
            console.log('✅ refreshPage called');
            originalRefreshPage.call(this);
        };
    }
    
    console.log('🛡️ Double refresh protection enabled');
})();
