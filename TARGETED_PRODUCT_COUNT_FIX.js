// TARGETED PRODUCT COUNT FIX - Fix the main product count display
// Add this to browser console to fix the 0 TOTAL PRODUCTS issue

console.log("🔧 TARGETED PRODUCT COUNT FIX: Fixing main product count display");

// The issue: Brands (32) and Product Types (12) are showing, but TOTAL PRODUCTS shows 0
// This means the data is there but the main count isn't being calculated correctly

async function fixProductCountDisplay() {
    console.log("🔄 Fixing product count display...");
    
    try {
        // Get fresh data from all endpoints
        const [statsResponse, tagsResponse, vendorResponse] = await Promise.all([
            fetch('/api/database-stats'),
            fetch('/api/available-tags'),
            fetch('/api/database-vendor-stats')
        ]);
        
        const stats = await statsResponse.json();
        const tags = await tagsResponse.json();
        const vendors = await vendorResponse.json();
        
        console.log("📊 Raw API data:", {
            stats: stats.stats,
            tagsCount: tags.tags?.length || 0,
            totalCount: tags.total_count || 0,
            vendorsCount: vendors.vendors?.length || 0
        });
        
        // Calculate the correct product count
        let totalProducts = 0;
        
        // Method 1: Use stats.total_products
        if (stats.stats && stats.stats.total_products) {
            totalProducts = stats.stats.total_products;
            console.log(`✅ Using stats.total_products: ${totalProducts}`);
        }
        // Method 2: Use stats.total_records
        else if (stats.stats && stats.stats.total_records) {
            totalProducts = stats.stats.total_records;
            console.log(`✅ Using stats.total_records: ${totalProducts}`);
        }
        // Method 3: Use tags.total_count
        else if (tags.total_count) {
            totalProducts = tags.total_count;
            console.log(`✅ Using tags.total_count: ${totalProducts}`);
        }
        // Method 4: Use tags array length
        else if (tags.tags && tags.tags.length > 0) {
            totalProducts = tags.tags.length;
            console.log(`✅ Using tags array length: ${totalProducts}`);
        }
        // Method 5: Calculate from product type distribution
        else if (stats.stats && stats.stats.product_type_distribution) {
            const distribution = stats.stats.product_type_distribution;
            totalProducts = Object.values(distribution).reduce((sum, count) => sum + (count || 0), 0);
            console.log(`✅ Calculated from product_type_distribution: ${totalProducts}`);
        }
        
        console.log(`🎯 Final calculated total products: ${totalProducts}`);
        
        if (totalProducts > 0) {
            // Update the DOM elements
            updateProductCountInDOM(totalProducts);
        } else {
            console.warn("⚠️ Could not determine product count from any source");
        }
        
        // Also update vendor count
        const vendorCount = vendors.vendors?.length || 0;
        if (vendorCount > 0) {
            updateVendorCountInDOM(vendorCount);
        }
        
    } catch (error) {
        console.error("❌ Error fixing product count:", error);
    }
}

function updateProductCountInDOM(count) {
    console.log(`🔄 Updating DOM with product count: ${count}`);
    
    // Try multiple selectors to find the element
    const selectors = [
        '[data-stat="total_products"]',
        '.total-products',
        '#total-products',
        '.dashboard-stat:first-child .stat-number',
        '.stat-card:first-child .stat-number',
        '.product-count',
        '.total-count'
    ];
    
    let element = null;
    for (const selector of selectors) {
        element = document.querySelector(selector);
        if (element) {
            console.log(`✅ Found element with selector: ${selector}`);
            break;
        }
    }
    
    if (element) {
        element.textContent = count.toLocaleString();
        console.log(`✅ Updated element text to: ${count.toLocaleString()}`);
    } else {
        console.warn("⚠️ Could not find product count element, trying text replacement...");
        
        // Fallback: Replace text content directly
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === '0 TOTAL PRODUCTS') {
                node.textContent = `${count.toLocaleString()} TOTAL PRODUCTS`;
                console.log(`✅ Replaced text node: ${count.toLocaleString()} TOTAL PRODUCTS`);
                break;
            }
        }
    }
}

function updateVendorCountInDOM(count) {
    console.log(`🔄 Updating DOM with vendor count: ${count}`);
    
    // Try multiple selectors for vendor count
    const selectors = [
        '[data-stat="total_vendors"]',
        '.total-vendors',
        '#total-vendors',
        '.dashboard-stat:nth-child(2) .stat-number',
        '.stat-card:nth-child(2) .stat-number'
    ];
    
    let element = null;
    for (const selector of selectors) {
        element = document.querySelector(selector);
        if (element) {
            console.log(`✅ Found vendor element with selector: ${selector}`);
            break;
        }
    }
    
    if (element) {
        element.textContent = count.toLocaleString();
        console.log(`✅ Updated vendor element text to: ${count.toLocaleString()}`);
    } else {
        console.warn("⚠️ Could not find vendor count element, trying text replacement...");
        
        // Fallback: Replace text content directly
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === '0 UNIQUE VENDORS') {
                node.textContent = `${count.toLocaleString()} UNIQUE VENDORS`;
                console.log(`✅ Replaced vendor text node: ${count.toLocaleString()} UNIQUE VENDORS`);
                break;
            }
        }
    }
}

// Override the dashboard update function if it exists
if (typeof window.updateDashboardStats === 'function') {
    const originalUpdateDashboardStats = window.updateDashboardStats;
    
    window.updateDashboardStats = function(stats) {
        console.log("🔧 Enhanced updateDashboardStats called with:", stats);
        
        // Call original function
        const result = originalUpdateDashboardStats.call(this, stats);
        
        // Force update product count
        setTimeout(() => {
            fixProductCountDisplay();
        }, 1000);
        
        return result;
    };
    
    console.log("✅ Enhanced updateDashboardStats installed");
}

// Immediate fix
console.log("🚀 Applying immediate product count fix...");
fixProductCountDisplay();

// Set up periodic refresh with CPU optimization
setInterval(() => {
    // Check if CPU usage is high before running
    if (window.CPUOptimizer && window.CPUOptimizer.isHighCPU()) {
        console.log("🔄 Skipping product count refresh due to high CPU usage");
        return;
    }
    
    console.log("🔄 Periodic product count refresh...");
    fixProductCountDisplay();
}, 30000); // Increased from 15 seconds to 30 seconds

console.log("🎉 TARGETED PRODUCT COUNT FIX APPLIED!");
console.log("Product count should now display correctly");
console.log("Will refresh every 15 seconds to maintain accuracy");
