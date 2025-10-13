// RESTORE TOTAL PRODUCTS CARD - Fix missing TOTAL PRODUCTS card
// Add this to browser console to restore the missing card

console.log("🔧 RESTORE TOTAL PRODUCTS CARD: Fixing missing TOTAL PRODUCTS card");

// The issue: TOTAL PRODUCTS card has disappeared from the dashboard
// But the Product Type Distribution shows 2,724+ products, so data exists

async function restoreTotalProductsCard() {
    console.log("🔄 Restoring missing TOTAL PRODUCTS card...");
    
    try {
        // Get fresh data to calculate total products
        const [statsResponse, tagsResponse] = await Promise.all([
            fetch('/api/database-stats'),
            fetch('/api/available-tags')
        ]);
        
        const stats = await statsResponse.json();
        const tags = await tagsResponse.json();
        
        console.log("📊 API data:", {
            stats: stats.stats,
            tagsCount: tags.tags?.length || 0,
            totalCount: tags.total_count || 0
        });
        
        // Calculate total products from multiple sources
        let totalProducts = 0;
        
        // Method 1: Use API stats
        if (stats.stats && stats.stats.total_products) {
            totalProducts = stats.stats.total_products;
        } else if (stats.stats && stats.stats.total_records) {
            totalProducts = stats.stats.total_records;
        }
        // Method 2: Use tags count
        else if (tags.total_count) {
            totalProducts = tags.total_count;
        } else if (tags.tags && tags.tags.length > 0) {
            totalProducts = tags.tags.length;
        }
        // Method 3: Calculate from Product Type Distribution
        else if (stats.stats && stats.stats.product_type_distribution) {
            const distribution = stats.stats.product_type_distribution;
            totalProducts = Object.values(distribution).reduce((sum, count) => sum + (count || 0), 0);
        }
        
        console.log(`🎯 Calculated total products: ${totalProducts}`);
        
        if (totalProducts > 0) {
            // Find the dashboard container
            const dashboardContainer = findDashboardContainer();
            
            if (dashboardContainer) {
                // Create or restore the TOTAL PRODUCTS card
                createTotalProductsCard(dashboardContainer, totalProducts);
            } else {
                console.warn("⚠️ Could not find dashboard container");
            }
        } else {
            console.warn("⚠️ Could not determine total products");
        }
        
    } catch (error) {
        console.error("❌ Error restoring TOTAL PRODUCTS card:", error);
    }
}

function findDashboardContainer() {
    console.log("🔍 Looking for dashboard container...");
    
    // Try multiple selectors to find the dashboard
    const selectors = [
        '.dashboard-stats',
        '.stats-container',
        '.dashboard-container',
        '.summary-cards',
        '.stat-cards',
        '.dashboard-summary',
        '.main-dashboard',
        '[class*="dashboard"]',
        '[class*="stats"]'
    ];
    
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            console.log(`✅ Found dashboard container with selector: ${selector}`);
            return element;
        }
    }
    
    // Fallback: look for elements with stat cards
    const statElements = document.querySelectorAll('[class*="stat"], [class*="card"]');
    if (statElements.length > 0) {
        console.log(`✅ Found ${statElements.length} stat/card elements, using parent container`);
        return statElements[0].parentElement;
    }
    
    console.warn("⚠️ Could not find dashboard container");
    return null;
}

function createTotalProductsCard(container, totalProducts) {
    console.log(`🔄 Creating TOTAL PRODUCTS card with ${totalProducts} products...`);
    
    // Check if card already exists
    const existingCard = container.querySelector('[data-stat="total_products"], .total-products, #total-products');
    if (existingCard) {
        console.log("✅ TOTAL PRODUCTS card already exists, updating...");
        updateExistingCard(existingCard, totalProducts);
        return;
    }
    
    // Create new card
    const card = document.createElement('div');
    card.className = 'stat-card total-products';
    card.setAttribute('data-stat', 'total_products');
    
    // Get the style from existing cards
    const existingCards = container.querySelectorAll('[class*="stat"], [class*="card"]');
    if (existingCards.length > 0) {
        const existingCard = existingCards[0];
        card.className = existingCard.className;
        card.style.cssText = existingCard.style.cssText;
    }
    
    // Create card content
    card.innerHTML = `
        <div class="stat-number">${totalProducts.toLocaleString()}</div>
        <div class="stat-label">TOTAL PRODUCTS</div>
    `;
    
    // Insert at the beginning of the container
    container.insertBefore(card, container.firstChild);
    
    console.log(`✅ Created TOTAL PRODUCTS card with ${totalProducts.toLocaleString()} products`);
}

function updateExistingCard(card, totalProducts) {
    console.log(`🔄 Updating existing TOTAL PRODUCTS card...`);
    
    // Update the number
    const numberElement = card.querySelector('.stat-number, [class*="number"]');
    if (numberElement) {
        numberElement.textContent = totalProducts.toLocaleString();
        console.log(`✅ Updated number to: ${totalProducts.toLocaleString()}`);
    }
    
    // Update the label
    const labelElement = card.querySelector('.stat-label, [class*="label"]');
    if (labelElement) {
        labelElement.textContent = 'TOTAL PRODUCTS';
        console.log(`✅ Updated label to: TOTAL PRODUCTS`);
    }
    
    // Make sure card is visible
    card.style.display = '';
    card.style.visibility = 'visible';
    card.style.opacity = '1';
    
    console.log(`✅ Updated existing card successfully`);
}

// Also update vendor count while we're at it
async function updateVendorCount() {
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
                '.stat-card:nth-child(2) .stat-number'
            ];
            
            for (const selector of vendorSelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = vendorCount.toLocaleString();
                    console.log(`✅ Updated vendor count to: ${vendorCount}`);
                    break;
                }
            }
        }
    } catch (error) {
        console.error("❌ Error updating vendor count:", error);
    }
}

// Immediate fix
console.log("🚀 Restoring TOTAL PRODUCTS card immediately...");
restoreTotalProductsCard();

// Also update vendor count
setTimeout(() => {
    updateVendorCount();
}, 1000);

// Set up periodic refresh
setInterval(() => {
    console.log("🔄 Periodic TOTAL PRODUCTS card refresh...");
    restoreTotalProductsCard();
    updateVendorCount();
}, 20000); // Every 20 seconds

console.log("🎉 RESTORE TOTAL PRODUCTS CARD FIX APPLIED!");
console.log("TOTAL PRODUCTS card should now be visible and show correct count");
console.log("Will refresh every 20 seconds to maintain accuracy");
