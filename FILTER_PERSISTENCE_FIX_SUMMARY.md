# Filter Persistence Fix Summary

## Problem Description
The user reported that "new filter wipes list" - meaning that when filters were applied, the selected tags list was being cleared or reset, which was not the desired behavior.

## Root Cause Analysis
The issue was in the `applyFilters()` function in `static/js/main.js`. When filters were applied, the function was calling:

```javascript
this.debouncedUpdateAvailableTags(filteredTags);
```

This was passing only the filtered tags to the `_updateAvailableTags` function, which then stored these filtered tags in `this.state.tags`. This meant that when the selected tags were updated, they were looking for tags in the filtered list instead of the original list, causing the selected tags to disappear or become inconsistent.

## Solution Implemented

### 1. Modified Function Signatures
Updated the `debouncedUpdateAvailableTags` and `_updateAvailableTags` functions to accept both original tags and filtered tags:

```javascript
// Before
debouncedUpdateAvailableTags: debounce(function(tags) {
    this._updateAvailableTags(tags);
}, 100),

// After
debouncedUpdateAvailableTags: debounce(function(originalTags, filteredTags = null) {
    this._updateAvailableTags(originalTags, filteredTags);
}, 100),
```

### 2. Updated applyFilters() Function
Modified the `applyFilters()` function to always pass original tags while using filtered tags for display:

```javascript
// Before
this.debouncedUpdateAvailableTags(filteredTags);

// After
this.debouncedUpdateAvailableTags(this.state.originalTags, filteredTags);
```

### 3. Enhanced _updateAvailableTags() Function
Updated the internal function to handle both original and filtered tags:

```javascript
_updateAvailableTags(originalTags, filteredTags = null) {
    // Store original tags in state for later use
    this.state.originalTags = [...originalTags];
    
    // Use filtered tags for display if provided, otherwise use original tags
    const tagsToDisplay = filteredTags || originalTags;
    this.state.tags = [...tagsToDisplay];
    
    // ... rest of the function uses tagsToDisplay for rendering
}
```

### 4. Updated All Function Calls
Updated all calls to `debouncedUpdateAvailableTags` throughout the codebase to use the new signature:

- **Search functionality**: Now passes original tags with filtered results
- **Move operations**: Pass original tags to preserve selections
- **Initial data loading**: Passes original tags with null for filtered tags
- **Lineage editor**: Updated to pass both original and current tags

## Key Benefits

### 1. Persistent Selected Tags
Selected tags now remain unchanged when filters are applied, allowing users to build selections from different filter criteria.

### 2. Independent Filtering
The available tags display is filtered based on user selections, but the selected tags list operates independently.

### 3. Consistent State Management
The system now maintains a clear separation between:
- `originalTags`: The complete dataset
- `tags`: The currently displayed/filtered tags
- `persistentSelectedTags`: The user's selections (independent of filters)

### 4. Backward Compatibility
All existing functionality continues to work as expected, with no breaking changes to the user interface.

## Testing

### Test File Created
Created `test_filter_persistence.html` with comprehensive test steps to verify:
1. Tags can be selected from different vendors
2. Filters can be applied without affecting selected tags
3. Additional tags can be selected from filtered views
4. Multiple filter changes preserve all selections
5. Clearing filters shows all available tags while preserving selections

### Test Scenarios
- Select tags from Vendor A
- Apply filter for Vendor B
- Select tags from Vendor B
- Apply Product Type filter
- Clear all filters
- Verify all selections remain intact

## Files Modified

### Primary Changes
- `static/js/main.js`: Updated filter logic and function signatures
- `static/js/lineage-editor.js`: Updated function calls

### Documentation
- `FILTER_PERSISTENCE_FIX_SUMMARY.md`: This summary document
- `test_filter_persistence.html`: Test file for verification

## Technical Details

### State Management
The fix ensures proper state management by:
1. Always maintaining the original dataset in `this.state.originalTags`
2. Using filtered data only for display purposes in `this.state.tags`
3. Keeping persistent selections in `this.state.persistentSelectedTags`

### Performance Considerations
- No performance impact as the same data is being processed
- Filter caching is preserved
- Debouncing is maintained for smooth user experience

### Error Handling
- Graceful fallback when filtered tags are not provided
- Maintains existing error handling patterns
- No new error conditions introduced

## Conclusion

This fix successfully resolves the issue where applying filters would wipe the selected tags list. Users can now:

1. Select tags from one filter view
2. Change filters to see different tags
3. Select additional tags from the new filter view
4. Have all selections persist across filter changes

The implementation maintains the existing user interface while providing the expected behavior for persistent tag selections. 