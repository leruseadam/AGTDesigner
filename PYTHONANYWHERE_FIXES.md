# PythonAnywhere Fixes

This document tracks fixes applied to make the app work properly on PythonAnywhere.

## Issue 1: File Upload Not Working Until Page Refresh

**Problem:** File upload functionality doesn't work on first page load, only after refreshing the page.

**Root Cause:** 
- The file upload event listener was being attached before `TagManager` (from `main.js`) was fully loaded
- PythonAnywhere's slower script loading/caching caused a race condition where the event listener tried to call `window.TagManager.uploadFile()` before the method existed

**Fixes Applied:**

### 1. Improved File Upload Initialization (templates/index.html)
- Added retry mechanism that waits for `TagManager` to be fully loaded
- Checks for both `window.TagManager` existence AND `uploadFile` method availability
- Automatically retries every 100ms until TagManager is ready
- Added error handling with user-friendly alert messages

**Code Location:** `templates/index.html` lines 6702-6735

```javascript
function initializeFileUpload() {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput) {
    console.error('fileInput element not found');
    return;
  }
  
  // Check if TagManager and uploadFile method are available
  if (window.TagManager && typeof window.TagManager.uploadFile === 'function') {
    console.log('✓ TagManager ready, attaching file upload listener');
    
    fileInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        console.log('File selected:', file.name);
        try {
          window.TagManager.uploadFile(file);
        } catch (error) {
          console.error('Error uploading file:', error);
          alert('Error uploading file. Please try again or refresh the page.');
        }
      }
    });
  } else {
    console.warn('TagManager not ready yet, retrying in 100ms...');
    setTimeout(initializeFileUpload, 100);
  }
}

initializeFileUpload();
```

### 2. Added Cache Control Headers (app.py)
- Prevents PythonAnywhere from aggressively caching JavaScript/CSS/HTML files
- Ensures latest version of files are always loaded
- Forces browser to check for updated files on each request

**Code Location:** `app.py` lines 1474-1485

```python
@app.after_request
def add_cache_control_headers(response):
    """Add cache control headers to prevent aggressive caching on PythonAnywhere."""
    # Don't cache JavaScript, CSS, or HTML files
    if (response.content_type and 
        ('javascript' in response.content_type or 
         'css' in response.content_type or 
         'html' in response.content_type)):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response
```

### 3. Existing Cache Busting
- Already had cache busting query parameters: `?v={{ cache_bust }}`
- `cache_bust` is a timestamp that changes on each page load
- Combined with new headers for maximum effectiveness

**Status:** ✅ Fixed - File upload should now work on first page load

---

## Testing Checklist for PythonAnywhere

After deploying, test these scenarios:

- [ ] Fresh page load → file upload works immediately
- [ ] After browser cache clear → file upload works
- [ ] After code update → JavaScript loads new version (not cached)
- [ ] Multiple rapid uploads → no errors
- [ ] Large file upload (> 100MB) → works with progress indicator
- [ ] Network interruption during upload → shows appropriate error

---

## Additional PythonAnywhere Considerations

### Static File Serving
PythonAnywhere uses its own static file serving. Make sure static files mapping is configured in the Web app settings:

```
URL: /static/
Directory: /home/yourusername/your-project/static/
```

### WSGI Configuration
Ensure your WSGI file properly imports the Flask app:

```python
import sys
path = '/home/yourusername/your-project'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### Reloading Web App
After making changes, always reload your web app:
- Go to Web tab
- Click the big green "Reload" button
- Wait for reload to complete before testing

### Console Debugging
Use browser console (F12) to check for:
- `✓ TagManager ready` message
- Any JavaScript errors
- Upload progress logs

---

## Future Issues to Watch For

1. **Session Management**: PythonAnywhere has different session handling than local Flask
2. **File Paths**: Make sure all paths are absolute or properly resolved
3. **Database Locking**: SQLite can have locking issues with multiple concurrent requests
4. **Memory Limits**: Free tier has memory limits, may need to optimize large file processing
5. **Worker Timeouts**: Long-running requests may timeout (configure in WSGI/uwsgi settings)

---

## Performance Optimizations Applied

1. **DISABLE_STARTUP_FILE_LOADING**: Set to True to speed up app startup
2. **Caching**: Flask caching with fallback if Redis not available  
3. **Lazy Loading**: Excel processor loads on-demand rather than startup
4. **Optimized Queries**: Product database uses indexed queries

---

## Deployment Checklist

- [x] File upload initialization fixed
- [x] Cache control headers added
- [x] Cache busting query parameters in place
- [ ] Test on PythonAnywhere after deployment
- [ ] Monitor error logs for issues
- [ ] Set up database backup schedule

---

## Contact & Support

If you encounter issues after deploying:

1. Check browser console for errors (F12)
2. Check PythonAnywhere error log
3. Check Flask application logs
4. Reload web app from Web tab

For PythonAnywhere-specific issues:
- https://www.pythonanywhere.com/forums/
- help@pythonanywhere.com

