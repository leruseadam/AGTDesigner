// Quick diagnostic script to check cache status
// Run this in browser console to see what's happening with the cache

(function() {
    console.log('=== CACHE DIAGNOSTIC ===');
    
    // Check sessionStorage availability
    console.log('1. SessionStorage available:', !!window.sessionStorage);
    
    if (window.sessionStorage) {
        // Check store and file values
        const store1 = sessionStorage.getItem('selected_store');
        const store2 = sessionStorage.getItem('store');
        const file1 = sessionStorage.getItem('uploaded_filename');
        const file2 = sessionStorage.getItem('file_path');
        const currentStore = window.currentStore;
        
        console.log('2. Store values:');
        console.log('   - selected_store:', store1);
        console.log('   - store:', store2);
        console.log('   - window.currentStore:', currentStore);
        
        console.log('3. File values:');
        console.log('   - uploaded_filename:', file1);
        console.log('   - file_path:', file2);
        
        const finalStore = store1 || store2 || currentStore || 'default';
        const finalFile = file1 || file2 || 'nofile';
        const cacheKey = `agt_available_tags_${finalStore}_${finalFile}`;
        
        console.log('4. Generated cache key:', cacheKey);
        
        // Check if cache exists
        const cached = sessionStorage.getItem(cacheKey);
        if (cached) {
            try {
                const parsed = JSON.parse(cached);
                const age = Date.now() - parsed.timestamp;
                const ageMinutes = (age / 60000).toFixed(1);
                console.log('5. ✅ Cache EXISTS:');
                console.log('   - Tags count:', parsed.tags ? parsed.tags.length : 0);
                console.log('   - Age:', ageMinutes, 'minutes');
                console.log('   - Expired:', age > (10 * 60 * 1000));
            } catch (e) {
                console.log('5. ❌ Cache exists but is invalid:', e);
            }
        } else {
            console.log('5. ❌ No cache found for key:', cacheKey);
            
            // List all cache keys that exist
            console.log('6. All cache keys in sessionStorage:');
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                if (key && key.startsWith('agt_available_tags_')) {
                    const value = sessionStorage.getItem(key);
                    try {
                        const parsed = JSON.parse(value);
                        console.log(`   - ${key}: ${parsed.tags ? parsed.tags.length : 0} tags`);
                    } catch (e) {
                        console.log(`   - ${key}: invalid`);
                    }
                }
            }
        }
    }
    
    console.log('=== END DIAGNOSTIC ===');
})();
