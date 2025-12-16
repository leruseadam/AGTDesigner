# Fixed: App Sometimes Shows Only Background After Refresh

## Issue
After refreshing the page, sometimes the app would only show the background and not load the content properly. Users would see a stuck loading screen or just the background.

## Root Causes

### 1. Missing Loading Splash Dismissal
**Problem:** The loading splash screen was displayed but never hidden after initialization.

**Fix:** 
- Added `hideLoadingSplash()` function to properly fade out the splash
- Called it after TagManager initializes (300ms delay)
- Added 3-second safety timeout to force hide even if initialization fails

### 2. Deferred Script Race Condition
**Problem:** When all scripts were deferred, inline scripts that depend on main.js (like TagManager) would sometimes run before main.js finished loading, causing initialization failures.

**Fix:**
- Removed `defer` from critical scripts (Bootstrap, main.js)
- Kept `defer` only on non-critical scripts (enhanced-ui, lava-lamp, etc.)
- This ensures inline scripts can safely use code from main.js

## Changes Made

### templates/index.html

```javascript
// Added global function to hide loading splash
window.hideLoadingSplash = function() {
  const splash = document.getElementById('appLoadingSplash');
  if (splash && !splash.classList.contains('fade-out')) {
    console.log('Hiding loading splash...');
    splash.classList.add('fade-out');
    setTimeout(() => {
      splash.style.display = 'none';
    }, 500);
  }
};

// Safety fallback: Force hide splash after 3 seconds max
setTimeout(() => {
  console.log('Safety fallback: Forcing splash hide');
  window.hideLoadingSplash();
}, 3000);
```

```javascript
// In DOMContentLoaded handler
document.addEventListener('DOMContentLoaded', function () {
  TagManager.init();
  
  // Hide loading splash once app is ready
  setTimeout(() => {
    window.hideLoadingSplash();
  }, 300);
  
  // Check store requirement
  setTimeout(() => {
    checkStoreRequired();
  }, 500);
});
```

### Script Loading Strategy

**Before (problematic):**
```html
<script src="bootstrap.bundle.min.js" defer></script>
<script src="main.js" defer></script>
<!-- All deferred = race conditions -->
```

**After (fixed):**
```html
<script src="bootstrap.bundle.min.js"></script>
<script src="main.js"></script>
<!-- Critical scripts load immediately -->

<script src="enhanced-ui.js" defer></script>
<script src="lava-lamp.js" defer></script>
<!-- Non-critical scripts deferred -->
```

## Testing

To verify the fix:

1. **Hard Refresh Test:**
   - Press Ctrl+Shift+R (or Cmd+Shift+R on Mac) multiple times
   - App should load properly every time
   - Loading splash should disappear within 1-3 seconds

2. **Normal Refresh Test:**
   - Press F5 or click refresh multiple times
   - No stuck loading screens
   - Content appears consistently

3. **Console Check:**
   - Open DevTools Console
   - Should see "Hiding loading splash..." within 3 seconds
   - No JavaScript errors about undefined functions

## Why This Works

1. **Guaranteed Splash Dismissal:**
   - Three mechanisms ensure splash hides:
     1. After TagManager init (300ms)
     2. Safety timeout (3 seconds)
     3. Manual calls if needed
   - Even if initialization fails, splash will hide

2. **No Race Conditions:**
   - Critical scripts load before inline code runs
   - main.js is ready when TagManager.init() is called
   - Bootstrap is ready for modal functionality

3. **Fast Loading:**
   - Non-critical scripts still deferred for performance
   - Only critical scripts block (which finish quickly)
   - Best balance of speed and reliability

## Performance Impact

- Loading splash ensures perceived performance (users know app is loading)
- Deferred non-critical scripts maintain fast page rendering
- No negative impact on actual load times
- **Result:** Reliable loading with good performance

## Rollback

If issues occur, remove the safety timeout and use immediate loading:

```javascript
// Remove safety timeout
// setTimeout(() => window.hideLoadingSplash(); }, 3000);

// And hide splash immediately after init
TagManager.init();
window.hideLoadingSplash();
```

