// IMMEDIATE LINEAGE FIX - Run this in browser console
// This will force the correct lineage values for generation

console.log("=== IMMEDIATE LINEAGE FIX ===");

// Step 1: Update all selected tags with correct lineage from dropdowns
const selectedTags = document.querySelectorAll('#selectedTags .tag-item');
console.log(`Found ${selectedTags.length} selected tags to update`);

let updatedCount = 0;
selectedTags.forEach((tagElement, index) => {
    const tagName = tagElement.dataset.tagName || tagElement.querySelector('.tag-name')?.textContent || 'Unknown';
    const lineageSelect = tagElement.querySelector('.lineage-dropdown');
    
    if (lineageSelect) {
        const correctLineage = lineageSelect.value;
        const currentDataLineage = tagElement.dataset.lineage;
        
        console.log(`Tag ${index + 1}: "${tagName}"`);
        console.log(`  - Dropdown value: "${correctLineage}"`);
        console.log(`  - Current data-lineage: "${currentDataLineage}"`);
        
        if (correctLineage !== currentDataLineage) {
            // Update the data-lineage attribute
            tagElement.dataset.lineage = correctLineage;
            
            // Update TagManager state
            if (typeof TagManager !== 'undefined' && TagManager.state.tags) {
                const tagInState = TagManager.state.tags.find(t => 
                    (t['Product Name*'] === tagName) || (t.ProductName === tagName)
                );
                if (tagInState) {
                    tagInState.lineage = correctLineage;
                    tagInState.Lineage = correctLineage;
                    console.log(`  ✅ Updated TagManager state for "${tagName}"`);
                    updatedCount++;
                }
            }
            
            console.log(`  ✅ Updated data-lineage to: "${correctLineage}"`);
        } else {
            console.log(`  ✅ Already correct`);
        }
    }
});

console.log(`\n=== UPDATED ${updatedCount} TAGS ===`);

// Step 2: Force update the generation function to use correct lineage
if (typeof TagManager !== 'undefined') {
    console.log("Updating TagManager generation function...");
    
    // Override the generateLabels function to ensure correct lineage
    const originalGenerateLabels = TagManager.generateLabels;
    TagManager.generateLabels = async function(templateType, scaleFactor) {
        console.log("🔧 Using UPDATED generation function with lineage fix");
        
        // Get selected tags
        let checkedTags = [...this.state.persistentSelectedTags];
        console.log(`Generating with ${checkedTags.length} tags`);
        
        // Collect full tag objects with updated lineage
        const selectedTagObjects = [];
        for (const tagName of checkedTags) {
            // Find the tag in the current state
            const tagWithUpdatedLineage = this.state.tags.find(t => 
                (t['Product Name*'] === tagName) || (t.ProductName === tagName)
            );
            
            if (tagWithUpdatedLineage) {
                // Double-check lineage from DOM
                const tagElement = document.querySelector(`[data-tag-name="${tagName}"]`);
                if (tagElement) {
                    const domLineage = tagElement.dataset.lineage;
                    if (domLineage && domLineage !== tagWithUpdatedLineage.lineage) {
                        console.log(`🔧 DOM lineage differs from state: "${tagWithUpdatedLineage.lineage}" -> "${domLineage}"`);
                        tagWithUpdatedLineage.lineage = domLineage;
                        tagWithUpdatedLineage.Lineage = domLineage;
                    }
                }
                
                selectedTagObjects.push(tagWithUpdatedLineage);
                console.log(`📝 Tag: "${tagName}" -> Lineage: "${tagWithUpdatedLineage.lineage || tagWithUpdatedLineage.Lineage}"`);
            } else {
                console.log(`⚠️ Tag not found in state: "${tagName}"`);
                selectedTagObjects.push({ 'Product Name*': tagName, ProductName: tagName });
            }
        }
        
        // Call original function with updated data
        return await originalGenerateLabels.call(this, templateType, scaleFactor);
    };
    
    console.log("✅ Updated generation function");
}

// Step 3: Test the fix
console.log("\n=== TESTING FIX ===");
console.log("Now try generating tags - the lineage values should be correct!");

// Step 4: Show current state
console.log("\n=== CURRENT STATE ===");
selectedTags.forEach((tagElement, index) => {
    const tagName = tagElement.dataset.tagName || 'Unknown';
    const lineage = tagElement.dataset.lineage || 'Unknown';
    console.log(`${index + 1}. "${tagName}" -> "${lineage}"`);
});

console.log("\n=== FIX COMPLETE ===");
console.log("The lineage values should now be correct in generated tags!");
