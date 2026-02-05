# Fixed: App Loading Tags Before Store Selection Modal

## Problem

The app was trying to load tags before checking if a store was selected, causing:
1. Unnecessary API calls to `/api/available-tags` before store is set
2. Potential errors or empty tag lists
3. Poor user experience with loading indicators before the store modal appears

## Root Cause

In the `DOMContentLoaded` handler, the initialization order was wrong:

**Before (WRONG ORDER):**
```javascript
document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize TagManager IMMEDIATELY (loads tags)
  TagManager.init();  
  
  // 2. Check store 500ms LATER
  setTimeout(() => {
    checkStoreRequired();
  }, 500);
});
```

This meant:
- TagManager.init() → loadAvailableTags() → API call
- THEN store check happens
- Tags loading with no store selected!

## Solution

Reversed the order and added a callback pattern:

**After (CORRECT ORDER):**
```javascript
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    // 1. Check store FIRST
    checkStoreRequired(function() {
      // 2. This callback ONLY runs when store is confirmed
      console.log('✅ Store confirmed! Initializing TagManager...');
      TagManager.init();
    });
  }, 100);
});
```

### Modified Functions

#### 1. `checkStoreRequired(onStoreConfirmed)` - Added callback parameter

```javascript
function checkStoreRequired(onStoreConfirmed) {
  // ... existing store check logic ...
  
  .then(data => {
    const userHasStore = (data.success && !data.requires_store && data.store);
    
    if (userHasStore) {
      // Store confirmed - show content
      // ... existing show content logic ...
      
      // NEW: Call callback to initialize TagManager
      if (typeof onStoreConfirmed === 'function') {
        console.log('🔄 Store confirmed, calling initialization callback...');
        setTimeout(() => onStoreConfirmed(), 100);
      }
    } else {
      // No store - show modal
      // Callback is NOT called, so TagManager is NOT initialized
    }
  });
}
```

## Flow Now Works Correctly

### Scenario 1: User Has Store Already
1. Page loads
2. `checkStoreRequired()` called with callback
3. Backend returns store exists
4. Content shown, modal hidden
5. **Callback runs** → `TagManager.init()` → Tags load ✅
6. User sees fully initialized app

### Scenario 2: No Store Selected Yet
1. Page loads
2. `checkStoreRequired()` called with callback
3. Backend returns no store
4. Modal shown, content hidden
5. **Callback NOT called** → TagManager NOT initialized ✅
6. User selects store
7. Page reloads → Goes to Scenario 1

### Scenario 3: User Changes Store
1. User clicks "Change" on store selector
2. User selects different store
3. Page reloads
4. Goes to Scenario 1 with new store

## Benefits

✅ **No unnecessary API calls** - Tags only load when store is confirmed
✅ **Cleaner initialization** - Proper sequential flow
✅ **Better performance** - No wasted requests
✅ **Better UX** - No loading states before store selection
✅ **No race conditions** - Callback ensures proper timing

## Testing

To verify the fix:

1. **Clear cookies/session** and load the app
   - Should see store modal immediately
   - Should NOT see tag loading
   - Console should NOT show `/api/available-tags` call until after store selected

2. **Select a store**
   - Page reloads
   - Content appears
   - Tags load AFTER content is shown
   - Console shows correct order:
     ```
     ✅ STORE FOUND: AGT_Bothell
     ✅ Content shown, modal hidden
     🔄 Store confirmed, calling initialization callback...
     ✅ Store confirmed! Initializing TagManager...
     Loading available tags from API...
     ```

3. **Reload page with store selected**
   - Should NOT show modal
   - Should load tags immediately
   - Normal operation

## Files Changed

- `templates/index.html`:
  - Modified `checkStoreRequired()` to accept `onStoreConfirmed` callback
  - Added callback invocation when store is confirmed (line 557-560)
  - Modified `DOMContentLoaded` to use callback pattern (line 6797-6801)

## Related Issues Fixed

This also fixes:
- API errors when no store is set
- Empty tag lists on initial load
- Console warnings about missing store context
- Performance issues from redundant API calls

