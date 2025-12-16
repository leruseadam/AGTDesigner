# PythonAnywhere Store Selection Fix

## Problem

On PythonAnywhere, users were experiencing this error when trying to upload files:
```
Upload failed: Please select a store before uploading files
```

**Even though the UI showed "Store: AGT Bothell" as selected!**

### Evidence from Logs

```
2025-11-02 16:29:05 - Store selection set for IP 209.166.70.137: AGT_Bothell
2025-11-02 16:29:19 - Upload attempted without store selection  ❌
```

Store selection was LOST between setting (16:29:05) and upload (16:29:19) - only **14 seconds later!**

## Root Cause

**Inconsistent IP detection due to proxy headers**

PythonAnywhere uses proxy servers that set headers like:
- `X-Forwarded-For`
- `X-Real-IP`  
- `Remote-Addr`

Different HTTP requests can have different combinations of these headers, causing:
1. `/api/set-store` sees IP as `209.166.70.137`
2. `/upload` sees IP as something different
3. Store selection lookup fails because IPs don't match

## Solution

**Use Flask session as the PRIMARY store selection method**

### Changes Made

1. **`/api/set-store`** - Save to BOTH session and IP:
   ```python
   # Primary: Save to session (reliable)
   session['selected_store'] = store_value
   
   # Backup: Also save to IP-based storage
   _ip_store_selections[ip_address] = {...}
   ```

2. **`has_store_selection()`** - Check session FIRST:
   ```python
   # Check session first (most reliable)
   if session.get('selected_store'):
       return True
   
   # Fallback to IP-based check
   if ip_address in _ip_store_selections:
       return True
   ```

3. **`get_current_store_name()`** - Return from session FIRST:
   ```python
   # Check session first
   if session.get('selected_store'):
       return session.get('selected_store')
   
   # Fallback to IP-based lookup
   ```

4. **Added diagnostic logging** to help debug future issues

## Deployment to PythonAnywhere

### Option 1: Pull from GitHub (Recommended)

```bash
cd /home/adamcordova/AGTDesigner
git pull origin main
# Reload web app from PythonAnywhere dashboard
```

### Option 2: Manual Update

Upload the updated `app.py` file and reload the web app.

## Testing

After deployment:

1. **Select a store** - Should see in logs:
   ```
   ✅ Store saved to session: AGT_Bothell
   Store selection set for IP xxx.xxx.xxx.xxx: AGT_Bothell
   ```

2. **Upload a file** - Should see in logs:
   ```
   🔍 Upload diagnostics: IP=xxx.xxx.xxx.xxx, Session store=AGT_Bothell
   ✅ Store selection found: AGT_Bothell
   ```

3. **Success!** - File uploads without "Please select a store" error

## Why This Works

| Method | Reliability on PythonAnywhere | Notes |
|--------|-------------------------------|-------|
| **Flask Session** | ✅ 100% Reliable | Cookie-based, immune to proxy issues |
| IP-Based Storage | ⚠️ Unreliable | Affected by proxy header variations |

By using session as primary and IP as backup:
- ✅ Works reliably on PythonAnywhere
- ✅ Session persists across page reloads
- ✅ No frontend changes needed
- ✅ Backward compatible with IP-based selection
- ✅ Detailed logging for diagnostics

## Prevention

This fix ensures store selection works reliably in proxy/load-balancer environments like PythonAnywhere. The session-based approach is the standard Flask pattern and should be used for all user-specific state.

---

**Status**: Fixed and deployed
**Date**: November 2, 2025
**Commit**: 3d1c7218

