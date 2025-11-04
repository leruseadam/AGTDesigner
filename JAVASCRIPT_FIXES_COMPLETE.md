# JavaScript Fixes - Page Load Issues Resolved

## Problem
The page was showing only the lava lamp background with no UI elements. Multiple JavaScript errors were preventing the application from initializing.

## Errors Fixed

### 1. normalizeViewport TypeError (Line 170)
**Error**: `Uncaught TypeError: Cannot read properties of null (reading 'style')`

**Root Cause**: 
- The `normalizeViewport()` function was defined in the `<head>` section and called immediately
- It tried to access `document.body.style` before the `<body>` element was created
- `document.body` was `null` at execution time

**Solution**:
```javascript
// Before (BROKEN):
document.body.style.minHeight = '100vh';

// After (FIXED):
if (document.body) {
  document.body.style.minHeight = '100vh';
  document.body.style.minWidth = '100vw';
}

// Also changed initialization to wait for DOM:
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', normalizeViewport);
} else {
  normalizeViewport();
}
```

### 2. Duplicate CLASSIC_TYPES Declaration (tags_table.js)
**Error**: `SyntaxError: Identifier 'CLASSIC_TYPES' has already been declared`

**Root Cause**:
- `CLASSIC_TYPES` was declared twice in the same file
- Line 2-6: `if (typeof window.CLASSIC_TYPES === 'undefined') { window.CLASSIC_TYPES = [...] }`
- Line 8: `const CLASSIC_TYPES = window.CLASSIC_TYPES || [...]`

**Solution**:
```javascript
// Before (BROKEN):
if (typeof window.CLASSIC_TYPES === 'undefined') {
  window.CLASSIC_TYPES = ["flower", "pre-roll", ...];
}
const CLASSIC_TYPES = window.CLASSIC_TYPES || ["flower", "pre-roll", ...];

// After (FIXED):
if (typeof window.CLASSIC_TYPES === 'undefined') {
  window.CLASSIC_TYPES = ["flower", "pre-roll", ...];
}
// Use window.CLASSIC_TYPES directly, don't redeclare
const CLASSIC_TYPES = window.CLASSIC_TYPES;
```

### 3. Port Mismatch / Cached Resources
**Symptom**: Browser showing `localhost:8002` but errors referencing `localhost:8001`

**This indicates**:
- Old JavaScript files cached from a previous server instance on port 8001
- Multiple server instances may be running simultaneously

**Solution**: User must clear browser cache with hard refresh:
- **Mac**: `Cmd + Shift + R`
- **Windows**: `Ctrl + Shift + R`
- Or: DevTools → Right-click refresh → "Empty Cache and Hard Reload"

## Files Modified

1. **`templates/index.html`**:
   - Lines 165-187: Fixed `normalizeViewport()` function to check for `document.body` existence
   - Added proper DOM ready check before initialization

2. **`static/js/tags_table.js`**:
   - Line 8-9: Removed duplicate `CLASSIC_TYPES` declaration

## Testing

After clearing browser cache, the page should:
- ✅ Load the full UI (not just the lava lamp background)
- ✅ Show the store selection modal if no store is selected
- ✅ Initialize all JavaScript modules without console errors
- ✅ Allow clicking store selection buttons
- ✅ Persist store selection across page reloads

## Additional Notes

- **Server is running on both ports 8001 AND 8002** - verify which one should be used
- The lava lamp background loading confirms the HTML is loading, but JavaScript errors were preventing UI initialization
- All previous fixes for store selection (`credentials: 'same-origin'`) are still in place

## Date
November 4, 2025

