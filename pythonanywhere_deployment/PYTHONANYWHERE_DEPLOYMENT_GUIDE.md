# PythonAnywhere Deployment Guide

## Current Issue
The PythonAnywhere deployment is experiencing `BlockingIOError` due to buffered output in the WSGI environment. The current WSGI file on PythonAnywhere hasn't been updated with our fixes.

## Immediate Solution

### **Step 1: Upload the Fixed Files**
Upload these files to your PythonAnywhere account:

1. **`wsgi_simple.py`** (Recommended for immediate fix)
2. **`wsgi_ultra_minimal.py`** (Alternative)
3. **`app.py`** (Fixed version)
4. **`src/core/generation/unified_font_sizing.py`** (Fixed syntax)

### **Step 2: Update WSGI File Path**
In your PythonAnywhere web app configuration:

1. Go to **Web** tab
2. Find your web app
3. Click **Edit** next to the WSGI file path
4. Change to: `/home/yourusername/path/to/wsgi_simple.py`
5. Click **Save**

### **Step 3: Restart Web App**
1. Click **Reload** button for your web app
2. Wait for the restart to complete
3. Check the error logs

## WSGI File Options

### **Option 1: `wsgi_simple.py` (Recommended)**
- **Purpose**: Immediate fix with minimal Flask app
- **Features**: 
  - No complex imports
  - No print statements
  - Forces unbuffered output
  - Always works
- **Use case**: Quick fix to get the site working

### **Option 2: `wsgi_ultra_minimal.py`**
- **Purpose**: Full application with error handling
- **Features**:
  - Imports your full app
  - Error fallback if import fails
  - Production configuration
- **Use case**: Full functionality when app imports work

### **Option 3: `wsgi_minimal.py`**
- **Purpose**: Balanced approach
- **Features**:
  - Full app import
  - Robust error handling
  - Minimal complexity
- **Use case**: Best long-term solution

## Step-by-Step Deployment

### **Phase 1: Quick Fix (Immediate)**
```bash
# 1. Upload wsgi_simple.py to PythonAnywhere
# 2. Update WSGI file path to point to wsgi_simple.py
# 3. Reload web app
# 4. Test: http://your-domain.com/health
```

### **Phase 2: Full Application (After Phase 1 works)**
```bash
# 1. Upload all fixed files
# 2. Update WSGI file path to wsgi_ultra_minimal.py
# 3. Reload web app
# 4. Test full functionality
```

### **Phase 3: Production (After Phase 2 works)**
```bash
# 1. Use wsgi_minimal.py for production
# 2. Configure proper logging
# 3. Set up monitoring
```

## File Upload Instructions

### **Using PythonAnywhere File Browser:**
1. Go to **Files** tab
2. Navigate to your project directory
3. Upload the WSGI files
4. Upload the fixed app.py
5. Upload the fixed template processor

### **Using Git (Recommended):**
```bash
# On PythonAnywhere console:
cd /home/yourusername/your-project
git pull origin main
```

## Testing Steps

### **Test 1: Basic WSGI Loading**
```bash
# On PythonAnywhere console:
python wsgi_simple.py
# Should show: "Simple WSGI test successful"
```

### **Test 2: Web App Response**
```bash
# Visit in browser:
http://your-domain.com/health
# Should return: "OK"
```

### **Test 3: Full Application**
```bash
# Visit in browser:
http://your-domain.com/
# Should show Label Maker interface
```

## Troubleshooting

### **If BlockingIOError persists:**
1. Use `wsgi_simple.py` (guaranteed to work)
2. Check PythonAnywhere error logs
3. Verify file paths are correct
4. Restart web app

### **If import errors occur:**
1. Check Python version compatibility
2. Verify all dependencies are installed
3. Use `wsgi_simple.py` as fallback
4. Check file permissions

### **If app loads but doesn't work:**
1. Check application logs
2. Verify database connections
3. Test individual components
4. Use error fallback routes

## Error Log Analysis

### **Current Error Pattern:**
```
BlockingIOError: [Errno 11] write could not complete without blocking
  File "/var/www/www_agtpricetags_com_wsgi.py", line 115, in <module>
    print(f"✗ Error creating application: {e}")
```

### **This indicates:**
- Current WSGI file has print statements
- Buffering is causing blocking
- Need to use our fixed WSGI files

## Success Criteria

### **✅ Working Deployment:**
- No BlockingIOError in logs
- Web app responds to requests
- Health endpoint returns "OK"
- Full application functionality works

### **✅ Production Ready:**
- Proper error handling
- Logging configured
- Performance optimized
- Security configured

## Files Summary

| File | Purpose | Use Case |
|------|---------|----------|
| `wsgi_simple.py` | Immediate fix | Get site working quickly |
| `wsgi_ultra_minimal.py` | Full app with fallback | Full functionality |
| `wsgi_minimal.py` | Production ready | Long-term deployment |
| `app.py` | Fixed application | Core functionality |
| `unified_font_sizing.py` | Fixed template processor | Template generation |

## Next Steps

1. **Upload `wsgi_simple.py`** to PythonAnywhere
2. **Update WSGI file path** in web app configuration
3. **Reload web app** and test
4. **If successful**, upgrade to full application
5. **Monitor logs** for any remaining issues

The key is to start with the simplest working solution (`wsgi_simple.py`) and then gradually upgrade to the full application once the basic deployment is working. 