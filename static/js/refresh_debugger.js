// Refresh Debugger - Logs all refresh attempts to help identify the cause
(function() {
    console.log('🔍 Refresh Debugger Active - Monitoring all refresh attempts');
    
    // Track all reload attempts
    const reloadAttempts = [];
    
    // Override window.location.reload
    const originalReload = window.location.reload;
    window.location.reload = function(forceReload) {
        const stack = new Error().stack;
        const timestamp = new Date().toISOString();
        
        console.error('🚨 REFRESH ATTEMPT DETECTED!');
        console.error('Timestamp:', timestamp);
        console.error('Force Reload:', forceReload);
        console.error('Call Stack:', stack);
        
        reloadAttempts.push({
            timestamp,
            forceReload,
            stack
        });
        
        // Store in sessionStorage for persistence
        try {
            sessionStorage.setItem('refreshAttempts', JSON.stringify(reloadAttempts));
        } catch (e) {
            console.error('Failed to store refresh attempts:', e);
        }
        
        // Call original reload
        return originalReload.call(this, forceReload);
    };
    
    // Override window.location.href setter
    const originalHref = Object.getOwnPropertyDescriptor(window.location, 'href');
    Object.defineProperty(window.location, 'href', {
        get: originalHref.get,
        set: function(value) {
            const stack = new Error().stack;
            const timestamp = new Date().toISOString();
            
            console.error('🚨 LOCATION.HREF CHANGE DETECTED!');
            console.error('Timestamp:', timestamp);
            console.error('New URL:', value);
            console.error('Call Stack:', stack);
            
            reloadAttempts.push({
                timestamp,
                type: 'href',
                url: value,
                stack
            });
            
            try {
                sessionStorage.setItem('refreshAttempts', JSON.stringify(reloadAttempts));
            } catch (e) {
                console.error('Failed to store refresh attempts:', e);
            }
            
            return originalHref.set.call(this, value);
        }
    });
    
    // Log previous refresh attempts if any
    try {
        const previousAttempts = sessionStorage.getItem('refreshAttempts');
        if (previousAttempts) {
            const attempts = JSON.parse(previousAttempts);
            if (attempts.length > 0) {
                console.warn('📋 Previous refresh attempts found:', attempts.length);
                console.table(attempts.map(a => ({
                    timestamp: a.timestamp,
                    type: a.type || 'reload',
                    forceReload: a.forceReload
                })));
                
                // Show the last attempt's stack trace
                const lastAttempt = attempts[attempts.length - 1];
                console.warn('Last refresh stack trace:', lastAttempt.stack);
            }
        }
    } catch (e) {
        console.error('Failed to retrieve previous refresh attempts:', e);
    }
    
    // Expose function to check refresh attempts
    window.getRefreshAttempts = function() {
        return reloadAttempts;
    };
    
    window.clearRefreshLog = function() {
        reloadAttempts.length = 0;
        sessionStorage.removeItem('refreshAttempts');
        console.log('✅ Refresh log cleared');
    };
    
    console.log('✅ Refresh Debugger Ready');
    console.log('💡 Use window.getRefreshAttempts() to see all refresh attempts');
    console.log('💡 Use window.clearRefreshLog() to clear the log');
})();

