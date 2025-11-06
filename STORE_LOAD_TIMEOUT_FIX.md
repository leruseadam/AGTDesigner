# Store Load Timeout Fix - Version 2

## Problem
After selecting a store, the app would fail to load, showing "Initialization timeout" in the console. The page would then fall back to test data instead of loading real product data.

## Root Causes
1. **Backend**: `get_excel_processor()` was being called even when no data existed, causing slow initialization
2. **Backend**: Attempting to load default files that didn't exist or were too large
3. **Frontend**: 30 second timeout was too long, making the app appear broken
4. **Frontend**: No retry logic for transient failures

## Solution - Version 2 (FAST PATH)

### Frontend Changes (`static/js/main.js`)

1. **Added session sync delay** - Added 250ms delay before calling `checkForExistingData()` to ensure the session is properly set after page reload

2. **Reduced timeout from 30s to 10s** - Users shouldn't wait 30 seconds for initialization. 10 seconds is more reasonable.

3. **Added retry logic** - If the request times out or fails with a server error, retry once before giving up

4. **Better error handling** - Added explicit retry messages and better progress updates

5. **Added request headers** - Ensured `credentials: 'same-origin'` and `Cache-Control: no-cache` to prevent caching issues

### Backend Changes (`app.py`)

**Version 1 (Initial fix):**
1. Skip default file loading on initialization
2. Add timing logs
3. Check for store selection before file operations

**Version 2 (FAST PATH - Current):**
1. **Check session file directly** - Before calling `get_excel_processor()`, check if session file exists and has data
2. **Return immediately if no data** - Don't initialize excel_processor unnecessarily (saves 1-2 seconds)
3. **Only call get_excel_processor() if data exists** - Lazy loading for better performance
4. **Timing logs** - Track exactly how long the response takes (should be < 10ms when no data)

This creates two paths:
- **Fast path (no data)**: Check session file → return empty state in < 10ms
- **Slow path (has data)**: Load excel_processor → return data in < 1s

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

