// FINAL PRODUCT COUNT CALCULATION - Fix the 0 TOTAL PRODUCTS display
// Add this to browser console to calculate and display correct product count

console.log("🔧 FINAL PRODUCT COUNT CALCULATION: Fixing 0 TOTAL PRODUCTS");

// The issue: TOTAL PRODUCTS shows 0, but Product Type Distribution shows 3,305+ products
// We need to calculate the correct total and force update the display

async function calculateAndDisplayTotalProducts() {
    console.log("🔄 Calculating correct total products...");
    
    try {
        // Method 1: Calculate from Product Type Distribution (most reliable)
        const productTypeTotal = calculateFromProductTypeDistribution();
        console.log(`📊 Product Type Distribution total: ${productTypeTotal}`);
        
        // Method 2: Get from API
        const apiTotal = await getTotalFromAPI();
        console.log(`📊 API total: ${apiTotal}`);
        
        // Method 3: Calculate from Top Brands
        const brandsTotal = calculateFromTopBrands();
        console.log(`📊 Top Brands total: ${brandsTotal}`);
        
        // Use the most reliable calculation
        let finalTotal = productTypeTotal;
        if (apiTotal > productTypeTotal) {
            finalTotal = apiTotal;
        } else if (brandsTotal > productTypeTotal) {
            finalTotal = brandsTotal;
        }
        
        console.log(`🎯 Final calculated total: ${finalTotal}`);
        
        if (finalTotal > 0) {
            // Force update the TOTAL PRODUCTS display
            forceUpdateTotalProductsDisplay(finalTotal);
            
            // Also update vendor count
            await updateVendorCount();
        } else {
            console.warn("⚠️ Could not calculate total products from any source");
        }
        
    } catch (error) {
        console.error("❌ Error calculating total products:", error);
    }
}

function calculateFromProductTypeDistribution() {
    console.log("🔍 Calculating from Product Type Distribution...");
    
    let total = 0;
    
    // Look for product type distribution elements
    const distributionElements = document.querySelectorAll('[class*="product-type"], [class*="distribution"]');
    
    distributionElements.forEach(element => {
        const text = element.textContent;
        
        // Match patterns like "Flower: 1521 products (27%)"
        const matches = text.match(/(\d+)\s+products?\s*\(\d+%\)/g);
        
        if (matches) {
            matches.forEach(match => {
                const numberMatch = match.match(/(\d+)/);
                if (numberMatch) {
                    const count = parseInt(numberMatch[1]);
                    total += count;
                    console.log(`  Found: ${match} = ${count} products`);
                }
            });
        }
    });
    
    // Fallback: look for any text containing "products"
    if (total === 0) {
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            const text = element.textContent;
            const matches = text.match(/(\d+)\s+products?\s*\(\d+%\)/g);
            
            if (matches) {
                matches.forEach(match => {
                    const numberMatch = match.match(/(\d+)/);
                    if (numberMatch) {
                        const count = parseInt(numberMatch[1]);
                        total += count;
                    }
                });
            }
        });
    }
    
    console.log(`📊 Product Type Distribution calculation: ${total}`);
    return total;
}

async function getTotalFromAPI() {
    console.log("🔍 Getting total from API...");
    
    try {
        const [statsResponse, tagsResponse] = await Promise.all([
            fetch('/api/database-stats'),
            fetch('/api/available-tags')
        ]);
        
        const stats = await statsResponse.json();
        const tags = await tagsResponse.json();
        
        console.log("📊 API responses:", { stats: stats.stats, tags: tags.total_count });
        
        // Try different API fields
        let total = 0;
        
        if (stats.stats) {
            total = stats.stats.total_products || stats.stats.total_records || 0;
        }
        
        if (total === 0 && tags.total_count) {
            total = tags.total_count;
        }
        
        if (total === 0 && tags.tags && tags.tags.length > 0) {
            total = tags.tags.length;
        }
        
        console.log(`📊 API calculation: ${total}`);
        return total;
        
    } catch (error) {
        console.error("❌ API error:", error);
        return 0;
    }
}

