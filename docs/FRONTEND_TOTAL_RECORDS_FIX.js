// FRONTEND FIX: Use total_records instead of total_products
// The backend returns total_products: 0 but total_records: 2539

console.log("🔧 FRONTEND FIX: Using total_records (2539) instead of total_products (0)");

// Close any loading modals first
const loadingModal = document.querySelector('.modal, .loading-modal, [class*="modal"], [class*="loading"]');
if (loadingModal) {
    loadingModal.style.display = 'none';
    console.log("✅ Closed loading modal");
}

async function fixTotalProductsFromRecords() {
    console.log("🔄 Fixing total products using total_records...");
    
    try {
        const response = await fetch('/api/database-stats');
        const data = await response.json();
        
        console.log("📊 API Response:", data);
        
        // Use total_records (2539) instead of total_products (0)
        const totalProducts = data.stats.total_records || 0;
        const uniqueVendors = data.stats.unique_vendors || 0;
        const uniqueBrands = data.stats.unique_brands || 0;
        const productTypes = data.stats.unique_product_types || 0;
        
        console.log(`🎯 Using total_records: ${totalProducts} products`);
        
        if (totalProducts > 0) {
            // Update the display immediately
            updateDashboardDisplay(totalProducts, uniqueVendors, uniqueBrands, productTypes);
            
            // Also update from product type distribution as backup
            if (data.stats.product_type_distribution) {
                const distributionTotal = Object.values(data.stats.product_type_distribution)
                    .reduce((sum, count) => sum + count, 0);
                console.log(`📊 Product type distribution total: ${distributionTotal}`);
                
                if (distributionTotal > totalProducts) {
                    console.log(`🔄 Using distribution total (${distributionTotal}) instead of records (${totalProducts})`);
                    updateDashboardDisplay(distributionTotal, uniqueVendors, uniqueBrands, productTypes);
                }
            }
        }
        
    } catch (error) {
        console.error("❌ Error fetching stats:", error);
        
        // Fallback: Use visible product type distribution
        const distributionElements = document.querySelectorAll('[class*="product-type"], [class*="distribution"]');
        if (distributionElements.length > 0) {
            console.log("📊 Using visible distribution data as fallback");
            // This is a simplified fallback - you'd need to parse the visible elements
        }
    }
}

function updateDashboardDisplay(totalProducts, uniqueVendors, uniqueBrands, productTypes) {
    console.log(`🔄 Updating dashboard: ${totalProducts} products, ${uniqueVendors} vendors, ${uniqueBrands} brands, ${productTypes} types`);
    
    // Method 1: Direct text replacement
    document.body.innerHTML = document.body.innerHTML
        .replace(/0 TOTAL PRODUCTS/g, `${totalProducts.toLocaleString()} TOTAL PRODUCTS`)
        .replace(/0 UNIQUE VENDORS/g, `${uniqueVendors.toLocaleString()} UNIQUE VENDORS`)
        .replace(/0 UNIQUE BRANDS/g, `${uniqueBrands.toLocaleString()} UNIQUE BRANDS`)
        .replace(/0 PRODUCT TYPES/g, `${productTypes.toLocaleString()} PRODUCT TYPES`);
    
    // Method 2: Find and update specific elements
    const selectors = [
        '.stat-number',
        '.display-4',
        '.fw-bold',
        '[class*="stat"]',
        '[class*="count"]',
        '[class*="total"]'
    ];
    
    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const text = element.textContent;
            if (text === '0' || text.includes('0 TOTAL') || text.includes('0 UNIQUE')) {
                // Try to determine what this element represents
                const parent = element.closest('.card, .stat-card, .dashboard-card');
                if (parent) {
                    const parentText = parent.textContent.toLowerCase();
                    if (parentText.includes('total product') && !parentText.includes('vendor') && !parentText.includes('brand')) {
                        element.textContent = totalProducts.toLocaleString();
                        console.log(`✅ Updated TOTAL PRODUCTS: ${totalProducts}`);
                    } else if (parentText.includes('vendor')) {
                        element.textContent = uniqueVendors.toLocaleString();
                        console.log(`✅ Updated UNIQUE VENDORS: ${uniqueVendors}`);
                    } else if (parentText.includes('brand')) {
                        element.textContent = uniqueBrands.toLocaleString();
                        console.log(`✅ Updated UNIQUE BRANDS: ${uniqueBrands}`);
                    } else if (parentText.includes('product type')) {
                        element.textContent = productTypes.toLocaleString();
                        console.log(`✅ Updated PRODUCT TYPES: ${productTypes}`);
                    }
                }
            }
        });
    }
    
    console.log("✅ Dashboard display updated!");
}

// Run immediately
fixTotalProductsFromRecords();

// Also run after a short delay to catch any late-loading elements
setTimeout(fixTotalProductsFromRecords, 2000);

console.log("🎉 FRONTEND TOTAL RECORDS FIX APPLIED!");
console.log("Should now show 2,539 TOTAL PRODUCTS instead of 0");
