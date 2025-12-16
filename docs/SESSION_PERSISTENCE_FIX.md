# Session Persistence Fix - Store Selection Not Remembered

## Problem
After selecting a store on PythonAnywhere (www.agtpricetags.com), the page reloads but keeps showing the store selection modal again. Tags don't load and the user is stuck in a loop.

## Root Cause
Flask-Session wasn't properly configured before initialization. While config.py had SESSION_TYPE='filesystem', it wasn't being explicitly set on app.config before Session(app) was called, causing sessions to not persist properly on PythonAnywhere.

## Fix Applied

### Explicit Session Configuration (Lines 1233-1248)

**Before:**
```python
if Session:
    sessions_dir = app.config.get('SESSION_FILE_DIR')
    if sessions_dir:
        os.makedirs(sessions_dir, exist_ok=True)
    Session(app)
    logging.info("Flask-Session initialized with filesystem storage")
```

**After:**
```python
if Session:
    # CRITICAL FIX: Explicitly set session configuration before initializing
    sessions_dir = os.path.join(current_dir, 'sessions')
    os.makedirs(sessions_dir, exist_ok=True)
    
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = sessions_dir
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'labelmaker:'
    app.config['SESSION_FILE_THRESHOLD'] = 500
    
    Session(app)
    logging.info(f"Flask-Session initialized with filesystem storage at {sessions_dir}")
    logging.info(f"Session config: TYPE={app.config.get('SESSION_TYPE')}, DIR={app.config.get('SESSION_FILE_DIR')}")
```

### Added Debug Logging (Lines 4706-4711)

Added detailed session debugging to `/api/check-store-required`:
- Logs session['selected_store'] value
- Logs full session dictionary
- Logs session.permanent flag
- Returns debug info in API response

**Purpose:** Helps diagnose session issues on PythonAnywhere

## Session Configuration Details

### Key Settings:
- **SESSION_TYPE**: `'filesystem'` - Store sessions in files (persistent across restarts)
- **SESSION_FILE_DIR**: `./sessions/` - Directory for session files
- **SESSION_PERMANENT**: `False` - Sessions expire after browser close (unless marked permanent)
- **SESSION_USE_SIGNER**: `True` - Sign cookies to prevent tampering
- **SESSION_KEY_PREFIX**: `'labelmaker:'` - Prefix for session keys
- **SESSION_FILE_THRESHOLD**: `500` - Max number of session files to keep

### Session Directory:
- Location: `./sessions/`
- Created automatically if doesn't exist
- Contains one file per active session
- Files are named by session ID hash

## How It Works

### Store Selection Flow:
1. User clicks store button
2. Frontend calls `/api/set-store` with store name
3. Backend saves to `session['selected_store']` with `session.permanent = True`
4. Page reloads with `store_just_selected` flag
5. On reload, `/api/check-store-required` checks session
6. If store found → shows main content and loads tags
7. If not found → shows store modal again

### Session Persistence:
- **Filesystem storage** ensures sessions survive app restarts
- **Signed cookies** prevent session hijacking
- **12-hour expiration** (configurable via PERMANENT_SESSION_LIFETIME)

## Files Modified
- `app.py`
  - Session configuration (lines 1233-1248)
  - Debug logging (lines 4706-4756)

## Testing on PythonAnywhere

### To Deploy:
1. Push changes to GitHub
2. Pull on PythonAnywhere
3. Reload web app
4. Test store selection
5. Check logs at `/var/log/` for session debug info

### To Verify:
1. Select a store (e.g., AGT Bothell)
2. Page should reload and show tags
3. Refresh page - store should still be selected
4. Close browser and reopen - session may expire (normal behavior)

### Debug Console Commands:
```python
# Check session on PythonAnywhere
from app import app
with app.test_client() as client:
    with client.session_transaction() as sess:
        print(f"Session: {dict(sess)}")
        print(f"Store: {sess.get('selected_store')}")
```

## Potential Issues on PythonAnywhere

### If Still Not Working:
1. **Permissions**: Check that `sessions/` directory is writable
   ```bash
   chmod 755 sessions
   ls -la sessions
   ```

2. **Flask-Session Installation**: Ensure flask-session is installed
   ```bash
   pip install flask-session
   ```

3. **Session Files**: Check if session files are being created
   ```bash
   ls -la sessions/ | head
   ```

4. **Cookie Settings**: Browser might be blocking cookies
   - Check browser cookie settings
   - Try incognito/private mode
   - Check HTTPS/HTTP mismatch

5. **CORS Issues**: Check if cookies are being sent
   - Browser console → Network tab → Check request headers
   - Should see `Cookie: session=...`

## Date
November 6, 2025

