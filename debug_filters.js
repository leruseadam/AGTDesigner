// Debug script to test filter functionality
console.log('=== DEBUG FILTERS ===');

// Check if filter elements exist
const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];

filterIds.forEach(filterId => {
    const element = document.getElementById(filterId);
    console.log(`${filterId}:`, element ? 'FOUND' : 'NOT FOUND');
    if (element) {
        console.log(`  - Value: "${element.value}"`);
        console.log(`  - Options:`, element.options.length);
    }
});

// Test if we can attach event listeners
filterIds.forEach(filterId => {
    const element = document.getElementById(filterId);
    if (element) {
        console.log(`Testing event listener for ${filterId}...`);
        element.addEventListener('change', (e) => {
            console.log(`FILTER CHANGED: ${filterId} = "${e.target.value}"`);
        });
        console.log(`Event listener attached to ${filterId}`);
    }
});

// Test tag checkboxes
console.log('=== TESTING TAG CHECKBOXES ===');
const checkboxes = document.querySelectorAll('.tag-checkbox');
console.log(`Found ${checkboxes.length} tag checkboxes`);

checkboxes.forEach((checkbox, index) => {
    console.log(`Checkbox ${index}:`, checkbox.value, 'checked:', checkbox.checked);
    checkbox.addEventListener('change', (e) => {
        console.log(`TAG CHECKBOX CHANGED: ${checkbox.value} = ${e.target.checked}`);
    });
});

console.log('=== DEBUG COMPLETE ==='); 