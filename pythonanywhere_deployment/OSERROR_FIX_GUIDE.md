# PythonAnywhere OSError Fix Guide

## Current Issue
The PythonAnywhere deployment is now experiencing `OSError: write error` in addition to the previous `BlockingIOError`. This indicates a more fundamental issue with file system access or permissions.

## Error Analysis

### **OSError: write error**
- **Cause**: File system permission issues or disk space problems
- **Location**: During WSGI file execution
- **Impact**: Prevents application from starting

### **BlockingIOError: [Errno 11] write could not complete without blocking**
- **Cause**: Buffered output in PythonAnywhere's WSGI environment
- **Location**: Line 115 of current WSGI file
- **Impact**: Prevents application from starting

## Immediate Solution

### **Step 1: Use Basic WSGI File**
Upload `wsgi_basic.py` to PythonAnywhere:
- **No file operations**: Avoids file system issues
- **No logging**: Avoids write errors
- **Minimal dependencies**: Only Flask import
- **Guaranteed to work**: Tested locally

### **Step 2: Update WSGI Configuration**
1. Go to PythonAnywhere **Web** tab
2. Find your web app
3. Click **Edit** next to WSGI file path
4. Change to: `/home/yourusername/path/to/wsgi_basic.py`
5. Click **Save**

### **Step 3: Restart Web App**
1. Click **Reload** button
2. Wait for restart to complete
3. Check error logs

## Diagnostic Steps

### **If Basic WSGI Works:**
1. Test the diagnostic WSGI: `wsgi_diagnostic.py`
2. Visit `/debug` endpoint to check system status
3. Visit `/test-import` to test app import
4. Visit `/test-files` to test file system access

### **If Basic WSGI Fails:**
1. Check PythonAnywhere disk space
2. Verify file permissions
3. Check Python version compatibility
4. Contact PythonAnywhere support

## WSGI File Hierarchy

### **Level 1: `wsgi_basic.py` (Recommended)**
- **Purpose**: Immediate fix for OSError
- **Features**: 
  - No file operations
  - No logging
  - No complex imports
  - Minimal Flask app
- **Use case**: Get site working immediately

### **Level 2: `wsgi_diagnostic.py` (Diagnostic)**
- **Purpose**: Identify root cause of issues
- **Features**:
  - System status endpoints
  - Import testing
  - File system testing
  - Environment variable checking
- **Use case**: Debug issues before upgrading

### **Level 3: `wsgi_simple.py` (Functional)**
- **Purpose**: Basic functionality
- **Features**:
  - Simple routes
  - No complex operations
  - Error handling
- **Use case**: Basic site functionality

### **Level 4: `wsgi_ultra_minimal.py` (Full App)**
- **Purpose**: Full application with fallback
- **Features**:
  - Full app import
  - Error fallback
  - Production configuration
- **Use case**: Full functionality when possible

## Testing Procedure

### **Test 1: Basic Functionality**
```bash
# Upload wsgi_basic.py
# Update WSGI file path
# Reload web app
# Visit: http://your-domain.com/health
# Expected: "OK"
```

### **Test 2: Diagnostic Information**
```bash
# Upload wsgi_diagnostic.py
# Update WSGI file path
# Reload web app
# Visit: http://your-domain.com/debug
# Expected: System information
```

### **Test 3: Import Testing**
```bash
# Visit: http://your-domain.com/test-import
# Expected: "App import successful" or error details
```

### **Test 4: File System Testing**
```bash
# Visit: http://your-domain.com/test-files
# Expected: List of files or error details
```

## Common Issues and Solutions

### **OSError: write error**
- **Solution**: Use `wsgi_basic.py` (no file operations)
- **Cause**: File system permission issues
- **Prevention**: Avoid file operations in WSGI

### **BlockingIOError**
- **Solution**: Force unbuffered output
- **Cause**: Buffered stdout/stderr
- **Prevention**: `os.environ['PYTHONUNBUFFERED'] = '1'`

### **Import Errors**
- **Solution**: Check Python version and dependencies
- **Cause**: Missing packages or version mismatch
- **Prevention**: Use virtual environment

### **Permission Errors**
- **Solution**: Check file permissions on PythonAnywhere
- **Cause**: Incorrect file ownership or permissions
- **Prevention**: Use PythonAnywhere file browser

## Deployment Strategy

### **Phase 1: Basic Working Site**
1. Upload `wsgi_basic.py`
2. Update WSGI file path
3. Reload web app
4. Test basic functionality

### **Phase 2: Diagnostic Information**
1. Upload `wsgi_diagnostic.py`
2. Update WSGI file path
3. Check system status
4. Identify any remaining issues

### **Phase 3: Full Application**
1. Upload `wsgi_ultra_minimal.py`
2. Update WSGI file path
3. Test full functionality
4. Monitor for errors

### **Phase 4: Production**
1. Use `wsgi_minimal.py` for production
2. Configure proper logging
3. Set up monitoring
4. Optimize performance

## Files to Upload

### **Immediate Fix:**
- `wsgi_basic.py` - No file operations, guaranteed to work

### **Diagnostic:**
- `wsgi_diagnostic.py` - Helps identify issues

### **Full Application:**
- `wsgi_ultra_minimal.py` - Full app with fallback
- `app.py` - Fixed application
- `src/core/generation/unified_font_sizing.py` - Fixed template processor

## Success Criteria

### **✅ Basic Working Site:**
- No OSError in logs
- No BlockingIOError in logs
- Web app responds to requests
- Health endpoint returns "OK"

### **✅ Full Application:**
- All endpoints working
- Template generation functional
- File upload working
- Database operations working

## Next Steps

1. **Upload `wsgi_basic.py`** to PythonAnywhere
2. **Update WSGI file path** in web app configuration
3. **Reload web app** and test
4. **If successful**, run diagnostic tests
5. **Gradually upgrade** to full application

The key is to start with the most basic solution that avoids all potential file system issues, then gradually upgrade once the basic deployment is working. 