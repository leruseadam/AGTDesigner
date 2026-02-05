// FRONTEND DISPLAY FIX - Fix frontend showing 0 products when database has data
// Add this to browser console to fix the display issue

console.log("🔧 FRONTEND DISPLAY FIX: Fixing 0 products display issue");

// The API shows 2539 products but frontend shows 0 - this is a display bug

// Fix 1: Force refresh all data
async function forceRefreshAllData() {
    console.log("🔄 Forcing refresh of all data...");
    
    try {
        // Clear any cached data
        await fetch('/api/clear-cache', { method: 'POST' }).catch(() => {});
        
        // Fetch fresh data
        const [statsResponse, tagsResponse, vendorResponse] = await Promise.all([
            fetch('/api/database-stats'),
            fetch('/api/available-tags'),
            fetch('/api/database-vendor-stats')
        ]);
        
        const stats = await statsResponse.json();
        const tags = await tagsResponse.json();
        const vendors = await vendorResponse.json();
        
        console.log("📊 Fresh data fetched:", {
            stats: stats.stats,
            tagsCount: tags.tags?.length || 0,
            vendorsCount: vendors.vendors?.length || 0
        });
        
        // Force update the dashboard display
        updateDashboardDisplay(stats.stats, tags.tags, vendors);
        
        // Force update TagManager state
        if (typeof TagManager !== 'undefined') {
            console.log("🔄 Updating TagManager state...");
            
            // Clear current state
            TagManager.state.tags = [];
            TagManager.state.originalTags = [];
            TagManager.state.selectedTags.clear();
            
            // Update with fresh data
            if (tags.tags && tags.tags.length > 0) {
                TagManager.state.tags = tags.tags;
                TagManager.state.originalTags = tags.tags;
                
                // Update UI
                TagManager._updateAvailableTags({
                    originalTagsLength: tags.tags.length,
                    filteredTagsLength: tags.tags.length,
                    tags: tags.tags
                });
                
                console.log(`✅ Updated TagManager with ${tags.tags.length} tags`);
            }
        }
        
    } catch (error) {
        console.error("❌ Error refreshing data:", error);
    }
}

// Fix 2: Update dashboard display
function updateDashboardDisplay(stats, tags, vendors) {
    console.log("📊 Updating dashboard display...");
    
    // Update product counts
    const totalProducts = stats.total_products || stats.total_records || 0;
    const totalVendors = vendors.vendors?.length || 0;
    const totalBrands = vendors.brands?.length || 0;
    const totalProductTypes = stats.product_type_distribution ? Object.keys(stats.product_type_distribution).length : 0;
    
    console.log("📊 Dashboard numbers:", {
        totalProducts,
        totalVendors,
        totalBrands,
        totalProductTypes
    });
    
    // Update DOM elements
    const elements = {
        totalProducts: document.querySelector('[data-stat="total_products"]') || 
                      document.querySelector('.total-products') ||
                      document.querySelector('#total-products'),
        totalVendors: document.querySelector('[data-stat="total_vendors"]') ||
                     document.querySelector('.total-vendors') ||
                     document.querySelector('#total-vendors'),
        totalBrands: document.querySelector('[data-stat="total_brands"]') ||
                    document.querySelector('.total-brands') ||
                    document.querySelector('#total-brands'),
        totalProductTypes: document.querySelector('[data-stat="total_product_types"]') ||
                          document.querySelector('.total-product-types') ||
                          document.querySelector('#total-product-types')
    };
    
    // Update each element
    Object.entries(elements).forEach(([key, element]) => {
        if (element) {
            const value = { totalProducts, totalVendors, totalBrands, totalProductTypes }[key];
            element.textContent = value.toLocaleString();
            console.log(`✅ Updated ${key}: ${value}`);
        } else {
            console.warn(`⚠️ Element not found for ${key}`);
        }
    });
    
    // Also try to update any text content that contains the numbers
    const textNodes = document.querySelectorAll('*');
    textNodes.forEach(node => {
        if (node.textContent === '0 TOTAL PRODUCTS') {
            node.textContent = `${totalProducts.toLocaleString()} TOTAL PRODUCTS`;
            console.log(`✅ Updated text node: ${totalProducts} TOTAL PRODUCTS`);
        }
        if (node.textContent === '0 UNIQUE VENDORS') {
            node.textContent = `${totalVendors} UNIQUE VENDORS`;
            console.log(`✅ Updated text node: ${totalVendors} UNIQUE VENDORS`);
        }
        if (node.textContent === '0 UNIQUE BRANDS') {
            node.textContent = `${totalBrands} UNIQUE BRANDS`;
            console.log(`✅ Updated text node: ${totalBrands} UNIQUE BRANDS`);
        }
        if (node.textContent === '0 PRODUCT TYPES') {
            node.textContent = `${totalProductTypes} PRODUCT TYPES`;
            console.log(`✅ Updated text node: ${totalProductTypes} PRODUCT TYPES`);
        }
    });
}

// Fix 3: Override the data loading functions
if (typeof TagManager !== 'undefined') {
    // Store original functions
    TagManager.originalCheckForExistingData = TagManager.checkForExistingData;
    TagManager.originalFetchAndUpdateAvailableTags = TagManager.fetchAndUpdateAvailableTags;
    
    // Replace with enhanced versions
    TagManager.checkForExistingData = async function() {
        console.log("🔧 Enhanced checkForExistingData called");
        
        try {
            // Call original function
            const result = await TagManager.originalCheckForExistingData.call(this);
            
            // Force refresh dashboard after loading
            setTimeout(() => {
                forceRefreshAllData();
            }, 2000);
            
            return result;
        } catch (error) {
            console.error("❌ Error in checkForExistingData:", error);
            
            // Fallback: force refresh anyway
            setTimeout(() => {
                forceRefreshAllData();
            }, 2000);
            
            return { success: false, error: error.message };
        }
    };
    
    TagManager.fetchAndUpdateAvailableTags = async function() {
        console.log("🔧 Enhanced fetchAndUpdateAvailableTags called");
        
        try {
            const result = await TagManager.originalFetchAndUpdateAvailableTags.call(this);
            
            // Force dashboard update
            setTimeout(() => {
                forceRefreshAllData();
            }, 1000);
            
            return result;
        } catch (error) {
            console.error("❌ Error in fetchAndUpdateAvailableTags:", error);
            
            // Fallback: force refresh anyway
            setTimeout(() => {
                forceRefreshAllData();
            }, 1000);
            
            return { success: false, error: error.message };
        }
    };
    
    console.log("✅ Enhanced TagManager functions installed");
}

// Fix 4: Immediate refresh
console.log("🚀 Starting immediate data refresh...");
forceRefreshAllData();

// Fix 5: Set up periodic refresh
setInterval(() => {
    console.log("🔄 Periodic data refresh...");
    forceRefreshAllData();
}, 30000); // Every 30 seconds

console.log("🎉 FRONTEND DISPLAY FIX APPLIED!");
console.log("Dashboard should now show correct product counts");
console.log("Data will refresh automatically every 30 seconds");
