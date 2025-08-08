// Debug script to identify tag display issues
console.log('=== TAG DISPLAY DEBUG START ===');

// Check if TagManager exists
if (typeof TagManager !== 'undefined') {
    console.log('TagManager found:', TagManager);
    
    // Check state
    if (TagManager.state) {
        console.log('TagManager state:', {
            tags: TagManager.state.tags ? TagManager.state.tags.length : 0,
            originalTags: TagManager.state.originalTags ? TagManager.state.originalTags.length : 0,
            selectedTags: TagManager.state.selectedTags ? TagManager.state.selectedTags.length : 0
        });
    }
} else {
    console.log('TagManager not found');
}

// Check DOM elements
const availableTagsContainer = document.getElementById('availableTags');
const selectedTagsContainer = document.getElementById('selectedTags');

if (availableTagsContainer) {
    console.log('Available tags container found');
    const tagElements = availableTagsContainer.querySelectorAll('.tag-item, .tag-row');
    console.log('Available tag elements found:', tagElements.length);
    
    // Check for hidden elements
    let hiddenCount = 0;
    tagElements.forEach((el, index) => {
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
            hiddenCount++;
            console.log(`Hidden tag at index ${index}:`, el.textContent.trim());
        }
    });
    console.log('Hidden tag elements:', hiddenCount);
} else {
    console.log('Available tags container not found');
}

if (selectedTagsContainer) {
    console.log('Selected tags container found');
    const tagElements = selectedTagsContainer.querySelectorAll('.tag-item, .tag-row');
    console.log('Selected tag elements found:', tagElements.length);
} else {
    console.log('Selected tags container not found');
}

// Check CSS height restrictions
const tagListContainers = document.querySelectorAll('.tag-list-container');
tagListContainers.forEach((container, index) => {
    const style = window.getComputedStyle(container);
    console.log(`Tag list container ${index}:`, {
        maxHeight: style.maxHeight,
        height: style.height,
        overflow: style.overflow,
        display: style.display
    });
});

// Check for any JavaScript errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error detected:', event.error);
    console.error('Error location:', event.filename, 'line:', event.lineno);
});

console.log('=== TAG DISPLAY DEBUG END ==='); 