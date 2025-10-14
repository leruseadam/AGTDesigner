// EMERGENCY FIX: Force correct product count in frontend
// Add this to browser console to fix the display immediately

console.log("🚨 EMERGENCY FIX: Forcing correct product count");

// Get the actual data
fetch('/api/available-tags')
  .then(response => response.json())
  .then(data => {
    const actualCount = data.tags ? data.tags.length : 0;
    console.log(`✅ Actual product count: ${actualCount}`);
    
    // Update all product count displays
    const countElements = document.querySelectorAll('h3');
    countElements.forEach(element => {
      if (element.textContent.includes('Total Products')) {
        element.textContent = `${actualCount}`;
        console.log(`✅ Updated Total Products to: ${actualCount}`);
      }
    });
    
    // Also update the parent elements
    const productCards = document.querySelectorAll('.card');
    productCards.forEach(card => {
      const text = card.textContent;
      if (text.includes('Total Products')) {
        const h3 = card.querySelector('h3');
        if (h3 && h3.textContent === '0') {
          h3.textContent = actualCount.toString();
          console.log(`✅ Fixed card display: ${actualCount}`);
        }
      }
    });
    
    console.log(`🎉 EMERGENCY FIX COMPLETE: ${actualCount} products displayed`);
  })
  .catch(error => {
    console.error("❌ Emergency fix failed:", error);
  });

// Also try to refresh the dashboard
setTimeout(() => {
  if (typeof openDatabaseAnalytics === 'function') {
    openDatabaseAnalytics();
    console.log("🔄 Refreshed dashboard");
  }
}, 1000);
