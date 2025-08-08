# Collapse/Expand Filter Feature Summary

## Feature Description
Implemented a smart collapse/expand system that keeps vendors collapsed by default when no filters are active, but automatically expands all sections when filters are selected. This provides a cleaner initial view while making it easier to see relevant items when filtering.

## Behavior

### Default State (No Filters Active)
- **Vendors**: Collapsed by default (▶ icon)
- **Brands**: Collapsed by default (▶ icon)
- **Product Types**: Collapsed by default (▶ icon)
- **Weights**: Collapsed by default (▶ icon)

### When Filters Are Active
- **Vendors**: Expanded (▼ icon)
- **Brands**: Expanded (▼ icon)
- **Product Types**: Expanded (▼ icon)
- **Weights**: Expanded (▼ icon)

## Implementation Details

### 1. Filter Detection Function (static/js/main.js)

Added `hasActiveFilters()` function to detect when any filter is active:

```javascript
hasActiveFilters() {
    // Check if any filters are currently active (not set to "All")
    const vendorFilter = document.getElementById('vendorFilter')?.value || '';
    const brandFilter = document.getElementById('brandFilter')?.value || '';
    const productTypeFilter = document.getElementById('productTypeFilter')?.value || '';
    const lineageFilter = document.getElementById('lineageFilter')?.value || '';
    const weightFilter = document.getElementById('weightFilter')?.value || '';
    const dohFilter = document.getElementById('dohFilter')?.value || '';
    const highCbdFilter = document.getElementById('highCbdFilter')?.value || '';
    
    const filters = [vendorFilter, brandFilter, productTypeFilter, lineageFilter, weightFilter, dohFilter, highCbdFilter];
    
    // Return true if any filter is not empty and not "All"
    return filters.some(filter => filter && filter.trim() !== '' && filter.toLowerCase() !== 'all');
}
```

### 2. Dynamic Collapse State Logic

Applied to all hierarchical levels (vendor, brand, product type, weight):

```javascript
// Check if any filters are active to determine initial collapse state
const hasActiveFilters = this.hasActiveFilters();
const shouldStartCollapsed = !hasActiveFilters;

// Set appropriate icon
element.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';

// Add collapsed class if needed
if (shouldStartCollapsed) {
    contentElement.classList.add('collapsed');
}
```

### 3. CSS Support

The feature leverages existing CSS classes for collapsed states:

```css
.vendor-content.collapsed,
.brand-content.collapsed,
.product-type-content.collapsed,
.weight-content.collapsed {
    display: none;
}
```

## Benefits

1. **Cleaner Initial View**: Users see a compact, organized list when no filters are applied
2. **Better Filter Experience**: When filters are active, all relevant sections are expanded for easy browsing
3. **Consistent Behavior**: All hierarchical levels follow the same collapse/expand logic
4. **Intuitive Icons**: Clear visual indicators (▶ for collapsed, ▼ for expanded)
5. **Performance**: Reduces initial DOM complexity when no filters are active

## User Experience

### Scenario 1: No Filters
- User opens the application
- All vendor sections are collapsed
- User can click to expand specific vendors
- Clean, organized view of available vendors

### Scenario 2: Filter Applied
- User selects a filter (e.g., "Capsule" product type)
- All sections automatically expand
- User can see all relevant items across all vendors
- Easier to browse filtered results

### Scenario 3: Filter Removed
- User changes filter back to "All"
- All sections automatically collapse
- Returns to clean, organized view

## Testing Recommendations

1. **Default State Test**: Load application and verify all sections start collapsed
2. **Filter Application Test**: Apply various filters and verify sections expand
3. **Filter Removal Test**: Remove filters and verify sections collapse
4. **Mixed Filter Test**: Apply multiple filters and verify expansion behavior
5. **Manual Toggle Test**: Verify users can still manually expand/collapse sections

## Files Modified

1. **static/js/main.js**
   - Added `hasActiveFilters()` function
   - Updated vendor section creation with dynamic collapse logic
   - Updated brand section creation with dynamic collapse logic
   - Updated product type section creation with dynamic collapse logic
   - Updated weight section creation with dynamic collapse logic

## Impact

- **Positive**: Cleaner initial user interface
- **Positive**: Better user experience when filtering
- **Positive**: Consistent behavior across all hierarchical levels
- **Positive**: Maintains manual control while providing smart defaults

The feature provides an intelligent collapse/expand system that adapts to user behavior, making the interface more user-friendly and efficient for both browsing and filtering operations. 