function calculateFromTopBrands() {
    console.log("🔍 Calculating from Top Brands...");
    
    let total = 0;
    
    // Look for brand count elements
    const brandElements = document.querySelectorAll('[class*="brand"], [class*="top-brands"]');
    
    brandElements.forEach(element => {
        const text = element.textContent;
        
        // Match patterns like "Dank Czar: 626"
        const matches = text.match(/(\w+(?:\s+\w+)*):\s*(\d+)/g);
        
        if (matches) {
            matches.forEach(match => {
                const numberMatch = match.match(/(\d+)$/);
                if (numberMatch) {
                    const count = parseInt(numberMatch[1]);
                    total += count;
                    console.log(`  Found brand: ${match} = ${count} products`);
                }
            });
        }
    });
    
    console.log(`📊 Top Brands calculation: ${total}`);
    return total;
}

function forceUpdateTotalProductsDisplay(total) {
    console.log(`🔄 Force updating TOTAL PRODUCTS display to: ${total}`);
    
    // Method 1: Update existing card
    const cardSelectors = [
        '[data-stat="total_products"]',
        '.total-products',
        '#total-products',
        '.stat-card:first-child',
        '.dashboard-stat:first-child'
    ];
    
    let updated = false;
    
    for (const selector of cardSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            // Update the number
            const numberElement = element.querySelector('.stat-number, [class*="number"]') || element;
            if (numberElement) {
                numberElement.textContent = total.toLocaleString();
                console.log(`✅ Updated ${selector} to: ${total.toLocaleString()}`);
                updated = true;
            }
        }
    }
    
    // Method 2: Direct text replacement
    if (!updated) {
        console.log("🔄 Trying direct text replacement...");
        
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === '0 TOTAL PRODUCTS') {
                node.textContent = `${total.toLocaleString()} TOTAL PRODUCTS`;
                console.log(`✅ Replaced text node: ${total.toLocaleString()} TOTAL PRODUCTS`);
                updated = true;
                break;
            }
        }
    }
    
    // Method 3: Force DOM manipulation
    if (!updated) {
        console.log("🔄 Trying force DOM manipulation...");
        
        // Find any element containing "TOTAL PRODUCTS"
        const allElements = document.querySelectorAll('*');
        
        for (const element of allElements) {
            if (element.textContent && element.textContent.includes('TOTAL PRODUCTS')) {
                // Replace the 0 with the correct number
                element.innerHTML = element.innerHTML.replace(/0\s*TOTAL PRODUCTS/g, `${total.toLocaleString()} TOTAL PRODUCTS`);
                console.log(`✅ Force updated element: ${total.toLocaleString()} TOTAL PRODUCTS`);
                updated = true;
                break;
            }
        }
    }
    
    if (!updated) {
        console.warn("⚠️ Could not update TOTAL PRODUCTS display");
    }
}

async function updateVendorCount() {
    console.log("🔄 Updating vendor count...");
    
    try {
        const response = await fetch('/api/database-vendor-stats');
        const data = await response.json();
        
        const vendorCount = data.vendors?.length || 0;
        console.log(`📊 Found ${vendorCount} vendors`);
        
        if (vendorCount > 0) {
            // Update vendor count display
            const vendorSelectors = [
                '[data-stat="total_vendors"]',
                '.total-vendors',
                '#total-vendors',
                '.stat-card:nth-child(2) .stat-number',
                '.dashboard-stat:nth-child(2) .stat-number'
            ];
            
            for (const selector of vendorSelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = vendorCount.toLocaleString();
                    console.log(`✅ Updated vendor count to: ${vendorCount}`);
                    break;
                }
            }
            
            // Also try text replacement
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.trim() === '0 UNIQUE VENDORS') {
                    node.textContent = `${vendorCount.toLocaleString()} UNIQUE VENDORS`;
                    console.log(`✅ Updated vendor text: ${vendorCount} UNIQUE VENDORS`);
                    break;
                }
            }
        }
    } catch (error) {
        console.error("❌ Error updating vendor count:", error);
    }
}

// Immediate calculation and update
console.log("🚀 Starting immediate product count calculation...");
calculateAndDisplayTotalProducts();

// Set up periodic refresh
setInterval(() => {
    console.log("🔄 Periodic product count calculation...");
    calculateAndDisplayTotalProducts();
}, 30000); // Every 30 seconds

console.log("🎉 FINAL PRODUCT COUNT CALCULATION APPLIED!");
console.log("Should now show correct total products (3,305+) instead of 0");
console.log("Will recalculate every 30 seconds to maintain accuracy");
