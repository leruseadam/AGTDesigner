# Lineage UI Hang Fix

## Problem
When users changed lineage values in the UI, the interface would hang/freeze because the code was:
1. Calling `fetchAndUpdateAvailableTags()` - refetching ALL available tags
2. Calling `fetchAndUpdateSelectedTags()` - refetching ALL selected tags
3. Making blocking `await fetch()` calls that froze the UI

## Solution
Optimized the lineage update flow to be non-blocking:

### 1. **tags_table.js** (handleLineageChange)
**Before:**
```javascript
// Always fetch latest tags from backend to ensure UI matches backend normalization
if (typeof TagManager !== 'undefined' && typeof TagManager.fetchAndUpdateAvailableTags === 'function') {
  await TagManager.fetchAndUpdateAvailableTags();
  console.log('✅ Refreshed available tags from backend after lineage update');
}
if (typeof TagManager !== 'undefined' && typeof TagManager.fetchAndUpdateSelectedTags === 'function') {
  await TagManager.fetchAndUpdateSelectedTags();
  console.log('✅ Refreshed selected tags from backend after lineage update');
}
```

**After:**
```javascript
// Update UI elements directly without full refresh (prevents hanging)
if (typeof TagManager !== 'undefined' && typeof TagManager.updateTagLineageInUI === 'function') {
  TagManager.updateTagLineageInUI(tagName, newLineage);
  console.log(`🎨 Updated lineage UI for ${tagName}`);
}

// Update similar products in the background (non-blocking)
if (typeof TagManager !== 'undefined' && typeof TagManager.updateSimilarLineages === 'function') {
  TagManager.updateSimilarLineages(tagName, newLineage);
  console.log(`🎨 Updated similar lineages for ${tagName}`);
}

// Refresh backend cache in the background (non-blocking)
setTimeout(async () => {
  try {
    if (typeof TagManager !== 'undefined' && typeof TagManager.refreshBackendCache === 'function') {
      await TagManager.refreshBackendCache();
      console.log('✅ Backend cache refreshed in background');
    }
  } catch (e) {
    console.warn('Background cache refresh failed:', e);
  }
}, 100);
```

### 2. **main.js** (updateLineageOnBackend)
**Before:**
```javascript
// CRITICAL: Force backend cache refresh after lineage update
try {
  // Fetch fresh data from backend to ensure lineage changes persist
  console.log('🔄 Fetching fresh tag data after lineage update...');
  const freshTagsResponse = await fetch('/api/available-tags?nocache=1&prefer_db=1&t=' + Date.now());
  if (freshTagsResponse.ok) {
    const freshData = await freshTagsResponse.json();
    console.log(`✅ Refreshed ${freshData.tags?.length || 0} tags from backend after lineage update`);
    
    // Update state with fresh data to ensure persistence
    if (freshData.tags && freshData.tags.length > 0) {
      this.state.originalTags = freshData.tags;
      console.log('✅ Backend cache refreshed with new lineage data');
    }
  }
} catch (refreshError) {
  console.warn('Could not refresh backend cache:', refreshError);
}
```

**After:**
```javascript
// CRITICAL: Refresh backend cache in background (non-blocking)
setTimeout(() => {
  this.refreshBackendCache();
}, 100);
```

### 3. **main.js** (Added refreshBackendCache method)
```javascript
// Refresh backend cache without blocking UI (for lineage updates)
async refreshBackendCache() {
  try {
    console.log('🔄 Refreshing backend cache in background...');
    const freshTagsResponse = await fetch('/api/available-tags?nocache=1&prefer_db=1&t=' + Date.now());
    if (freshTagsResponse.ok) {
      const freshData = await freshTagsResponse.json();
      console.log(`✅ Refreshed ${freshData.tags?.length || 0} tags from backend`);
      
      // Update state with fresh data to ensure persistence
      if (freshData.tags && freshData.tags.length > 0) {
        this.state.originalTags = freshData.tags;
        console.log('✅ Backend cache refreshed with new data');
      }
    }
  } catch (refreshError) {
    console.warn('Could not refresh backend cache:', refreshError);
  }
}
```

### 4. **service-worker.js** (Prevent caching mutation endpoints)
**Before:**
- All API endpoints were cached, including mutation endpoints
- Cache TTL was 5 minutes

**After:**
```javascript
// Handle API requests - network first, limited caching
if (url.pathname.startsWith('/api/')) {
  // Never cache mutation endpoints (update, save, delete, etc.)
  const isMutationEndpoint = url.pathname.includes('update') || 
                             url.pathname.includes('save') || 
                             url.pathname.includes('delete') ||
                             url.pathname.includes('upload');
  
  if (isMutationEndpoint) {
    console.log('[Service Worker] Not caching mutation endpoint:', url.pathname);
    event.respondWith(fetch(request));
    return;
  }
  
  // For read-only endpoints, use network-first with cache fallback
  // Cache TTL reduced to 2 minutes for faster updates
  ...
}
```

## Benefits
1. ✅ **No UI Hanging** - Lineage changes are now instant and responsive
2. ✅ **Instant Visual Feedback** - UI updates immediately without waiting for backend
3. ✅ **Background Sync** - Backend cache refreshes in background without blocking UI
4. ✅ **Better UX** - Users can continue working while updates happen in background
5. ✅ **No Stale Cache** - Service worker no longer caches mutation endpoints

## Files Modified
- `static/js/tags_table.js` - Made lineage changes non-blocking
- `static/js/main.js` - Added refreshBackendCache method, made updates non-blocking
- `static/service-worker.js` - Prevent caching of mutation endpoints

## Testing
1. Change a lineage value in any tag
2. UI should update instantly without hanging
3. Backend cache refreshes in background (check console logs)
4. Similar products are updated automatically

