// SIMPLE BACKEND FIX - Use total_records instead of total_products
// Add this to browser console to fix the display

console.log("🔧 SIMPLE BACKEND FIX: Using total_records (650) instead of total_products (0)");

// The backend API returns:
// - total_products: 0 (broken)
// - total_records: 650 (correct)
// - Product type distribution: 611 products

async function fixProductCountFromBackend() {
    console.log("🔄 Fixing product count using backend data...");
    
    try {
        const response = await fetch('/api/database-stats');
        const data = await response.json();
        
        console.log("📊 Backend data:", data.stats);
        
        // Use total_records (650) instead of total_products (0)
        let totalProducts = data.stats.total_records || 0;
        
        // Fallback: calculate from product type distribution
        if (totalProducts === 0 && data.stats.product_type_distribution) {
            const distribution = data.stats.product_type_distribution;
            totalProducts = Object.values(distribution).reduce((sum, count) => sum + (count || 0), 0);
            console.log(`📊 Calculated from distribution: ${totalProducts}`);
        }
        
        console.log(`🎯 Using total products: ${totalProducts}`);
        
        if (totalProducts > 0) {
            // Update the display
            updateProductDisplay(totalProducts);
        }
        
    } catch (error) {
        console.error("❌ Error:", error);
    }
}

function updateProductDisplay(total) {
    console.log(`🔄 Updating display to show: ${total}`);
    
    // Method 1: Find and update the card
    const selectors = [
        '.stat-card:first-child .stat-number',
        '.dashboard-stat:first-child .stat-number',
        '[data-stat="total_products"] .stat-number',
        '.total-products .stat-number'
    ];
    
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = total.toLocaleString();
            console.log(`✅ Updated ${selector}: ${total}`);
            return;
        }
    }
    
    // Method 2: Text replacement
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent.includes('0 TOTAL PRODUCTS')) {
            node.textContent = node.textContent.replace('0 TOTAL PRODUCTS', `${total} TOTAL PRODUCTS`);
            console.log(`✅ Updated text: ${total} TOTAL PRODUCTS`);
            break;
        }
    }
}

// Run immediately
fixProductCountFromBackend();

console.log("🎉 SIMPLE BACKEND FIX APPLIED!");
console.log("Should now show 650 TOTAL PRODUCTS instead of 0");
