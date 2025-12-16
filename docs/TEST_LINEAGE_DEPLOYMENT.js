// Test script to verify lineage fix deployment
// Run this in the browser console on PythonAnywhere

console.log("=== TESTING LINEAGE FIX DEPLOYMENT ===");

// Test 1: Check if the updated generation function exists
if (typeof TagManager !== 'undefined' && TagManager.generateLabels) {
    console.log("✅ TagManager.generateLabels exists");
    
    // Check if the function has been updated to send full tag objects
    const functionString = TagManager.generateLabels.toString();
    if (functionString.includes('selectedTagObjects')) {
        console.log("✅ Generation function has been updated to send full tag objects");
    } else {
        console.log("❌ Generation function has NOT been updated - still using old format");
    }
    
    if (functionString.includes('CRITICAL FIX: Collect full tag data')) {
        console.log("✅ Generation function includes the lineage fix");
    } else {
        console.log("❌ Generation function does NOT include the lineage fix");
    }
} else {
    console.log("❌ TagManager.generateLabels not found");
}

// Test 2: Check if TagsTable.handleLineageChange has been updated
if (typeof TagsTable !== 'undefined' && TagsTable.handleLineageChange) {
    console.log("✅ TagsTable.handleLineageChange exists");
    
    const functionString = TagsTable.handleLineageChange.toString();
    if (functionString.includes('tagElement.dataset.lineage = newLineage')) {
        console.log("✅ handleLineageChange includes data-lineage attribute update");
    } else {
        console.log("❌ handleLineageChange does NOT include data-lineage attribute update");
    }
} else {
    console.log("❌ TagsTable.handleLineageChange not found");
}

// Test 3: Check current lineage values in selected tags
const selectedTags = document.querySelectorAll('#selectedTags .tag-item');
console.log(`Found ${selectedTags.length} selected tags`);

selectedTags.forEach((tagElement, index) => {
    const tagName = tagElement.dataset.tagName || tagElement.querySelector('.tag-name')?.textContent || 'Unknown';
    const currentLineage = tagElement.dataset.lineage || 'Unknown';
    const lineageSelect = tagElement.querySelector('.lineage-dropdown');
    const selectedValue = lineageSelect ? lineageSelect.value : 'Unknown';
    
    console.log(`Tag ${index + 1}: "${tagName}"`);
    console.log(`  - data-lineage: "${currentLineage}"`);
    console.log(`  - dropdown value: "${selectedValue}"`);
    
    if (currentLineage !== selectedValue) {
        console.log(`  ⚠️ MISMATCH: data-lineage (${currentLineage}) != dropdown value (${selectedValue})`);
    } else {
        console.log(`  ✅ Match: data-lineage matches dropdown value`);
    }
});

// Test 4: Simulate a lineage change
console.log("\n=== SIMULATING LINEAGE CHANGE ===");
const firstTag = selectedTags[0];
if (firstTag) {
    const lineageSelect = firstTag.querySelector('.lineage-dropdown');
    if (lineageSelect) {
        const originalValue = lineageSelect.value;
        console.log(`Original lineage: ${originalValue}`);
        
        // Change to HYBRID/INDICA if available
        if (lineageSelect.querySelector('option[value="HYBRID/INDICA"]')) {
            lineageSelect.value = 'HYBRID/INDICA';
            lineageSelect.dispatchEvent(new Event('change'));
            console.log(`Changed to: ${lineageSelect.value}`);
            console.log(`Updated data-lineage: ${firstTag.dataset.lineage}`);
        } else {
            console.log("HYBRID/INDICA option not available");
        }
    }
}

console.log("=== TEST COMPLETE ===");
