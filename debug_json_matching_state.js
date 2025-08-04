// Debug script to check JSON matching state
// Run this in the browser console after performing JSON matching

function debugJsonMatchingState() {
    console.log('=== JSON Matching State Debug ===');
    
    if (typeof TagManager === 'undefined') {
        console.error('TagManager not found');
        return;
    }
    
    // Check TagManager state
    console.log('TagManager State:', {
        tags: TagManager.state.tags ? TagManager.state.tags.length : 0,
        originalTags: TagManager.state.originalTags ? TagManager.state.originalTags.length : 0,
        persistentSelectedTags: TagManager.state.persistentSelectedTags ? TagManager.state.persistentSelectedTags.length : 0,
        selectedTags: TagManager.state.selectedTags ? TagManager.state.selectedTags.size : 0
    });
    
    // Check for JSON matched items
    if (TagManager.state.tags) {
        const jsonMatchedItems = TagManager.state.tags.filter(tag => tag.Source === 'JSON Match');
        console.log('JSON Matched Items in tags:', jsonMatchedItems.length);
        if (jsonMatchedItems.length > 0) {
            console.log('Sample JSON matched items:', jsonMatchedItems.slice(0, 3).map(t => t['Product Name*']));
        }
    }
    
    if (TagManager.state.originalTags) {
        const originalJsonMatchedItems = TagManager.state.originalTags.filter(tag => tag.Source === 'JSON Match');
        console.log('JSON Matched Items in originalTags:', originalJsonMatchedItems.length);
        if (originalJsonMatchedItems.length > 0) {
            console.log('Sample original JSON matched items:', originalJsonMatchedItems.slice(0, 3).map(t => t['Product Name*']));
        }
    }
    
    // Check DOM state
    const availableContainer = document.getElementById('availableTags');
    if (availableContainer) {
        const tagElements = availableContainer.querySelectorAll('.tag-checkbox');
        console.log('Available Tags in DOM:', tagElements.length);
        
        // Check if any DOM elements have JSON Match source
        const jsonMatchedElements = Array.from(tagElements).filter(el => {
            const tagName = el.value;
            const tag = TagManager.state.tags ? TagManager.state.tags.find(t => t['Product Name*'] === tagName) : null;
            return tag && tag.Source === 'JSON Match';
        });
        console.log('JSON Matched Elements in DOM:', jsonMatchedElements.length);
    }
    
    // Check backend state
    fetch('/api/available-tags')
        .then(response => response.json())
        .then(tags => {
            const backendJsonMatched = tags.filter(tag => tag.Source === 'JSON Match');
            console.log('Backend Available Tags:', tags.length);
            console.log('Backend JSON Matched Items:', backendJsonMatched.length);
            if (backendJsonMatched.length > 0) {
                console.log('Sample backend JSON matched items:', backendJsonMatched.slice(0, 3).map(t => t['Product Name*']));
            }
        })
        .catch(error => {
            console.error('Error fetching backend state:', error);
        });
    
    console.log('=== End Debug ===');
}

// Function to force refresh available tags
function forceRefreshAvailableTags() {
    console.log('Forcing refresh of available tags...');
    if (typeof TagManager !== 'undefined' && TagManager.fetchAndUpdateAvailableTags) {
        TagManager.fetchAndUpdateAvailableTags();
    } else {
        console.error('TagManager or fetchAndUpdateAvailableTags not found');
    }
}

// Function to manually update available tags with JSON matched data
function manuallyUpdateWithJsonData() {
    console.log('Manually updating with JSON data...');
    if (typeof TagManager !== 'undefined' && TagManager._updateAvailableTags) {
        // Get current tags and mark them as JSON matched
        const currentTags = TagManager.state.tags || [];
        const jsonMatchedTags = currentTags.map(tag => ({
            ...tag,
            Source: 'JSON Match'
        }));
        
        console.log('Updating with', jsonMatchedTags.length, 'JSON matched tags');
        TagManager._updateAvailableTags(jsonMatchedTags, null);
    } else {
        console.error('TagManager or _updateAvailableTags not found');
    }
}

// Export functions for use in console
window.debugJsonMatchingState = debugJsonMatchingState;
window.forceRefreshAvailableTags = forceRefreshAvailableTags;
window.manuallyUpdateWithJsonData = manuallyUpdateWithJsonData;

console.log('JSON Matching Debug functions loaded:');
console.log('- debugJsonMatchingState() - Check current state');
console.log('- forceRefreshAvailableTags() - Force refresh');
console.log('- manuallyUpdateWithJsonData() - Manual update with JSON data'); 