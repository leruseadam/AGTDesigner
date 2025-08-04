# PythonAnywhere File Upload Fix Guide

## 🚨 Problem
Your PythonAnywhere web version works, but file upload fails. This is a common issue due to:
- Directory permissions
- File path configuration
- WSGI configuration
- Environment variables

## 🔧 Solution

### Step 1: Upload the Fixed Files to PythonAnywhere

1. **Upload these files to your PythonAnywhere project:**
   - `wsgi_pythonanywhere.py` (new optimized WSGI file)
   - Updated `app.py` (with PythonAnywhere-specific configuration)
   - `fix_pythonanywhere_upload.py` (diagnostic script)

### Step 2: Run the Fix Script on PythonAnywhere

1. **Open PythonAnywhere Bash Console**
2. **Navigate to your project directory:**
   ```bash
   cd /home/yourusername/yourproject
   ```

3. **Run the fix script:**
   ```bash
   python fix_pythonanywhere_upload.py
   ```

4. **Run the test script:**
   ```bash
   python test_pythonanywhere_upload.py
   ```

### Step 3: Update WSGI Configuration

1. **Go to PythonAnywhere Web tab**
2. **Click on your web app**
3. **Click on the WSGI configuration file link**
4. **Replace the content with the content from `wsgi_pythonanywhere.py`**

### Step 4: Set Environment Variables

1. **In the Web tab, go to Environment variables**
2. **Add these variables:**
   ```
   PYTHONANYWHERE=true
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```

### Step 5: Reload Web App

1. **Click the "Reload" button in the Web tab**
2. **Check the error logs if there are any issues**

## 🔍 What the Fix Does

### 1. Directory Permissions
- Creates `uploads/` directory with proper permissions (755)
- Creates `output/`, `cache/`, `logs/`, `temp/` directories
- Sets correct file permissions for PythonAnywhere

### 2. PythonAnywhere-Specific Configuration
- Detects PythonAnywhere environment automatically
- Sets appropriate file size limits (50MB max)
- Configures upload paths correctly
- Optimizes memory usage

### 3. WSGI Configuration
- Proper virtual environment activation
- Environment variable setup
- Error handling and logging
- File upload support

### 4. Error Handling
- Comprehensive error logging
- Graceful failure recovery
- User-friendly error messages

## 🧪 Testing

### Test File Upload
1. Go to your web app URL
2. Try uploading an Excel (.xlsx) file
3. Check the browser console for errors
4. Check PythonAnywhere error logs

### Test API Endpoints
```bash
# Test basic functionality
curl https://yourusername.pythonanywhere.com/api/status

# Test upload endpoint
curl -X POST -F "file=@test.xlsx" https://yourusername.pythonanywhere.com/upload
```

## 🐛 Troubleshooting

### Common Issues:

#### 1. "Permission Denied" Errors
```bash
# Check directory permissions
ls -la uploads/
# Should show: drwxr-xr-x

# Fix permissions if needed
chmod 755 uploads/
```

#### 2. "File Not Found" Errors
```bash
# Check if uploads directory exists
ls -la | grep uploads

# Create if missing
mkdir -p uploads
chmod 755 uploads
```

#### 3. "Import Error" in WSGI
- Make sure you're using `wsgi_pythonanywhere.py`
- Check that all dependencies are installed
- Verify the virtual environment path

#### 4. "Upload Failed" in Browser
- Check browser console for JavaScript errors
- Check PythonAnywhere error logs
- Verify file size is under 50MB
- Ensure file is .xlsx format

### Debug Commands

```bash
# Check PythonAnywhere environment
python -c "import os; print('PYTHONANYWHERE:', os.environ.get('PYTHONANYWHERE'))"

# Test file creation
python -c "import os; open('uploads/test.txt', 'w').write('test'); print('File creation OK')"

# Test Flask app import
python -c "from app import create_app; app = create_app(); print('Flask app OK')"
```

## 📁 File Structure After Fix

```
/home/yourusername/yourproject/
├── app.py                          # Updated with PythonAnywhere config
├── wsgi_pythonanywhere.py          # New optimized WSGI file
├── fix_pythonanywhere_upload.py    # Diagnostic script
├── test_pythonanywhere_upload.py   # Test script
├── uploads/                        # Upload directory (755 permissions)
├── output/                         # Output directory
├── cache/                          # Cache directory
├── logs/                           # Logs directory
├── temp/                           # Temp directory
└── venv_pythonanywhere/           # Virtual environment
```

## ✅ Success Indicators

After applying the fix, you should see:

1. **✅ Uploads directory exists with 755 permissions**
2. **✅ Flask app imports successfully**
3. **✅ File upload works in web interface**
4. **✅ No permission errors in logs**
5. **✅ API endpoints respond correctly**

## 🚀 Performance Optimizations

The fix includes these optimizations:

- **Memory Management**: Automatic garbage collection
- **File Size Limits**: 50MB max for PythonAnywhere
- **Chunked Reading**: For large files
- **Caching**: Reduced cache size for PythonAnywhere
- **Error Recovery**: Graceful handling of failures

## 📞 Support

If you still have issues:

1. **Check the error logs** in PythonAnywhere Web tab
2. **Run the diagnostic script** again
3. **Verify all files are uploaded** correctly
4. **Check file permissions** on all directories

---

**🎉 Your PythonAnywhere file upload should now work correctly!** 