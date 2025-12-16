# How to Fix "Tags Don't Load" Issue

## Problem
After the performance updates, your browser may be using old cached JavaScript code, preventing tags from loading properly.

## Quick Fix Options

### Option 1: Hard Refresh (Recommended)
**Mac:**
- Press `Cmd + Shift + R`
- Or hold `Shift` and click the refresh button

**Windows/Linux:**
- Press `Ctrl + Shift + R`
- Or hold `Shift` and click the refresh button

This will:
- Clear the browser cache
- Reload all JavaScript files
- Update the service worker to v2

### Option 2: Clear Browser Cache Manually
1. Open Developer Tools (`F12` or `Cmd+Option+I`)
2. Go to the "Application" tab
3. Click "Clear storage" in the left sidebar
4. Click "Clear site data" button
5. Refresh the page

### Option 3: Let the Auto-Fixer Do It
1. Just refresh the page normally (`Cmd+R` or `F5`)
2. The `force-cache-clear.js` script will detect old cache
3. It will automatically clear it and reload the page
4. You'll see a green banner: "✨ Update Available - Refreshing to load the latest version..."

## Verify It's Fixed
After clearing cache, you should see:
1. Tags load within 1-2 seconds
2. Console shows: "✅ Cache version is up to date"
3. Console shows: "📦 Loading X tags from initial data..."
4. Console shows: "✅ Background data loading complete"

## If Still Not Working

### Check Console for Errors
1. Open Developer Tools (`F12`)
2. Go to "Console" tab
3. Look for errors (red text)
4. Common issues:
   - "Failed to load resource" - Network issue
   - "Unexpected token" - Syntax error in JS
   - "Cannot read property" - JavaScript error

### Check Network Tab
1. Open Developer Tools (`F12`)
2. Go to "Network" tab
3. Refresh the page
4. Look for `/api/initial-data` request
5. Check its response:
   - Should return `success: true`
   - Should have `available_tags` array
   - Should have `total_records` count

### Check Service Worker
1. Open Developer Tools (`F12`)
2. Go to "Application" tab
3. Click "Service Workers" in left sidebar
4. Should see service worker with status "activated"
5. Cache Storage should show "labelmaker-static-v2"

## Manual Cache Clear (Nuclear Option)
If nothing else works:

```javascript
// Paste this in the browser console:
caches.keys().then(keys => {
    return Promise.all(keys.map(key => caches.delete(key)));
}).then(() => {
    return navigator.serviceWorker.getRegistrations();
}).then(registrations => {
    return Promise.all(registrations.map(r => r.unregister()));
}).then(() => {
    console.log('All caches and service workers cleared');
    window.location.reload(true);
});
```

## For Production (PythonAnywhere)
After uploading the new files:

1. **Clear Flask cache:**
   ```bash
   # In PythonAnywhere Bash console:
   rm -rf ~/mysite/__pycache__
   rm -rf ~/mysite/src/__pycache__
   ```

2. **Reload web app:**
   - Go to "Web" tab
   - Click "Reload" button

3. **Force browser cache clear:**
   - All users need to do hard refresh: `Cmd+Shift+R` or `Ctrl+Shift+R`
   - Or the auto-fixer will handle it on next page visit

## Files Modified
- `static/js/force-cache-clear.js` - Auto-detects and clears old cache
- `static/js/main.js` - Non-blocking tag loading
- `static/service-worker.js` - Updated to v2
- `templates/index.html` - Added force-cache-clear script

## Prevention
The service worker cache version is now v2. Future updates should increment this version number to force cache refresh:

In `static/service-worker.js`:
```javascript
const CACHE_NAME = 'labelmaker-v3';  // Increment on major changes
const STATIC_CACHE_NAME = 'labelmaker-static-v3';
const API_CACHE_NAME = 'labelmaker-api-v3';
```

