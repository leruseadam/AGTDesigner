# File Persistence Fix - Uploaded Files No Longer Disappear on Refresh

## Date: October 12, 2025

## Problem

When users uploaded an Excel file on PythonAnywhere and then refreshed the page, the uploaded file would disappear and the application would revert to the default file from the Downloads folder.

### User Experience Before Fix:
1. User uploads their Excel file ✅
2. File loads and tags appear ✅  
3. User refreshes the page 🔄
4. **Uploaded file disappears** ❌
5. Application loads default file instead ❌
6. User loses all their uploaded data ❌

## Root Cause

The `/api/initial-data` endpoint was not checking the session for uploaded files before loading the default file. When the page refreshed:

1. Frontend called `/api/initial-data`
2. Backend checked if data was loaded
3. If empty, it **immediately loaded the default file** 
4. Session file was never checked
5. User's uploaded file was ignored

### Code Flow Before Fix:
```python
def get_initial_data():
    excel_processor = get_excel_processor()
    
    if excel_processor.df is None:
        # ❌ Directly loads default file, ignoring session
        default_file = get_default_upload_file()
        excel_processor.load_file(default_file)
```

## Solution

### 1. **Changed Priority in `/api/initial-data`**

Now checks session FIRST, then falls back to default file:

```python
def get_initial_data():
    excel_processor = get_excel_processor()
    
    if excel_processor.df is None or excel_processor.df.empty:
        # ✅ PRIORITY 1: Check session for uploaded file
        session_file_path = session.get('file_path')
        if session_file_path and os.path.exists(session_file_path):
            excel_processor.load_file(session_file_path)
        else:
            # ✅ PRIORITY 2: Load default file only if no session file
            default_file = get_default_upload_file()
            excel_processor.load_file(default_file)
```

### 2. **Added Session Persistence to ALL Upload Endpoints**

Ensured all upload endpoints properly set session flags:

```python
# Before (some endpoints):
session['file_path'] = file_path

# After (all endpoints):
session.permanent = True          # ✅ Makes session persistent
session['file_path'] = file_path
session['uploaded_filename'] = filename
session['selected_tags'] = []
session.modified = True          # ✅ Forces session save
```

### Endpoints Fixed:
- `/upload` ✅
- `/upload-pythonanywhere` ✅
- `/upload-simple` ✅
- `/upload-optimized` ✅
- `/upload-fast` ✅

## How It Works Now

### Session Configuration:
```python
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
```

### File Upload Flow:
1. User uploads file
2. File saved to `/uploads/` folder
3. Session updated:
   - `session.permanent = True` (persists across requests)
   - `session['file_path']` = uploaded file path
   - `session['uploaded_filename']` = filename
   - `session.modified = True` (saves immediately)

### Page Refresh Flow:
1. User refreshes page
2. Frontend calls `/api/initial-data`
3. Backend checks session:
   - **Found uploaded file?** → Load that ✅
   - **No uploaded file?** → Load default file ✅
4. User's uploaded file persists! 🎉

## Benefits

### ✅ Session Persistence
- Uploaded files persist across page refreshes
- Session lasts 1 hour (configurable)
- Works on both local and PythonAnywhere

### ✅ Better User Experience
- No data loss on refresh
- Seamless workflow
- Users can refresh without losing work

### ✅ Proper Priority
- User uploads > Default files
- Explicit session checking
- Clear fallback logic

### ✅ Logging
- Clear logs showing which file is loaded
- Easy to debug session issues
- Visible in PythonAnywhere error logs

## Files Modified

**`app.py`:**
- Lines 10136-10191: Updated `/api/initial-data` endpoint
- Lines 1658-1660, 1881-1885: Added session persistence to upload endpoints
- Lines 1964-1968, 11660-11663, 11745-11749: Session persistence for all upload variants

## Testing

### Test Case 1: Upload and Refresh
1. Upload Excel file ✅
2. Verify file loads ✅
3. Refresh page ✅
4. **Verify uploaded file still loaded** ✅

### Test Case 2: Session Expiration
1. Upload file
2. Wait > 1 hour
3. Refresh page
4. Should load default file (session expired) ✅

### Test Case 3: Multiple Users
1. User A uploads file A
2. User B uploads file B
3. Each user sees their own file ✅
4. No cross-contamination ✅

## Deployment

### For PythonAnywhere:

**Quick Deploy:**
```bash
cd /home/adamcordova/AGTDesigner
git pull origin main
```

**Then Reload:**
1. Go to Web tab
2. Click "Reload" button
3. Wait 15 seconds

**Test:**
1. Upload a file
2. Refresh the page (Ctrl+R or F5)
3. Verify file is still loaded
4. Check logs: Should see "✅ Found uploaded file in session"

## Session Storage

Sessions are stored in the `sessions/` folder:
```
/sessions/
  ├── 2029240f6d1128be89ddc32729463129  (session file)
  └── ...
```

Each session file contains:
- `file_path`: Path to uploaded file
- `uploaded_filename`: Original filename
- `selected_tags`: User's selected tags
- Expiration timestamp

## Troubleshooting

### Issue: File still disappears after refresh

**Check:**
1. Session folder exists: `/sessions/`
2. Session folder is writable
3. `SESSION_TYPE = 'filesystem'` in config
4. Check error logs for session errors

**On PythonAnywhere:**
```bash
ls -la /home/adamcordova/AGTDesigner/sessions/
```

### Issue: Session not persisting

**Check:**
1. All upload endpoints set `session.permanent = True`
2. All upload endpoints set `session.modified = True`
3. Check `PERMANENT_SESSION_LIFETIME` value
4. Verify session folder permissions

### Issue: Wrong file loads

**Check logs for:**
```
✅ Found uploaded file in session: /path/to/uploaded/file.xlsx
```

If you see:
```
No uploaded file in session, attempting to load default file
```

Then session is not being set properly during upload.

## Additional Notes

- Session lifetime: 1 hour (3600 seconds)
- After 1 hour of inactivity, session expires
- On session expiry, application loads default file
- User can upload new file to override
- Sessions are per-user, not shared

## Commit

```
Commit: 67161127
Message: Fix file persistence issue: uploaded files now persist after page refresh
Branch: main
```

---

**Status:** ✅ Fixed and Deployed to GitHub

**Next Step:** Deploy to PythonAnywhere with `git pull origin main` and reload

