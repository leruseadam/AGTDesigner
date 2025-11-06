# Store Load Timeout Fix

## Problem
After selecting a store, the app would sometimes fail to load, showing "Initialization timeout" in the console. The page would then fall back to test data instead of loading real product data.

## Root Cause
When a store was selected:
1. The page would reload to sync the session
2. On reload, `TagManager.init()` would call `checkForExistingData()`
3. `checkForExistingData()` would call `/api/initial-data`
4. The backend would try to load a default Excel file for the selected store
5. Loading the default file could take 30+ seconds, causing the frontend to timeout
6. The app would fall back to test data, appearing broken to the user

## Solution

### Frontend Changes (`static/js/main.js`)

1. **Added session sync delay** - Added 250ms delay before calling `checkForExistingData()` to ensure the session is properly set after page reload

2. **Reduced timeout from 30s to 10s** - Users shouldn't wait 30 seconds for initialization. 10 seconds is more reasonable.

3. **Added retry logic** - If the request times out or fails with a server error, retry once before giving up

4. **Better error handling** - Added explicit retry messages and better progress updates

5. **Added request headers** - Ensured `credentials: 'same-origin'` and `Cache-Control: no-cache` to prevent caching issues

### Backend Changes (`app.py`)

1. **Skip default file loading** - Instead of trying to load a potentially large default file on every initialization, return quickly with an empty state. Users can upload files explicitly.

2. **Better logging** - Added timing information to help diagnose slow operations:
   - Log session ID and store selection
   - Time file search operations
   - Time file loading operations
   - Log exception details

3. **Early validation** - Check if store is selected before attempting any file operations

## Testing

Test the fix by:
1. Reload the app
2. Select a store (e.g., AGT Bothell)
3. Verify the app loads within 2-3 seconds
4. Check console for proper initialization messages
5. Upload an Excel file to populate with real data

## Expected Behavior After Fix

- App loads quickly (< 3 seconds) after store selection
- No more "Initialization timeout" errors
- Clean console logs showing successful initialization
- Ready to accept file uploads immediately
- Retry logic handles intermittent network issues

## Monitoring

Check the Flask logs for timing information:
```
Store from session: AGT_Bothell
No data loaded - returning empty state for faster initialization
```

This confirms the fast path is being taken.

