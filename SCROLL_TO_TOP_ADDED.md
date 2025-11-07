# ✅ Auto-Scroll to Top on Filter Change

## What Changed

When you select a filter (VENDOR, BRAND, PRODUCT TYPE, etc.), the **CURRENT INVENTORY list now automatically scrolls to the top**.

### Why This is Better:

**Before:**
- Select a filter
- List updates but stays at current scroll position
- Have to manually scroll up to see the filtered results from the beginning
- Confusing UX

**After:**
- Select a filter
- List updates AND scrolls to top automatically ✅
- Immediately see filtered results from the beginning
- Intuitive and smooth

## How It Works

### Code Location:
`static/js/main.js`, lines 1882-1892

### New Function:
```javascript
_scrollAvailableTagsToTop() {
    const availableTagsContainer = document.getElementById('availableTags');
    if (availableTagsContainer) {
        availableTagsContainer.scrollTop = 0;
    }
}
```

### When It Triggers:
- ✅ When ANY filter is changed (vendor, brand, type, lineage, weight, doh, cbd)
- ✅ When filters are cleared (reset to "All")
- ✅ When cached filter results are loaded
- ✅ After filter results are rendered

### What Gets Scrolled:
The **"CURRENT INVENTORY"** section (left column) scrolls to show the first filtered item.

## Testing

1. **Refresh**: http://localhost:8003
2. **Scroll down** in the CURRENT INVENTORY list
3. **Select a filter** (e.g., VENDOR: "American Cannabis Outlet")
4. **The list automatically scrolls to the top!** ✅
5. Try different filters - each time it scrolls to top

## Combined with Previous Fix

This works together with the "show all options" fix:
- ✅ All filter options remain visible (no need to reset to "All")
- ✅ List scrolls to top when filter changes
- ✅ Easy to see what changed
- ✅ Smooth workflow

---
**Status**: ✅ IMPLEMENTED  
**Date**: November 7, 2025  
**User Preference**: Applied

