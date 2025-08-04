# Upload Troubleshooting Guide for PythonAnywhere

## Common Upload Issues and Solutions

### 1. File Permissions Issues

**Problem**: Files can't be saved to upload directory
**Solution**: Fix directory permissions

```bash
# On PythonAnywhere console
cd /home/adamcordova/AGTDesigner

# Fix upload directory permissions
chmod 777 uploads
chmod 777 output
chmod 777 cache
chmod 777 logs

# Verify permissions
ls -la uploads/
```

### 2. Directory Doesn't Exist

**Problem**: Upload directory missing
**Solution**: Create required directories

```bash
# Create all required directories
mkdir -p uploads
mkdir -p output
mkdir -p cache
mkdir -p logs
mkdir -p static
mkdir -p templates
```

### 3. Flask Configuration Issues

**Problem**: Upload folder not configured correctly
**Solution**: Check app configuration

```python
# In your app.py, ensure these settings:
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### 4. Virtual Environment Issues

**Problem**: Dependencies not available
**Solution**: Activate virtual environment

```bash
# Activate virtual environment
workon AGTDesigner

# Verify dependencies
pip list | grep -E "(Flask|pandas|openpyxl)"
```

### 5. Web App Configuration Issues

**Problem**: Static files not configured
**Solution**: Configure static files in PythonAnywhere

In the **Web** tab, add these static file mappings:
- URL: `/uploads/` → Directory: `/home/adamcordova/AGTDesigner/uploads/`
- URL: `/output/` → Directory: `/home/adamcordova/AGTDesigner/output/`
- URL: `/static/` → Directory: `/home/adamcordova/AGTDesigner/static/`

### 6. File Size Limits

**Problem**: Files too large
**Solution**: Increase file size limits

```python
# In app.py, increase max file size
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### 7. File Type Validation

**Problem**: Only .xlsx files allowed
**Solution**: Ensure file is Excel format

The application only accepts `.xlsx` files. Make sure your file:
- Has `.xlsx` extension
- Is a valid Excel file
- Is not corrupted

### 8. Background Processing Issues

**Problem**: File uploads but processing fails
**Solution**: Check background processing

```bash
# Check if background processing is working
python -c "
from app import app
with app.test_client() as client:
    response = client.get('/api/status')
    print('Status:', response.get_json())
"
```

## Quick Fix Script

Run the upload fix script to automatically diagnose and fix issues:

```bash
# On PythonAnywhere console
cd /home/adamcordova/AGTDesigner
python fix_upload_issues.py
```

## Manual Testing Steps

### Step 1: Test Directory Permissions
```bash
# Check if uploads directory exists and is writable
ls -la uploads/
touch uploads/test.txt
rm uploads/test.txt
```

### Step 2: Test Flask App
```bash
# Test if Flask app loads correctly
python -c "from app import app; print('App loaded successfully')"
```

### Step 3: Test Upload Endpoint
```bash
# Create a test file
python -c "
import pandas as pd
df = pd.DataFrame({'test': [1, 2, 3]})
df.to_excel('test.xlsx', index=False)
print('Test file created')
"

# Test upload
python -c "
from app import app
with app.test_client() as client:
    with open('test.xlsx', 'rb') as f:
        response = client.post('/upload', data={'file': ('test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
        print('Upload response:', response.get_json())
"
```

## Error Messages and Solutions

### "No file uploaded"
- **Cause**: File not selected or form data missing
- **Solution**: Ensure file is selected in the upload form

### "File too large"
- **Cause**: File exceeds size limit
- **Solution**: Reduce file size or increase limit in app configuration

### "Only .xlsx files are allowed"
- **Cause**: Wrong file format
- **Solution**: Convert file to Excel (.xlsx) format

### "Failed to save file"
- **Cause**: Permission or disk space issues
- **Solution**: Check directory permissions and disk space

### "Processing timeout"
- **Cause**: File too large or processing too slow
- **Solution**: Use smaller files or optimize processing

## PythonAnywhere Specific Issues

### 1. Disk Space
```bash
# Check disk space
df -h
```

### 2. Memory Limits
```bash
# Check memory usage
free -h
```

### 3. Process Limits
```bash
# Check running processes
ps aux | grep python
```

### 4. Log Files
```bash
# Check error logs
tail -f /var/log/adamcordova.pythonanywhere.com.error.log
```

## Web App Configuration Checklist

1. **Virtual Environment**: Set to `/home/adamcordova/.virtualenvs/AGTDesigner`
2. **Source Code**: Set to `/home/adamcordova/AGTDesigner`
3. **WSGI File**: Configured correctly
4. **Static Files**: Mapped properly
5. **Reload**: Clicked after changes

## Testing Upload Functionality

### Browser Test
1. Go to your PythonAnywhere URL
2. Click "Choose File" or drag file to upload area
3. Select an Excel file (.xlsx)
4. Click upload
5. Check for success/error messages

### API Test
```bash
# Test upload via curl
curl -X POST -F "file=@test.xlsx" https://adamcordova.pythonanywhere.com/upload
```

## Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Permission denied | `chmod 777 uploads/` |
| Directory missing | `mkdir -p uploads/` |
| Dependencies missing | `pip install -r requirements_pythonanywhere_py310.txt` |
| Virtual env not active | `workon AGTDesigner` |
| Static files not working | Configure in Web tab |
| File too large | Increase `MAX_CONTENT_LENGTH` |
| Wrong file type | Convert to .xlsx format |

## Still Having Issues?

If the upload still doesn't work after trying these solutions:

1. **Check PythonAnywhere error logs** in the Web tab
2. **Run the fix script**: `python fix_upload_issues.py`
3. **Test with a simple file** first
4. **Verify all dependencies** are installed
5. **Check web app configuration** is correct

## Support

For additional help:
1. Check the PythonAnywhere error logs
2. Run the diagnostic script
3. Test with a minimal file
4. Verify all configuration steps 